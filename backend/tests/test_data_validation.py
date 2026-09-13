"""Fixture-only data-quality tests; no live source is needed."""

import pandas as pd

from app.services.data import RawPriceCatcherData, SourceArtifact, month_sequence, monthly_url
from app.services.validation import validate_raw_data


def _source(name: str = "fixture") -> SourceArtifact:
    return SourceArtifact(
        name=name,
        url=f"https://example.test/{name}.csv",
        retrieved_at="2026-09-13T00:00:00+00:00",
        status="LIVE",
        row_count=1,
    )


def _raw_data(transactions: pd.DataFrame) -> RawPriceCatcherData:
    return RawPriceCatcherData(
        transactions=transactions,
        items=pd.DataFrame(
            [
                {
                    "item_code": 1,
                    "item": "TEST ITEM",
                    "unit": "1kg",
                    "item_group": "TEST",
                    "item_category": "TEST",
                }
            ]
        ),
        premises=pd.DataFrame(
            [
                {
                    "premise_code": 10,
                    "premise": "TEST PREMISE",
                    "address": "TEST ADDRESS",
                    "premise_type": "TEST",
                    "state": "Test State",
                    "district": "Test District",
                }
            ]
        ),
        sources=(_source("transactions"), _source("items"), _source("premises")),
    )


def test_validation_profiles_invalid_rows_without_silently_dropping_them() -> None:
    transactions = pd.DataFrame(
        [
            {"date": "2026-01-01", "premise_code": 10, "item_code": 1, "price": 3.0},
            {"date": "not-a-date", "premise_code": 99, "item_code": 77, "price": -1},
            {"date": "2026-01-01", "premise_code": 10, "item_code": 1, "price": 3.0},
        ]
    )

    result = validate_raw_data(_raw_data(transactions))

    assert result.row_count == 3
    assert result.invalid_date_rows == 1
    assert result.negative_price_rows == 1
    assert result.duplicate_rows == 1
    assert result.unmatched_item_rows == 1
    assert result.unmatched_premise_rows == 1
    assert result.status == "PASS_WITH_LIMITATIONS"


def test_validation_rejects_missing_required_schema() -> None:
    result = validate_raw_data(_raw_data(pd.DataFrame([{"date": "2026-01-01"}])))

    assert result.status == "REJECT"
    assert any(issue.code == "SCHEMA_MISMATCH" for issue in result.issues)


def test_validation_reports_missing_date_continuity() -> None:
    transactions = pd.DataFrame(
        [
            {"date": "2026-01-01", "premise_code": 10, "item_code": 1, "price": 3.0},
            {"date": "2026-01-03", "premise_code": 10, "item_code": 1, "price": 3.1},
        ]
    )

    result = validate_raw_data(_raw_data(transactions))

    assert result.missing_dates == 1
    assert any(issue.code == "DATE_GAP" for issue in result.issues)


def test_month_utilities_validate_and_build_official_paths() -> None:
    assert monthly_url("2026-09").endswith("pricecatcher_2026-09.csv")
    assert month_sequence("2025-12", "2026-02") == ["2025-12", "2026-01", "2026-02"]
