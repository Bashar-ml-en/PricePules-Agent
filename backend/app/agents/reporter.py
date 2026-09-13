"""Deterministic evidence reporter that never creates an independent claim."""

from app.agents.contracts import AgentDecision, CriticDecision
from app.services.forecasting import AnomalyResult


def create_report(
    critic: CriticDecision,
    anomalies: AnomalyResult | None,
    agent_decisions: tuple[AgentDecision, ...],
) -> dict[str, object]:
    """Format only critic-approved fields for the API and dashboard."""

    can_recommend_review = bool(
        critic.status in {"PASS", "PASS_WITH_LIMITATIONS"}
        and anomalies
        and not anomalies.anomalies.empty
    )
    recommendation = (
        "Observed price is materially above or below the historical expectation and "
        "qualified coverage meets the configured threshold; conduct a human "
        "price-surveillance review."
        if can_recommend_review
        else None
    )
    return {
        "critic_status": critic.status,
        "approved_claims": list(critic.approved_claims),
        "rejected_claims": list(critic.rejected_claims),
        "limitations": list(critic.limitations),
        "recommendation": recommendation,
        "agent_statuses": {decision.agent: decision.status for decision in agent_decisions},
    }
