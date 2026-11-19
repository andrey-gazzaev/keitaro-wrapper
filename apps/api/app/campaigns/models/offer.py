"""Offer stored for the editor."""


class Offer:
    """An offer the editor can show."""

    id: int
    """Keitaro offer id."""

    name: str
    """Offer name. Empty when Keitaro sends no name."""

    def __init__(self, id: int, name: str) -> None:
        """An offer with this id and name."""
        self.id = id
        self.name = name
