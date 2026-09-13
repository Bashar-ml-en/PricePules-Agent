# Build stages

Use the focused instruction set for the current stage. Do not add later-stage features early.

## Stage 0 — Foundation and contract

Inspect the official catalogue and actual files. Verify provenance, schema, freshness, availability, date coverage, prices, units, location fields, lookup relationships, and practical volume constraints. Create `README.md`, `AGENTS.md`, `docs/data_contract.md`, `docs/agent_prompts.md`, and `docs/architecture.md`. Record every unknown as `UNKNOWN`; write no application code.

Acceptance: the contract distinguishes verified facts from assumptions and repeats the evidence boundaries.

## Stage 1 — Scaffold

Create a minimal React/Vite/TypeScript frontend and FastAPI/Python backend, typed contracts, config, structured logs, safe errors, CORS, `/health`, and a health test. Use local SQLite only when persistence is implemented; do not require Supabase. No fake analyses or data.

Acceptance: the health test passes and local run commands are documented.

## Stage 2 — Ingestion and data quality

Implement download, cache, and safe loading of official monthly transaction data and lookup tables. The deterministic Data Quality Agent checks required schema, parseable dates, non-negative numeric price, lookup-match rate, duplicates, missing unit, file freshness, date continuity, and item/location coverage. Record exclusions rather than repairing them. Return status, sources, files, date range, counts, issues, limitations, and approved use cases.

Acceptance: fixture-only tests cover malformed schemas, invalid prices, duplicate rows, missing lookups, and limited coverage.

## Stage 3 — Unit-safe daily series and baseline

Accept a single `item_code`, a geography type/value, and dates. Verify its item and unit, aggregate comparable records into a daily median, and include daily transaction/premise counts and quartiles. Gate days lacking configured coverage. Implement a trailing and, when valid, same-day-of-week baseline using only prior observations. Create chronological splitting utilities.

Acceptance: tests prove no mixing of item codes, correct median aggregation, no future baseline leakage, and coverage gating.

## Stage 4 — Forecast and anomaly analysis

Evaluate the baseline first. If enough qualified history exists, compare a Ridge model using only historical lag, rolling, and calendar features. Use chronological validation and an untouched chronological test period. Report configuration, split dates, MAE, RMSE, and selection. Create residual anomalies with a documented MAD score/threshold only from out-of-sample expectations.

Acceptance: tests cover chronological splitting, feature leakage, baseline choice, robust scoring, and invalid coverage exclusions.

## Stage 5 — Deterministic specialist agents

Create typed agents: Data Quality, Price Signal, Market Scope, Reliability Critic, and Reporter. Their only inputs are structured results from earlier deterministic tools. The critic returns `PASS`, `PASS_WITH_LIMITATIONS`, `REJECT`, or `INCONCLUSIVE`, plus approved/rejected claims, required changes, evidence references, and limitations. Store concise outcomes only, never hidden reasoning.

Acceptance: end-to-end tests cover a valid pass, insufficient evidence, and an explicit rejected unsupported claim.

## Stage 6 — API and local persistence

Expose health, catalogue, dataset status, analysis creation, and analysis retrieval endpoints. Persist analysis metadata, metrics, anomalies, and concise agent outcomes to SQLite. APIs must return provenance, unit, coverage evidence, limitations, and only approved recommendations.

Acceptance: contract tests validate normal, error, and inconclusive paths.

## Stage 7 — Dashboard

Implement the responsive evidence dashboard described in [UI specification](ui-spec.md). Bind every displayed number and status to API results. Include loading, empty, rejected, insufficient-data, and error states.

Acceptance: TypeScript checks and a production build pass; mobile, keyboard, and contrast checks are performed.

## Stage 8 — Reliability audit and demo

Audit provenance, hard-coded or fabricated values, unit safety, leakage, random splitting, baseline fairness, final-test tuning, coverage gates, unsupported language, error handling, and exposed secrets. Fix only critical issues. Run backend tests and the frontend production build. Create a 90-second demo script explaining the decision problem, source, deterministic ML, critic, and limits.

Acceptance: all relevant checks pass or remaining blockers are reported without minimization.
