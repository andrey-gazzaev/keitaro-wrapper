"""Create, list, and sync campaigns."""

import json
import secrets
from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import Depends
from sqlalchemy import DateTime, Integer, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.campaigns.client import CampaignRemote, KeitaroClient, KeitaroError, StreamRemote, get_keitaro
from app.campaigns.model import Campaign, CampaignDraft
from app.db import Base, SessionDep

_GOOGLE = "https://www.google.com"


class CampaignRecord(Base):
    """One campaign. `deleted_at` set means the row is a tombstone and stays stored."""

    __tablename__ = "campaigns"
    """Table where these campaigns are stored."""

    keitaro_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    """Keitaro campaign id. This is the primary key."""

    name: Mapped[str] = mapped_column(Text, nullable=False)
    """Name shown to the operator."""

    alias: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    """Public alias. Unique across stored campaigns."""

    country: Mapped[str] = mapped_column(Text, nullable=False)
    """Two-letter country code."""

    offer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro offer on the offer flow."""

    domain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro domain used at creation."""

    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro campaign group used at creation."""

    traffic_source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro traffic source used at creation."""

    country_stream_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    """Keitaro id of the country flow. Unique across stored campaigns."""

    offer_stream_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    """Keitaro id of the offer flow. Unique across stored campaigns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this row was stored."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """When this row became a tombstone. None while the campaign is live."""


class CampaignSetupError(Exception):
    """Keitaro has no domain, campaign group, or traffic source."""


class CampaignCallError(Exception):
    """A campaign call to Keitaro failed."""

    kind: Literal["not_found", "unavailable", "not_configured"]
    """not_found, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)


class Campaigns:
    """The only writer of campaign rows."""

    def __init__(self, session: Session, keitaro: KeitaroClient) -> None:
        """A campaign service for one database session and one Keitaro client."""
        self._session = session
        self._keitaro = keitaro

    def create(self, draft: CampaignDraft) -> Campaign:
        """The campaign stored for this draft."""
        try:
            return self._create(draft)
        except KeitaroError as error:
            raise CampaignCallError(error.kind) from None

    def list(self) -> list[Campaign]:
        """Every stored campaign, newest first. Empty when none are stored."""
        rows = self._session.scalars(select(CampaignRecord).order_by(CampaignRecord.created_at.desc()))

        return [_campaign(row) for row in rows]

    def sync(self) -> list[Campaign]:
        """Every stored campaign after this sync, newest first. Empty when none are stored."""
        try:
            return self._sync()
        except KeitaroError as error:
            raise CampaignCallError(error.kind) from None

    def _create(self, draft: CampaignDraft) -> Campaign:
        domain_id, group_id, traffic_source_id = self._placement()

        self._keitaro.require_offer(draft.offer_id)

        alias = _alias()
        campaign_id = self._keitaro.create_campaign(
            {
                "name": draft.name,
                "alias": alias,
                "type": "position",
                "domain_id": domain_id,
                "group_id": group_id,
                "traffic_source_id": traffic_source_id,
            }
        )

        country_stream_id = self._keitaro.create_stream(_country_stream_body(campaign_id, draft.country))
        offer_stream_id = self._keitaro.create_stream(_offer_stream_body(campaign_id, draft.offer_id))

        self._session.add(
            CampaignRecord(
                keitaro_id=campaign_id,
                name=draft.name,
                alias=alias,
                country=draft.country,
                offer_id=draft.offer_id,
                domain_id=domain_id,
                group_id=group_id,
                traffic_source_id=traffic_source_id,
                country_stream_id=country_stream_id,
                offer_stream_id=offer_stream_id,
                created_at=datetime.now(UTC),
                deleted_at=None,
            )
        )
        self._session.flush()

        return Campaign(id=campaign_id, name=draft.name, deleted=False)

    def _sync(self) -> list[Campaign]:
        rows = list(
            self._session.scalars(select(CampaignRecord).where(CampaignRecord.deleted_at.is_(None)))
        )
        stale: list[CampaignRecord] = []

        for row in rows:
            remote = self._keitaro.get_campaign(row.keitaro_id)

            if remote is None or not _campaign_matches(row, remote):
                stale.append(row)
                continue

            streams = self._keitaro.list_streams(row.keitaro_id)

            if not _streams_match(row, streams):
                stale.append(row)

        deleted_at = datetime.now(UTC)

        for row in stale:
            row.deleted_at = deleted_at

        self._session.flush()

        return self.list()

    def _placement(self) -> tuple[int, int, int]:
        domains = self._keitaro.list_domains()
        groups = self._keitaro.list_campaign_groups()
        sources = self._keitaro.list_traffic_sources()

        if not domains or not groups or not sources:
            raise CampaignSetupError

        return domains[0], groups[0], sources[0]


KeitaroDep = Annotated[KeitaroClient, Depends(get_keitaro)]


def get_campaigns(session: SessionDep, keitaro: KeitaroDep) -> Campaigns:
    """Campaign service for one request."""
    return Campaigns(session, keitaro)


def _alias() -> str:
    return f"c{secrets.token_hex(6)}"


def _country_stream_body(campaign_id: int, country: str) -> dict[str, object]:
    return {
        "campaign_id": campaign_id,
        "type": "regular",
        "name": "Country",
        "position": 1,
        "schema": "redirect",
        "action_type": "http",
        "action_payload": _GOOGLE,
        "offers": [],
        "filters": [
            {
                "name": "country",
                "mode": "accept",
                "payload": [country],
            }
        ],
    }


def _offer_stream_body(campaign_id: int, offer_id: int) -> dict[str, object]:
    return {
        "campaign_id": campaign_id,
        "type": "regular",
        "name": "Offer",
        "position": 2,
        "schema": "landings",
        "action_type": "http",
        "filters": [],
        "offers": [
            {
                "offer_id": offer_id,
                "share": 100,
                "state": "active",
            }
        ],
    }


def _campaign(row: CampaignRecord) -> Campaign:
    return Campaign(id=row.keitaro_id, name=row.name, deleted=row.deleted_at is not None)


def _campaign_matches(row: CampaignRecord, remote: CampaignRemote) -> bool:
    if remote.state == "deleted":
        return False

    return (
        remote.name == row.name
        and remote.alias == row.alias
        and remote.type == "position"
        and remote.group_id == row.group_id
        and remote.traffic_source_id == row.traffic_source_id
    )


def _streams_match(row: CampaignRecord, streams: list[StreamRemote]) -> bool:
    if len(streams) != 2:
        return False

    by_id = {stream.id: stream for stream in streams}

    if set(by_id) != {row.country_stream_id, row.offer_stream_id}:
        return False

    country = by_id[row.country_stream_id]
    offer = by_id[row.offer_stream_id]

    return _country_stream_matches(row, country) and _offer_stream_matches(row, offer)


def _active(stream: StreamRemote) -> bool:
    return stream.state == "active" and stream.type == "regular"


def _country_stream_matches(row: CampaignRecord, stream: StreamRemote) -> bool:
    if not _active(stream):
        return False

    if stream.schema != "redirect" or stream.action_type != "http":
        return False

    if stream.action_payload != _GOOGLE:
        return False

    if len(stream.offers) != 0 or len(stream.filters) != 1:
        return False

    country_filter = stream.filters[0]

    return (
        country_filter.name == "country"
        and country_filter.mode == "accept"
        and _country_payload(country_filter.payload) == [row.country]
    )


def _offer_stream_matches(row: CampaignRecord, stream: StreamRemote) -> bool:
    if not _active(stream):
        return False

    if stream.schema != "landings" or stream.action_type != "http":
        return False

    if len(stream.filters) != 0 or len(stream.offers) != 1:
        return False

    offer = stream.offers[0]

    return offer.offer_id == row.offer_id and offer.share == 100 and offer.state == "active"


def _country_payload(payload: object) -> list[str] | None:
    value = payload

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None

    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None

    return value
