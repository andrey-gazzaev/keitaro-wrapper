"""Campaigns to add, tombstone, or restore from one Keitaro list."""

from dataclasses import dataclass

from app.campaigns.models.campaign_remote import CampaignRemote


@dataclass(frozen=True)
class CampaignPresence:
    """Campaigns to add, tombstone, or restore from one Keitaro list."""

    add: tuple[CampaignRemote, ...]
    """Campaigns to insert. Empty when every listed id is already stored."""

    tombstone_ids: tuple[int, ...]
    """Live stored ids missing from the list. Empty when every live campaign is listed."""

    restore_ids: tuple[int, ...]
    """Tombstoned ids present in the list. Empty when no tombstone is listed."""
