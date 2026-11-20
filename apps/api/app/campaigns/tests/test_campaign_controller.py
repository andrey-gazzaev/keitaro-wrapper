"""Campaign create, list, and sync."""

import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.offer_record import OfferRecord
from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_record import StreamRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import get_keitaro
from app.campaigns.tests.campaign_controller_mocks import FakeKeitaro, fake_keitaro, remote_stream
from app.db import SessionLocal, engine
from app.main import app
from app.schema import apply_schema

_ALIAS = re.compile(r"c[0-9a-f]{12}")


def _name(suffix: str = "campaign1") -> str:
    return f"{os.environ['CAMPAIGN_PREFIX']}{suffix}"


def _misspelled(suffix: str = "campaign1") -> tuple[str, str]:
    prefix = os.environ["CAMPAIGN_PREFIX"]
    first = prefix[0].swapcase() + prefix[1:]
    pivot = min(5, len(prefix) - 1)
    middle = prefix[:pivot] + prefix[pivot].swapcase() + prefix[pivot + 1 :]

    return first + suffix, middle + suffix


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


@pytest.fixture(autouse=True)
def empty_campaigns() -> Iterator[None]:
    apply_schema(engine)

    with SessionLocal() as session:
        session.execute(delete(StreamOfferRecord))
        session.execute(delete(StreamRecord))
        session.execute(delete(OfferRecord))
        session.execute(delete(CampaignRecord))
        session.commit()

    yield


def _post(
    http: TestClient,
    *,
    name: str | None = None,
    country: str = "us",
    offer_id: int = 7,
) -> dict[str, object]:
    response = http.post(
        "/campaigns",
        json={"name": _name() if name is None else name, "country": country, "offer_id": offer_id},
    )

    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()
    assert isinstance(body, dict)

    return body


def _row(campaign_id: int) -> CampaignRecord:
    with SessionLocal() as session:
        found = session.get(CampaignRecord, campaign_id)
        assert found is not None
        session.expunge(found)

        return found


def _set_created_at(campaign_id: int, when: datetime) -> None:
    with SessionLocal() as session:
        found = session.get(CampaignRecord, campaign_id)
        assert found is not None
        found.created_at = when
        session.commit()


def test_cc_01_campaign_uses_the_given_name(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http, name=f"  {_name()}  ")
    body = keitaro.campaign_bodies[0]

    assert created["name"] == _name()
    assert body["name"] == _name()
    assert body["type"] == "position"
    assert _ALIAS.fullmatch(str(body["alias"]))


def test_bare_prefix_is_accepted(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http, name=_name(""))

    assert created["name"] == _name("")
    assert keitaro.campaign_bodies[0]["name"] == _name("")


def test_cc_02_country_stream_filters_the_country_and_opens_google(
    http: TestClient,
    keitaro: FakeKeitaro,
) -> None:
    created = _post(http, country="au")
    country = keitaro.stream_bodies[0]

    assert country["campaign_id"] == created["id"]
    assert country["type"] == "regular"
    assert country["name"] == "Country"
    assert country["position"] == 1
    assert country["schema"] == "redirect"
    assert country["action_type"] == "http"
    assert country["action_payload"] == "https://www.google.com"
    assert country["offers"] == []
    assert country["filters"] == [{"name": "country", "mode": "accept", "payload": ["AU"]}]


def test_cc_03_offer_stream_sends_the_chosen_offer(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http, offer_id=7)
    offer = keitaro.stream_bodies[1]

    assert offer["campaign_id"] == created["id"]
    assert offer["type"] == "regular"
    assert offer["name"] == "Offer"
    assert offer["position"] == 2
    assert offer["schema"] == "landings"
    assert offer["action_type"] == "http"
    assert "action_payload" not in offer
    assert offer["filters"] == []
    assert offer["offers"] == [{"offer_id": 7, "share": 100, "state": "active"}]


def test_cc_04_campaign_uses_the_first_domain(http: TestClient, keitaro: FakeKeitaro) -> None:
    _post(http)

    assert keitaro.campaign_bodies[0]["domain_id"] == 11
    assert keitaro.campaign_bodies[0]["domain_id"] in keitaro.domains


def test_cc_05_campaign_uses_the_first_group(http: TestClient, keitaro: FakeKeitaro) -> None:
    _post(http)

    assert keitaro.campaign_bodies[0]["group_id"] == 21
    assert keitaro.campaign_bodies[0]["group_id"] in keitaro.groups


def test_cc_06_campaign_uses_the_first_traffic_source(http: TestClient, keitaro: FakeKeitaro) -> None:
    _post(http)

    assert keitaro.campaign_bodies[0]["traffic_source_id"] == 31
    assert keitaro.campaign_bodies[0]["traffic_source_id"] in keitaro.sources


def test_create_stores_one_row(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http, name=f"  {_name()}  ", country="us", offer_id=7)
    campaign_id = created["id"]
    assert isinstance(campaign_id, int)
    row = _row(campaign_id)
    listed = http.get("/campaigns")

    assert listed.status_code == status.HTTP_200_OK
    assert listed.json() == [{"id": campaign_id, "name": _name(), "deleted": False}]
    assert row.name == _name()
    assert row.country == "US"
    assert row.offer_id == 7
    assert row.domain_id == 11
    assert row.group_id == 21
    assert row.traffic_source_id == 31
    assert row.alias == keitaro.campaign_bodies[0]["alias"]
    assert _ALIAS.fullmatch(row.alias)
    assert row.country_stream_id == keitaro.streams[campaign_id][0][0]
    assert row.offer_stream_id == keitaro.streams[campaign_id][1][0]
    assert row.created_at is not None
    assert row.deleted_at is None
    assert created["deleted"] is False


def test_empty_setup_is_conflict_and_stores_nothing(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.domains = []
    response = http.post("/campaigns", json={"name": _name(), "country": "US", "offer_id": 7})

    assert response.status_code == status.HTTP_409_CONFLICT
    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_missing_offer_is_not_found(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = set()
    response = http.post("/campaigns", json={"name": _name(), "country": "US", "offer_id": 7})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_unconfigured_keitaro_is_unavailable(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.setup_error = KeitaroError("not_configured")
    response = http.post("/campaigns", json={"name": _name(), "country": "US", "offer_id": 7})

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert _count() == 0


def test_keitaro_failure_during_create_stores_nothing(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.stream_error = KeitaroError("unavailable")
    response = http.post("/campaigns", json={"name": _name(), "country": "US", "offer_id": 7})

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert keitaro.campaigns != {}
    assert _count() == 0


def test_invalid_campaign_is_rejected(http: TestClient, keitaro: FakeKeitaro) -> None:
    rejected = [
        {"name": "   ", "country": "US", "offer_id": 7},
        {"name": "Spring", "country": "US", "offer_id": 7},
        {"name": _misspelled()[0], "country": "US", "offer_id": 7},
        {"name": _misspelled()[1], "country": "US", "offer_id": 7},
        {"name": _name(), "country": "USA", "offer_id": 7},
        {"name": _name(), "country": "U1", "offer_id": 7},
        {"name": _name(), "country": "US", "offer_id": 0},
    ]

    for payload in rejected:
        response = http.post("/campaigns", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_sync_mismatch_sets_deleted_at_and_keeps_the_row(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, name="Other")
    response = http.post("/campaigns/sync")
    row = _row(campaign_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": campaign_id, "name": _name(), "deleted": True}]
    assert row.deleted_at is not None
    assert row.name == _name()


def test_sync_404_is_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = None
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["deleted"] is True
    assert ("streams", campaign_id) not in keitaro.reads
    assert _row(campaign_id).deleted_at is not None


def test_sync_deleted_state_is_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, state="deleted")
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["deleted"] is True


def test_sync_match_leaves_deleted_at_null(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    response = http.post("/campaigns/sync")
    row = _row(campaign_id)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{"id": campaign_id, "name": _name(), "deleted": False}]
    assert row.deleted_at is None
    assert ("campaign", campaign_id) in keitaro.reads
    assert ("streams", campaign_id) in keitaro.reads


def test_sync_disabled_campaign_still_matches(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, state="disabled")
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["deleted"] is False
    assert _row(campaign_id).deleted_at is None


def test_sync_json_country_payload_matches(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http, country="us")
    campaign_id = int(created["id"])
    row = _row(campaign_id)
    posted = keitaro.streams[campaign_id]
    country_body = dict(posted[0][1])
    country_body["filters"] = [{"name": "country", "mode": "accept", "payload": '["US"]'}]
    keitaro.stream_overrides[campaign_id] = [
        remote_stream(posted[0][0], country_body),
        remote_stream(posted[1][0], posted[1][1]),
    ]
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["deleted"] is False
    assert row.country == "US"


def test_sync_error_tombstones_nothing(http: TestClient, keitaro: FakeKeitaro) -> None:
    first = _post(http, name=_name("first"))
    second = _post(http, name=_name("second"))
    first_id = int(first["id"])
    second_id = int(second["id"])
    keitaro.campaign_overrides[first_id] = None
    keitaro.campaign_errors.add(second_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert _row(first_id).deleted_at is None
    assert _row(second_id).deleted_at is None


def test_sync_offer_change_and_extra_stream_still_match(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    posted = keitaro.streams[campaign_id]
    offer_body = dict(posted[1][1])
    offer_body["offers"] = [
        {"offer_id": 7, "share": 50, "state": "active"},
        {"offer_id": 8, "share": 50, "state": "active"},
    ]
    extra = dict(posted[1][1])
    extra["position"] = 3
    keitaro.stream_overrides[campaign_id] = [
        remote_stream(posted[0][0], posted[0][1]),
        remote_stream(posted[1][0], offer_body),
        remote_stream(999, extra),
    ]
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["deleted"] is False
    assert _row(campaign_id).deleted_at is None


def test_sync_stream_error_is_not_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.stream_errors.add(campaign_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert _row(campaign_id).deleted_at is None


def test_sync_skips_tombstones_and_returns_newest_first(http: TestClient, keitaro: FakeKeitaro) -> None:
    older = _post(http, name=_name("older"))
    current = _post(http, name=_name("current"))
    newer = _post(http, name=_name("newer"))
    older_id = int(older["id"])
    current_id = int(current["id"])
    newer_id = int(newer["id"])
    now = datetime.now(UTC)
    _set_created_at(older_id, now - timedelta(hours=2))
    _set_created_at(current_id, now - timedelta(hours=1))
    _set_created_at(newer_id, now)
    _mark_deleted(current_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == status.HTTP_200_OK
    assert [item["name"] for item in response.json()] == [
        _name("newer"),
        _name("current"),
        _name("older"),
    ]
    assert response.json()[1]["deleted"] is True
    assert ("campaign", current_id) not in keitaro.reads
    assert ("streams", current_id) not in keitaro.reads
    assert _row(current_id).deleted_at is not None
    assert _row(older_id).deleted_at is None
    assert _row(newer_id).deleted_at is None


def _count() -> int:
    with SessionLocal() as session:
        return len(session.query(CampaignRecord).all())


def _mark_deleted(campaign_id: int) -> None:
    with SessionLocal() as session:
        found = session.get(CampaignRecord, campaign_id)
        assert found is not None
        found.deleted_at = datetime.now(UTC)
        session.commit()
