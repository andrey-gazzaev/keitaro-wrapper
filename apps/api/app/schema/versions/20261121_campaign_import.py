"""Imported campaigns may omit snapshot columns."""

from alembic import op
from sqlalchemy import Integer, Text

revision = "20261121_campaign_import"
down_revision = "20261120_editor"


def upgrade() -> None:
    """Make campaign snapshot columns nullable. Existing rows stay."""
    with op.batch_alter_table("campaigns") as batch:
        batch.alter_column("country", existing_type=Text(), nullable=True)
        batch.alter_column("offer_id", existing_type=Integer(), nullable=True)
        batch.alter_column("domain_id", existing_type=Integer(), nullable=True)
        batch.alter_column("group_id", existing_type=Integer(), nullable=True)
        batch.alter_column("traffic_source_id", existing_type=Integer(), nullable=True)
        batch.alter_column("country_stream_id", existing_type=Integer(), nullable=True)
        batch.alter_column("offer_stream_id", existing_type=Integer(), nullable=True)


def downgrade() -> None:
    """Leave stored campaigns in place."""
    raise RuntimeError("Downgrade does not restore campaign column nullability.")
