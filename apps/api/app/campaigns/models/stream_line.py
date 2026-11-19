"""One offer row in the stream editor."""

from decimal import Decimal


class StreamLine:
    """One offer binding shown on a stream."""

    id: int
    """Binding id."""

    offer_id: int
    """Keitaro offer id."""

    name: str
    """Offer name. Empty when the catalog has no name."""

    share: Decimal
    """Working share from 0 to 100. Zero when the offer is deleted."""

    pinned: bool
    """True when the working share stays fixed."""

    deleted: bool
    """True when the offer is removed from the stream and kept on the row."""

    def __init__(
        self,
        id: int,
        offer_id: int,
        name: str,
        share: Decimal,
        pinned: bool,
        deleted: bool,
    ) -> None:
        """A line with this binding, offer, share, and flags."""
        self.id = id
        self.offer_id = offer_id
        self.name = name
        self.share = share
        self.pinned = pinned
        self.deleted = deleted
