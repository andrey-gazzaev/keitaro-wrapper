"""A failed stream editor call."""

from typing import Literal


class StreamEditorError(Exception):
    """The editor could not finish a call."""

    kind: Literal["not_found", "conflict", "invalid", "unavailable", "not_configured"]
    """not_found, conflict, invalid, unavailable, or not_configured."""

    def __init__(self, kind: Literal["not_found", "conflict", "invalid", "unavailable", "not_configured"]) -> None:
        """A failed call of this kind."""
        self.kind = kind
        super().__init__(kind)
