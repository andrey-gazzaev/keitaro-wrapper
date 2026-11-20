"""Campaign fields read from Keitaro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignRemote:
    """One campaign read from Keitaro."""

    id: int
    """Keitaro campaign id."""

    name: str
    """Campaign name. Empty when Keitaro omits it."""

    alias: str
    """Campaign alias. Empty when Keitaro omits it."""

    type: str
    """Campaign type. Empty when Keitaro omits it."""

    state: str
    """Campaign state. Empty when Keitaro omits it."""

    domain_id: int | None
    """Domain id. None when Keitaro has no domain."""

    group_id: int | None
    """Group id. None when Keitaro has no group."""

    traffic_source_id: int | None
    """Traffic source id. None when Keitaro has no traffic source."""
