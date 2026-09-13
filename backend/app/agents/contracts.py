"""Typed, concise agent artifacts without hidden reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal


DecisionStatus = Literal["PASS", "PASS_WITH_LIMITATIONS", "REJECT", "INCONCLUSIVE"]


@dataclass(frozen=True)
class EvidenceFinding:
    claim_class: Literal[
        "source_fact", "data_finding", "model_result", "statistical_interpretation"
    ]
    statement: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class AgentDecision:
    agent: str
    run_id: str
    status: DecisionStatus
    findings: tuple[EvidenceFinding, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    rejected_claims: tuple[str, ...] = field(default_factory=tuple)
    next_action: str = "stop"

    def to_dict(self) -> dict[str, object]:
        return {
            **asdict(self),
            "findings": [asdict(finding) for finding in self.findings],
        }


@dataclass(frozen=True)
class CriticDecision(AgentDecision):
    approved_claims: tuple[str, ...] = field(default_factory=tuple)
    required_changes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            **super().to_dict(),
            "approved_claims": list(self.approved_claims),
            "required_changes": list(self.required_changes),
        }
