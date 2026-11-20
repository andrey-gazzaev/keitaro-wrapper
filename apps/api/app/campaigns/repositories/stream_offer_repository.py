"""Stored offer binding access."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.db import SessionDep


class StreamOfferRepository:
    """Reads and writes stored offer bindings."""

    def __init__(self, session: Session) -> None:
        """A stream-offer repository for one request session."""
        self._session = session

    def get(self, binding_id: int) -> StreamOfferRecord | None:
        """The binding for this id. None when it is not stored."""
        return _detach(self._session, self._session.get(StreamOfferRecord, binding_id))

    def list_for_stream(self, stream_id: int) -> list[StreamOfferRecord]:
        """Bindings on this stream, oldest first. Empty when the stream has none."""
        rows = self._session.scalars(
            select(StreamOfferRecord)
            .where(StreamOfferRecord.stream_keitaro_id == stream_id)
            .order_by(StreamOfferRecord.created_at, StreamOfferRecord.id)
        )

        return _detach_all(self._session, list(rows))

    def find_pair(self, stream_id: int, offer_id: int) -> StreamOfferRecord | None:
        """The binding of this offer on this stream. None when that pair is not stored."""
        row = self._session.scalar(
            select(StreamOfferRecord).where(
                StreamOfferRecord.stream_keitaro_id == stream_id,
                StreamOfferRecord.offer_keitaro_id == offer_id,
            )
        )

        return _detach(self._session, row)

    def insert(
        self,
        *,
        stream_keitaro_id: int,
        offer_keitaro_id: int,
        share: Decimal,
        pinned: bool,
        deleted: bool,
        published_share: Decimal | None,
        published_pinned: bool | None,
        published_deleted: bool | None,
        created_at: datetime,
    ) -> None:
        """Store one offer binding."""
        self._session.add(
            StreamOfferRecord(
                stream_keitaro_id=stream_keitaro_id,
                offer_keitaro_id=offer_keitaro_id,
                share=share,
                pinned=pinned,
                deleted=deleted,
                published_share=published_share,
                published_pinned=published_pinned,
                published_deleted=published_deleted,
                created_at=created_at,
            )
        )
        self._session.flush()

    def delete(self, binding_id: int) -> None:
        """Remove this binding."""
        row = self._session.get(StreamOfferRecord, binding_id)
        self._session.delete(row)
        self._session.flush()

    def set_working(self, binding_id: int, *, share: Decimal, pinned: bool, deleted: bool) -> None:
        """Set this binding's working share, pin, and deleted flag."""
        row = self._session.get(StreamOfferRecord, binding_id)
        row.share = share
        row.pinned = pinned
        row.deleted = deleted
        self._session.flush()

    def set_published(self, binding_id: int, *, share: Decimal, pinned: bool, deleted: bool) -> None:
        """Set this binding's published share, pin, and deleted flag."""
        row = self._session.get(StreamOfferRecord, binding_id)
        row.published_share = share
        row.published_pinned = pinned
        row.published_deleted = deleted
        self._session.flush()

    def set_shares(self, shares: dict[int, Decimal]) -> None:
        """Set these working shares. Nothing changes when none are listed."""
        for binding_id, share in shares.items():
            row = self._session.get(StreamOfferRecord, binding_id)
            row.share = share

        self._session.flush()


def get_stream_offer_repository(session: SessionDep) -> StreamOfferRepository:
    """Stream-offer repository for one request."""
    return StreamOfferRepository(session)


StreamOfferRepositoryDep = Annotated[StreamOfferRepository, Depends(get_stream_offer_repository)]


def _detach(session: Session, row: StreamOfferRecord | None) -> StreamOfferRecord | None:
    if row is not None:
        session.expunge(row)

    return row


def _detach_all(session: Session, rows: list[StreamOfferRecord]) -> list[StreamOfferRecord]:
    for row in rows:
        session.expunge(row)

    return rows
