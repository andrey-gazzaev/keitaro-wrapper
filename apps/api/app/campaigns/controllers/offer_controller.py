"""Offer catalog routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.campaigns.dtos.offer_out_dto import OfferOutDto
from app.campaigns.models.offer import Offer
from app.campaigns.services.offer_catalog_error import OfferCatalogError
from app.campaigns.services.offer_catalog_service import OfferCatalogService, get_offer_catalog_service

OfferCatalogServiceDep = Annotated[OfferCatalogService, Depends(get_offer_catalog_service)]

_STATUS = {
    "unavailable": status.HTTP_502_BAD_GATEWAY,
    "not_configured": status.HTTP_503_SERVICE_UNAVAILABLE,
}


class OfferController:
    """Search offers over HTTP."""

    router: APIRouter
    """Routes this controller serves."""

    def __init__(self) -> None:
        """Routes for the offer catalog."""
        self.router = APIRouter(prefix="/offers", tags=["offers"])
        self.router.get("")(self.search)

    def search(self, catalog: OfferCatalogServiceDep, q: str = "") -> list[OfferOutDto]:
        """Offers matching this text. Empty when the text is blank or nothing matches."""
        try:
            found = catalog.search(q)
        except OfferCatalogError as error:
            raise self._http_error(error) from None

        return [self._offer(offer) for offer in found]

    def _offer(self, offer: Offer) -> OfferOutDto:
        return OfferOutDto(id=offer.id, name=offer.name)

    def _http_error(self, error: OfferCatalogError) -> HTTPException:
        return HTTPException(status_code=_STATUS[error.kind])


offer_controller = OfferController()
