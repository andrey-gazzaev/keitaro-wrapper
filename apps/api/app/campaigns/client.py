"""Keitaro Admin API client."""

import os
from collections.abc import Generator
from dataclasses import dataclass
from typing import Literal

import httpx


class KeitaroError(Exception):
    """Keitaro could not complete a call. The API key is not part of this error."""

    kind: Literal["not_found", "unavailable", "not_configured"]
    """Why the call failed: not_found, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)


@dataclass(frozen=True)
class CampaignRemote:
    """Campaign fields read from Keitaro for a sync comparison."""

    name: str
    """Campaign name. Empty when Keitaro omits it."""

    alias: str
    """Campaign alias. Empty when Keitaro omits it."""

    type: str
    """Campaign type. Empty when Keitaro omits it."""

    state: str
    """Campaign state. Empty when Keitaro omits it."""

    group_id: int | None
    """Group id. None when Keitaro has no group."""

    traffic_source_id: int | None
    """Traffic source id. None when Keitaro has no traffic source."""


@dataclass(frozen=True)
class OfferRemote:
    """One offer on a Keitaro flow."""

    offer_id: object
    """Offer id as Keitaro sent it. None when the field is missing."""

    share: object
    """Share as Keitaro sent it. None when the field is missing."""

    state: object
    """Offer state as Keitaro sent it. None when the field is missing."""


@dataclass(frozen=True)
class FilterRemote:
    """One filter on a Keitaro flow."""

    name: str
    """Filter name. Empty when Keitaro omits it."""

    mode: str
    """Filter mode. Empty when Keitaro omits it."""

    payload: object
    """Filter payload as Keitaro sent it. None when the field is missing."""


@dataclass(frozen=True)
class StreamRemote:
    """One flow read from Keitaro for a sync comparison."""

    id: int
    """Keitaro flow id."""

    type: str
    """Flow type. Empty when Keitaro omits it."""

    state: str
    """Flow state. Empty when Keitaro omits it."""

    schema: str
    """Flow schema. Empty when Keitaro omits it."""

    action_type: str
    """Action type. Empty when Keitaro omits it."""

    action_payload: object
    """Action payload as Keitaro sent it. None when the field is missing."""

    offers: tuple[OfferRemote, ...]
    """Offers on this flow. Empty when the flow has none."""

    filters: tuple[FilterRemote, ...]
    """Filters on this flow. Empty when the flow has none."""


class KeitaroClient:
    """Client for the Keitaro admin API."""

    def __init__(self) -> None:
        """A client for the configured tracker. Calls do not run when the base URL or API key is missing."""
        base = os.environ.get("KEITARO_BASE_URL", "").strip().rstrip("/")
        key = os.environ.get("KEITARO_API_KEY", "").strip()
        self._http: httpx.Client | None = None

        if base and key:
            self._http = httpx.Client(
                base_url=f"{base}/admin_api/v1",
                headers={"Api-Key": key},
                timeout=30.0,
            )

    def close(self) -> None:
        """Close this client. Nothing to close when the tracker is not configured."""
        if self._http is not None:
            self._http.close()

    def list_domains(self) -> list[int]:
        """Domain ids in Keitaro order. Empty when the tracker has none."""
        return _ids(self._json(self._raise_for_status(self._request("GET", "/domains"))))

    def list_campaign_groups(self) -> list[int]:
        """Campaign group ids in Keitaro order. Empty when the tracker has none."""
        return _ids(self._json(self._raise_for_status(self._request("GET", "/groups", params={"type": "campaigns"}))))

    def list_traffic_sources(self) -> list[int]:
        """Traffic source ids in Keitaro order. Empty when the tracker has none."""
        return _ids(self._json(self._raise_for_status(self._request("GET", "/traffic_sources"))))

    def require_offer(self, offer_id: int) -> None:
        """Nothing when the offer exists. A missing offer or an unreadable tracker raises."""
        self._raise_for_status(self._request("GET", f"/offers/{offer_id}"))

    def create_campaign(self, body: dict[str, object]) -> int:
        """Create a campaign and return its Keitaro id."""
        return _resource_id(self._json(self._raise_for_status(self._request("POST", "/campaigns", json=body))))

    def create_stream(self, body: dict[str, object]) -> int:
        """Create a flow and return its Keitaro id."""
        return _resource_id(self._json(self._raise_for_status(self._request("POST", "/streams", json=body))))

    def get_campaign(self, campaign_id: int) -> CampaignRemote | None:
        """Campaign fields, or none when Keitaro answers 404."""
        response = self._request("GET", f"/campaigns/{campaign_id}")

        if response.status_code == 404:
            return None

        payload = self._json(self._raise_for_status(response))

        if not isinstance(payload, dict):
            raise KeitaroError("unavailable")

        return CampaignRemote(
            name=_text(payload.get("name")),
            alias=_text(payload.get("alias")),
            type=_text(payload.get("type")),
            state=_text(payload.get("state")),
            group_id=_whole(payload.get("group_id")),
            traffic_source_id=_whole(payload.get("traffic_source_id")),
        )

    def list_streams(self, campaign_id: int) -> list[StreamRemote]:
        """Flows on one campaign. Empty when the campaign has none."""
        payload = self._json(self._raise_for_status(self._request("GET", f"/campaigns/{campaign_id}/streams")))

        if not isinstance(payload, list):
            raise KeitaroError("unavailable")

        return [_stream(item) for item in payload]

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        http = self._http

        if http is None:
            raise KeitaroError("not_configured")

        try:
            return http.request(method, path, params=params, json=json)
        except httpx.HTTPError:
            raise KeitaroError("unavailable") from None

    def _raise_for_status(self, response: httpx.Response) -> httpx.Response:
        if response.status_code == 404:
            raise KeitaroError("not_found")

        if response.status_code >= 400:
            raise KeitaroError("unavailable")

        return response

    def _json(self, response: httpx.Response) -> object:
        try:
            return response.json()
        except ValueError:
            raise KeitaroError("unavailable") from None


def get_keitaro() -> Generator[KeitaroClient, None, None]:
    """Open a Keitaro client for one request and close it afterwards."""
    client = KeitaroClient()

    try:
        yield client
    finally:
        client.close()


def _ids(payload: object) -> list[int]:
    if not isinstance(payload, list):
        raise KeitaroError("unavailable")

    ids: list[int] = []

    for item in payload:
        if not isinstance(item, dict):
            raise KeitaroError("unavailable")

        item_id = _whole(item.get("id"))

        if item_id is None:
            raise KeitaroError("unavailable")

        ids.append(item_id)

    return ids


def _resource_id(payload: object) -> int:
    if not isinstance(payload, dict):
        raise KeitaroError("unavailable")

    resource_id = _whole(payload.get("id"))

    if resource_id is None:
        raise KeitaroError("unavailable")

    return resource_id


def _stream(payload: object) -> StreamRemote:
    if not isinstance(payload, dict):
        raise KeitaroError("unavailable")

    stream_id = _whole(payload.get("id"))

    if stream_id is None:
        raise KeitaroError("unavailable")

    return StreamRemote(
        id=stream_id,
        type=_text(payload.get("type")),
        state=_text(payload.get("state")),
        schema=_text(payload.get("schema")),
        action_type=_text(payload.get("action_type")),
        action_payload=payload.get("action_payload"),
        offers=_offers(payload.get("offers")),
        filters=_filters(payload.get("filters")),
    )


def _offers(payload: object) -> tuple[OfferRemote, ...]:
    if payload is None:
        return ()

    if not isinstance(payload, list):
        raise KeitaroError("unavailable")

    offers: list[OfferRemote] = []

    for item in payload:
        if not isinstance(item, dict):
            raise KeitaroError("unavailable")

        offers.append(
            OfferRemote(
                offer_id=item.get("offer_id"),
                share=item.get("share"),
                state=item.get("state"),
            )
        )

    return tuple(offers)


def _filters(payload: object) -> tuple[FilterRemote, ...]:
    if payload is None:
        return ()

    if not isinstance(payload, list):
        raise KeitaroError("unavailable")

    filters: list[FilterRemote] = []

    for item in payload:
        if not isinstance(item, dict):
            raise KeitaroError("unavailable")

        filters.append(
            FilterRemote(
                name=_text(item.get("name")),
                mode=_text(item.get("mode")),
                payload=item.get("payload"),
            )
        )

    return tuple(filters)


def _text(value: object) -> str:
    if isinstance(value, str):
        return value

    return ""


def _whole(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None

    return value
