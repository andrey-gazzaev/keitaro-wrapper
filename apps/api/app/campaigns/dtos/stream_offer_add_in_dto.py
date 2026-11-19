"""Add-offer request body."""

from typing import Annotated

from pydantic import BaseModel, Field


class StreamOfferAddInDto(BaseModel):
    """Stream and offer to bind."""

    stream_id: Annotated[int, Field(ge=1)]
    """Keitaro stream id. Values below 1 are rejected."""

    offer_id: Annotated[int, Field(ge=1)]
    """Keitaro offer id. Values below 1 are rejected."""
