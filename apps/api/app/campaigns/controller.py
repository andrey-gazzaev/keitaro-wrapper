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

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

CampaignServiceDep = Annotated[CampaignService, Depends(get_campaign_service)]

_STATUS = {
    "not_found": 404,
    "unavailable": 502,
    "not_configured": 503,
}


def _http_error(error: CampaignCallError) -> HTTPException:
    return HTTPException(status_code=_STATUS[error.kind])


def _draft(incoming: CampaignInDto) -> CampaignDraft:
    return CampaignDraft(name=incoming.name, country=incoming.country, offer_id=incoming.offer_id)


def _response(campaign: Campaign) -> CampaignOutDto:
    return CampaignOutDto(id=campaign.id, name=campaign.name, deleted=campaign.deleted)


@router.post("")
def create_campaign(incoming: CampaignInDto, campaigns: CampaignServiceDep) -> CampaignOutDto:
    """Create one campaign in Keitaro and store the row."""
    try:
        created = campaigns.create(_draft(incoming))
    except CampaignCallError as error:
        raise _http_error(error) from None
    except CampaignSetupError:
        raise HTTPException(status_code=409) from None

    return _response(created)


@router.get("")
def list_campaigns(campaigns: CampaignServiceDep) -> list[CampaignOutDto]:
    """Every stored campaign, newest first."""
    return [_response(campaign) for campaign in campaigns.list()]


@router.post("/sync")
def sync_campaigns(campaigns: CampaignServiceDep) -> list[CampaignOutDto]:
    """Compare live rows with Keitaro and return every stored campaign."""
    try:
        synced = campaigns.sync()
    except CampaignCallError as error:
        raise _http_error(error) from None

    return [_response(campaign) for campaign in synced]
