"""HTTP application."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.campaigns.controllers.campaign_controller import campaign_controller
from app.campaigns.controllers.stream_editor_controller import stream_editor_controller
from app.db import engine
from app.health.controllers.health_controller import health_controller
from app.schema import apply_schema


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Move the database to the latest revision."""
    await asyncio.to_thread(apply_schema, engine)
    yield


app = FastAPI(title="Keitaro wrapper", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(campaign_controller.router)
app.include_router(stream_editor_controller.router)
app.include_router(health_controller.router)
