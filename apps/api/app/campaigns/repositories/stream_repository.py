"""Stored stream access."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.repositories.stream_record import StreamRecord
from app.db import SessionDep


class StreamRepository:
    """Reads and writes stored streams."""

    def __init__(self, session: Session) -> None:
        """A stream repository for one request session."""
        self._session = session

    def get(self, stream_id: int) -> StreamRecord | None:
        """The stream for this id. None when it is not stored."""
        return _detach(self._session, self._session.get(StreamRecord, stream_id))

    def list_for_campaign(self, campaign_id: int) -> list[StreamRecord]:
        """Streams on this campaign, in position order. Empty when the campaign has none."""
        rows = self._session.scalars(
            select(StreamRecord)
            .where(StreamRecord.campaign_keitaro_id == campaign_id)
            .order_by(StreamRecord.position, StreamRecord.keitaro_id)
        )

        return _detach_all(self._session, list(rows))

    def insert(
        self,
        *,
        keitaro_id: int,
        campaign_keitaro_id: int,
        name: str,
        position: int,
        flow_schema: str,
        deleted: bool,
        published_deleted: bool,
        created_at: datetime,
    ) -> StreamRecord:
        """The stream just stored."""
        row = StreamRecord(
            keitaro_id=keitaro_id,
            campaign_keitaro_id=campaign_keitaro_id,
            name=name,
            position=position,
            flow_schema=flow_schema,
            deleted=deleted,
            published_deleted=published_deleted,
            created_at=created_at,
        )
        self._session.add(row)
        self._session.flush()
        self._session.expunge(row)

        return row

    def set_deleted_flags(self, stream_id: int, *, deleted: bool, published_deleted: bool) -> None:
        """Set this stream's working and published deleted flags."""
        row = self._session.get(StreamRecord, stream_id)
        row.deleted = deleted
        row.published_deleted = published_deleted
        self._session.flush()


def get_stream_repository(session: SessionDep) -> StreamRepository:
    """Stream repository for one request."""
    return StreamRepository(session)


StreamRepositoryDep = Annotated[StreamRepository, Depends(get_stream_repository)]


def _detach(session: Session, row: StreamRecord | None) -> StreamRecord | None:
    if row is not None:
        session.expunge(row)

    return row


def _detach_all(session: Session, rows: list[StreamRecord]) -> list[StreamRecord]:
    for row in rows:
        session.expunge(row)

    return rows
