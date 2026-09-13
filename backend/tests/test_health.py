"""Health endpoint contract test."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_the_public_readiness_contract() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "PricePulse MY API",
        "version": "0.1.0",
    }
