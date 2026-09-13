"""Market Scope Agent: classifies coverage evidence without inferring causality."""

import pandas as pd

from app.agents.contracts import AgentDecision, EvidenceFinding


def assess(run_id: str, anomalies: pd.DataFrame) -> AgentDecision:
    if anomalies.empty:
        return AgentDecision(
            agent="market_scope",
            run_id=run_id,
            status="INCONCLUSIVE",
            limitations=("No coverage-qualified held-out anomaly is available to scope.",),
            next_action="proceed_to_critic",
        )

    minimum_premises = int(anomalies["premise_count"].min())
    minimum_transactions = int(anomalies["transaction_count"].min())
    return AgentDecision(
        agent="market_scope",
        run_id=run_id,
        status="PASS",
        findings=(
            EvidenceFinding(
                claim_class="data_finding",
                statement=(
                    "Every reported anomaly passed the configured coverage gate; the lowest "
                    f"support was {minimum_transactions} transactions across {minimum_premises} premises."
                ),
                evidence_refs=("anomaly.rows.transaction_count", "anomaly.rows.premise_count"),
            ),
        ),
        limitations=(
            "Coverage corroborates an observed local signal only; it does not establish a market-wide effect or cause.",
        ),
        next_action="proceed_to_critic",
    )
