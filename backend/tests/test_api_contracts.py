from fastapi.testclient import TestClient

from app.main import app


def test_product_brief_states_human_approval_boundary() -> None:
    response = TestClient(app).get("/product/brief")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "foundation"
    assert "autonomous purchasing" in payload["non_goals"]
    assert len(payload["how"]) == 4
