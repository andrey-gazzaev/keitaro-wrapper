"""One stream in an editor response."""

from pydantic import BaseModel

from app.campaigns.dtos.stream_line_out_dto import StreamLineOutDto


class StreamGroupOutDto(BaseModel):
    """One stream and the offer rows the client can show."""

    id: int
    """Keitaro stream id."""

    name: str
    """Stream name. Empty when Keitaro sends no name."""

    position: int
    """Order of this stream on the campaign."""

    accepts_offers: bool
    """True when this live landings stream can take an offer."""

    deleted: bool
    """True when Keitaro no longer returns this stream."""

    dirty: bool
    """True when this stream has unpublished working changes."""

    lines: list[StreamLineOutDto]
    """Offer rows in stored order. Empty when the stream has no offers."""
