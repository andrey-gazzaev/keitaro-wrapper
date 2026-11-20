"""Stored stream row."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class StreamRecord(Base):
    """One stream imported for the editor. `deleted` means Keitaro no longer returns it."""

    __tablename__ = "streams"
    """Table where editor streams are stored."""

    __table_args__ = (Index("ix_streams_campaign_keitaro_id", "campaign_keitaro_id"),)

    keitaro_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    """Keitaro stream id. This is the primary key."""

    campaign_keitaro_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("campaigns.keitaro_id", name="fk_streams_campaign_keitaro_id", ondelete="RESTRICT"),
        nullable=False,
    )
    """Campaign this stream belongs to."""

    name: Mapped[str] = mapped_column(Text, nullable=False)
    """Stream name."""

    position: Mapped[int] = mapped_column(Integer, nullable=False)
    """Order of this stream on the campaign."""

    flow_schema: Mapped[str] = mapped_column(Text, nullable=False)
    """Keitaro flow schema, such as landings or redirect."""

    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    """True when Keitaro no longer returns this stream."""

    published_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    """Last fetched or pushed deleted flag."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this row was stored."""
