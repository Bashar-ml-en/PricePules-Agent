"""Schema and data-quality checks that preserve raw-source evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

import pandas as pd

from app.services.data import RawPriceCatcherData, SourceArtifact


QualityStatus = Literal["PASS", "PASS_WITH_LIMITATIONS", "REJECT", "INCONCLUSIVE"]

TRANSACTION_COLUMNS = {"date", "premise_code", "item_code", "price"}
ITEM_COLUMNS = {"item_code", "item", "unit", "item_group", "item_category"}
PREMISE_COLUMNS = {
    "premise_code",
    "premise",
    "address",
    "premise_type",
    "state",
    "district",
}


@dataclass(frozen=True)
class QualityIssue:
    """A precise quality observation without an implicit data repair."""

    code: str
    severity: Literal["INFO", "LIMITATION", "BLOCKER"]
    message: str
    count: int | None = None


@dataclass(frozen=True)
class DataQualityResult:
    """Structured validation result consumed by later stages and the critic."""

    status: QualityStatus
    row_count: int
    date_range: tuple[str | None, str | None]
    missing_dates: int | None
    invalid_date_rows: int
    invalid_price_rows: int
    negative_price_rows: int
    duplicate_rows: int
    unmatched_item_rows: int
    missing_unit_rows: int
    unmatched_premise_rows: int
    source_artifacts: tuple[SourceArtifact, ...]
    issues: tuple[QualityIssue, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Provide a JSON-serialisable artifact without exposing raw rows."""

        return {
            **asdict(self),
            "source_artifacts": [asdict(source) for source in self.source_artifacts],
            "issues": [asdict(issue) for issue in self.issues],
        }


def validate_raw_data(raw_data: RawPriceCatcherData) -> DataQualityResult:
    """Profile official raw frames without dropping or imputing any records."""

    issues: list[QualityIssue] = []
    transaction_schema_ok = _check_schema(
        raw_data.transactions, TRANSACTION_COLUMNS, "transaction", issues
    )
    item_schema_ok = _check_schema(raw_data.items, ITEM_COLUMNS, "item lookup", issues)
    premise_schema_ok = _check_schema(
        raw_data.premises, PREMISE_COLUMNS, "premise lookup", issues
    )

    unavailable_sources = [
        source for source in raw_data.sources if source.status == "UNAVAILABLE"
    ]
    for source in unavailable_sources:
        issues.append(
            QualityIssue(
                code="SOURCE_UNAVAILABLE",
                severity="BLOCKER",
                message=f"Official source '{source.name}' was unavailable.",
            )
        )

    if not all((transaction_schema_ok, item_schema_ok, premise_schema_ok)):
        return _empty_result(raw_data.sources, issues, status="REJECT")
    if raw_data.transactions.empty:
        issues.append(
            QualityIssue(
                code="NO_TRANSACTION_ROWS",
                severity="BLOCKER",
                message="No transaction rows were loaded for the requested months.",
            )
        )
        return _empty_result(raw_data.sources, issues, status="INCONCLUSIVE")

    transactions = raw_data.transactions.copy()
    parsed_dates = pd.to_datetime(transactions["date"], errors="coerce")
    parsed_prices = pd.to_numeric(transactions["price"], errors="coerce")
    invalid_date_rows = int(parsed_dates.isna().sum())
    invalid_price_rows = int(parsed_prices.isna().sum())
    negative_price_rows = int((parsed_prices < 0).sum())
    duplicate_rows = int(transactions.duplicated().sum())

    item_probe = transactions[["item_code"]].merge(
        raw_data.items[["item_code", "unit"]],
        on="item_code",
        how="left",
        indicator=True,
    )
    unmatched_item_rows = int((item_probe["_merge"] == "left_only").sum())
    missing_unit_rows = int(
        item_probe["unit"].isna().sum()
        + item_probe["unit"].astype("string").str.strip().eq("").sum()
    )

    premise_probe = transactions[["premise_code"]].merge(
        raw_data.premises[["premise_code"]],
        on="premise_code",
        how="left",
        indicator=True,
    )
    unmatched_premise_rows = int((premise_probe["_merge"] == "left_only").sum())

    valid_dates = parsed_dates.dropna().sort_values().drop_duplicates()
    min_date = valid_dates.min() if not valid_dates.empty else None
    max_date = valid_dates.max() if not valid_dates.empty else None
    missing_dates = _missing_date_count(valid_dates)

    _append_count_issues(
        issues,
        invalid_date_rows,
        "INVALID_DATE",
        "Transaction rows have unparseable dates.",
    )
    _append_count_issues(
        issues,
        invalid_price_rows,
        "INVALID_PRICE",
        "Transaction rows have non-numeric or missing prices.",
    )
    _append_count_issues(
        issues,
        negative_price_rows,
        "NEGATIVE_PRICE",
        "Transaction rows have negative prices.",
    )
    _append_count_issues(
        issues,
        duplicate_rows,
        "DUPLICATE_ROW",
        "Exact duplicate transaction rows were found.",
    )
    _append_count_issues(
        issues,
        unmatched_item_rows,
        "UNMATCHED_ITEM",
        "Transaction rows have no item lookup match.",
    )
    _append_count_issues(
        issues,
        missing_unit_rows,
        "MISSING_UNIT",
        "Transaction rows map to a missing or blank item unit.",
    )
    _append_count_issues(
        issues,
        unmatched_premise_rows,
        "UNMATCHED_PREMISE",
        "Transaction rows have no premise lookup match.",
    )
    _append_count_issues(
        issues,
        missing_dates or 0,
        "DATE_GAP",
        "Date gaps were found within the loaded range.",
        severity="LIMITATION",
    )

    has_blocker = any(issue.severity == "BLOCKER" for issue in issues)
    has_limitation = any(issue.severity == "LIMITATION" for issue in issues)
    status: QualityStatus = (
        "REJECT" if has_blocker else "PASS_WITH_LIMITATIONS" if has_limitation else "PASS"
    )

    return DataQualityResult(
        status=status,
        row_count=len(transactions),
        date_range=(
            min_date.strftime("%Y-%m-%d") if min_date is not None else None,
            max_date.strftime("%Y-%m-%d") if max_date is not None else None,
        ),
        missing_dates=missing_dates,
        invalid_date_rows=invalid_date_rows,
        invalid_price_rows=invalid_price_rows,
        negative_price_rows=negative_price_rows,
        duplicate_rows=duplicate_rows,
        unmatched_item_rows=unmatched_item_rows,
        missing_unit_rows=missing_unit_rows,
        unmatched_premise_rows=unmatched_premise_rows,
        source_artifacts=raw_data.sources,
        issues=tuple(issues),
    )


def _check_schema(
    frame: pd.DataFrame,
    required_columns: set[str],
    label: str,
    issues: list[QualityIssue],
) -> bool:
    missing_columns = sorted(required_columns.difference(frame.columns))
    if missing_columns:
        issues.append(
            QualityIssue(
                code="SCHEMA_MISMATCH",
                severity="BLOCKER",
                message=f"{label.capitalize()} is missing required columns: {missing_columns}.",
            )
        )
        return False
    return True


def _missing_date_count(dates: pd.Series) -> int | None:
    if dates.empty:
        return None
    expected = pd.date_range(dates.min(), dates.max(), freq="D")
    return len(expected.difference(pd.DatetimeIndex(dates)))


def _append_count_issues(
    issues: list[QualityIssue],
    count: int,
    code: str,
    message: str,
    severity: Literal["INFO", "LIMITATION", "BLOCKER"] = "LIMITATION",
) -> None:
    if count:
        issues.append(
            QualityIssue(code=code, severity=severity, message=message, count=count)
        )


def _empty_result(
    sources: tuple[SourceArtifact, ...],
    issues: list[QualityIssue],
    status: QualityStatus,
) -> DataQualityResult:
    return DataQualityResult(
        status=status,
        row_count=0,
        date_range=(None, None),
        missing_dates=None,
        invalid_date_rows=0,
        invalid_price_rows=0,
        negative_price_rows=0,
        duplicate_rows=0,
        unmatched_item_rows=0,
        missing_unit_rows=0,
        unmatched_premise_rows=0,
        source_artifacts=sources,
        issues=tuple(issues),
    )
