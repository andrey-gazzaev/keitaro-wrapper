"""Search offers by name or id."""

from typing import Literal

from app.campaigns.models.offer import Offer
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroDep, KeitaroService
from app.campaigns.services.offer_catalog_error import OfferCatalogError


class OfferCatalogService:
    """Searches offers by name or id."""

    def __init__(self, keitaro: KeitaroService) -> None:
        """A catalog for this Keitaro service."""
        self._keitaro = keitaro

    def search(self, query: str) -> list[Offer]:
        """Up to ten offers whose name or id contains this text. Empty when the text is blank or nothing matches."""
        needle = query.strip()

        if needle == "":
            return []

        try:
            offers = self._keitaro.list_offers()
        except KeitaroError as error:
            raise OfferCatalogError(_catalog_kind(error)) from None

        found: list[Offer] = []
        folded = needle.casefold()

        for offer in offers:
            if folded in offer.name.casefold() or needle in str(offer.id):
                found.append(offer)

                if len(found) == 10:
                    return found

        return found


def get_offer_catalog_service(keitaro: KeitaroDep) -> OfferCatalogService:
    """Offer catalog for one request."""
    return OfferCatalogService(keitaro)


def _catalog_kind(error: KeitaroError) -> Literal["unavailable", "not_configured"]:
    if error.kind == "not_configured":
        return "not_configured"

    return "unavailable"
