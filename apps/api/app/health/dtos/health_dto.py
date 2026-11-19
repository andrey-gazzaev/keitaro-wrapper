"""Health response body."""

from typing import Literal

from pydantic import BaseModel


class HealthDto(BaseModel):
    """Reachability of the API and the database."""

    status: Literal["ok"]
    """ok when the process is up and the database accepts a query."""
