"""Keitaro Admin API client."""

import os
from collections.abc import Generator
from typing import Literal

import httpx

from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.models.filter_remote import FilterRemote
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_remote import StreamRemote


class KeitaroError(Exception):
    """Keitaro could not complete a call. The API key is not part of this error."""

    kind: Literal["not_found", "unavailable", "not_configured"]
    """Why the call failed: not_found, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)


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
