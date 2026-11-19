"""HTTP application."""

from typing import Literal

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_session

app = FastAPI(title="Keitaro wrapper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


class HealthOut(BaseModel):
    """Reachability of the API and the database."""

    status: Literal["ok"]


@app.get("/health")
def read_health(session: Session = Depends(get_session)) -> HealthOut:
    """Report that the process is up and the database accepts a query."""
    session.execute(text("SELECT 1"))

    return HealthOut(status="ok")
