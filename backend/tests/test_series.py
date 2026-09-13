"""Unit-safe aggregation and historical-only baseline tests."""

import pandas as pd

from app.services.data import RawPriceCatcherData, SourceArtifact
from app.services.series import AnalysisScope, CoverageThresholds, build_daily_series


def _raw_data(rows: list[dict[str, object]]) -> RawPriceCatcherData:
    return RawPriceCatcherData(
        transactions=pd.DataFrame(rows),
        items=pd.DataFrame(
            [
                {"item_code": 1, "item": "Rice A", "unit": "1kg", "item_group": "Food", "item_category": "Rice"},
                {"item_code": 2, "item": "Rice B", "unit": "500g", "item_group": "Food", "item_category": "Rice"},
            ]
        ),
        premises=pd.DataFrame(
            [
                {"premise_code": 10, "premise": "A", "address": "A", "premise_type": "Market", "state": "Selangor", "district": "Petaling"},
                {"premise_code": 11, "premise": "B", "address": "B", "premise_type": "Market", "state": "Selangor", "district": "Petaling"},
                {"premise_code": 12, "premise": "C", "address": "C", "premise_type": "Market", "state": "Perak", "district": "Kinta"},
            ]
        ),
        sources=(
            SourceArtifact("fixture", "https://example.test", "2026-09-13T00:00:00Z", "LIVE"),
        ),
    )


def _daily_rows(prices: list[float]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for day, price in enumerate(prices, start=1):
        date = f"2026-01-{day:02d}"
        rows.extend(
            [
                {"date": date, "premise_code": 10, "item_code": 1, "price": price},
                {"date": date, "premise_code": 11, "item_code": 1, "price": price + 2},
            ]
        )
    return rows


def test_daily_series_uses_one_item_code_and_its_verified_unit() -> None:
    rows = _daily_rows([10])
    rows.append({"date": "2026-01-01", "premise_code": 10, "item_code": 2, "price": 100})

    result = build_daily_series(
        _raw_data(rows),
        AnalysisScope(item_code=1, geography_type="national"),
        CoverageThresholds(min_transactions=2, min_premises=2),
    )

    assert result.unit == "1kg"
    assert result.points.iloc[0]["observed_price"] == 11
    assert result.exclusions["non_selected_item_rows"] == 1


def test_coverage_gate_marks_low_evidence_dates_without_anomaly_eligibility() -> None:
    result = build_daily_series(
        _raw_data(
            [{"date": "2026-01-01", "premise_code": 10, "item_code": 1, "price": 10}]
        ),
        AnalysisScope(item_code=1, geography_type="national"),
        CoverageThresholds(min_transactions=2, min_premises=2),
    )

    assert not bool(result.points.iloc[0]["coverage_qualified"])
    assert result.status == "INCONCLUSIVE"


def test_future_prices_do_not_change_a_past_baseline_prediction() -> None:
    baseline_rows = _daily_rows([10, 11, 12, 13, 14])
    altered_future_rows = _daily_rows([10, 11, 12, 13, 999])
    scope = AnalysisScope(item_code=1, geography_type="national")
    thresholds = CoverageThresholds(min_transactions=2, min_premises=2)

    original = build_daily_series(_raw_data(baseline_rows), scope, thresholds)
    altered = build_daily_series(_raw_data(altered_future_rows), scope, thresholds)

    assert original.points.iloc[3]["baseline_expected"] == altered.points.iloc[3]["baseline_expected"]
