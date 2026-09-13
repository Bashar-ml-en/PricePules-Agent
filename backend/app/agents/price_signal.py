"""Price Signal Agent: reports deterministic model and residual evidence only."""

from app.agents.contracts import AgentDecision, EvidenceFinding
from app.services.forecasting import AnomalyResult, ForecastResult


def assess(run_id: str, forecast: ForecastResult, anomalies: AnomalyResult) -> AgentDecision:
    if forecast.status != "PASS" or forecast.chosen_model is None:
        return AgentDecision(
            agent="price_signal",
            run_id=run_id,
            status="INCONCLUSIVE",
            limitations=forecast.limitations,
            next_action="stop",
        )

    baseline = forecast.baseline_test
    findings = [
        EvidenceFinding(
            claim_class="model_result",
            statement=(
                f"The selected {forecast.chosen_model} model was chosen using chronological validation."
            ),
            evidence_refs=("forecast.selection_reason", "forecast.split_dates"),
        )
    ]
    if baseline:
        findings.append(
            EvidenceFinding(
                claim_class="model_result",
                statement=(
                    f"Held-out baseline MAE is {baseline.mae:.4f} RM per verified unit "
                    f"across {baseline.sample_size} observations."
                ),
                evidence_refs=("forecast.baseline_test",),
            )
        )
    if not anomalies.anomalies.empty:
        findings.append(
            EvidenceFinding(
                claim_class="statistical_interpretation",
                statement=(
                    f"{len(anomalies.anomalies)} qualified held-out residual anomaly or anomalies "
                    f"met the configured robust threshold."
                ),
                evidence_refs=("anomaly.method", "anomaly.threshold", "anomaly.rows"),
            )
        )

    return AgentDecision(
        agent="price_signal",
        run_id=run_id,
        status="PASS_WITH_LIMITATIONS" if anomalies.limitations else "PASS",
        findings=tuple(findings),
        limitations=tuple((*forecast.limitations, *anomalies.limitations)),
        next_action="proceed_to_market_scope",
    )
