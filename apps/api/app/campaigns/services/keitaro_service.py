"""Keitaro Admin API calls."""

import os
from collections.abc import Generator
from typing import Annotated

import httpx
from fastapi import Depends, status

from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.models.filter_remote import FilterRemote
from app.campaigns.models.offer import Offer
from app.campaigns.models.offer_remote import OfferRemote
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.services.keitaro_error import KeitaroError
from app.campaigns.utilities.text import text
from app.campaigns.utilities.whole import whole


class KeitaroService:
    """Calls the Keitaro admin API."""

    def __init__(self) -> None:
        """A service for the configured tracker. Calls do not run when the base URL or API key is missing."""
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

    def list_campaigns(self) -> list[CampaignRemote]:
        """Every campaign on this tracker. Empty when the tracker has none."""
        payload = self._json(self._raise_for_status(self._request("GET", "/campaigns")))

        if not isinstance(payload, list):
            raise KeitaroError("unavailable")

        return [_campaign_remote(item) for item in payload]

    def get_campaign(self, campaign_id: int) -> CampaignRemote | None:
        """Campaign fields, or none when Keitaro answers 404."""
        response = self._request("GET", f"/campaigns/{campaign_id}")

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None

        payload = self._json(self._raise_for_status(response))

        if not isinstance(payload, dict):
            raise KeitaroError("unavailable")

        return _campaign_remote({**payload, "id": campaign_id})

    def list_streams(self, campaign_id: int) -> list[StreamRemote]:
        """Flows on one campaign. Empty when the campaign has none."""
        payload = self._json(self._raise_for_status(self._request("GET", f"/campaigns/{campaign_id}/streams")))

        if not isinstance(payload, list):
            raise KeitaroError("unavailable")

        return [_stream(item) for item in payload]

    def get_offer(self, offer_id: int) -> Offer:
        """The offer for this id. A missing offer raises not_found."""
        payload = self._json(self._raise_for_status(self._request("GET", f"/offers/{offer_id}")))

        if not isinstance(payload, dict) or whole(payload.get("id")) is None:
            raise KeitaroError("unavailable")

        return Offer(id=offer_id, name=text(payload.get("name")))

    def get_stream(self, stream_id: int) -> dict[str, object]:
        """Live stream body. Filters and the redirect stay in the body for a later write."""
        payload = self._json(self._raise_for_status(self._request("GET", f"/streams/{stream_id}")))

        if not isinstance(payload, dict):
            raise KeitaroError("unavailable")

        return payload

    def update_stream(self, stream_id: int, body: dict[str, object]) -> None:
        """Write this stream body back. The caller chooses the offers."""
        self._raise_for_status(self._request("PUT", f"/streams/{stream_id}", json=body))

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
        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise KeitaroError("not_found")

        if response.status_code >= status.HTTP_400_BAD_REQUEST:
            raise KeitaroError("unavailable")

        return response

    def _json(self, response: httpx.Response) -> object:
        try:
            return response.json()
        except ValueError:
            raise KeitaroError("unavailable") from None


def get_keitaro() -> Generator[KeitaroService, None, None]:
    """Open a Keitaro service for one request and close it afterwards."""
    client = KeitaroService()

    try:
        yield client
    finally:
        client.close()


KeitaroDep = Annotated[KeitaroService, Depends(get_keitaro)]


def _ids(payload: object) -> list[int]:
    if not isinstance(payload, list):
        raise KeitaroError("unavailable")

    ids: list[int] = []

    for item in payload:
        if not isinstance(item, dict):
            raise KeitaroError("unavailable")

        item_id = whole(item.get("id"))

        if item_id is None:
            raise KeitaroError("unavailable")

        ids.append(item_id)

    return ids


def _campaign_remote(payload: object) -> CampaignRemote:
    if not isinstance(payload, dict):
        raise KeitaroError("unavailable")

    campaign_id = whole(payload.get("id"))

    if campaign_id is None:
        raise KeitaroError("unavailable")

    return CampaignRemote(
        id=campaign_id,
        name=text(payload.get("name")),
        alias=text(payload.get("alias")),
        type=text(payload.get("type")),
        state=text(payload.get("state")),
        domain_id=whole(payload.get("domain_id")),
        group_id=whole(payload.get("group_id")),
        traffic_source_id=whole(payload.get("traffic_source_id")),
    )


def _resource_id(payload: object) -> int:
    if not isinstance(payload, dict):
        raise KeitaroError("unavailable")

    resource_id = whole(payload.get("id"))

    if resource_id is None:
        raise KeitaroError("unavailable")

    return resource_id


def _stream(payload: object) -> StreamRemote:
    if not isinstance(payload, dict):
        raise KeitaroError("unavailable")

    stream_id = whole(payload.get("id"))

    if stream_id is None:
        raise KeitaroError("unavailable")

    if "position" not in payload or payload.get("position") is None:
        position = 0
    else:
        position = whole(payload.get("position"))

        if position is None:
            raise KeitaroError("unavailable")

    return StreamRemote(
        id=stream_id,
        name=text(payload.get("name")),
        position=position,
        type=text(payload.get("type")),
        state=text(payload.get("state")),
        schema=text(payload.get("schema")),
        action_type=text(payload.get("action_type")),
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
                name=text(item.get("name")),
                mode=text(item.get("mode")),
                payload=item.get("payload"),
            )
        )

    return tuple(filters)
