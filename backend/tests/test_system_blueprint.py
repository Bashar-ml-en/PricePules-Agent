from fastapi.testclient import TestClient

from app.main import app


def test_system_blueprint_is_explicit_about_what_is_not_live() -> None:
    response = TestClient(app).get("/system/blueprint")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "ARCHITECTURE_BLUEPRINT"
    assert payload["live_workloads"] == "NONE"
    assert len(payload["agents"]) == 6
    assert "parallel agent orchestration" in payload["truthful_status"]["not_running_yet"]


def test_system_blueprint_keeps_human_approval_as_a_control() -> None:
    payload = TestClient(app).get("/system/blueprint").json()

    controls = {control["title"]: control for control in payload["controls"]}
    assert controls["Human decision boundary"]["state"] == "ENFORCED_BY_POLICY"
