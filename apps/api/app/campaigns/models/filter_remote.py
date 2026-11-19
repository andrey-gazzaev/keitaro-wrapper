"""One filter on a Keitaro flow."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FilterRemote:
    """One filter on a Keitaro flow."""

    name: str
    """Filter name. Empty when Keitaro omits it."""

    mode: str
    """Filter mode. Empty when Keitaro omits it."""

    payload: object
    """Filter payload as Keitaro sent it. None when the field is missing."""
