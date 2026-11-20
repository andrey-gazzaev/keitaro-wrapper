"""Edit offer shares for one stored campaign."""

from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.models.offer import Offer
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_editor import StreamEditor
from app.campaigns.models.stream_group import StreamGroup
from app.campaigns.models.stream_line import StreamLine
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.offer_record import OfferRecord
from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_record import StreamRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroDep, KeitaroService
from app.campaigns.services.stream_editor_error import StreamEditorError
from app.db import SessionDep

_HUNDRED = Decimal("100")
_CENT = Decimal("0.01")


class StreamEditorService:
    """The only writer of editor streams and offer bindings."""

    def __init__(self, session: Session, keitaro: KeitaroService) -> None:
        """An editor for one database session and one Keitaro service."""
        self._session = session
        self._keitaro = keitaro

    def get(self, campaign_id: int) -> StreamEditor:
        """Editor state for this campaign. Streams are empty before the first fetch."""
        self._campaign(campaign_id)

        return self._editor(campaign_id)

    def fetch(self, campaign_id: int) -> StreamEditor:
        """Editor state after reading this campaign's flows. Empty when Keitaro has none."""
        try:
            return self._fetch(campaign_id)
        except KeitaroError as error:
            raise StreamEditorError(error.kind) from None

    def find_offer(self, campaign_id: int, offer_id: int) -> Offer:
        """The Keitaro offer for this id. Missing when the campaign or the offer is gone."""
        try:
            self._campaign(campaign_id)

            return self._keitaro.get_offer(offer_id)
        except KeitaroError as error:
            raise StreamEditorError(error.kind) from None

    def add(self, campaign_id: int, stream_id: int, offer_id: int) -> StreamEditor:
        """Editor state after binding this offer. The new row has no published snapshot."""
        try:
            return self._add(campaign_id, stream_id, offer_id)
        except KeitaroError as error:
            raise StreamEditorError(error.kind) from None

    def remove(self, campaign_id: int, binding_id: int) -> StreamEditor:
        """Editor state after this live binding is archived at share 0."""
        return self._remove(campaign_id, binding_id)

    def bring_back(self, campaign_id: int, binding_id: int) -> StreamEditor:
        """Editor state after this deleted binding is active again."""
        return self._bring_back(campaign_id, binding_id)

    def pin(self, campaign_id: int, binding_id: int, share: Decimal) -> StreamEditor:
        """Editor state after this offer keeps the given share."""
        return self._pin(campaign_id, binding_id, share)

    def unpin(self, campaign_id: int, binding_id: int) -> StreamEditor:
        """Editor state after this offer joins the split again."""
        return self._unpin(campaign_id, binding_id)

    def push(self, campaign_id: int, stream_id: int) -> StreamEditor:
        """Editor state after active offers replace the live flow's offers."""
        try:
            return self._push(campaign_id, stream_id)
        except KeitaroError as error:
            raise StreamEditorError(error.kind) from None

    def cancel(self, campaign_id: int, stream_id: int) -> StreamEditor:
        """Editor state after unpublished bindings are dropped and the snapshot is restored."""
        return self._cancel(campaign_id, stream_id)

    def _fetch(self, campaign_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        remote_streams = self._keitaro.list_streams(campaign_id)
        stored = {row.keitaro_id: row for row in self._campaign_streams(campaign_id)}
        returned: set[int] = set()

        for remote in remote_streams:
            returned.add(remote.id)
            stream = stored.get(remote.id)

            if stream is None:
                stream = self._insert_stream(campaign_id, remote)
                stored[remote.id] = stream

            self._fetch_offers(stream, remote.offers)

        for stream in stored.values():
            if stream.keitaro_id not in returned:
                self._archive_stream(stream)

        self._session.flush()

        return self._editor(campaign_id)

    def _add(self, campaign_id: int, stream_id: int, offer_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        if stream.deleted or stream.flow_schema != "landings":
            raise StreamEditorError("conflict")

        offer = self._keitaro.get_offer(offer_id)

        if self._pair(stream_id, offer_id) is not None:
            raise StreamEditorError("conflict")

        self._insert_offer(offer)
        self._session.add(
            StreamOfferRecord(
                stream_keitaro_id=stream_id,
                offer_keitaro_id=offer.id,
                share=_money(0),
                pinned=False,
                deleted=False,
                published_share=None,
                published_pinned=None,
                published_deleted=None,
                created_at=datetime.now(UTC),
            )
        )
        self._session.flush()
        self._split(stream_id)

        return self._editor(campaign_id)

    def _remove(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if binding.deleted:
            raise StreamEditorError("conflict")

        binding.deleted = True
        binding.share = _money(0)
        binding.pinned = False
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _bring_back(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or not binding.deleted:
            raise StreamEditorError("conflict")

        binding.deleted = False
        binding.pinned = False
        binding.share = _money(0)
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _pin(self, campaign_id: int, binding_id: int, share: Decimal) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or binding.deleted:
            raise StreamEditorError("conflict")

        binding.pinned = True
        binding.share = _money(share)
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _unpin(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or binding.deleted:
            raise StreamEditorError("conflict")

        binding.pinned = False
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _push(self, campaign_id: int, stream_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        if stream.deleted:
            raise StreamEditorError("conflict")

        body = self._keitaro.get_stream(stream_id)
        bindings = self._bindings(stream_id)
        body["offers"] = [
            {"offer_id": row.offer_keitaro_id, "share": _json_share(row.share), "state": "active"}
            for row in bindings
            if not row.deleted
        ]
        self._keitaro.update_stream(stream_id, body)

        for row in bindings:
            row.published_share = _money(_decimal(row.share))
            row.published_pinned = row.pinned
            row.published_deleted = row.deleted

        stream.published_deleted = stream.deleted
        self._session.flush()

        return self._editor(campaign_id)

    def _cancel(self, campaign_id: int, stream_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        for row in self._bindings(stream_id):
            if row.published_share is None:
                self._session.delete(row)
                continue

            row.share = _money(_decimal(row.published_share))
            row.pinned = bool(row.published_pinned)
            row.deleted = bool(row.published_deleted)

        stream.deleted = stream.published_deleted
        self._session.flush()

        return self._editor(campaign_id)

    def _fetch_offers(self, stream: StreamRecord, offers: tuple[OfferRemote, ...]) -> None:
        seen: set[int] = set()

        for remote in offers:
            offer_id = _offer_id(remote.offer_id)

            if offer_id in seen:
                continue

            share = _remote_share(remote.share)
            seen.add(offer_id)

            if self._pair(stream.keitaro_id, offer_id) is not None:
                continue

            self._catalog_offer(offer_id)
            self._session.add(
                StreamOfferRecord(
                    stream_keitaro_id=stream.keitaro_id,
                    offer_keitaro_id=offer_id,
                    share=share,
                    pinned=False,
                    deleted=False,
                    published_share=share,
                    published_pinned=False,
                    published_deleted=False,
                    created_at=datetime.now(UTC),
                )
            )

        self._session.flush()

        for binding in self._bindings(stream.keitaro_id):
            if binding.offer_keitaro_id in seen or binding.published_share is None:
                continue

            _archive_binding(binding)

    def _archive_stream(self, stream: StreamRecord) -> None:
        for binding in self._bindings(stream.keitaro_id):
            if binding.published_share is None:
                self._session.delete(binding)
                continue

            _archive_binding(binding)

        stream.deleted = True
        stream.published_deleted = True

    def _insert_stream(self, campaign_id: int, remote: StreamRemote) -> StreamRecord:
        stream = StreamRecord(
            keitaro_id=remote.id,
            campaign_keitaro_id=campaign_id,
            name=remote.name,
            position=remote.position,
            flow_schema=remote.schema,
            deleted=False,
            published_deleted=False,
            created_at=datetime.now(UTC),
        )
        self._session.add(stream)
        self._session.flush()

        return stream

    def _catalog_offer(self, offer_id: int) -> None:
        if self._session.get(OfferRecord, offer_id) is not None:
            return

        self._insert_offer(self._keitaro.get_offer(offer_id))

    def _insert_offer(self, offer: Offer) -> None:
        if self._session.get(OfferRecord, offer.id) is not None:
            return

        self._session.add(
            OfferRecord(keitaro_id=offer.id, name=offer.name, created_at=datetime.now(UTC))
        )
        self._session.flush()

    def _split(self, stream_id: int) -> None:
        rows = self._bindings(stream_id)
        pinned_total = sum(
            (_decimal(row.share) for row in rows if not row.deleted and row.pinned),
            Decimal("0"),
        )
        remainder = _HUNDRED - pinned_total

        if remainder < 0:
            raise StreamEditorError("invalid")

        unpinned = sorted(
            (row for row in rows if not row.deleted and not row.pinned),
            key=lambda row: (row.created_at, row.id),
        )

        if not unpinned:
            return

        each = _money(remainder / Decimal(len(unpinned)))
        last = _money(remainder - each * (len(unpinned) - 1))

        if last < 0:
            raise StreamEditorError("invalid")

        for row in unpinned[:-1]:
            row.share = each

        unpinned[-1].share = last

    def _editor(self, campaign_id: int) -> StreamEditor:
        groups: list[StreamGroup] = []

        for stream in self._campaign_streams(campaign_id):
            bindings = self._bindings(stream.keitaro_id)
            groups.append(
                StreamGroup(
                    id=stream.keitaro_id,
                    name=stream.name,
                    position=stream.position,
                    accepts_offers=not stream.deleted and stream.flow_schema == "landings",
                    deleted=stream.deleted,
                    dirty=_dirty(stream, bindings),
                    lines=[self._line(row) for row in bindings],
                )
            )

        return StreamEditor(campaign_id=campaign_id, streams=groups)

    def _line(self, row: StreamOfferRecord) -> StreamLine:
        offer = self._session.get(OfferRecord, row.offer_keitaro_id)

        return StreamLine(
            id=row.id,
            offer_id=row.offer_keitaro_id,
            name="" if offer is None else offer.name,
            share=_money(_decimal(row.share)),
            pinned=row.pinned,
            deleted=row.deleted,
        )

    def _campaign(self, campaign_id: int) -> CampaignRecord:
        row = self._session.get(CampaignRecord, campaign_id)

        if row is None or row.deleted_at is not None:
            raise StreamEditorError("not_found")

        return row

    def _require_stream(self, campaign_id: int, stream_id: int) -> StreamRecord:
        stream = self._session.get(StreamRecord, stream_id)

        if stream is None or stream.campaign_keitaro_id != campaign_id:
            raise StreamEditorError("not_found")

        return stream

    def _require_binding(self, campaign_id: int, binding_id: int) -> tuple[StreamRecord, StreamOfferRecord]:
        binding = self._session.get(StreamOfferRecord, binding_id)

        if binding is None:
            raise StreamEditorError("not_found")

        return self._require_stream(campaign_id, binding.stream_keitaro_id), binding

    def _campaign_streams(self, campaign_id: int) -> list[StreamRecord]:
        rows = self._session.scalars(
            select(StreamRecord)
            .where(StreamRecord.campaign_keitaro_id == campaign_id)
            .order_by(StreamRecord.position, StreamRecord.keitaro_id)
        )

        return list(rows)

    def _bindings(self, stream_id: int) -> list[StreamOfferRecord]:
        rows = self._session.scalars(
            select(StreamOfferRecord)
            .where(StreamOfferRecord.stream_keitaro_id == stream_id)
            .order_by(StreamOfferRecord.created_at, StreamOfferRecord.id)
        )

        return list(rows)

    def _pair(self, stream_id: int, offer_id: int) -> StreamOfferRecord | None:
        return self._session.scalar(
            select(StreamOfferRecord).where(
                StreamOfferRecord.stream_keitaro_id == stream_id,
                StreamOfferRecord.offer_keitaro_id == offer_id,
            )
        )


def get_stream_editor_service(session: SessionDep, keitaro: KeitaroDep) -> StreamEditorService:
    """Stream editor for one request."""
    return StreamEditorService(session, keitaro)


def _archive_binding(row: StreamOfferRecord) -> None:
    row.deleted = True
    row.share = _money(0)
    row.pinned = False
    row.published_deleted = True
    row.published_share = _money(0)
    row.published_pinned = False


def _dirty(stream: StreamRecord, rows: list[StreamOfferRecord]) -> bool:
    if stream.deleted != stream.published_deleted:
        return True

    for row in rows:
        if row.published_share is None or row.published_pinned is None or row.published_deleted is None:
            return True

        if row.pinned != row.published_pinned or row.deleted != row.published_deleted:
            return True

        if _money(_decimal(row.share)) != _money(_decimal(row.published_share)):
            return True

    return False


def _offer_id(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise KeitaroError("unavailable")

    return value


def _remote_share(value: object) -> Decimal:
    if isinstance(value, bool):
        raise KeitaroError("unavailable")

    if isinstance(value, int):
        share = Decimal(value)
    elif isinstance(value, float):
        share = Decimal(str(value))
    elif isinstance(value, str):
        try:
            share = Decimal(value)
        except ArithmeticError:
            raise KeitaroError("unavailable") from None
    else:
        raise KeitaroError("unavailable")

    share = _money(share)

    if share < 0 or share > _HUNDRED:
        raise KeitaroError("unavailable")

    return share


def _decimal(value: Decimal | int | float | str) -> Decimal:
    if isinstance(value, Decimal):
        return value

    return Decimal(str(value))


def _money(value: Decimal | int) -> Decimal:
    return Decimal(value).quantize(_CENT, rounding=ROUND_HALF_UP)


def _json_share(value: Decimal | int | float | str) -> int | float:
    text = format(_money(_decimal(value)), "f")

    if text.endswith(".00"):
        return int(text[:-3])

    return float(text)
