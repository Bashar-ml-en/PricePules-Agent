"""Data Quality Agent: translates deterministic validation into an eligibility decision."""

from app.agents.contracts import AgentDecision, EvidenceFinding
from app.services.validation import DataQualityResult


def assess(run_id: str, result: DataQualityResult) -> AgentDecision:
    source_refs = tuple(source.url for source in result.source_artifacts)
    findings = (
        EvidenceFinding(
            claim_class="data_finding",
            statement=(
                f"Validated {result.row_count} transaction rows from "
                f"{result.date_range[0] or 'UNKNOWN'} to {result.date_range[1] or 'UNKNOWN'}."
            ),
            evidence_refs=source_refs,
        ),
    )
    limitations = tuple(issue.message for issue in result.issues)
    return AgentDecision(
        agent="data_quality",
        run_id=run_id,
        status=result.status,
        findings=findings,
        limitations=limitations,
        next_action="proceed_to_series" if result.status.startswith("PASS") else "stop",
    )
