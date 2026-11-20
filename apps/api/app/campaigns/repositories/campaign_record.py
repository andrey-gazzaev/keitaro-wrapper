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

    country: Mapped[str] = mapped_column(Text, nullable=False)
    """Two-letter country code."""

    offer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro offer on the offer flow."""

    domain_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro domain used at creation."""

    group_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro campaign group used at creation."""

    traffic_source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    """Keitaro traffic source used at creation."""

    country_stream_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    """Keitaro id of the country flow. Unique across stored campaigns."""

    offer_stream_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    """Keitaro id of the offer flow. Unique across stored campaigns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this row was stored."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    """When this row became a tombstone. None while the campaign is live."""
