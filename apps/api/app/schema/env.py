"""Online migrations for one database engine."""

from alembic import context

from app.campaigns.repositories.campaign_record import CampaignRecord
from app.campaigns.repositories.offer_record import OfferRecord
from app.campaigns.repositories.stream_offer_record import StreamOfferRecord
from app.campaigns.repositories.stream_record import StreamRecord
from app.db import Base


def run_migrations_online() -> None:
    """Move the connected database to the latest revision."""
    connectable = context.config.attributes["engine"]
    metadata = Base.metadata

    records = (CampaignRecord, OfferRecord, StreamRecord, StreamOfferRecord)

    for record in records:
        if record.__tablename__ not in metadata.tables:
            raise RuntimeError("Stored tables are missing from metadata.")

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
