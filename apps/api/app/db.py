"""SQLAlchemy engine and request sessions."""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Metadata for tables in the Keitaro wrapper."""


def database_url() -> str:
    """Postgres URL. The local API uses the published Docker port; Compose sets the in-network host."""
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://keitaro:keitaro@127.0.0.1:54330/keitaro",
    )


def _connect_args(url: str) -> dict[str, bool]:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


_url = database_url()
engine = create_engine(_url, connect_args=_connect_args(_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Open a session for one request and close it afterwards."""
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
