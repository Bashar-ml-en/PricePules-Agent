"""Unit-safe daily aggregation and historical-only baselines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from app.services.data import RawPriceCatcherData


GeographyType = Literal["national", "state", "district"]


@dataclass(frozen=True)
class AnalysisScope:
    """The only approved grain for a PricePulse price series."""

    item_code: int
    geography_type: GeographyType
    geography_value: str | None = None
    start_date: str | None = None
    end_date: str | None = None


@dataclass(frozen=True)
class CoverageThresholds:
    """Minimum evidence required before a date can be modelled or scored."""

    min_transactions: int = 3
    min_premises: int = 2

    def __post_init__(self) -> None:
        if self.min_transactions < 1 or self.min_premises < 1:
            raise ValueError("Coverage thresholds must be positive integers.")


@dataclass(frozen=True)
class DailySeriesResult:
    """Qualified and unqualified daily summaries plus explicit exclusions."""

    item_code: int
    item_name: str
    unit: str
    geography_type: GeographyType
    geography_value: str | None
    points: pd.DataFrame
    exclusions: dict[str, int]
    status: Literal["PASS", "INCONCLUSIVE"]
    limitations: tuple[str, ...]


def build_daily_series(
    raw_data: RawPriceCatcherData,
    scope: AnalysisScope,
    thresholds: CoverageThresholds = CoverageThresholds(),
) -> DailySeriesResult:
    """Aggregate only one verified item/unit after an explicit geography filter.

    Invalid or unmatched source rows are not repaired. They are excluded from the
    analytical series only with an explicit count in `exclusions`.
    """

    item_rows = raw_data.items.loc[raw_data.items["item_code"] == scope.item_code]
    if len(item_rows) != 1:
        raise ValueError("Selected item_code must map to exactly one official item row.")

    item = item_rows.iloc[0]
    unit = str(item["unit"]).strip() if pd.notna(item["unit"]) else ""
    if not unit:
        raise ValueError("Selected item_code has no verified unit.")

    transactions = raw_data.transactions.copy()
    total_rows = len(transactions)
    transactions["parsed_date"] = pd.to_datetime(transactions["date"], errors="coerce")
    transactions["parsed_price"] = pd.to_numeric(transactions["price"], errors="coerce")

    matched_item = transactions.loc[transactions["item_code"] == scope.item_code].copy()
    invalid_date_count = int(matched_item["parsed_date"].isna().sum())
    invalid_price_count = int(
        (matched_item["parsed_price"].isna() | (matched_item["parsed_price"] < 0)).sum()
    )

    premises = raw_data.premises[["premise_code", "state", "district"]].copy()
    merged = matched_item.merge(premises, on="premise_code", how="left", indicator=True)
    unmatched_premise_count = int((merged["_merge"] == "left_only").sum())
    merged = merged.loc[
        merged["parsed_date"].notna()
        & merged["parsed_price"].notna()
        & (merged["parsed_price"] >= 0)
        & merged["_merge"].eq("both")
    ].copy()

    if scope.geography_type == "national":
        geography_value = None
    else:
        if not scope.geography_value or not scope.geography_value.strip():
            raise ValueError(f"{scope.geography_type} analysis requires a geography_value.")
        geography_value = scope.geography_value.strip()
        column = scope.geography_type
        merged = merged.loc[
            merged[column].astype("string").str.casefold()
            == geography_value.casefold()
        ].copy()

    if scope.start_date:
        start_date = pd.Timestamp(scope.start_date)
        merged = merged.loc[merged["parsed_date"] >= start_date].copy()
    if scope.end_date:
        end_date = pd.Timestamp(scope.end_date)
        merged = merged.loc[merged["parsed_date"] <= end_date].copy()

    exclusions = {
        "non_selected_item_rows": total_rows - len(matched_item),
        "invalid_date_rows": invalid_date_count,
        "invalid_or_negative_price_rows": invalid_price_count,
        "unmatched_premise_rows": unmatched_premise_count,
    }

    if merged.empty:
        return DailySeriesResult(
            item_code=scope.item_code,
            item_name=str(item["item"]),
            unit=unit,
            geography_type=scope.geography_type,
            geography_value=geography_value,
            points=_empty_points(),
            exclusions=exclusions,
            status="INCONCLUSIVE",
            limitations=("No valid selected-item observations matched the requested scope.",),
        )

    daily = (
        merged.groupby("parsed_date", as_index=False)
        .agg(
            observed_price=("parsed_price", "median"),
            q1_price=("parsed_price", lambda series: series.quantile(0.25)),
            q3_price=("parsed_price", lambda series: series.quantile(0.75)),
            transaction_count=("parsed_price", "size"),
            premise_count=("premise_code", "nunique"),
        )
        .rename(columns={"parsed_date": "date"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    daily["coverage_qualified"] = (
        (daily["transaction_count"] >= thresholds.min_transactions)
        & (daily["premise_count"] >= thresholds.min_premises)
    )
    daily["baseline_expected"] = pd.NA
    daily["baseline_method"] = pd.NA
    daily = _add_historical_baseline(daily)

    qualified_count = int(daily["coverage_qualified"].sum())
    limitations: list[str] = []
    if qualified_count != len(daily):
        limitations.append(
            "Some dates fail the configured transaction/premise coverage threshold."
        )
    if qualified_count < 4:
        limitations.append(
            "Fewer than four coverage-qualified dates are available for a historical baseline."
        )

    return DailySeriesResult(
        item_code=scope.item_code,
        item_name=str(item["item"]),
        unit=unit,
        geography_type=scope.geography_type,
        geography_value=geography_value,
        points=daily,
        exclusions=exclusions,
        status="PASS" if qualified_count else "INCONCLUSIVE",
        limitations=tuple(limitations),
    )


def _add_historical_baseline(points: pd.DataFrame) -> pd.DataFrame:
    """Predict each date from qualified observations strictly before that date."""

    output = points.copy()
    history: list[dict[str, object]] = []
    for index, row in output.iterrows():
        if not bool(row["coverage_qualified"]):
            continue

        prior = pd.DataFrame(history)
        expected: float | None = None
        method: str | None = None
        if not prior.empty:
            weekday_prior = prior.loc[prior["weekday"] == row["date"].weekday(), "price"]
            if len(weekday_prior) >= 2:
                expected = float(weekday_prior.tail(8).median())
                method = "same_day_of_week_median"
            elif len(prior) >= 3:
                expected = float(prior["price"].tail(7).median())
                method = "trailing_median"

        if expected is not None:
            output.at[index, "baseline_expected"] = expected
            output.at[index, "baseline_method"] = method

        history.append({"weekday": row["date"].weekday(), "price": row["observed_price"]})
    return output


def _empty_points() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "date",
            "observed_price",
            "q1_price",
            "q3_price",
            "transaction_count",
            "premise_count",
            "coverage_qualified",
            "baseline_expected",
            "baseline_method",
        ]
    )
