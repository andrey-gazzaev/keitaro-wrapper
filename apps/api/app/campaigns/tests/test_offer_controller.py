"""Offer catalog search."""

from collections.abc import Iterator

import httpx
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.campaigns.models.offer import Offer
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroService, get_keitaro
from app.campaigns.tests.offer_controller_mocks import (
    FakeKeitaro,
    OfferBodyClient,
    OfferListClient,
    fake_keitaro,
)
from app.main import app


@pytest.fixture
def keitaro() -> Iterator[FakeKeitaro]:
    fake = fake_keitaro()
    app.dependency_overrides[get_keitaro] = lambda: fake

    yield fake

    app.dependency_overrides.clear()


@pytest.fixture
def http(keitaro: FakeKeitaro) -> Iterator[TestClient]:
    with TestClient(app) as client:
        yield client


def test_blank_query_is_empty_and_does_not_read(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = [Offer(1, "Alpha")]
    missing = http.get("/offers")
    empty = http.get("/offers", params={"q": ""})
    spaces = http.get("/offers", params={"q": "   "})

    assert missing.status_code == status.HTTP_200_OK
    assert missing.json() == []
    assert empty.json() == []
    assert spaces.json() == []
    assert keitaro.reads == []


def test_name_and_id_matches_keep_keitaro_order(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = [
        Offer(17, "Beta"),
        Offer(3, "N7"),
        Offer(8, "Alpha"),
        Offer(4, "Other"),
    ]
    by_digit = http.get("/offers", params={"q": "7"})
    by_name = http.get("/offers", params={"q": "  ALPHA  "})

    assert by_digit.status_code == status.HTTP_200_OK
    assert by_digit.json() == [
        {"id": 17, "name": "Beta"},
        {"id": 3, "name": "N7"},
    ]
    assert by_name.status_code == status.HTTP_200_OK
    assert by_name.json() == [{"id": 8, "name": "Alpha"}]


def test_eleventh_match_is_cut(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = [Offer(offer_id, "Same") for offer_id in range(1, 13)]
    found = http.get("/offers", params={"q": "same"})

    assert found.status_code == status.HTTP_200_OK
    assert [item["id"] for item in found.json()] == list(range(1, 11))


def test_non_match_is_dropped(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = [Offer(1, "Alpha"), Offer(2, "Beta")]
    found = http.get("/offers", params={"q": "alpha"})

    assert found.status_code == status.HTTP_200_OK
    assert found.json() == [{"id": 1, "name": "Alpha"}]


def test_empty_catalog_is_empty(http: TestClient, keitaro: FakeKeitaro) -> None:
    found = http.get("/offers", params={"q": "alpha"})

    assert found.status_code == status.HTTP_200_OK
    assert found.json() == []
    assert keitaro.reads == ["offers"]


def test_unavailable_tracker_is_bad_gateway(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.error = KeitaroError("unavailable")
    response = http.get("/offers", params={"q": "alpha"})

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


def test_missing_configuration_is_service_unavailable(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.error = KeitaroError("not_configured")
    response = http.get("/offers", params={"q": "alpha"})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_malformed_list_is_bad_gateway(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.body = {"id": 7}
    response = http.get("/offers", params={"q": "alpha"})

    assert response.status_code == status.HTTP_502_BAD_GATEWAY


def test_list_offers_reads_objects_and_rejects_a_non_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEITARO_BASE_URL", "http://keitaro.test")
    monkeypatch.setenv("KEITARO_API_KEY", "secret")
    monkeypatch.setattr(httpx, "Client", OfferListClient)
    service = KeitaroService()
    offers = service.list_offers()

    assert [(offer.id, offer.name) for offer in offers] == [(7, "Alpha"), (8, "Beta")]
    service.close()

    monkeypatch.setattr(httpx, "Client", OfferBodyClient)
    service = KeitaroService()

    with pytest.raises(KeitaroError) as error:
        service.list_offers()

    assert error.value.kind == "unavailable"
    service.close()
