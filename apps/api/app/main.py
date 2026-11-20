"""HTTP application."""

import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.campaigns.controllers.campaign_board_controller import campaign_board_controller
from app.campaigns.controllers.campaign_controller import campaign_controller
from app.campaigns.controllers.offer_controller import offer_controller
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


def _cors_origins() -> list[str]:
    configured = os.environ.get("CORS_ORIGINS", "")

    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(campaign_controller.router)
app.include_router(campaign_board_controller.router)
app.include_router(stream_editor_controller.router)
app.include_router(offer_controller.router)
app.include_router(health_controller.router)
