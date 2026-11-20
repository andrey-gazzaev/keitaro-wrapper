"""Stored offer row."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class OfferRecord(Base):
    """One offer catalog row. The editor keeps it when a binding is cancelled."""

    __tablename__ = "offers"
    """Table where offer names are stored."""

    keitaro_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    """Keitaro offer id. This is the primary key."""

    name: Mapped[str] = mapped_column(Text, nullable=False)
    """Offer name."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this row was stored."""
