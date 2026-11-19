"""Read whether the database accepts a query."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionDep
from app.health.model import Health


class HealthCheck:
    """Whether the database accepts a query."""

    def __init__(self, session: Session) -> None:
        """A health check bound to one database session."""
        self._session = session

    def read(self) -> Health:
        """Reachability of the database. The status is ok when the query succeeds."""
        self._session.execute(text("SELECT 1"))

        return Health(status="ok")


def get_health_check(session: SessionDep) -> HealthCheck:
    """Health check for one request."""
    return HealthCheck(session)
