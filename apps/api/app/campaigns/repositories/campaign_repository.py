"""Stored campaign access."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.campaigns.repositories.campaign_record import CampaignRecord
from app.db import SessionDep


class CampaignRepository:
    """Reads and writes stored campaigns."""

    def __init__(self, session: Session) -> None:
        """A campaign repository for one request session."""
        self._session = session

    def get(self, campaign_id: int) -> CampaignRecord | None:
        """The campaign for this id. None when it is not stored."""
        return _detach(self._session, self._session.get(CampaignRecord, campaign_id))

    def list_newest(self) -> list[CampaignRecord]:
        """Every stored campaign, newest first. Empty when none are stored."""
        rows = self._session.scalars(select(CampaignRecord).order_by(CampaignRecord.created_at.desc()))

        return _detach_all(self._session, list(rows))

    def list_live(self) -> list[CampaignRecord]:
        """Stored campaigns that are still live. Empty when none are live."""
        rows = self._session.scalars(select(CampaignRecord).where(CampaignRecord.deleted_at.is_(None)))

        return _detach_all(self._session, list(rows))

    def insert(
        self,
        *,
        keitaro_id: int,
        name: str,
        alias: str,
        country: str,
        offer_id: int,
        domain_id: int,
        group_id: int,
        traffic_source_id: int,
        country_stream_id: int,
        offer_stream_id: int,
        created_at: datetime,
    ) -> None:
        """Store one live campaign."""
        self._session.add(
            CampaignRecord(
                keitaro_id=keitaro_id,
                name=name,
                alias=alias,
                country=country,
                offer_id=offer_id,
                domain_id=domain_id,
                group_id=group_id,
                traffic_source_id=traffic_source_id,
                country_stream_id=country_stream_id,
                offer_stream_id=offer_stream_id,
                created_at=created_at,
                deleted_at=None,
            )
        )
        self._session.flush()

    def mark_deleted(self, keitaro_ids: list[int], deleted_at: datetime) -> None:
        """Mark these campaigns as tombstones at this time. Nothing changes when none are listed."""
        for keitaro_id in keitaro_ids:
            row = self._session.get(CampaignRecord, keitaro_id)
            row.deleted_at = deleted_at

        self._session.flush()


def get_campaign_repository(session: SessionDep) -> CampaignRepository:
    """Campaign repository for one request."""
    return CampaignRepository(session)


CampaignRepositoryDep = Annotated[CampaignRepository, Depends(get_campaign_repository)]


def _detach(session: Session, row: CampaignRecord | None) -> CampaignRecord | None:
    if row is not None:
        session.expunge(row)

    return row


def _detach_all(session: Session, rows: list[CampaignRecord]) -> list[CampaignRecord]:
    for row in rows:
        session.expunge(row)

    return rows
