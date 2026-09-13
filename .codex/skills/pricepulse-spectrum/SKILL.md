---
name: pricepulse-spectrum
description: Build or extend PricePulse MY, an evidence-first Malaysian essential-goods price surveillance MVP using official PriceCatcher data, leakage-safe analysis, deterministic agents, and a premium analytical dashboard.
---

# PricePulse Spectrum

Use this skill only for PricePulse MY work: data contract, deterministic price analysis, agentic review, API, dashboard, or reliability audit. Do not apply it to unrelated analytics products.

## Product boundary

PricePulse MY helps a human reviewer find statistically unusual local movements in prices for an individual essential-good item. It is decision support, not price regulation or enforcement.

Use only the official PriceCatcher transactions and its item and premise lookup datasets. Treat the selected `item_code` and verified unit as the atomic comparison unit. Do not combine item codes, infer a unit, or compare incompatible units.

The product must not claim inflation, price gouging, profiteering, hoarding, supply disruption, a cause of price change, or wrongdoing. An anomaly may only support a recommendation for human price-surveillance review. If data quality or coverage is inadequate, return `INCONCLUSIVE`.

No external LLM or paid AI API is required. The agents are deterministic, typed Python components that inspect verified computation results. They must not invent facts, results, or explanations.

The repository's [constitution](../../../docs/constitution.md) and [prompting standard](../../../docs/prompting_standard.md) are mandatory for workflow, agent, model, claim, and API-contract changes.

## Workflow routing

Work through the smallest applicable stage. Start at Stage 0 for a new repository; do not begin a later stage until its prerequisite artifacts and tests exist.

- Read [build stages](references/build-stages.md) for the requested implementation stage.
- Read [evidence rules](references/evidence-rules.md) before touching ingestion, modelling, agents, or claims.
- Read [UI specification](references/ui-spec.md) only when implementing or reviewing the frontend.

When extending existing work, inspect the current code and contract first. Preserve valid user changes. Do not replace verified outputs with mock data merely to make the dashboard look populated.

## Completion gate

For a changed stage, run the relevant tests and check its explicit acceptance criteria. Before presenting a full-MVP result, run backend tests, the frontend production build, and the reliability audit in Stage 8. Report unavailable data, failed checks, and limitations plainly.
