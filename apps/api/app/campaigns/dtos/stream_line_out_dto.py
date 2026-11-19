"""One offer row in an editor response."""

from pydantic import BaseModel


class StreamLineOutDto(BaseModel):
    """One offer binding the client can show."""

    id: int
    """Binding id."""

    offer_id: int
    """Keitaro offer id."""

    name: str
    """Offer name. Empty when the catalog has no name."""

    share: str
    """Working share with two decimal places, such as 37.50. Zero when the offer is deleted."""

    pinned: bool
    """True when the working share stays fixed."""

    deleted: bool
    """True when the offer is removed and the row stays."""
