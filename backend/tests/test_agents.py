"""Deterministic specialist-agent contract tests."""

import pandas as pd

from app.agents.contracts import AgentDecision
from app.agents.critic import assess as assess_critic
from app.agents.market_scope import assess as assess_market_scope
from app.agents.reporter import create_report
from app.services.forecasting import AnomalyResult, ForecastResult
from app.services.series import DailySeriesResult


def _quality(status: str = "PASS") -> AgentDecision:
    return AgentDecision(agent="data_quality", run_id="run-1", status=status)  # type: ignore[arg-type]


def _series() -> DailySeriesResult:
    return DailySeriesResult(
        item_code=1,
        item_name="Test item",
        unit="1kg",
        geography_type="national",
        geography_value=None,
        points=pd.DataFrame(),
        exclusions={},
        status="PASS",
        limitations=(),
    )


def _forecast() -> ForecastResult:
    return ForecastResult(
        status="PASS",
        chosen_model="baseline",
        selection_reason="test",
        feature_names=(),
        split_dates={},
        baseline_validation=None,
        baseline_test=None,
        ridge_validation=None,
        ridge_test=None,
        predictions=pd.DataFrame(),
        limitations=(),
    )


def test_critic_rejects_a_prohibited_claim() -> None:
    critic = assess_critic(
        "run-1",
        _quality(),
        _series(),
        _forecast(),
        None,
        proposed_claims=("This proves price gouging.",),
    )

    assert critic.status == "REJECT"
    assert critic.rejected_claims == ("This proves price gouging.",)


def test_market_scope_never_treats_missing_anomalies_as_a_positive_signal() -> None:
    decision = assess_market_scope("run-1", pd.DataFrame())

    assert decision.status == "INCONCLUSIVE"


def test_reporter_recommends_review_only_for_critic_approved_anomaly() -> None:
    anomaly = AnomalyResult(
        method="modified_z_score_mad",
        threshold=3.5,
        median_residual=0.0,
        mad=1.0,
        anomalies=pd.DataFrame([{"date": "2026-01-01"}]),
        limitations=(),
    )
    critic = assess_critic("run-1", _quality(), _series(), _forecast(), anomaly)

    report = create_report(critic, anomaly, (_quality(),))

    assert report["recommendation"] is not None
