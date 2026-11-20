"""Edit offer shares for one stored campaign."""

from datetime import UTC, datetime
from decimal import Decimal

from app.campaigns.models.offer import Offer
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_editor import StreamEditor
from app.campaigns.models.stream_group import StreamGroup
from app.campaigns.models.stream_line import StreamLine
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.campaign_repository import CampaignRepository, CampaignRepositoryDep
from app.campaigns.repositories.offer_repository import OfferRepository, OfferRepositoryDep
from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_offer_repository import StreamOfferRepository, StreamOfferRepositoryDep
from app.campaigns.repositories.stream_record import StreamRecord
from app.campaigns.repositories.stream_repository import StreamRepository, StreamRepositoryDep
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroDep, KeitaroService
from app.campaigns.services.offer_share_service import OfferShareService
from app.campaigns.services.stream_editor_error import StreamEditorError


class StreamEditorService:
    """Edits offer shares for one stored campaign."""

    def __init__(
        self,
        campaigns: CampaignRepository,
        streams: StreamRepository,
        offers: OfferRepository,
        bindings: StreamOfferRepository,
        keitaro: KeitaroService,
    ) -> None:
        """An editor for these repositories and one Keitaro service."""
        self._campaigns = campaigns
        self._streams = streams
        self._offers = offers
        self._bindings = bindings
        self._keitaro = keitaro
        self._shares = OfferShareService()

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
        stored = {row.keitaro_id: row for row in self._streams.list_for_campaign(campaign_id)}
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

        return self._editor(campaign_id)

    def _add(self, campaign_id: int, stream_id: int, offer_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        if stream.deleted or stream.flow_schema != "landings":
            raise StreamEditorError("conflict")

        offer = self._keitaro.get_offer(offer_id)

        if self._bindings.find_pair(stream_id, offer_id) is not None:
            raise StreamEditorError("conflict")

        self._insert_offer(offer)
        self._bindings.insert(
            stream_keitaro_id=stream_id,
            offer_keitaro_id=offer.id,
            share=self._shares.money(0),
            pinned=False,
            deleted=False,
            published_share=None,
            published_pinned=None,
            published_deleted=None,
            created_at=datetime.now(UTC),
        )
        self._split(stream_id)

        return self._editor(campaign_id)

    def _remove(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if binding.deleted:
            raise StreamEditorError("conflict")

        self._bindings.set_working(binding.id, share=self._shares.money(0), pinned=False, deleted=True)
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _bring_back(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or not binding.deleted:
            raise StreamEditorError("conflict")

        self._bindings.set_working(binding.id, share=self._shares.money(0), pinned=False, deleted=False)
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _pin(self, campaign_id: int, binding_id: int, share: Decimal) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or binding.deleted:
            raise StreamEditorError("conflict")

        self._bindings.set_working(binding.id, share=self._shares.money(share), pinned=True, deleted=binding.deleted)
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _unpin(self, campaign_id: int, binding_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream, binding = self._require_binding(campaign_id, binding_id)

        if stream.deleted or binding.deleted:
            raise StreamEditorError("conflict")

        self._bindings.set_working(
            binding.id,
            share=self._shares.money(binding.share),
            pinned=False,
            deleted=binding.deleted,
        )
        self._split(stream.keitaro_id)

        return self._editor(campaign_id)

    def _push(self, campaign_id: int, stream_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        if stream.deleted:
            raise StreamEditorError("conflict")

        body = self._keitaro.get_stream(stream_id)
        bindings = self._bindings.list_for_stream(stream_id)
        body["offers"] = [
            {"offer_id": row.offer_keitaro_id, "share": self._shares.json_share(row.share), "state": "active"}
            for row in bindings
            if not row.deleted
        ]
        self._keitaro.update_stream(stream_id, body)

        for row in bindings:
            self._bindings.set_published(
                row.id,
                share=self._shares.money(row.share),
                pinned=row.pinned,
                deleted=row.deleted,
            )

        self._streams.set_deleted_flags(
            stream.keitaro_id,
            deleted=stream.deleted,
            published_deleted=stream.deleted,
        )

        return self._editor(campaign_id)

    def _cancel(self, campaign_id: int, stream_id: int) -> StreamEditor:
        self._campaign(campaign_id)
        stream = self._require_stream(campaign_id, stream_id)

        for row in self._bindings.list_for_stream(stream_id):
            published_share = row.published_share

            if published_share is None:
                self._bindings.delete(row.id)
                continue

            self._bindings.set_working(
                row.id,
                share=self._shares.money(published_share),
                pinned=bool(row.published_pinned),
                deleted=bool(row.published_deleted),
            )

        self._streams.set_deleted_flags(
            stream.keitaro_id,
            deleted=stream.published_deleted,
            published_deleted=stream.published_deleted,
        )

        return self._editor(campaign_id)

    def _fetch_offers(self, stream: StreamRecord, offers: tuple[OfferRemote, ...]) -> None:
        seen: set[int] = set()

        for remote in offers:
            offer_id = self._shares.offer_id(remote.offer_id)

            if offer_id in seen:
                continue

            share = self._shares.remote_share(remote.share)
            seen.add(offer_id)

            if self._bindings.find_pair(stream.keitaro_id, offer_id) is not None:
                continue

            self._catalog_offer(offer_id)
            self._bindings.insert(
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

        for binding in self._bindings.list_for_stream(stream.keitaro_id):
            if binding.offer_keitaro_id in seen or binding.published_share is None:
                continue

            self._archive_binding(binding)

    def _archive_stream(self, stream: StreamRecord) -> None:
        for binding in self._bindings.list_for_stream(stream.keitaro_id):
            if binding.published_share is None:
                self._bindings.delete(binding.id)
                continue

            self._archive_binding(binding)

        self._streams.set_deleted_flags(stream.keitaro_id, deleted=True, published_deleted=True)

    def _archive_binding(self, row: StreamOfferRecord) -> None:
        self._bindings.set_working(row.id, share=self._shares.money(0), pinned=False, deleted=True)
        self._bindings.set_published(row.id, share=self._shares.money(0), pinned=False, deleted=True)

    def _insert_stream(self, campaign_id: int, remote: StreamRemote) -> StreamRecord:
        return self._streams.insert(
            keitaro_id=remote.id,
            campaign_keitaro_id=campaign_id,
            name=remote.name,
            position=remote.position,
            flow_schema=remote.schema,
            deleted=False,
            published_deleted=False,
            created_at=datetime.now(UTC),
        )

    def _catalog_offer(self, offer_id: int) -> None:
        if self._offers.get(offer_id) is not None:
            return

        self._insert_offer(self._keitaro.get_offer(offer_id))

    def _insert_offer(self, offer: Offer) -> None:
        if self._offers.get(offer.id) is not None:
            return

        self._offers.insert(keitaro_id=offer.id, name=offer.name, created_at=datetime.now(UTC))

    def _split(self, stream_id: int) -> None:
        shares = self._shares.split(self._bindings.list_for_stream(stream_id))

        if not shares:
            return

        self._bindings.set_shares(shares)

    def _editor(self, campaign_id: int) -> StreamEditor:
        groups: list[StreamGroup] = []

        for stream in self._streams.list_for_campaign(campaign_id):
            bindings = self._bindings.list_for_stream(stream.keitaro_id)
            groups.append(
                StreamGroup(
                    id=stream.keitaro_id,
                    name=stream.name,
                    position=stream.position,
                    accepts_offers=not stream.deleted and stream.flow_schema == "landings",
                    deleted=stream.deleted,
                    dirty=self._shares.dirty(stream, bindings),
                    lines=[self._line(row) for row in bindings],
                )
            )

        return StreamEditor(campaign_id=campaign_id, streams=groups)

    def _line(self, row: StreamOfferRecord) -> StreamLine:
        offer = self._offers.get(row.offer_keitaro_id)

        return StreamLine(
            id=row.id,
            offer_id=row.offer_keitaro_id,
            name="" if offer is None else offer.name,
            share=self._shares.money(row.share),
            pinned=row.pinned,
            deleted=row.deleted,
        )

    def _campaign(self, campaign_id: int) -> CampaignRecord:
        row = self._campaigns.get(campaign_id)

        if row is None or row.deleted_at is not None:
            raise StreamEditorError("not_found")

        return row

    def _require_stream(self, campaign_id: int, stream_id: int) -> StreamRecord:
        stream = self._streams.get(stream_id)

        if stream is None or stream.campaign_keitaro_id != campaign_id:
            raise StreamEditorError("not_found")

        return stream

    def _require_binding(self, campaign_id: int, binding_id: int) -> tuple[StreamRecord, StreamOfferRecord]:
        binding = self._bindings.get(binding_id)

        if binding is None:
            raise StreamEditorError("not_found")

        return self._require_stream(campaign_id, binding.stream_keitaro_id), binding


def get_stream_editor_service(
    campaigns: CampaignRepositoryDep,
    streams: StreamRepositoryDep,
    offers: OfferRepositoryDep,
    bindings: StreamOfferRepositoryDep,
    keitaro: KeitaroDep,
) -> StreamEditorService:
    """Stream editor for one request."""
    return StreamEditorService(campaigns, streams, offers, bindings, keitaro)
