"""Health domain type."""

from typing import Literal


class Health:
    """Reachability of the database."""

    status: Literal["ok"]
    """ok when the database accepts a query."""

    def __init__(self, status: Literal["ok"]) -> None:
        """A health result with this status."""
        self.status = status
