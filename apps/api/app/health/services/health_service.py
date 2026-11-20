"""Read whether the database accepts a query."""

from app.health.models.health import Health
from app.health.repositories.health_repository import HealthRepository, HealthRepositoryDep


class HealthService:
    """Whether the database accepts a query."""

    def __init__(self, database: HealthRepository) -> None:
        """A health service for one health repository."""
        self._database = database

    def read(self) -> Health:
        """Reachability of the database. The status is ok when the query succeeds."""
        self._database.ping()

        return Health(status="ok")


def get_health_service(database: HealthRepositoryDep) -> HealthService:
    """Health service for one request."""
    return HealthService(database)
