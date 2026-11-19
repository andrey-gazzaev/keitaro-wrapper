"""Campaign create, list, and sync."""

import re
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.campaigns.services.campaign_record import CampaignRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import get_keitaro
from app.campaigns.tests.campaign_controller_mocks import FakeKeitaro, fake_keitaro, remote_stream
from app.db import SessionLocal, engine
from app.main import app
from app.schema import apply_schema

_ALIAS = re.compile(r"c[0-9a-f]{12}")


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
        session.execute(delete(CampaignRecord))
        session.commit()

    yield


def _post(
    http: TestClient,
    *,
    name: str = "Spring",
    country: str = "us",
    offer_id: int = 7,
) -> dict[str, object]:
    response = http.post(
        "/campaigns",
        json={"name": name, "country": country, "offer_id": offer_id},
    )

    assert response.status_code == 200, response.text

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
    created = _post(http, name="  Spring  ")
    body = keitaro.campaign_bodies[0]

    assert created["name"] == "Spring"
    assert body["name"] == "Spring"
    assert body["type"] == "position"
    assert _ALIAS.fullmatch(str(body["alias"]))


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
    created = _post(http, name="  Spring  ", country="us", offer_id=7)
    campaign_id = created["id"]
    assert isinstance(campaign_id, int)
    row = _row(campaign_id)
    listed = http.get("/campaigns")

    assert listed.status_code == 200
    assert listed.json() == [{"id": campaign_id, "name": "Spring", "deleted": False}]
    assert row.name == "Spring"
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
    response = http.post("/campaigns", json={"name": "Spring", "country": "US", "offer_id": 7})

    assert response.status_code == 409
    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_missing_offer_is_not_found(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.offers = set()
    response = http.post("/campaigns", json={"name": "Spring", "country": "US", "offer_id": 7})

    assert response.status_code == 404
    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_unconfigured_keitaro_is_unavailable(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.setup_error = KeitaroError("not_configured")
    response = http.post("/campaigns", json={"name": "Spring", "country": "US", "offer_id": 7})

    assert response.status_code == 503
    assert _count() == 0


def test_keitaro_failure_during_create_stores_nothing(http: TestClient, keitaro: FakeKeitaro) -> None:
    keitaro.stream_error = KeitaroError("unavailable")
    response = http.post("/campaigns", json={"name": "Spring", "country": "US", "offer_id": 7})

    assert response.status_code == 502
    assert keitaro.campaigns != {}
    assert _count() == 0


def test_invalid_campaign_is_rejected(http: TestClient, keitaro: FakeKeitaro) -> None:
    rejected = [
        {"name": "   ", "country": "US", "offer_id": 7},
        {"name": "Spring", "country": "USA", "offer_id": 7},
        {"name": "Spring", "country": "U1", "offer_id": 7},
        {"name": "Spring", "country": "US", "offer_id": 0},
    ]

    for payload in rejected:
        response = http.post("/campaigns", json=payload)

        assert response.status_code == 422

    assert keitaro.campaign_bodies == []
    assert _count() == 0


def test_sync_mismatch_sets_deleted_at_and_keeps_the_row(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, name="Other")
    response = http.post("/campaigns/sync")
    row = _row(campaign_id)

    assert response.status_code == 200
    assert response.json() == [{"id": campaign_id, "name": "Spring", "deleted": True}]
    assert row.deleted_at is not None
    assert row.name == "Spring"


def test_sync_404_is_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = None
    response = http.post("/campaigns/sync")

    assert response.status_code == 200
    assert response.json()[0]["deleted"] is True
    assert ("streams", campaign_id) not in keitaro.reads
    assert _row(campaign_id).deleted_at is not None


def test_sync_deleted_state_is_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, state="deleted")
    response = http.post("/campaigns/sync")

    assert response.status_code == 200
    assert response.json()[0]["deleted"] is True


def test_sync_match_leaves_deleted_at_null(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    response = http.post("/campaigns/sync")
    row = _row(campaign_id)

    assert response.status_code == 200
    assert response.json() == [{"id": campaign_id, "name": "Spring", "deleted": False}]
    assert row.deleted_at is None
    assert ("campaign", campaign_id) in keitaro.reads
    assert ("streams", campaign_id) in keitaro.reads


def test_sync_disabled_campaign_still_matches(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.campaign_overrides[campaign_id] = keitaro.echo(campaign_id, state="disabled")
    response = http.post("/campaigns/sync")

    assert response.status_code == 200
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

    assert response.status_code == 200
    assert response.json()[0]["deleted"] is False
    assert row.country == "US"


def test_sync_error_tombstones_nothing(http: TestClient, keitaro: FakeKeitaro) -> None:
    first = _post(http, name="First")
    second = _post(http, name="Second")
    first_id = int(first["id"])
    second_id = int(second["id"])
    keitaro.campaign_overrides[first_id] = None
    keitaro.campaign_errors.add(second_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == 502
    assert _row(first_id).deleted_at is None
    assert _row(second_id).deleted_at is None


def test_sync_stream_error_is_not_a_mismatch(http: TestClient, keitaro: FakeKeitaro) -> None:
    created = _post(http)
    campaign_id = int(created["id"])
    keitaro.stream_errors.add(campaign_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == 502
    assert _row(campaign_id).deleted_at is None


def test_sync_skips_tombstones_and_returns_newest_first(http: TestClient, keitaro: FakeKeitaro) -> None:
    older = _post(http, name="Older")
    current = _post(http, name="Current")
    newer = _post(http, name="Newer")
    older_id = int(older["id"])
    current_id = int(current["id"])
    newer_id = int(newer["id"])
    now = datetime.now(UTC)
    _set_created_at(older_id, now - timedelta(hours=2))
    _set_created_at(current_id, now - timedelta(hours=1))
    _set_created_at(newer_id, now)
    _mark_deleted(current_id)
    response = http.post("/campaigns/sync")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["Newer", "Current", "Older"]
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
