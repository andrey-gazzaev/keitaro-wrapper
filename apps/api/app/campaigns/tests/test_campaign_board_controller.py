"""Campaign board search and pages."""

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
from app.db import SessionLocal, engine
from app.main import app
from app.schema import apply_schema

_WHEN = datetime(2026, 1, 1, tzinfo=UTC)


@pytest.fixture
def http() -> Iterator[TestClient]:
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


def _store(
    campaign_id: int,
    name: str,
    created_at: datetime,
    deleted_at: datetime | None = None,
) -> None:
    with SessionLocal() as session:
        session.add(
            CampaignRecord(
                keitaro_id=campaign_id,
                name=name,
                alias=f"board-{campaign_id}",
                created_at=created_at,
                deleted_at=deleted_at,
            )
        )
        session.commit()


def _board(http: TestClient, **params: object) -> dict[str, object]:
    response = http.get("/campaigns/board", params=params)

    assert response.status_code == status.HTTP_200_OK, response.text

    body = response.json()
    assert isinstance(body, dict)

    return body


def test_nothing_stored_is_empty(http: TestClient) -> None:
    assert _board(http) == {"campaigns": [], "page": 0, "page_count": 0, "state": "empty"}
    assert _board(http, q="spring", page=-1) == {"campaigns": [], "page": 0, "page_count": 0, "state": "empty"}


def test_blank_search_lists_every_campaign_newest_first(http: TestClient) -> None:
    _store(9, "Older", _WHEN)
    _store(2, "Newer", _WHEN + timedelta(seconds=1), _WHEN + timedelta(days=1))
    expected = [
        {"id": 2, "name": "Newer", "deleted": True},
        {"id": 9, "name": "Older", "deleted": False},
    ]

    assert _board(http)["campaigns"] == expected
    assert _board(http, q="   ")["campaigns"] == expected
    assert http.get("/campaigns").json() == expected


def test_name_match_is_a_trimmed_case_insensitive_substring(http: TestClient) -> None:
    _store(10, "Spring Sale", _WHEN)
    found = _board(http, q="  sPrIng ")

    assert found["state"] == "ready"
    assert found["campaigns"] == [{"id": 10, "name": "Spring Sale", "deleted": False}]
    assert _board(http, q="nope") == {"campaigns": [], "page": 0, "page_count": 0, "state": "none"}


def test_id_match_is_a_decimal_substring(http: TestClient) -> None:
    _store(120, "Alpha", _WHEN)
    _store(3, "Beta", _WHEN + timedelta(seconds=1))
    matched = _board(http, q="12")

    assert matched["campaigns"] == [{"id": 120, "name": "Alpha", "deleted": False}]
    assert _board(http, q="3")["campaigns"] == [{"id": 3, "name": "Beta", "deleted": False}]


def test_like_markers_stay_literal(http: TestClient) -> None:
    _store(1, "100% off", _WHEN)
    _store(2, "1000", _WHEN)
    _store(3, "a_b", _WHEN)
    _store(4, "axb", _WHEN)
    _store(5, "a\\b", _WHEN)

    assert [row["id"] for row in _board(http, q="%")["campaigns"]] == [1]
    assert [row["id"] for row in _board(http, q="_")["campaigns"]] == [3]
    assert [row["id"] for row in _board(http, q="a\\b")["campaigns"]] == [5]


def test_page_is_fifty_rows_clamped_and_stable(http: TestClient) -> None:
    for campaign_id in range(1, 52):
        name = "Keep" if campaign_id in {1, 51} else "Drop"
        _store(campaign_id, name, _WHEN)

    first = _board(http, page=-4)
    second = _board(http, page=1)
    clamped = _board(http, page=8)
    kept = _board(http, q="Keep", page=3)
    listed = http.get("/campaigns")

    assert first["page"] == 0
    assert first["page_count"] == 2
    assert first["state"] == "ready"
    assert [row["id"] for row in first["campaigns"]] == list(range(51, 1, -1))
    assert [row["id"] for row in second["campaigns"]] == [1]
    assert second["page"] == 1
    assert [row["id"] for row in clamped["campaigns"]] == [1]
    assert clamped["page"] == 1
    assert kept == {
        "campaigns": [
            {"id": 51, "name": "Keep", "deleted": False},
            {"id": 1, "name": "Keep", "deleted": False},
        ],
        "page": 0,
        "page_count": 1,
        "state": "ready",
    }
    assert {row["id"] for row in listed.json()} == set(range(1, 52))
