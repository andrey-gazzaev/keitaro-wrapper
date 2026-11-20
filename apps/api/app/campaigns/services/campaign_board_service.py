"""One page of stored campaigns for a search."""

from app.campaigns.models.campaign import Campaign
from app.campaigns.models.campaign_board import CampaignBoard
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.campaign_repository import CampaignRepository, CampaignRepositoryDep

_PAGE_SIZE = 50


class CampaignBoardService:
    """Reads one page of stored campaigns for a search."""

    def __init__(self, campaigns: CampaignRepository) -> None:
        """A board for this campaign repository."""
        self._campaigns = campaigns

    def show(self, needle: str, page: int) -> CampaignBoard:
        """Campaigns on this page of the search. No campaigns when nothing matches."""
        trimmed = needle.strip()
        matched, stored = self._campaigns.count_matching(trimmed)

        if stored == 0:
            return CampaignBoard(campaigns=[], page=0, page_count=0, state="empty")

        if matched == 0:
            return CampaignBoard(campaigns=[], page=0, page_count=0, state="none")

        page_count = (matched + _PAGE_SIZE - 1) // _PAGE_SIZE
        current = min(max(page, 0), page_count - 1)
        rows = self._campaigns.list_matching(trimmed, current * _PAGE_SIZE, _PAGE_SIZE)

        return CampaignBoard(
            campaigns=[_campaign(row) for row in rows],
            page=current,
            page_count=page_count,
            state="ready",
        )


def get_campaign_board_service(campaigns: CampaignRepositoryDep) -> CampaignBoardService:
    """Campaign board for one request."""
    return CampaignBoardService(campaigns)


def _campaign(row: CampaignRecord) -> Campaign:
    return Campaign(id=row.keitaro_id, name=row.name, deleted=row.deleted_at is not None)
