"""Whether a stored campaign still matches Keitaro."""

import json

from app.campaigns.models.campaign_remote import CampaignRemote
from app.campaigns.models.stream_remote import StreamRemote
from app.campaigns.services.campaign_record import CampaignRecord
from app.campaigns.services.campaign_stream_service import CampaignStreamService


class CampaignMatchService:
    """Compares a stored campaign with the campaign and flows Keitaro returns."""

    def matches_campaign(self, row: CampaignRecord, remote: CampaignRemote) -> bool:
        """True when the stored campaign still matches. False when Keitaro deleted it or a field differs."""
        if remote.state == "deleted":
            return False

        return (
            remote.name == row.name
            and remote.alias == row.alias
            and remote.type == "position"
            and remote.group_id == row.group_id
            and remote.traffic_source_id == row.traffic_source_id
        )

    def matches_streams(self, row: CampaignRecord, streams: list[StreamRemote]) -> bool:
        """True when both stored flows still match. False when a flow is missing or changed."""
        if len(streams) != 2:
            return False

        by_id = {stream.id: stream for stream in streams}

        if set(by_id) != {row.country_stream_id, row.offer_stream_id}:
            return False

        country = by_id[row.country_stream_id]
        offer = by_id[row.offer_stream_id]

        return _country_stream_matches(row, country) and _offer_stream_matches(row, offer)


def _active(stream: StreamRemote) -> bool:
    return stream.state == "active" and stream.type == "regular"


def _country_stream_matches(row: CampaignRecord, stream: StreamRemote) -> bool:
    if not _active(stream):
        return False

    if stream.schema != "redirect" or stream.action_type != "http":
        return False

    if stream.action_payload != CampaignStreamService.redirect_url:
        return False

    if len(stream.offers) != 0 or len(stream.filters) != 1:
        return False

    country_filter = stream.filters[0]

    return (
        country_filter.name == "country"
        and country_filter.mode == "accept"
        and _country_payload(country_filter.payload) == [row.country]
    )


def _offer_stream_matches(row: CampaignRecord, stream: StreamRemote) -> bool:
    if not _active(stream):
        return False

    if stream.schema != "landings" or stream.action_type != "http":
        return False

    if len(stream.filters) != 0 or len(stream.offers) != 1:
        return False

    offer = stream.offers[0]

    return offer.offer_id == row.offer_id and offer.share == 100 and offer.state == "active"


def _country_payload(payload: object) -> list[str] | None:
    value = payload

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None

    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        return None

    return value
