"""Editor streams and offer bindings."""

from alembic import op
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    inspect,
)

revision = "20261120_editor"
down_revision = "20261119_campaigns"


def upgrade() -> None:
    """Create editor tables when they are not already stored."""
    inspector = inspect(op.get_bind())

    if inspector.has_table("offers") and inspector.has_table("streams") and inspector.has_table("stream_offers"):
        return

    op.create_table(
        "offers",
        Column("keitaro_id", Integer, primary_key=True, autoincrement=False),
        Column("name", Text, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "streams",
        Column("keitaro_id", Integer, primary_key=True, autoincrement=False),
        Column(
            "campaign_keitaro_id",
            Integer,
            ForeignKey("campaigns.keitaro_id", name="fk_streams_campaign_keitaro_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        Column("name", Text, nullable=False),
        Column("position", Integer, nullable=False),
        Column("flow_schema", Text, nullable=False),
        Column("deleted", Boolean, nullable=False),
        Column("published_deleted", Boolean, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_streams_campaign_keitaro_id", "streams", ["campaign_keitaro_id"])
    op.create_table(
        "stream_offers",
        Column("id", Integer, Identity(), primary_key=True),
        Column(
            "stream_keitaro_id",
            Integer,
            ForeignKey("streams.keitaro_id", name="fk_stream_offers_stream_keitaro_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        Column(
            "offer_keitaro_id",
            Integer,
            ForeignKey("offers.keitaro_id", name="fk_stream_offers_offer_keitaro_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        Column("share", Numeric(5, 2), nullable=False),
        Column("pinned", Boolean, nullable=False),
        Column("deleted", Boolean, nullable=False),
        Column("published_share", Numeric(5, 2), nullable=True),
        Column("published_pinned", Boolean, nullable=True),
        Column("published_deleted", Boolean, nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
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
        UniqueConstraint("stream_keitaro_id", "offer_keitaro_id", name="uq_stream_offers_stream_offer"),
    )
    op.create_index("ix_stream_offers_stream_keitaro_id", "stream_offers", ["stream_keitaro_id"])
    op.create_index("ix_stream_offers_offer_keitaro_id", "stream_offers", ["offer_keitaro_id"])


def downgrade() -> None:
    """Leave stored editor rows in place."""
    raise RuntimeError("Downgrade does not drop editor tables.")
