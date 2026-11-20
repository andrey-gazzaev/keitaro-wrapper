"""Database reachability check."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import SessionDep


class HealthRepository:
    """Checks that the database accepts a query."""

    def __init__(self, session: Session) -> None:
        """A health repository for one request session."""
        self._session = session

    def ping(self) -> None:
        """Nothing when the database accepts a query."""
        self._session.execute(text("SELECT 1"))


def get_health_repository(session: SessionDep) -> HealthRepository:
    """Health repository for one request."""
    return HealthRepository(session)


HealthRepositoryDep = Annotated[HealthRepository, Depends(get_health_repository)]
