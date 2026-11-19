"""Create, list, and sync campaigns."""

import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.models.campaign import Campaign
from app.campaigns.models.campaign_draft import CampaignDraft
from app.campaigns.services.campaign_call_error import CampaignCallError
from app.campaigns.services.campaign_match_service import CampaignMatchService
from app.campaigns.services.campaign_record import CampaignRecord
from app.campaigns.services.campaign_setup_error import CampaignSetupError
from app.campaigns.services.campaign_stream_service import CampaignStreamService
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroDep, KeitaroService
from app.db import SessionDep


class CampaignService:
    """The only writer of campaign rows."""

    def __init__(self, session: Session, keitaro: KeitaroService) -> None:
        """A campaign service for one database session and one Keitaro service."""
        self._session = session
        self._keitaro = keitaro
        self._streams = CampaignStreamService()
        self._match = CampaignMatchService()

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

        country_stream_id = self._keitaro.create_stream(self._streams.country(campaign_id, draft.country))
        offer_stream_id = self._keitaro.create_stream(self._streams.offer(campaign_id, draft.offer_id))

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

            if remote is None or not self._match.matches_campaign(row, remote):
                stale.append(row)
                continue

            streams = self._keitaro.list_streams(row.keitaro_id)

            if not self._match.matches_streams(row, streams):
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


def get_campaign_service(session: SessionDep, keitaro: KeitaroDep) -> CampaignService:
    """Campaign service for one request."""
    return CampaignService(session, keitaro)


def _alias() -> str:
    return f"c{secrets.token_hex(6)}"


def _campaign(row: CampaignRecord) -> Campaign:
    return Campaign(id=row.keitaro_id, name=row.name, deleted=row.deleted_at is not None)
