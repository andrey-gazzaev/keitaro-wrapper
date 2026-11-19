"""Campaign routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.campaigns.dtos.campaign_in_dto import CampaignInDto
from app.campaigns.dtos.campaign_out_dto import CampaignOutDto
from app.campaigns.models.campaign import Campaign
from app.campaigns.models.campaign_draft import CampaignDraft
from app.campaigns.services.campaign_call_error import CampaignCallError
from app.campaigns.services.campaign_service import CampaignService, get_campaign_service
from app.campaigns.services.campaign_setup_error import CampaignSetupError

CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]

_STATUS = {
    "not_found": 404,
    "unavailable": 502,
    "not_configured": 503,
}


class CampaignController:
    """Create, list, and sync campaigns over HTTP."""

    router: APIRouter
    """Routes this controller serves."""

    def __init__(self) -> None:
        """Routes for creating, listing, and syncing campaigns."""
        self.router = APIRouter(prefix="/campaigns", tags=["campaigns"])
        self.router.post("")(self.create_campaign)
        self.router.get("")(self.list_campaigns)
        self.router.post("/sync")(self.sync_campaigns)

    def create_campaign(self, incoming: CampaignInDto, campaigns: CampaignServiceDep) -> CampaignOutDto:
        """Create one campaign in Keitaro and store the row."""
        try:
            created = campaigns.create(self._draft(incoming))
        except CampaignCallError as error:
            raise self._http_error(error) from None
        except CampaignSetupError:
            raise HTTPException(status_code=409) from None

        return self._response(created)

    def list_campaigns(self, campaigns: CampaignServiceDep) -> list[CampaignOutDto]:
        """Every stored campaign, newest first."""
        return [self._response(campaign) for campaign in campaigns.list()]

    def sync_campaigns(self, campaigns: CampaignServiceDep) -> list[CampaignOutDto]:
        """Compare live rows with Keitaro and return every stored campaign."""
        try:
            synced = campaigns.sync()
        except CampaignCallError as error:
            raise self._http_error(error) from None

        return [self._response(campaign) for campaign in synced]

    def _draft(self, incoming: CampaignInDto) -> CampaignDraft:
        return CampaignDraft(name=incoming.name, country=incoming.country, offer_id=incoming.offer_id)

    def _response(self, campaign: Campaign) -> CampaignOutDto:
        return CampaignOutDto(id=campaign.id, name=campaign.name, deleted=campaign.deleted)

    def _http_error(self, error: CampaignCallError) -> HTTPException:
        return HTTPException(status_code=_STATUS[error.kind])


campaign_controller = CampaignController()
