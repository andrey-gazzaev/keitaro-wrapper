"""A failed Keitaro admin call."""

from typing import Literal


class KeitaroError(Exception):
    """Keitaro could not complete a call. The API key is not part of this error."""

    kind: Literal["not_found", "unavailable", "not_configured"]
    """Why the call failed: not_found, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)
