"""HTTP application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.health.controller import router as health_router

app = FastAPI(title="Keitaro wrapper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
