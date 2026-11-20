"""Health endpoint."""

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


def test_health_is_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
