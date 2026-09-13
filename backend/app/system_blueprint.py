"""Inspectable architecture metadata for the RetailOps control-room UI.

This module intentionally describes the target operating model; it does not
pretend that a connector, training job, model, or agent workload is live.
Keeping this boundary in the API lets the UI distinguish implemented controls
from components that must be built and validated in later stages.
"""

from typing import Any


def build_system_blueprint() -> dict[str, Any]:
    """Return the versioned system blueprint used by the architecture explorer."""

    return {
        "blueprint_version": "2026.09.foundation",
        "mode": "ARCHITECTURE_BLUEPRINT",
        "live_workloads": "NONE",
        "truthful_status": {
            "implemented_now": [
                "product and lifecycle governance",
                "typed agent-decision contract",
                "health, product-brief, and blueprint API routes",
                "architecture explorer UI",
            ],
            "not_running_yet": [
                "authorised retailer connector",
                "snapshot storage and feature jobs",
                "baseline or candidate model training",
                "parallel agent orchestration",
                "model registry, deployment, and drift monitoring",
            ],
        },
        "stages": [
            {
                "id": "connector",
                "title": "Authorised connector",
                "state": "PLANNED",
                "owner": "Data platform",
                "output": "Immutable, tenant-scoped retail snapshot",
            },
            {
                "id": "validation",
                "title": "Data contract gate",
                "state": "DESIGNED",
                "owner": "Data Contract Agent",
                "output": "Accepted scope or INCONCLUSIVE result",
            },
            {
                "id": "features",
                "title": "Historical feature build",
                "state": "PLANNED",
                "owner": "ML platform",
                "output": "Versioned chronology-safe features",
            },
            {
                "id": "evaluation",
                "title": "Baseline and ML backtest",
                "state": "DESIGNED",
                "owner": "Forecast Evaluation Agent",
                "output": "Registered validation comparison",
            },
            {
                "id": "review",
                "title": "Parallel decision review",
                "state": "CONTRACT_DEFINED",
                "owner": "Specialist agent group",
                "output": "Typed evidence and limitations",
            },
            {
                "id": "human",
                "title": "Human approval",
                "state": "DESIGNED",
                "owner": "Retail planner",
                "output": "Approved, declined, or deferred case",
            },
            {
                "id": "monitoring",
                "title": "Outcome and drift monitoring",
                "state": "PLANNED",
                "owner": "MLOps",
                "output": "Auditable alert, retrain, or rollback proposal",
            },
        ],
        "agents": [
            {
                "id": "data-contract",
                "name": "Data Contract Agent",
                "responsibility": "Checks identity, units, timestamps, coverage, and snapshot provenance.",
                "parallel_group": "evidence-review",
                "state": "CONTRACT_DEFINED",
            },
            {
                "id": "forecast-evaluation",
                "name": "Forecast Evaluation Agent",
                "responsibility": "Compares the declared baseline and eligible candidates on chronological validation.",
                "parallel_group": "evidence-review",
                "state": "CONTRACT_DEFINED",
            },
            {
                "id": "inventory-risk",
                "name": "Inventory Risk Agent",
                "responsibility": "Assesses the evidence needed to qualify a stockout or excess-inventory review case.",
                "parallel_group": "evidence-review",
                "state": "DESIGNED",
            },
            {
                "id": "impact-ranking",
                "name": "Impact Ranking Agent",
                "responsibility": "Ranks eligible cases using declared operational evidence, never hidden reasoning.",
                "parallel_group": "evidence-review",
                "state": "DESIGNED",
            },
            {
                "id": "policy-critic",
                "name": "Policy Critic",
                "responsibility": "Vetoes unsupported claims, incomplete evidence, unsafe drafts, and missing approval paths.",
                "parallel_group": "release-gate",
                "state": "CONTRACT_DEFINED",
            },
            {
                "id": "action-drafting",
                "name": "Action Drafting Agent",
                "responsibility": "Creates an evidence-linked draft only after all gates pass; a human still decides.",
                "parallel_group": "release-gate",
                "state": "DESIGNED",
            },
        ],
        "lifecycle": [
            "Version connector snapshot and mappings.",
            "Build historical-only features per compatible SKU, location, and unit.",
            "Backtest a simple baseline before candidate models using chronological splits.",
            "Lock the final test period; register selected model, metrics, configuration, and rollback target.",
            "Deploy only an approved champion behind release checks.",
            "Monitor realised error, coverage, schema/feature drift, freshness, and reviewer outcomes.",
            "Propose retraining or rollback through an auditable human-reviewed change request.",
        ],
        "controls": [
            {
                "title": "CI checks",
                "detail": "Unit tests, contract checks, chronological-evaluation checks, and frontend production build.",
                "state": "PARTIAL",
            },
            {
                "title": "CD release gate",
                "detail": "Package a versioned service only after quality, security, and model-promotion checks pass.",
                "state": "PLANNED",
            },
            {
                "title": "Data and model drift",
                "detail": "Detect schema changes, missing coverage, freshness loss, feature drift, and realised-error deterioration.",
                "state": "PLANNED",
            },
            {
                "title": "Human decision boundary",
                "detail": "No purchase, transfer, price, or supplier action is executed by the system.",
                "state": "ENFORCED_BY_POLICY",
            },
        ],
    }
