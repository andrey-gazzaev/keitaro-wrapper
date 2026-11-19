"""One flow read from Keitaro."""

from dataclasses import dataclass

from app.campaigns.models.filter_remote import FilterRemote
from app.campaigns.models.offer_remote import OfferRemote


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
