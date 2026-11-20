"""Campaign board response body."""

from typing import Literal

from pydantic import BaseModel

from app.campaigns.dtos.campaign_out_dto import CampaignOutDto


class CampaignBoardOutDto(BaseModel):
    """One page of campaigns the client can show."""

    campaigns: list[CampaignOutDto]
    """Campaigns on this page. Empty when nothing matches."""

    page: int
    """Zero-based page. Zero when nothing matches."""

    page_count: int
    """Pages of matches. Zero when nothing matches."""

    state: Literal["empty", "none", "ready"]
    """Empty when nothing is stored. None when the search misses. Ready when a match exists."""
