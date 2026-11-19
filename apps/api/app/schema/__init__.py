"""Database schema revisions."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine


def apply_schema(engine: Engine) -> None:
    """Move this database to the latest revision. Rows already stored stay."""
    location = str(Path(__file__).resolve().parent)
    config = Config()
    config.set_main_option("script_location", location)
    config.attributes["engine"] = engine

    command.upgrade(config, "head")
