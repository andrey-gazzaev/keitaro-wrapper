"""Stored offer binding on a stream."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class StreamOfferRecord(Base):
    """One offer on a stream. Null published columns mean the add was never fetched or pushed."""

    __tablename__ = "stream_offers"
    """Table where stream offer bindings are stored."""

    __table_args__ = (
        UniqueConstraint("stream_keitaro_id", "offer_keitaro_id", name="uq_stream_offers_stream_offer"),
        CheckConstraint("share >= 0 AND share <= 100", name="ck_stream_offers_share"),
        CheckConstraint(
            "published_share IS NULL OR (published_share >= 0 AND published_share <= 100)",
            name="ck_stream_offers_published_share",
        ),
        CheckConstraint("deleted = false OR share = 0", name="ck_stream_offers_deleted_share"),
        CheckConstraint(
            "published_deleted IS NOT TRUE OR published_share = 0",
            name="ck_stream_offers_published_deleted_share",
        ),
        CheckConstraint(
            "(published_share IS NULL AND published_pinned IS NULL AND published_deleted IS NULL) "
            "OR (published_share IS NOT NULL AND published_pinned IS NOT NULL AND published_deleted IS NOT NULL)",
            name="ck_stream_offers_published_together",
        ),
        Index("ix_stream_offers_stream_keitaro_id", "stream_keitaro_id"),
        Index("ix_stream_offers_offer_keitaro_id", "offer_keitaro_id"),
    )

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    """Binding id."""

    stream_keitaro_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("streams.keitaro_id", name="fk_stream_offers_stream_keitaro_id", ondelete="RESTRICT"),
        nullable=False,
    )
    """Stream this binding belongs to."""

    offer_keitaro_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("offers.keitaro_id", name="fk_stream_offers_offer_keitaro_id", ondelete="RESTRICT"),
        nullable=False,
    )
    """Offer this binding uses."""

    share: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    """Working share from 0 to 100."""

    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False)
    """True when the working share stays fixed."""

    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    """True when the offer is removed and the row stays."""

    published_share: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    """Last fetched or pushed share. None when this add was never acknowledged."""

    published_pinned: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    """Last fetched or pushed pin. None when this add was never acknowledged."""

    published_deleted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    """Last fetched or pushed deleted flag. None when this add was never acknowledged."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    """When this binding was stored."""
