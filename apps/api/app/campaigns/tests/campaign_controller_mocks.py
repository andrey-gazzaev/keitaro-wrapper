"""Fakes for campaign controller tests."""

from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.models.filter_remote import FilterRemote
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.services.keitaro_error import KeitaroError


class FakeKeitaro:
    """Keitaro stand-in. Tests never call the tracker or read the API key."""

    domains: list[int]
    """Domain ids. Empty when the tracker has none."""

    groups: list[int]
    """Campaign group ids. Empty when the tracker has none."""

    sources: list[int]
    """Traffic source ids. Empty when the tracker has none."""

    offers: set[int]
    """Offer ids that exist. Empty when every offer is missing."""

    campaign_bodies: list[dict[str, object]]
    """Bodies posted to create a campaign. Empty before the first create."""

    stream_bodies: list[dict[str, object]]
    """Bodies posted to create a flow. Empty before the first create."""

    campaigns: dict[int, dict[str, object]]
    """Created campaign bodies by id. Empty before the first create."""

    streams: dict[int, list[tuple[int, dict[str, object]]]]
    """Created flows by campaign id. Empty before the first flow."""

    campaign_overrides: dict[int, CampaignRemote | None]
    """Campaign reads replaced for a test. Empty when reads use the created body."""

    stream_overrides: dict[int, list[StreamRemote]]
    """Flow reads replaced for a test. Empty when reads use the created flows."""

    campaign_errors: set[int]
    """Campaign ids whose read fails. Empty when every read succeeds."""

    stream_errors: set[int]
    """Campaign ids whose flow read fails. Empty when every read succeeds."""

    reads: list[tuple[str, int]]
    """Campaign and flow reads, in call order. Empty before the first read."""

    setup_error: KeitaroError | None
    """Error raised before a setup call. None when setup should succeed."""

    create_error: KeitaroError | None
    """Error raised before a campaign create. None when create should succeed."""

    stream_error: KeitaroError | None
    """Error raised before a flow create. None when create should succeed."""

    def __init__(self) -> None:
        """A stand-in with the usual first domain, group, source, and offer."""
        self.domains = [11, 12]
        self.groups = [21, 22]
        self.sources = [31, 32]
        self.offers = {7}
        self.campaign_bodies = []
        self.stream_bodies = []
        self.campaigns = {}
        self.streams = {}
        self.campaign_overrides = {}
        self.stream_overrides = {}
        self.campaign_errors = set()
        self.stream_errors = set()
        self.reads = []
        self.setup_error = None
        self.create_error = None
        self.stream_error = None
        self._next_campaign = 100
        self._next_stream = 200

    def list_domains(self) -> list[int]:
        """Domain ids in list order. Empty when none are configured."""
        self._raise_setup()

        return list(self.domains)

    def list_campaign_groups(self) -> list[int]:
        """Campaign group ids in list order. Empty when none are configured."""
        self._raise_setup()

        return list(self.groups)

    def list_traffic_sources(self) -> list[int]:
        """Traffic source ids in list order. Empty when none are configured."""
        self._raise_setup()

        return list(self.sources)

    def require_offer(self, offer_id: int) -> None:
        """Nothing when the offer is present. A missing offer raises not_found."""
        self._raise_setup()

        if offer_id not in self.offers:
            raise KeitaroError("not_found")

    def create_campaign(self, body: dict[str, object]) -> int:
        """The id of the campaign created from this body."""
        self._raise_setup()

        if self.create_error is not None:
            raise self.create_error

        self.campaign_bodies.append(body)
        campaign_id = self._next_campaign
        self._next_campaign += 1
        self.campaigns[campaign_id] = body

        return campaign_id

    def create_stream(self, body: dict[str, object]) -> int:
        """The id of the flow created from this body."""
        self._raise_setup()

        if self.stream_error is not None:
            raise self.stream_error

        self.stream_bodies.append(body)
        stream_id = self._next_stream
        self._next_stream += 1
        campaign_id = body["campaign_id"]
        assert isinstance(campaign_id, int)
        self.streams.setdefault(campaign_id, []).append((stream_id, body))

        return stream_id

    def get_campaign(self, campaign_id: int) -> CampaignRemote | None:
        """Campaign fields for this id. None when the test marks the campaign missing."""
        self.reads.append(("campaign", campaign_id))

        if campaign_id in self.campaign_errors:
            raise KeitaroError("unavailable")

        if campaign_id in self.campaign_overrides:
            return self.campaign_overrides[campaign_id]

        return self.echo(campaign_id)

    def list_streams(self, campaign_id: int) -> list[StreamRemote]:
        """Flows on this campaign. Empty when the campaign has none."""
        self.reads.append(("streams", campaign_id))

        if campaign_id in self.stream_errors:
            raise KeitaroError("unavailable")

        if campaign_id in self.stream_overrides:
            return self.stream_overrides[campaign_id]

        return [remote_stream(stream_id, body) for stream_id, body in self.streams[campaign_id]]

    def echo(self, campaign_id: int, *, state: str = "active", name: str | None = None) -> CampaignRemote:
        """Campaign fields echoed from the created body."""
        body = self.campaigns[campaign_id]
        group_id = body["group_id"]
        source_id = body["traffic_source_id"]
        assert isinstance(group_id, int)
        assert isinstance(source_id, int)

        return CampaignRemote(
            name=str(body["name"] if name is None else name),
            alias=str(body["alias"]),
            type=str(body["type"]),
            state=state,
            group_id=group_id,
            traffic_source_id=source_id,
        )

    def _raise_setup(self) -> None:
        if self.setup_error is not None:
            raise self.setup_error


def fake_keitaro() -> FakeKeitaro:
    """A new Keitaro stand-in."""
    return FakeKeitaro()


def remote_stream(stream_id: int, body: dict[str, object]) -> StreamRemote:
    """A flow read built from a posted body."""
    raw_filters = body.get("filters", [])
    raw_offers = body.get("offers", [])
    assert isinstance(raw_filters, list)
    assert isinstance(raw_offers, list)

    position = body.get("position", 0)
    assert isinstance(position, int)

    return StreamRemote(
        id=stream_id,
        name=str(body.get("name", "")),
        position=position,
        type=str(body["type"]),
        state="active",
        schema=str(body["schema"]),
        action_type=str(body["action_type"]),
        action_payload=body.get("action_payload"),
        offers=tuple(_offer(item) for item in raw_offers),
        filters=tuple(_filter(item) for item in raw_filters),
    )


def _offer(item: object) -> OfferRemote:
    assert isinstance(item, dict)

    return OfferRemote(offer_id=item["offer_id"], share=item["share"], state=item["state"])


def _filter(item: object) -> FilterRemote:
    assert isinstance(item, dict)

    return FilterRemote(name=str(item["name"]), mode=str(item["mode"]), payload=item["payload"])
