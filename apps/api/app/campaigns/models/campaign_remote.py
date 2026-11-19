"""Campaign fields read from Keitaro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignRemote:
    """Campaign fields read from Keitaro for a sync comparison."""

    name: str
    """Campaign name. Empty when Keitaro omits it."""

    alias: str
    """Campaign alias. Empty when Keitaro omits it."""

    type: str
    """Campaign type. Empty when Keitaro omits it."""

    state: str
    """Campaign state. Empty when Keitaro omits it."""

    group_id: int | None
    """Group id. None when Keitaro has no group."""

    traffic_source_id: int | None
    """Traffic source id. None when Keitaro has no traffic source."""
