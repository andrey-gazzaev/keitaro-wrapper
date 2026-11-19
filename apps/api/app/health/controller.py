"""Health route."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.health.dto import HealthOut
from app.health.service import HealthCheck, get_health_check

router = APIRouter()

HealthCheckDep = Annotated[HealthCheck, Depends(get_health_check)]


@router.get("/health")
def read_health(checks: HealthCheckDep) -> HealthOut:
    """Report that the process is up and the database accepts a query."""
    found = checks.read()

    return HealthOut(status=found.status)
