"""Read whether the database accepts a query."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionDep
from app.health.models.health import Health


class HealthService:
    """Whether the database accepts a query."""

    def __init__(self, session: Session) -> None:
        """A health service bound to one database session."""
        self._session = session

    def read(self) -> Health:
        """Reachability of the database. The status is ok when the query succeeds."""
        self._session.execute(text("SELECT 1"))

        return Health(status="ok")


def get_health_service(session: SessionDep) -> HealthService:
    """Health service for one request."""
    return HealthService(session)
