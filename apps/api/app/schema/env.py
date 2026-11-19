"""Online migrations for one database engine."""

from alembic import context

from app.campaigns.service import CampaignRecord
from app.db import Base


def run_migrations_online() -> None:
    """Move the connected database to the latest revision."""
    connectable = context.config.attributes["engine"]
    metadata = Base.metadata

    if CampaignRecord.__table__.name not in metadata.tables:
        raise RuntimeError("Stored tables are missing from metadata.")

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
