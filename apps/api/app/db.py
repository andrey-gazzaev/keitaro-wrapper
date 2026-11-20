"""SQLAlchemy engine and request sessions."""

import os
from collections.abc import Generator
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

load_dotenv(override=False)


class Base(DeclarativeBase):
    """Metadata for tables in the Keitaro wrapper."""


def database_url() -> str:
    """Postgres URL. The local API uses the published Docker port; the Docker env file sets the in-network host."""
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://keitaro:keitaro@127.0.0.1:54330/keitaro",
    )


def _engine(url: str):
    if url.startswith("sqlite"):
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    return create_engine(url)


engine = _engine(database_url())
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Open a session, commit when the request succeeds, and roll back when it fails."""
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session, scope="function")]
