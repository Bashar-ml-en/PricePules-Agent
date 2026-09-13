"""Local SQLite audit storage for concise completed analysis artifacts."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from app.services.data import ROOT_DIR


DEFAULT_DB_PATH = ROOT_DIR / "data" / "pricepulse.db"


class RunStore:
    """Persist only concise run evidence; never raw source rows or hidden reasoning."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._initialise()

    def save(self, payload: dict[str, Any]) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analysis_runs
                (run_id, created_at, critic_status, scope_json, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    payload["run_id"],
                    payload["created_at"],
                    payload["report"]["critic_status"],
                    json.dumps(payload["scope"]),
                    json.dumps(payload),
                ),
            )
            connection.execute("DELETE FROM anomalies WHERE run_id = ?", (payload["run_id"],))
            connection.execute(
                "DELETE FROM agent_decisions WHERE run_id = ?", (payload["run_id"],)
            )
            for anomaly in payload.get("anomalies", []):
                connection.execute(
                    """
                    INSERT INTO anomalies
                    (run_id, date, observed_price, expected_price, residual, anomaly_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        payload["run_id"],
                        anomaly.get("date"),
                        anomaly.get("observed_price"),
                        anomaly.get("expected_price"),
                        anomaly.get("residual"),
                        anomaly.get("anomaly_score"),
                    ),
                )
            for decision in payload.get("agents", []):
                connection.execute(
                    """
                    INSERT INTO agent_decisions (run_id, agent, status, decision_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        payload["run_id"],
                        decision["agent"],
                        decision["status"],
                        json.dumps(decision),
                    ),
                )

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT payload_json FROM analysis_runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def _initialise(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    run_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    critic_status TEXT NOT NULL,
                    scope_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    date TEXT,
                    observed_price REAL,
                    expected_price REAL,
                    residual REAL,
                    anomaly_score REAL,
                    FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
                );
                CREATE TABLE IF NOT EXISTS agent_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    status TEXT NOT NULL,
                    decision_json TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id)
                );
                """
            )

    @contextmanager
    def _connection(self):
        """Commit successful work and always release the SQLite file handle."""

        connection = sqlite3.connect(self.db_path)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
