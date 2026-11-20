"""Create, list, and sync campaigns."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime

from app.campaigns.models.campaign import Campaign
from app.campaigns.models.campaign_draft import CampaignDraft
from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.campaign_repository import CampaignRepository, CampaignRepositoryDep
from app.campaigns.services.campaign_call_error import CampaignCallError
from app.campaigns.services.campaign_match_service import CampaignMatchService
from app.campaigns.services.campaign_setup_error import CampaignSetupError
from app.campaigns.services.campaign_stream_service import CampaignStreamService
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroDep, KeitaroService


class CampaignService:
    """Creates, lists, and syncs campaigns."""

    def __init__(self, campaigns: CampaignRepository, keitaro: KeitaroService) -> None:
        """A campaign service for one campaign repository and one Keitaro service."""
        self._campaigns = campaigns
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
        return [_campaign(row) for row in self._campaigns.list_newest()]

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

        self._campaigns.insert(
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
        )

        return Campaign(id=campaign_id, name=draft.name, deleted=False)

    def _sync(self) -> list[Campaign]:
        remote = self._keitaro.list_campaigns()
        presence = self._match.presence(self._campaigns.list_newest(), remote)
        now = datetime.now(UTC)

        for campaign in presence.add:
            self._campaigns.insert(
                keitaro_id=campaign.id,
                name=campaign.name,
                alias=_stored_alias(campaign),
                domain_id=campaign.domain_id,
                group_id=campaign.group_id,
                traffic_source_id=campaign.traffic_source_id,
                created_at=now,
            )

        self._campaigns.mark_deleted(list(presence.tombstone_ids), now)
        self._campaigns.mark_live(list(presence.restore_ids))

        return self.list()

    def _placement(self) -> tuple[int, int, int]:
        domains = self._keitaro.list_domains()
        groups = self._keitaro.list_campaign_groups()
        sources = self._keitaro.list_traffic_sources()

        if not domains or not groups or not sources:
            raise CampaignSetupError

        return domains[0], groups[0], sources[0]


def get_campaign_service(campaigns: CampaignRepositoryDep, keitaro: KeitaroDep) -> CampaignService:
    """Campaign service for one request."""
    return CampaignService(campaigns, keitaro)


def _alias() -> str:
    return f"c{secrets.token_hex(6)}"


def _stored_alias(campaign: CampaignRemote) -> str:
    if campaign.alias == "":
        return f"k{campaign.id}"

    return campaign.alias


def _campaign(row: CampaignRecord) -> Campaign:
    return Campaign(id=row.keitaro_id, name=row.name, deleted=row.deleted_at is not None)
