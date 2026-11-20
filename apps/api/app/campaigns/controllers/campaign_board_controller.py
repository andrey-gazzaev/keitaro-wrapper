"""Campaign board routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.campaigns.dtos.campaign_board_out_dto import CampaignBoardOutDto
from app.campaigns.dtos.campaign_out_dto import CampaignOutDto
from app.campaigns.models.campaign import Campaign
from app.campaigns.models.campaign_board import CampaignBoard
from app.campaigns.services.campaign_board_service import CampaignBoardService, get_campaign_board_service

CampaignBoardServiceDep = Annotated[CampaignBoardService, Depends(get_campaign_board_service)]


class CampaignBoardController:
    """Read one page of campaigns over HTTP."""

    router: APIRouter
    """Routes this controller serves."""

    def __init__(self) -> None:
        """Route for one page of campaigns."""
        self.router = APIRouter(prefix="/campaigns", tags=["campaigns"])
        self.router.get("/board")(self.show)

    def show(self, board: CampaignBoardServiceDep, q: str = "", page: int = 0) -> CampaignBoardOutDto:
        """One page of stored campaigns for this search."""
        return self._response(board.show(q, page))

    def _response(self, board: CampaignBoard) -> CampaignBoardOutDto:
        return CampaignBoardOutDto(
            campaigns=[self._campaign(campaign) for campaign in board.campaigns],
            page=board.page,
            page_count=board.page_count,
            state=board.state,
        )

    def _campaign(self, campaign: Campaign) -> CampaignOutDto:
        return CampaignOutDto(id=campaign.id, name=campaign.name, deleted=campaign.deleted)


campaign_board_controller = CampaignBoardController()
