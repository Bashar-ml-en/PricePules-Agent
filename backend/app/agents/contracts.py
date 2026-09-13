"""Shared typed decision artifacts for RetailOps ML."""

from dataclasses import dataclass, field
from typing import Literal


DecisionStatus = Literal["PASS", "PASS_WITH_LIMITATIONS", "REJECT", "INCONCLUSIVE"]


@dataclass(frozen=True)
class EvidenceFinding:
    statement: str
    evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentDecision:
    agent: str
    run_id: str
    status: DecisionStatus
    findings: tuple[EvidenceFinding, ...] = field(default_factory=tuple)
    limitations: tuple[str, ...] = field(default_factory=tuple)
    next_action: str = "stop"
