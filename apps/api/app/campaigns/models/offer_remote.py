"""One offer on a Keitaro flow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OfferRemote:
    """One offer on a Keitaro flow."""

    offer_id: object
    """Offer id as Keitaro sent it. None when the field is missing."""

    share: object
    """Share as Keitaro sent it. None when the field is missing."""

    state: object
    """Offer state as Keitaro sent it. None when the field is missing."""
