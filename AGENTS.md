# PricePulse MY — Project Constitution

## Mission

Build a reproducible, evidence-first Malaysian essential-goods price-surveillance prototype. The product surfaces statistically unusual qualified price signals for human review.

The mandatory governing documents are [the constitution](docs/constitution.md), [the data contract](docs/data_contract.md), and [the prompting standard](docs/prompting_standard.md). Read the relevant document before changing a workflow, agent, model, claim, or API contract.

## Source of truth

Use only the official PriceCatcher transaction data and its official item and premise lookup tables. Inspect live source files before assuming a filename, schema, date range, field, unit, or data value.

## Evidence boundary

- Process one official `item_code` and verified unit at a time.
- Never combine items or compare incompatible units.
- PriceCatcher supports local, high-frequency price surveillance. It does not establish inflation, a cause, a supply shortage, recommended prices, or misconduct.
- An anomaly may support only: “conduct a human price-surveillance review.”
- If coverage or evidence is insufficient, return `INCONCLUSIVE`.
- Do not invent values, dates, locations, sources, metrics, causes, or conclusions.

## Modelling rules

- Never randomize a temporal split or use future observations in a feature, baseline, training set, validation set, or prediction.
- Establish a simple historical baseline before an ML model.
- Calculate MAE and RMSE deterministically using chronological validation.
- Do not tune against the final chronological test set.
- Retain the baseline if an eligible ML model does not outperform it on validation.
- Use a documented residual anomaly method and never score a coverage-ineligible date as an anomaly.

## Agent rules

Agents are deterministic typed Python components, not LLM calls. They inspect structured tool results and return concise decisions, evidence references, and limitations. They must not calculate metrics mentally or create unverified prose.

The Reliability Critic can return only `PASS`, `PASS_WITH_LIMITATIONS`, `REJECT`, or `INCONCLUSIVE`. It must reject unsupported claims, weak coverage, incompatible units, unverified provenance, leakage, and missing baselines.

The workflow stays flat: one orchestrator and four specialists. Specialists return compact typed evidence artifacts, do not create subagents, and never communicate directly with the user. The reporter renders only critic-approved findings.

## Engineering

- Python, FastAPI, pandas, scikit-learn, React, Vite, TypeScript, and Recharts.
- Keep secrets out of the client; no paid AI API is required.
- Prefer focused, testable modules and structured API responses.
- Before completion, run relevant tests, frontend production build, and the reliability audit.
- Every source mapping, model/threshold, agent contract, or permitted claim change needs a documented rationale and regression coverage.
