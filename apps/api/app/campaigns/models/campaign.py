"""Stored campaign."""


class Campaign:
    """A campaign stored for this tracker."""

    id: int
    """Keitaro id of this campaign."""

    name: str
    """Name shown to the operator."""

    deleted: bool
    """True when the stored row is a tombstone. False while the campaign is live."""

    def __init__(self, id: int, name: str, deleted: bool) -> None:
        """A stored campaign with this id, name, and deleted flag."""
        self.id = id
        self.name = name
        self.deleted = deleted
