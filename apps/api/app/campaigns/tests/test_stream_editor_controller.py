"""Stream editor fetch, shares, push, and cancel."""

from collections.abc import Iterator
from decimal import Decimal

import httpx
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.campaigns.models.offer import Offer
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.services.keitaro_service import KeitaroService, get_keitaro
from app.campaigns.repositories.offer_record import OfferRecord
from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_record import StreamRecord
from app.campaigns.tests.stream_editor_controller_mocks import (
    FakeKeitaro,
    ScriptedClient,
    fake_keitaro,
    remote_stream,
    store_campaign,
)
from app.db import SessionLocal, engine
from app.main import app
from app.schema import apply_schema


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
def empty_editor() -> Iterator[None]:
    apply_schema(engine)

    with SessionLocal() as session:
        session.execute(delete(StreamOfferRecord))
        session.execute(delete(StreamRecord))
        session.execute(delete(OfferRecord))
        session.execute(delete(CampaignRecord))
        session.commit()

    yield


def test_editor_is_empty_before_fetch(http: TestClient) -> None:
    store_campaign()

    assert _ok(http.get("/campaigns/100/editor"))["streams"] == []


def test_fetch_imports_streams_and_offers(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    country = _stream(fetched, "Country")
    offer = _stream(fetched, "Offer")
    again = _ok(http.post("/campaigns/100/editor/fetch"))

    assert [item["name"] for item in fetched["streams"]] == ["Country", "Offer"]
    assert country["accepts_offers"] is False
    assert country["lines"] == []
    assert country["dirty"] is False
    assert offer["accepts_offers"] is True
    assert offer["dirty"] is False
    assert [(line["offer_id"], line["name"], line["share"]) for line in _lines(offer)] == [
        (1, "One", "10.00"),
        (2, "Two", "20.00"),
        (3, "Three", "70.00"),
    ]
    assert len(again["streams"]) == 2
    assert [line["share"] for line in _lines(_stream(again, "Offer"))] == ["10.00", "20.00", "70.00"]


def test_fetch_keeps_the_first_repeated_offer(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro, ((1, 10), (1, 90), (2, 20)))
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))

    assert [(line["offer_id"], line["share"]) for line in _lines(_stream(fetched, "Offer"))] == [
        (1, "10.00"),
        (2, "20.00"),
    ]


def test_fetch_leaves_a_dirty_share(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    added = _ok(_add(http, 201, 4))
    keitaro.streams[100][1] = remote_stream(201, name="Offer", position=2, offers=((1, 1), (2, 1), (3, 98)))
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    offer = _stream(fetched, "Offer")

    assert [line["share"] for line in _lines(_stream(added, "Offer"))] == ["25.00", "25.00", "25.00", "25.00"]
    assert [line["share"] for line in _lines(offer)] == ["25.00", "25.00", "25.00", "25.00"]
    assert offer["dirty"] is True
    assert ("update", 201) not in keitaro.reads


def test_fetch_archives_a_missing_stream(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 4))
    keitaro.streams[100] = [remote_stream(200, name="Country", position=1, flow_schema="redirect")]
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    offer = _stream(fetched, "Offer")

    assert offer["deleted"] is True
    assert offer["dirty"] is False
    assert [(line["offer_id"], line["share"], line["deleted"]) for line in _lines(offer)] == [
        (1, "0.00", True),
        (2, "0.00", True),
        (3, "0.00", True),
    ]
    assert _offer_ids() == {1, 2, 3, 4}
    assert _binding_offer_ids(201) == {1, 2, 3}


def test_fetch_archives_a_missing_offer(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    keitaro.streams[100][1] = remote_stream(201, name="Offer", position=2, offers=((1, 10), (3, 70)))
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    offer = _stream(fetched, "Offer")

    assert offer["dirty"] is False
    assert [(line["offer_id"], line["share"], line["deleted"], line["pinned"]) for line in _lines(offer)] == [
        (1, "10.00", False, False),
        (2, "0.00", True, False),
        (3, "70.00", False, False),
    ]


def test_fetch_keeps_an_unpublished_add(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro, ())
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 4))
    keitaro.streams[100] = [remote_stream(201, name="Offer", position=2)]
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    offer = _stream(fetched, "Offer")

    assert offer["deleted"] is False
    assert [line["offer_id"] for line in _lines(offer)] == [4]
    assert offer["dirty"] is True


def test_three_offers_split_the_remainder(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _landings(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 1))
    _ok(_add(http, 201, 2))
    added = _ok(_add(http, 201, 3))
    offer = _stream(added, "Offer")

    assert [line["share"] for line in _lines(offer)] == ["33.33", "33.33", "33.34"]
    assert offer["dirty"] is True
    assert keitaro.updates == []


def test_pinned_share_stays_while_others_split(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)
    first = _lines(_stream(editor, "Offer"))[0]
    pinned = _ok(_pin(http, int(first["id"]), "25.50"))
    lines = _lines(_stream(pinned, "Offer"))

    assert [(line["share"], line["pinned"]) for line in lines] == [
        ("25.50", True),
        ("37.25", False),
        ("37.25", False),
    ]


def test_unpin_clears_the_pin_and_splits_again(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)
    first = _lines(_stream(editor, "Offer"))[0]
    _ok(_pin(http, int(first["id"]), "25.00"))
    released = _ok(_unpin(http, int(first["id"])))

    assert [(line["share"], line["pinned"]) for line in _lines(_stream(released, "Offer"))] == [
        ("33.33", False),
        ("33.33", False),
        ("33.34", False),
    ]


def test_bring_back_splits_around_the_pin(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)
    lines = _lines(_stream(editor, "Offer"))
    pinned = _ok(_pin(http, int(lines[0]["id"]), "25"))
    removed = _ok(_remove(http, int(_lines(_stream(pinned, "Offer"))[2]["id"])))
    brought = _ok(_bring_back(http, int(_lines(_stream(removed, "Offer"))[2]["id"])))
    result = _lines(_stream(brought, "Offer"))

    assert [(line["share"], line["pinned"], line["deleted"]) for line in result] == [
        ("25.00", True, False),
        ("37.50", False, False),
        ("37.50", False, False),
    ]
    assert _stream(brought, "Offer")["dirty"] is True


def test_remove_sets_share_to_zero(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)
    target = _lines(_stream(editor, "Offer"))[2]
    removed = _ok(_remove(http, int(target["id"])))
    lines = _lines(_stream(removed, "Offer"))

    assert [(line["share"], line["deleted"], line["pinned"]) for line in lines] == [
        ("50.00", False, False),
        ("50.00", False, False),
        ("0.00", True, False),
    ]
    assert _stream(removed, "Offer")["dirty"] is True


def test_no_active_offers_is_an_empty_sum(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)

    for line in _lines(_stream(editor, "Offer")):
        editor = _ok(_remove(http, int(line["id"])))

    lines = _lines(_stream(editor, "Offer"))

    assert [line["share"] for line in lines] == ["0.00", "0.00", "0.00"]
    assert all(line["deleted"] is True for line in lines)


def test_pin_above_the_remainder_is_rejected(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _landings(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 1))
    added = _ok(_add(http, 201, 2))
    lines = _lines(_stream(added, "Offer"))
    _ok(_pin(http, int(lines[0]["id"]), "60"))
    rejected = _pin(http, int(lines[1]["id"]), "50")
    current = _lines(_stream(_ok(http.get("/campaigns/100/editor")), "Offer"))

    assert rejected.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert [(line["share"], line["pinned"]) for line in current] == [("60.00", True), ("40.00", False)]


def test_pin_that_rounds_a_share_below_zero_is_rejected(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _landings(keitaro)
    keitaro.offers[5] = "Five"
    _ok(http.post("/campaigns/100/editor/fetch"))

    for offer_id in (1, 2, 3, 4, 5):
        added = _ok(_add(http, 201, offer_id))

    first = _lines(_stream(added, "Offer"))[0]
    rejected = _pin(http, int(first["id"]), "99.98")
    current = _lines(_stream(_ok(http.get("/campaigns/100/editor")), "Offer"))

    assert rejected.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert [(line["share"], line["pinned"]) for line in current] == [("20.00", False)] * 5


def test_invalid_pin_share_is_rejected(http: TestClient) -> None:
    store_campaign()

    for share in ("25.555", "-1", "100.001", "101"):
        response = _pin(http, 1, share)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_add_conflicts(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 4))
    binding = _lines(_stream(_ok(http.get("/campaigns/100/editor")), "Offer"))[-1]
    _ok(_remove(http, int(binding["id"])))

    assert _add(http, 200, 4).status_code == status.HTTP_409_CONFLICT
    assert _add(http, 201, 4).status_code == status.HTTP_409_CONFLICT
    assert _add(http, 201, 8).status_code == status.HTTP_404_NOT_FOUND

    keitaro.streams[100] = [remote_stream(200, name="Country", position=1, flow_schema="redirect")]
    _ok(http.post("/campaigns/100/editor/fetch"))

    assert _add(http, 201, 1).status_code == status.HTTP_409_CONFLICT


def test_live_and_deleted_commands_conflict(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    editor = _three(http, keitaro)
    live = _lines(_stream(editor, "Offer"))[0]
    removed = _ok(_remove(http, int(live["id"])))
    deleted = _lines(_stream(removed, "Offer"))[0]

    assert _bring_back(http, int(_lines(_stream(removed, "Offer"))[1]["id"])).status_code == status.HTTP_409_CONFLICT
    assert _remove(http, int(deleted["id"])).status_code == status.HTTP_409_CONFLICT
    assert _pin(http, int(deleted["id"]), "10").status_code == status.HTTP_409_CONFLICT

    _ok(http.post("/campaigns/100/editor/streams/201/push"))
    keitaro.streams[100] = []
    archived = _ok(http.post("/campaigns/100/editor/fetch"))
    archived_line = _lines(_stream(archived, "Offer"))[0]
    updates = len(keitaro.updates)

    assert _bring_back(http, int(archived_line["id"])).status_code == status.HTTP_409_CONFLICT
    assert http.post("/campaigns/100/editor/streams/201/push").status_code == status.HTTP_409_CONFLICT
    assert len(keitaro.updates) == updates


def test_missing_campaign_is_not_found(http: TestClient, keitaro: FakeKeitaro) -> None:
    assert http.get("/campaigns/100/editor").status_code == status.HTTP_404_NOT_FOUND

    store_campaign(deleted=True)
    _landings(keitaro)

    assert http.get("/campaigns/100/editor").status_code == status.HTTP_404_NOT_FOUND
    assert http.post("/campaigns/100/editor/fetch").status_code == status.HTTP_404_NOT_FOUND
    assert http.get("/campaigns/100/editor/available-offers/7").status_code == status.HTTP_404_NOT_FOUND


def test_lookup_returns_the_offer(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    keitaro.offers[7] = "Alpha"
    found = http.get("/campaigns/100/editor/available-offers/7")
    missing = http.get("/campaigns/100/editor/available-offers/8")

    assert found.status_code == status.HTTP_200_OK
    assert found.json() == {"id": 7, "name": "Alpha"}
    assert missing.status_code == status.HTTP_404_NOT_FOUND
    assert ("offer", 7) in keitaro.reads


def test_push_replaces_offers_only(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    added = _ok(_add(http, 201, 4))
    pushed = _ok(http.post("/campaigns/100/editor/streams/201/push"))
    written = keitaro.updates[-1]
    removed = _ok(_remove(http, int(_lines(_stream(added, "Offer"))[0]["id"])))
    _ok(http.post("/campaigns/100/editor/streams/201/push"))

    assert written["filters"] == [{"name": "country"}]
    assert written["action_payload"] == "https://www.google.com"
    assert [_cents(item["share"]) for item in _offers(written)] == [Decimal("25.00")] * 4
    assert [item["state"] for item in _offers(written)] == ["active"] * 4
    assert _stream(pushed, "Offer")["dirty"] is False
    assert 1 not in [item["offer_id"] for item in _offers(keitaro.updates[-1])]
    assert _lines(_stream(removed, "Offer"))[0]["deleted"] is True


def test_cancel_drops_unpublished_bindings(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    _flows(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 4))
    reads = len(keitaro.reads)
    cancelled = _ok(http.post("/campaigns/100/editor/streams/201/cancel"))
    offer = _stream(cancelled, "Offer")

    assert [line["share"] for line in _lines(offer)] == ["10.00", "20.00", "70.00"]
    assert offer["dirty"] is False
    assert _offer_ids() == {1, 2, 3, 4}
    assert keitaro.updates == []
    assert len(keitaro.reads) == reads


def test_keitaro_failures_use_the_existing_status(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    keitaro.error = KeitaroError("unavailable")
    unavailable = http.post("/campaigns/100/editor/fetch")
    keitaro.error = KeitaroError("not_configured")
    unconfigured = http.post("/campaigns/100/editor/fetch")

    assert unavailable.status_code == status.HTTP_502_BAD_GATEWAY
    assert unconfigured.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_streams_follow_position_and_lines_follow_add_order(http: TestClient, keitaro: FakeKeitaro) -> None:
    store_campaign()
    keitaro.offers = {1: "One", 2: "Two"}
    keitaro.streams[100] = [
        remote_stream(202, name="Later", position=5),
        remote_stream(201, name="Earlier", position=0),
    ]
    fetched = _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 1))
    added = _ok(_add(http, 201, 2))

    assert [item["name"] for item in fetched["streams"]] == ["Earlier", "Later"]
    assert [line["offer_id"] for line in _lines(_stream(added, "Earlier"))] == [1, 2]


def test_omitted_position_is_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEITARO_BASE_URL", "http://keitaro.test")
    monkeypatch.setenv("KEITARO_API_KEY", "secret")
    monkeypatch.setattr(httpx, "Client", ScriptedClient)
    service = KeitaroService()

    assert service.list_streams(5)[0].position == 0
    assert service.list_streams(6)[0].position == 0

    with pytest.raises(KeitaroError) as error:
        service.list_streams(8)

    assert error.value.kind == "unavailable"
    service.close()


def test_offer_body_must_be_an_object_with_an_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEITARO_BASE_URL", "http://keitaro.test")
    monkeypatch.setenv("KEITARO_API_KEY", "secret")
    monkeypatch.setattr(httpx, "Client", ScriptedClient)
    service = KeitaroService()
    offer = service.get_offer(7)
    requested = service.get_offer(10)

    assert isinstance(offer, Offer)
    assert offer.id == 7
    assert offer.name == "Alpha"
    assert requested.id == 10
    assert requested.name == "Other"

    for offer_id in (8, 9):
        with pytest.raises(KeitaroError) as error:
            service.get_offer(offer_id)

        assert error.value.kind == "unavailable"

    service.close()


def _flows(keitaro: FakeKeitaro, offers: tuple[tuple[int, object], ...] = ((1, 10), (2, 20), (3, 70))) -> None:
    keitaro.offers = {1: "One", 2: "Two", 3: "Three", 4: "Four", 7: "Alpha"}
    keitaro.streams[100] = [
        remote_stream(200, name="Country", position=1, flow_schema="redirect"),
        remote_stream(201, name="Offer", position=2, offers=offers),
    ]
    keitaro.bodies[201] = {
        "filters": [{"name": "country"}],
        "offers": [],
        "action_payload": "https://www.google.com",
    }


def _landings(keitaro: FakeKeitaro) -> None:
    keitaro.offers = {1: "One", 2: "Two", 3: "Three", 4: "Four"}
    keitaro.streams[100] = [remote_stream(201, name="Offer", position=1)]
    keitaro.bodies[201] = {"filters": [], "offers": []}


def _three(http: TestClient, keitaro: FakeKeitaro) -> dict[str, object]:
    _landings(keitaro)
    _ok(http.post("/campaigns/100/editor/fetch"))
    _ok(_add(http, 201, 1))
    _ok(_add(http, 201, 2))

    return _ok(_add(http, 201, 3))


def _add(http: TestClient, stream_id: int, offer_id: int) -> httpx.Response:
    return http.post("/campaigns/100/editor/offers", json={"stream_id": stream_id, "offer_id": offer_id})


def _remove(http: TestClient, binding_id: int) -> httpx.Response:
    return http.post(f"/campaigns/100/editor/offers/{binding_id}/remove")


def _bring_back(http: TestClient, binding_id: int) -> httpx.Response:
    return http.post(f"/campaigns/100/editor/offers/{binding_id}/bring-back")


def _pin(http: TestClient, binding_id: int, share: str) -> httpx.Response:
    return http.post(f"/campaigns/100/editor/offers/{binding_id}/pin", json={"share": share})


def _unpin(http: TestClient, binding_id: int) -> httpx.Response:
    return http.post(f"/campaigns/100/editor/offers/{binding_id}/unpin")


def _ok(response: httpx.Response) -> dict[str, object]:
    assert response.status_code == status.HTTP_200_OK, response.text
    body = response.json()
    assert isinstance(body, dict)

    return body


def _stream(editor: dict[str, object], name: str) -> dict[str, object]:
    streams = editor["streams"]
    assert isinstance(streams, list)

    for stream in streams:
        assert isinstance(stream, dict)

        if stream["name"] == name:
            return stream

    raise AssertionError(name)


def _lines(stream: dict[str, object]) -> list[dict[str, object]]:
    lines = stream["lines"]
    assert isinstance(lines, list)
    assert all(isinstance(line, dict) for line in lines)

    return lines


def _offers(body: dict[str, object]) -> list[dict[str, object]]:
    offers = body["offers"]
    assert isinstance(offers, list)
    assert all(isinstance(item, dict) for item in offers)

    return offers


def _cents(value: object) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _offer_ids() -> set[int]:
    with SessionLocal() as session:
        return set(session.scalars(select(OfferRecord.keitaro_id)))


def _binding_offer_ids(stream_id: int) -> set[int]:
    with SessionLocal() as session:
        rows = session.scalars(
            select(StreamOfferRecord.offer_keitaro_id).where(StreamOfferRecord.stream_keitaro_id == stream_id)
        )

        return set(rows)
