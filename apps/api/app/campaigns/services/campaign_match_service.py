"""Membership of stored campaigns in a Keitaro list."""

from app.campaigns.models.campaign_presence import CampaignPresence
from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.repositories.campaign_record import CampaignRecord


class CampaignMatchService:
    """Membership of stored campaigns in one Keitaro list."""

    def presence(
        self,
        stored: list[CampaignRecord],
        remote: list[CampaignRemote],
    ) -> CampaignPresence:
        """Membership of stored ids in this Keitaro list."""
        stored_ids = {row.keitaro_id for row in stored}
        seen: set[int] = set()
        listed: list[CampaignRemote] = []

        for campaign in remote:
            if campaign.id in seen:
                continue

            seen.add(campaign.id)
            listed.append(campaign)

        listed_ids = {campaign.id for campaign in listed}

        return CampaignPresence(
            add=tuple(campaign for campaign in listed if campaign.id not in stored_ids),
            tombstone_ids=tuple(
                row.keitaro_id for row in stored if row.deleted_at is None and row.keitaro_id not in listed_ids
            ),
            restore_ids=tuple(
                row.keitaro_id for row in stored if row.deleted_at is not None and row.keitaro_id in listed_ids
            ),
        )
