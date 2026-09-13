"""Chronological forecasting and residual anomaly tests."""

import pandas as pd

from app.services.forecasting import detect_residual_anomalies, run_forecast_experiment


def _points(values: list[float], qualified: bool = True) -> pd.DataFrame:
    dates = pd.date_range("2026-01-01", periods=len(values), freq="D")
    baseline = [None, None, None] + values[:-3]
    return pd.DataFrame(
        {
            "date": dates,
            "observed_price": values,
            "baseline_expected": baseline,
            "baseline_method": ["trailing_median"] * len(values),
            "coverage_qualified": [qualified] * len(values),
            "transaction_count": [5] * len(values),
            "premise_count": [3] * len(values),
        }
    )


def test_experiment_uses_chronological_non_overlapping_partitions() -> None:
    result = run_forecast_experiment(_points([float(value) for value in range(1, 25)]))

    assert result.status == "PASS"
    assert result.split_dates["train"][1] < result.split_dates["validation"][0]
    assert result.split_dates["validation"][1] < result.split_dates["test"][0]


def test_baseline_is_retained_when_ridge_does_not_clear_both_validation_criteria() -> None:
    result = run_forecast_experiment(_points([10.0] * 24))

    assert result.status == "PASS"
    assert result.chosen_model == "baseline"


def test_anomaly_scoring_uses_only_qualified_held_out_predictions() -> None:
    result = run_forecast_experiment(_points([10.0] * 20 + [30.0, 10.0, 10.0, 10.0]))
    anomalies = detect_residual_anomalies(result, threshold=2.0)

    assert anomalies.method == "modified_z_score_mad"
    assert all(anomalies.anomalies["transaction_count"] >= 5)


def test_insufficient_history_stops_before_model_selection() -> None:
    result = run_forecast_experiment(_points([1.0] * 10))

    assert result.status == "INCONCLUSIVE"
    assert result.chosen_model is None
