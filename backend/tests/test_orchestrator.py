"""End-to-end fixed-workflow test using only deterministic fixture data."""

import json
from datetime import date

import pandas as pd

from app.schemas.contracts import AnalysisRequest
from app.services.data import RawPriceCatcherData, SourceArtifact
from app.services.orchestrator import PricePulseOrchestrator


class FixtureLoader:
    def load(self, months: list[str]) -> RawPriceCatcherData:
        dates = pd.date_range("2026-01-01", periods=36, freq="D")
        rows: list[dict[str, object]] = []
        for index, current_date in enumerate(dates):
            price = 10.0 + (index % 4) * 0.1
            rows.extend(
                [
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "premise_code": 10,
                        "item_code": 1,
                        "price": price,
                    },
                    {
                        "date": current_date.strftime("%Y-%m-%d"),
                        "premise_code": 11,
                        "item_code": 1,
                        "price": price + 0.2,
                    },
                ]
            )
        return RawPriceCatcherData(
            transactions=pd.DataFrame(rows),
            items=pd.DataFrame(
                [{"item_code": 1, "item": "Fixture rice", "unit": "1kg", "item_group": "Food", "item_category": "Rice"}]
            ),
            premises=pd.DataFrame(
                [
                    {"premise_code": 10, "premise": "A", "address": "A", "premise_type": "Market", "state": "Selangor", "district": "Petaling"},
                    {"premise_code": 11, "premise": "B", "address": "B", "premise_type": "Market", "state": "Selangor", "district": "Petaling"},
                ]
            ),
            sources=(
                SourceArtifact("transactions", "https://official.example/transactions", "2026-09-13T00:00:00Z", "LIVE", len(rows)),
                SourceArtifact("items", "https://official.example/items", "2026-09-13T00:00:00Z", "LIVE", 1),
                SourceArtifact("premises", "https://official.example/premises", "2026-09-13T00:00:00Z", "LIVE", 2),
            ),
        )


def test_orchestrator_returns_json_safe_evidence_without_an_unapproved_claim() -> None:
    request = AnalysisRequest(
        item_code=1,
        geography_type="national",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 5),
        min_transactions=2,
        min_premises=2,
    )

    payload = PricePulseOrchestrator(loader=FixtureLoader()).run(request).to_payload()

    assert payload["data_quality"]["status"] == "PASS"
    assert payload["series"]["unit"] == "1kg"
    assert payload["forecast"]["status"] == "PASS"
    assert payload["critic"]["status"] in {"PASS", "PASS_WITH_LIMITATIONS"}
    assert payload["report"]["recommendation"] is None
    json.dumps(payload)
