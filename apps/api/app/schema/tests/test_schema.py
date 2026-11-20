"""Schema upgrade on a fresh database and on an existing campaigns table."""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from app.schema import apply_schema


def test_fresh_database_creates_campaigns_and_records_the_revision() -> None:
    engine = _sqlite()

    with engine.connect() as connection:
        assert not inspect(connection).has_table("campaigns")

    apply_schema(engine)

    assert _has_campaigns(engine)
    assert _revision(engine) == "20261121_campaign_import"

    apply_schema(engine)

    assert _has_campaigns(engine)
    assert _revision(engine) == "20261121_campaign_import"


def test_existing_campaigns_table_keeps_the_row() -> None:
    engine = _sqlite()
    apply_schema(engine)

    with engine.begin() as connection:
        connection.execute(text("DROP TABLE alembic_version"))
        connection.execute(
            text(
                """
                INSERT INTO campaigns (
                    keitaro_id,
                    name,
                    alias,
                    country,
                    offer_id,
                    domain_id,
                    group_id,
                    traffic_source_id,
                    country_stream_id,
                    offer_stream_id,
                    created_at,
                    deleted_at
                ) VALUES (
                    :keitaro_id,
                    :name,
                    :alias,
                    :country,
                    :offer_id,
                    :domain_id,
                    :group_id,
                    :traffic_source_id,
                    :country_stream_id,
                    :offer_stream_id,
                    :created_at,
                    :deleted_at
                )
                """
            ),
            {
                "keitaro_id": 1,
                "name": "Spring",
                "alias": "c0123456789ab",
                "country": "US",
                "offer_id": 7,
                "domain_id": 11,
                "group_id": 21,
                "traffic_source_id": 31,
                "country_stream_id": 200,
                "offer_stream_id": 201,
                "created_at": "2026-11-19T00:00:00+00:00",
                "deleted_at": None,
            },
        )

    apply_schema(engine)

    with engine.connect() as connection:
        stored = connection.execute(text("SELECT name FROM campaigns")).scalar_one()
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert stored == "Spring"
    assert revision == "20261121_campaign_import"


def _sqlite() -> Engine:
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _has_campaigns(engine: Engine) -> bool:
    with engine.connect() as connection:
        return bool(inspect(connection).has_table("campaigns"))


def _revision(engine: Engine) -> str:
    with engine.connect() as connection:
        found = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert isinstance(found, str)

    return found
