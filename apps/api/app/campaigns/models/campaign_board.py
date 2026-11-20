"""One page of campaigns for a search."""

from typing import Literal

from app.campaigns.models.campaign import Campaign


class CampaignBoard:
    """One page of campaigns for a search."""

    campaigns: list[Campaign]
    """Campaigns on this page. Empty when nothing matches."""

    page: int
    """Zero-based page. Zero when nothing matches."""

    page_count: int
    """Pages of matches. Zero when nothing matches."""

    state: Literal["empty", "none", "ready"]
    """Empty when nothing is stored. None when the search misses. Ready when a match exists."""

    def __init__(
        self,
        campaigns: list[Campaign],
        page: int,
        page_count: int,
        state: Literal["empty", "none", "ready"],
    ) -> None:
        """A page of campaigns in this state."""
        self.campaigns = campaigns
        self.page = page
        self.page_count = page_count
        self.state = state
