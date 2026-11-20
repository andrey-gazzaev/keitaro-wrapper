"""A failed offer catalog call."""

from typing import Literal


class OfferCatalogError(Exception):
    """The offer catalog could not be read."""

    kind: Literal["unavailable", "not_configured"]
    """unavailable or not_configured."""

    def __init__(self, kind: Literal["unavailable", "not_configured"]) -> None:
        """A failed catalog call of this kind."""
        self.kind = kind
        super().__init__(kind)
