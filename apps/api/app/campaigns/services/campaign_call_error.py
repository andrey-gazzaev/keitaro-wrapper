"""A failed campaign call."""

from typing import Literal


class CampaignCallError(Exception):
    """A campaign call to Keitaro failed."""

    kind: Literal["not_found", "unavailable", "not_configured"]
    """not_found, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)
