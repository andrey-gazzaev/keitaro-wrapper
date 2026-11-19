"""One stream in the editor."""

from app.campaigns.models.stream_line import StreamLine


class StreamGroup:
    """One stream and the offer rows the editor shows."""

    id: int
    """Keitaro stream id."""

    name: str
    """Stream name. Empty when Keitaro sends no name."""

    position: int
    """Order of this stream on the campaign."""

    accepts_offers: bool
    """True when the stream is a live landings stream and can take an offer."""

    deleted: bool
    """True when Keitaro no longer returns this stream."""

    dirty: bool
    """True when this stream has unpublished working changes."""

    lines: list[StreamLine]
    """Offer rows. Empty when the stream has no offers."""

    def __init__(
        self,
        id: int,
        name: str,
        position: int,
        accepts_offers: bool,
        deleted: bool,
        dirty: bool,
        lines: list[StreamLine],
    ) -> None:
        """A stream with these rows and flags."""
        self.id = id
        self.name = name
        self.position = position
        self.accepts_offers = accepts_offers
        self.deleted = deleted
        self.dirty = dirty
        self.lines = lines
