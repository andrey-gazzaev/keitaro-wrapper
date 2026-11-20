"""Fakes for offer controller tests."""

import httpx
from fastapi import status

from app.campaigns.models.offer import Offer
from app.campaigns.services.keitaro_error import KeitaroError


class FakeKeitaro:
    """Keitaro stand-in for the offer catalog. Tests never call the tracker."""

    offers: list[Offer]
    """Catalog in Keitaro order. Empty when the tracker has none."""

    reads: list[str]
    """Offer-list reads. Empty before the first read."""

    error: KeitaroError | None
    """Error raised by the list. None when the list succeeds."""

    body: object | None
    """Raw catalog body. None uses offers. A non-list is unavailable."""

    def __init__(self) -> None:
        """A stand-in with an empty catalog."""
        self.offers = []
        self.reads = []
        self.error = None
        self.body = None

    def list_offers(self) -> list[Offer]:
        """Every offer on this tracker, in Keitaro order. Empty when the tracker has none."""
        self.reads.append("offers")

        if self.error is not None:
            raise self.error

        payload: object = self.offers if self.body is None else self.body

        if not isinstance(payload, list):
            raise KeitaroError("unavailable")

        offers: list[Offer] = []

        for item in payload:
            if not isinstance(item, Offer):
                raise KeitaroError("unavailable")

            offers.append(item)

        return offers


def fake_keitaro() -> FakeKeitaro:
    """A new catalog stand-in."""
    return FakeKeitaro()


class OfferListClient(httpx.Client):
    """HTTP client that returns a list of offer objects."""

    def __init__(self, **kwargs: object) -> None:
        """A client for the base URL the service passes in."""
        super().__init__(transport=httpx.MockTransport(_offer_list), base_url=str(kwargs["base_url"]))


class OfferBodyClient(httpx.Client):
    """HTTP client that returns a non-list offer body."""

    def __init__(self, **kwargs: object) -> None:
        """A client for the base URL the service passes in."""
        super().__init__(transport=httpx.MockTransport(_offer_body), base_url=str(kwargs["base_url"]))


def _offer_list(request: httpx.Request) -> httpx.Response:
    if request.method == "GET" and request.url.path.endswith("/offers"):
        return httpx.Response(
            status.HTTP_200_OK,
            json=[{"id": 7, "name": "Alpha"}, {"id": 8, "name": "Beta"}],
        )

    return httpx.Response(status.HTTP_404_NOT_FOUND)


def _offer_body(request: httpx.Request) -> httpx.Response:
    if request.method == "GET" and request.url.path.endswith("/offers"):
        return httpx.Response(status.HTTP_200_OK, json={"id": 7, "name": "Alpha"})

    return httpx.Response(status.HTTP_404_NOT_FOUND)
