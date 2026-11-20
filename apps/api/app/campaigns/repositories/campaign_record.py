"""Stored campaign row."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CampaignRecord(Base):
    """One campaign. `deleted_at` set means the row is a tombstone and stays stored."""

    __tablename__ = "campaigns"
    """Table where these campaigns are stored."""

    keitaro_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    """Keitaro campaign id. This is the primary key."""

    name: Mapped[str] = mapped_column(Text, nullable=False)
    """Name shown to the operator."""

    alias: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    """Public alias. Unique across stored campaigns."""

    country: Mapped[str | None] = mapped_column(Text, nullable=True)
    """Two-letter country code. None when no country is stored."""

    offer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    """Keitaro offer on the offer flow. None when no offer is stored."""

    domain_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    """Keitaro domain used at creation. None when no domain is stored."""

    group_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    """Keitaro campaign group used at creation. None when no group is stored."""

    traffic_source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    """Keitaro traffic source used at creation. None when no traffic source is stored."""

    country_stream_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    """Keitaro id of the country flow. None when no country flow is stored. Unique across stored campaigns."""

    offer_stream_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    """Keitaro id of the offer flow. None when no offer flow is stored. Unique across stored campaigns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this row was stored."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """When this row became a tombstone. None while the campaign is live."""
