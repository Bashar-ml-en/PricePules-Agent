"""Chronological model evaluation and residual anomaly scoring."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


@dataclass(frozen=True)
class ModelMetrics:
    """Metrics calculated only from a named chronological partition."""

    mae: float
    rmse: float
    sample_size: int


@dataclass(frozen=True)
class ForecastResult:
    """Fully auditable baseline/Ridge comparison and held-out predictions."""

    status: Literal["PASS", "INCONCLUSIVE"]
    chosen_model: Literal["baseline", "ridge"] | None
    selection_reason: str
    feature_names: tuple[str, ...]
    split_dates: dict[str, tuple[str | None, str | None]]
    baseline_validation: ModelMetrics | None
    baseline_test: ModelMetrics | None
    ridge_validation: ModelMetrics | None
    ridge_test: ModelMetrics | None
    predictions: pd.DataFrame
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AnomalyResult:
    """Robust residual scores calculated from held-out chosen-model predictions."""

    method: str
    threshold: float
    median_residual: float | None
    mad: float | None
    anomalies: pd.DataFrame
    limitations: tuple[str, ...]


FEATURE_NAMES = ("lag_1", "lag_7", "rolling_median_7", "weekday_sin", "weekday_cos")


def run_forecast_experiment(points: pd.DataFrame) -> ForecastResult:
    """Compare a historical baseline with Ridge without tuning on the final test set."""

    features = _build_historical_features(points)
    eligible = features.loc[
        features["coverage_qualified"].astype(bool)
        & features["baseline_expected"].notna()
    ].copy()
    eligible = eligible.sort_values("date").reset_index(drop=True)

    if len(eligible) < 12:
        return _inconclusive_forecast(
            features,
            "At least 12 baseline-eligible chronological observations are required for evaluation.",
        )

    partitions = _chronological_partitions(len(eligible))
    train = eligible.iloc[partitions["train"]].copy()
    validation = eligible.iloc[partitions["validation"]].copy()
    test = eligible.iloc[partitions["test"]].copy()
    if min(len(train), len(validation), len(test)) < 3:
        return _inconclusive_forecast(
            features,
            "Chronological partitions require at least three observations each.",
        )

    baseline_validation = _metrics(validation["observed_price"], validation["baseline_expected"])
    baseline_test = _metrics(test["observed_price"], test["baseline_expected"])
    split_dates = {
        "train": _date_bounds(train),
        "validation": _date_bounds(validation),
        "test": _date_bounds(test),
    }

    ridge_eligible = eligible.dropna(subset=list(FEATURE_NAMES)).copy()
    ridge_validation = None
    ridge_test = None
    ridge_model_is_eligible = len(ridge_eligible) >= 30
    if ridge_model_is_eligible:
        ridge_train = ridge_eligible.loc[ridge_eligible.index.isin(train.index)]
        ridge_validation_frame = ridge_eligible.loc[
            ridge_eligible.index.isin(validation.index)
        ]
        ridge_test_frame = ridge_eligible.loc[ridge_eligible.index.isin(test.index)]
        ridge_model_is_eligible = min(
            len(ridge_train), len(ridge_validation_frame), len(ridge_test_frame)
        ) >= 3
    if ridge_model_is_eligible:
        validation_model = _fit_ridge(ridge_train)
        ridge_validation_predictions = validation_model.predict(
            ridge_validation_frame[list(FEATURE_NAMES)]
        )
        ridge_validation = _metrics(
            ridge_validation_frame["observed_price"], ridge_validation_predictions
        )
    else:
        ridge_train = pd.DataFrame()
        ridge_validation_frame = pd.DataFrame()
        ridge_test_frame = pd.DataFrame()

    choose_ridge = bool(
        ridge_validation
        and ridge_validation.mae < baseline_validation.mae
        and ridge_validation.rmse <= baseline_validation.rmse
    )
    if choose_ridge:
        # The final test remains untouched: selection happened solely on validation.
        final_training = pd.concat([ridge_train, ridge_validation_frame], ignore_index=True)
        final_model = _fit_ridge(final_training)
        ridge_test_predictions = final_model.predict(ridge_test_frame[list(FEATURE_NAMES)])
        ridge_test = _metrics(ridge_test_frame["observed_price"], ridge_test_predictions)
        test_predictions = test.copy()
        test_predictions["expected_price"] = test_predictions["baseline_expected"]
        test_predictions.loc[ridge_test_frame.index, "expected_price"] = ridge_test_predictions
        test_predictions["selected_model"] = "ridge"
        chosen_model: Literal["baseline", "ridge"] = "ridge"
        selection_reason = "Ridge improved validation MAE and did not worsen validation RMSE."
    else:
        test_predictions = test.copy()
        test_predictions["expected_price"] = test_predictions["baseline_expected"]
        test_predictions["selected_model"] = "baseline"
        chosen_model = "baseline"
        selection_reason = (
            "The historical baseline remained preferred because Ridge was ineligible or "
            "did not improve both validation criteria."
        )

    test_predictions["residual"] = (
        test_predictions["observed_price"] - test_predictions["expected_price"]
    )
    return ForecastResult(
        status="PASS",
        chosen_model=chosen_model,
        selection_reason=selection_reason,
        feature_names=FEATURE_NAMES,
        split_dates=split_dates,
        baseline_validation=baseline_validation,
        baseline_test=baseline_test,
        ridge_validation=ridge_validation,
        ridge_test=ridge_test,
        predictions=test_predictions.reset_index(drop=True),
        limitations=(
            "Forecasts describe historical held-out periods only; they do not establish a cause of price change.",
        ),
    )


def detect_residual_anomalies(
    forecast: ForecastResult, threshold: float = 3.5
) -> AnomalyResult:
    """Flag robust out-of-sample residuals; never score coverage-ineligible dates."""

    if threshold <= 0:
        raise ValueError("Anomaly threshold must be positive.")
    if forecast.status != "PASS" or forecast.predictions.empty:
        return AnomalyResult(
            method="modified_z_score_mad",
            threshold=threshold,
            median_residual=None,
            mad=None,
            anomalies=_empty_anomaly_frame(),
            limitations=("No valid held-out forecast predictions are available.",),
        )

    scored = forecast.predictions.loc[
        forecast.predictions["coverage_qualified"].astype(bool)
        & forecast.predictions["expected_price"].notna()
    ].copy()
    if len(scored) < 3:
        return AnomalyResult(
            method="modified_z_score_mad",
            threshold=threshold,
            median_residual=None,
            mad=None,
            anomalies=_empty_anomaly_frame(),
            limitations=("At least three qualified held-out residuals are required.",),
        )

    median_residual = float(scored["residual"].median())
    mad = float((scored["residual"] - median_residual).abs().median())
    if mad == 0:
        return AnomalyResult(
            method="modified_z_score_mad",
            threshold=threshold,
            median_residual=median_residual,
            mad=mad,
            anomalies=_empty_anomaly_frame(),
            limitations=("Residual MAD is zero, so a robust anomaly score is undefined.",),
        )

    scored["anomaly_score"] = 0.6745 * (scored["residual"] - median_residual) / mad
    scored["is_anomaly"] = scored["anomaly_score"].abs() >= threshold
    anomaly_columns = _ANOMALY_COLUMNS
    return AnomalyResult(
        method="modified_z_score_mad",
        threshold=threshold,
        median_residual=median_residual,
        mad=mad,
        anomalies=scored.loc[scored["is_anomaly"], anomaly_columns].reset_index(drop=True),
        limitations=(
            "An anomaly is a residual deviation from historical expectation, not evidence of a cause or wrongdoing.",
        ),
    )


def _build_historical_features(points: pd.DataFrame) -> pd.DataFrame:
    output = points.copy().sort_values("date").reset_index(drop=True)
    output["date"] = pd.to_datetime(output["date"])
    for feature in FEATURE_NAMES:
        output[feature] = np.nan

    history: list[float] = []
    for index, row in output.iterrows():
        if bool(row["coverage_qualified"]):
            if len(history) >= 1:
                output.at[index, "lag_1"] = history[-1]
            if len(history) >= 7:
                output.at[index, "lag_7"] = history[-7]
                output.at[index, "rolling_median_7"] = float(np.median(history[-7:]))
            output.at[index, "weekday_sin"] = np.sin(2 * np.pi * row["date"].weekday() / 7)
            output.at[index, "weekday_cos"] = np.cos(2 * np.pi * row["date"].weekday() / 7)
            history.append(float(row["observed_price"]))
    return output


def _chronological_partitions(length: int) -> dict[str, slice]:
    test_size = max(3, ceil(length * 0.2))
    validation_size = max(3, ceil(length * 0.2))
    train_end = length - test_size - validation_size
    validation_end = length - test_size
    return {
        "train": slice(0, train_end),
        "validation": slice(train_end, validation_end),
        "test": slice(validation_end, length),
    }


def _fit_ridge(frame: pd.DataFrame) -> Ridge:
    model = Ridge(alpha=1.0)
    model.fit(frame[list(FEATURE_NAMES)], frame["observed_price"])
    return model


def _metrics(actual: pd.Series, predicted: pd.Series | np.ndarray) -> ModelMetrics:
    actual_array = np.asarray(actual, dtype=float)
    predicted_array = np.asarray(predicted, dtype=float)
    return ModelMetrics(
        mae=float(mean_absolute_error(actual_array, predicted_array)),
        rmse=float(mean_squared_error(actual_array, predicted_array) ** 0.5),
        sample_size=len(actual_array),
    )


def _date_bounds(frame: pd.DataFrame) -> tuple[str | None, str | None]:
    if frame.empty:
        return (None, None)
    return (
        pd.Timestamp(frame["date"].min()).strftime("%Y-%m-%d"),
        pd.Timestamp(frame["date"].max()).strftime("%Y-%m-%d"),
    )


def _inconclusive_forecast(points: pd.DataFrame, limitation: str) -> ForecastResult:
    return ForecastResult(
        status="INCONCLUSIVE",
        chosen_model=None,
        selection_reason="No model was selected.",
        feature_names=FEATURE_NAMES,
        split_dates={"train": (None, None), "validation": (None, None), "test": (None, None)},
        baseline_validation=None,
        baseline_test=None,
        ridge_validation=None,
        ridge_test=None,
        predictions=points.iloc[0:0].copy(),
        limitations=(limitation,),
    )


_ANOMALY_COLUMNS = [
    "date",
    "observed_price",
    "expected_price",
    "residual",
    "anomaly_score",
    "transaction_count",
    "premise_count",
    "selected_model",
    "is_anomaly",
]


def _empty_anomaly_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=_ANOMALY_COLUMNS)
