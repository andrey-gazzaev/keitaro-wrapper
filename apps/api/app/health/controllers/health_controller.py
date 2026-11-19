"""Health route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.health.dtos.health_dto import HealthDto
from app.health.services.health_service import HealthService, get_health_service

HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]


class HealthController:
    """Whether the process and the database are up."""

    router: APIRouter
    """Routes this controller serves."""

    def __init__(self) -> None:
        """The health route."""
        self.router = APIRouter()
        self.router.get("/health")(self.read_health)

    def read_health(self, checks: HealthServiceDep) -> HealthDto:
        """Report that the process is up and the database accepts a query."""
        found = checks.read()

        return HealthDto(status=found.status)


health_controller = HealthController()
