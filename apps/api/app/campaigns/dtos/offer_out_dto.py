"""Offer response body."""

from pydantic import BaseModel


class OfferOutDto(BaseModel):
    """Offer the client can show."""

    id: int
    """Keitaro offer id."""

    name: str
    """Offer name. Empty when Keitaro sends no name."""
