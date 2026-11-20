"""Fakes for stream editor controller tests."""

from datetime import UTC, datetime

import httpx

from app.campaigns.models.offer import Offer
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.services.keitaro_error import KeitaroError
from app.db import SessionLocal


class FakeKeitaro:
    """Keitaro stand-in for the editor. Tests never call the tracker."""

    offers: dict[int, str]
    """Offer names by id. Missing ids are unknown."""

    streams: dict[int, list[StreamRemote]]
    """Flows by campaign id. Empty when the campaign has none."""

    bodies: dict[int, dict[str, object]]
    """Live stream bodies by id. Missing ids are unknown."""

    updates: list[dict[str, object]]
    """Bodies written back. Empty before the first push."""

    reads: list[tuple[str, int]]
    """Offer, flow, and stream reads, in call order. Empty before the first read."""

    error: KeitaroError | None
    """Error raised before a read or write. None when the call should succeed."""

    def __init__(self) -> None:
        """A stand-in with no offers and no flows."""
        self.offers = {}
        self.streams = {}
        self.bodies = {}
        self.updates = []
        self.reads = []
        self.error = None

    def list_streams(self, campaign_id: int) -> list[StreamRemote]:
        """Flows on this campaign. Empty when the campaign has none."""
        self._raise()
        self.reads.append(("streams", campaign_id))

        return list(self.streams.get(campaign_id, []))

    def get_offer(self, offer_id: int) -> Offer:
        """The offer for this id. A missing offer raises not_found."""
        self._raise()
        self.reads.append(("offer", offer_id))

        if offer_id not in self.offers:
            raise KeitaroError("not_found")

        return Offer(id=offer_id, name=self.offers[offer_id])

    def get_stream(self, stream_id: int) -> dict[str, object]:
        """A copy of the live stream body. A missing stream raises not_found."""
        self._raise()
        self.reads.append(("stream", stream_id))

        if stream_id not in self.bodies:
            raise KeitaroError("not_found")

        return dict(self.bodies[stream_id])

    def update_stream(self, stream_id: int, body: dict[str, object]) -> None:
        """Store this stream body. The previous body is replaced."""
        self._raise()
        self.reads.append(("update", stream_id))
        self.updates.append(body)
        self.bodies[stream_id] = body

    def _raise(self) -> None:
        if self.error is not None:
            raise self.error


def fake_keitaro() -> FakeKeitaro:
    """A new editor stand-in."""
    return FakeKeitaro()


def store_campaign(campaign_id: int = 100, *, deleted: bool = False) -> int:
    """A stored campaign row. Tombstoned when deleted is true."""
    with SessionLocal() as session:
        session.add(
            CampaignRecord(
                keitaro_id=campaign_id,
                name="test_gazzaev_campaign1",
                alias=f"c{campaign_id:012x}",
                country="US",
                offer_id=7,
                domain_id=11,
                group_id=21,
                traffic_source_id=31,
                country_stream_id=200,
                offer_stream_id=201,
                created_at=datetime.now(UTC),
                deleted_at=datetime.now(UTC) if deleted else None,
            )
        )
        session.commit()

    return campaign_id


def remote_stream(
    stream_id: int,
    *,
    name: str = "Offer",
    position: int = 1,
    flow_schema: str = "landings",
    offers: tuple[tuple[int, object], ...] = (),
) -> StreamRemote:
    """One flow read. Offers are pairs of id and share."""
    return StreamRemote(
        id=stream_id,
        name=name,
        position=position,
        type="regular",
        state="active",
        schema=flow_schema,
        action_type="http",
        action_payload=None,
        offers=tuple(OfferRemote(offer_id=offer_id, share=share, state="active") for offer_id, share in offers),
        filters=(),
    )


class ScriptedClient(httpx.Client):
    """HTTP client that answers the editor's Keitaro reads from canned JSON."""

    def __init__(self, **kwargs: object) -> None:
        """A client for the base URL the service passes in."""
        super().__init__(transport=httpx.MockTransport(_scripted), base_url=str(kwargs["base_url"]))


def _scripted(request: httpx.Request) -> httpx.Response:
    path = request.url.path

    if path.endswith("/campaigns/5/streams"):
        return httpx.Response(200, json=[{"id": 9, "name": "Offer", "schema": "landings"}])

    if path.endswith("/campaigns/6/streams"):
        return httpx.Response(200, json=[{"id": 10, "name": "Offer", "position": None}])

    if path.endswith("/campaigns/8/streams"):
        return httpx.Response(200, json=[{"id": 12, "name": "Offer", "position": "nope"}])

    if path.endswith("/offers/7"):
        return httpx.Response(200, json={"id": 7, "name": "Alpha"})

    if path.endswith("/offers/10"):
        return httpx.Response(200, json={"id": 99, "name": "Other"})

    if path.endswith("/offers/8"):
        return httpx.Response(200, json={"name": "Alpha"})

    if path.endswith("/offers/9"):
        return httpx.Response(200, json=["nope"])

    return httpx.Response(404)
