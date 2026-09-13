"""Local audit storage tests."""

from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.storage import RunStore


def test_store_persists_concise_run_artifacts() -> None:
    payload = {
        "run_id": "run-1",
        "created_at": "2026-09-13T00:00:00Z",
        "scope": {"item_code": 1},
        "anomalies": [],
        "agents": [{"agent": "data_quality", "status": "PASS"}],
        "report": {"critic_status": "PASS_WITH_LIMITATIONS"},
    }

    with TemporaryDirectory(prefix="pricepulse-store-") as directory:
        store = RunStore(Path(directory) / "pricepulse.db")
        store.save(payload)

        assert store.get("run-1") == payload
        assert store.get("missing") is None
