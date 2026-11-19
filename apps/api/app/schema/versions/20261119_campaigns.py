"""Baseline for stored campaigns."""

from alembic import op
from sqlalchemy import Column, DateTime, Integer, Text, inspect

revision = "20261119_campaigns"
down_revision = None


def upgrade() -> None:
    """Create campaigns when that table is not already stored."""
    if inspect(op.get_bind()).has_table("campaigns"):
        return

    op.create_table(
        "campaigns",
        Column("keitaro_id", Integer, primary_key=True, autoincrement=False),
        Column("name", Text, nullable=False),
        Column("alias", Text, nullable=False, unique=True),
        Column("country", Text, nullable=False),
        Column("offer_id", Integer, nullable=False),
        Column("domain_id", Integer, nullable=False),
        Column("group_id", Integer, nullable=False),
        Column("traffic_source_id", Integer, nullable=False),
        Column("country_stream_id", Integer, nullable=False, unique=True),
        Column("offer_stream_id", Integer, nullable=False, unique=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("deleted_at", DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Leave stored campaigns in place."""
    raise RuntimeError("Downgrade does not drop campaigns.")
