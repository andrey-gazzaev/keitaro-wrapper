"""Stored offer access."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.campaigns.repositories.offer_record import OfferRecord
from app.db import SessionDep


class OfferRepository:
    """Reads and writes stored offers."""

    def __init__(self, session: Session) -> None:
        """An offer repository for one request session."""
        self._session = session

    def get(self, offer_id: int) -> OfferRecord | None:
        """The offer for this id. None when it is not stored."""
        return _detach(self._session, self._session.get(OfferRecord, offer_id))

    def insert(self, *, keitaro_id: int, name: str, created_at: datetime) -> None:
        """Store one offer."""
        self._session.add(OfferRecord(keitaro_id=keitaro_id, name=name, created_at=created_at))
        self._session.flush()


def get_offer_repository(session: SessionDep) -> OfferRepository:
    """Offer repository for one request."""
    return OfferRepository(session)


OfferRepositoryDep = Annotated[OfferRepository, Depends(get_offer_repository)]


def _detach(session: Session, row: OfferRecord | None) -> OfferRecord | None:
    if row is not None:
        session.expunge(row)

    return row
