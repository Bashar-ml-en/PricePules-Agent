"""Reliability Critic: vetoes unsupported claims and invalid workflow states."""

from app.agents.contracts import AgentDecision, CriticDecision
from app.services.forecasting import AnomalyResult, ForecastResult
from app.services.series import DailySeriesResult


PROHIBITED_CLAIM_TERMS = (
    "inflation",
    "price gouging",
    "profiteering",
    "hoarding",
    "wrongdoing",
    "supply shortage",
    "cause",
    "recommended price",
)


def assess(
    run_id: str,
    data_quality: AgentDecision,
    series: DailySeriesResult | None,
    forecast: ForecastResult | None,
    anomalies: AnomalyResult | None,
    proposed_claims: tuple[str, ...] = (),
) -> CriticDecision:
    blockers: list[str] = []
    rejected_claims: list[str] = []
    if data_quality.status not in {"PASS", "PASS_WITH_LIMITATIONS"}:
        blockers.append("Data quality did not approve analysis eligibility.")
    if series is None or series.status != "PASS":
        blockers.append("The requested item/location series was not coverage-eligible.")
    if forecast is None or forecast.status != "PASS":
        blockers.append("Chronological forecasting evidence is unavailable.")
    for claim in proposed_claims:
        if any(term in claim.casefold() for term in PROHIBITED_CLAIM_TERMS):
            rejected_claims.append(claim)
    if rejected_claims:
        blockers.append("One or more proposed claims exceed the evidence boundary.")

    if blockers:
        return CriticDecision(
            agent="reliability_critic",
            run_id=run_id,
            status="REJECT" if rejected_claims or data_quality.status == "REJECT" else "INCONCLUSIVE",
            limitations=tuple(blockers),
            rejected_claims=tuple(rejected_claims),
            required_changes=("Resolve the listed evidence or claim-boundary failure before reporting.",),
            next_action="stop",
        )

    has_anomaly = bool(anomalies and not anomalies.anomalies.empty)
    approved_claims = [
        "The analysis uses verified official source fields and deterministic computations.",
        "Model evaluation used chronological validation and an untouched final test partition.",
    ]
    if has_anomaly:
        approved_claims.append(
            "A coverage-qualified historical residual anomaly warrants human price-surveillance review."
        )
    limitations = [
        "The result does not determine inflation, a cause of price change, or wrongdoing."
    ]
    if data_quality.status == "PASS_WITH_LIMITATIONS":
        limitations.extend(data_quality.limitations)

    return CriticDecision(
        agent="reliability_critic",
        run_id=run_id,
        status="PASS_WITH_LIMITATIONS" if limitations else "PASS",
        limitations=tuple(limitations),
        approved_claims=tuple(approved_claims),
        next_action="proceed_to_reporter",
    )
