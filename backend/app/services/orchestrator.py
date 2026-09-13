"""Fixed, auditable PricePulse workflow orchestration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from uuid import uuid4

import pandas as pd

from app.agents import critic, data_quality, market_scope, price_signal, reporter
from app.agents.contracts import AgentDecision, CriticDecision
from app.schemas.contracts import AnalysisRequest
from app.services.data import PriceCatcherLoader, month_sequence
from app.services.forecasting import AnomalyResult, ForecastResult, detect_residual_anomalies, run_forecast_experiment
from app.services.series import AnalysisScope, CoverageThresholds, DailySeriesResult, build_daily_series
from app.services.validation import DataQualityResult, validate_raw_data


@dataclass(frozen=True)
class AnalysisRun:
    run_id: str
    created_at: str
    request: AnalysisRequest
    data_quality: DataQualityResult
    series: DailySeriesResult | None
    forecast: ForecastResult | None
    anomalies: AnomalyResult | None
    agents: tuple[AgentDecision, ...]
    critic: CriticDecision
    report: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "created_at": self.created_at,
            "scope": self.request.model_dump(mode="json"),
            "data_quality": self.data_quality.to_dict(),
            "series": _series_payload(self.series),
            "forecast": _forecast_payload(self.forecast),
            "anomalies": _records(self.anomalies.anomalies) if self.anomalies else [],
            "anomaly_method": self.anomalies.method if self.anomalies else None,
            "anomaly_threshold": self.anomalies.threshold if self.anomalies else None,
            "agents": [decision.to_dict() for decision in self.agents],
            "critic": self.critic.to_dict(),
            "report": self.report,
        }


class PricePulseOrchestrator:
    """Runs one fixed analysis path; no specialist can bypass a gate."""

    def __init__(self, loader: PriceCatcherLoader | None = None):
        self.loader = loader or PriceCatcherLoader()

    def run(self, request: AnalysisRequest) -> AnalysisRun:
        run_id = str(uuid4())
        created_at = datetime.now(UTC).isoformat()
        months = month_sequence(
            request.start_date.strftime("%Y-%m"), request.end_date.strftime("%Y-%m")
        )
        raw = self.loader.load(months)
        quality_result = validate_raw_data(raw)
        quality_decision = data_quality.assess(run_id, quality_result)

        if quality_decision.status not in {"PASS", "PASS_WITH_LIMITATIONS"}:
            critic_decision = critic.assess(run_id, quality_decision, None, None, None)
            decisions: tuple[AgentDecision, ...] = (quality_decision, critic_decision)
            return AnalysisRun(
                run_id,
                created_at,
                request,
                quality_result,
                None,
                None,
                None,
                decisions,
                critic_decision,
                reporter.create_report(critic_decision, None, decisions),
            )

        series_result = build_daily_series(
            raw,
            AnalysisScope(
                item_code=request.item_code,
                geography_type=request.geography_type,
                geography_value=request.geography_value,
                start_date=request.start_date.isoformat(),
                end_date=request.end_date.isoformat(),
            ),
            CoverageThresholds(request.min_transactions, request.min_premises),
        )
        forecast_result = run_forecast_experiment(series_result.points)
        anomaly_result = detect_residual_anomalies(
            forecast_result, request.anomaly_threshold
        )
        signal_decision = price_signal.assess(run_id, forecast_result, anomaly_result)
        scope_decision = market_scope.assess(run_id, anomaly_result.anomalies)
        critic_decision = critic.assess(
            run_id,
            quality_decision,
            series_result,
            forecast_result,
            anomaly_result,
        )
        decisions = (quality_decision, signal_decision, scope_decision, critic_decision)
        return AnalysisRun(
            run_id,
            created_at,
            request,
            quality_result,
            series_result,
            forecast_result,
            anomaly_result,
            decisions,
            critic_decision,
            reporter.create_report(critic_decision, anomaly_result, decisions),
        )


def _records(frame: pd.DataFrame) -> list[dict[str, object]]:
    if frame.empty:
        return []
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _series_payload(series: DailySeriesResult | None) -> dict[str, object] | None:
    if series is None:
        return None
    return {
        "item_code": series.item_code,
        "item_name": series.item_name,
        "unit": series.unit,
        "geography_type": series.geography_type,
        "geography_value": series.geography_value,
        "status": series.status,
        "exclusions": series.exclusions,
        "limitations": list(series.limitations),
        "points": _records(series.points),
    }


def _forecast_payload(forecast: ForecastResult | None) -> dict[str, object] | None:
    if forecast is None:
        return None
    return {
        "status": forecast.status,
        "chosen_model": forecast.chosen_model,
        "selection_reason": forecast.selection_reason,
        "feature_names": list(forecast.feature_names),
        "split_dates": forecast.split_dates,
        "baseline_validation": asdict(forecast.baseline_validation) if forecast.baseline_validation else None,
        "baseline_test": asdict(forecast.baseline_test) if forecast.baseline_test else None,
        "ridge_validation": asdict(forecast.ridge_validation) if forecast.ridge_validation else None,
        "ridge_test": asdict(forecast.ridge_test) if forecast.ridge_test else None,
        "limitations": list(forecast.limitations),
        "predictions": _records(forecast.predictions),
    }
