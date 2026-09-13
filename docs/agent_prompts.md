# PricePulse MY Deterministic Agent Specifications

These agents are Python components operating on typed deterministic outputs. They do not call an external LLM, fabricate values, or store hidden reasoning. Their required instruction structure and shared output schema are in [the prompting standard](prompting_standard.md); their governing authority is [the constitution](constitution.md).

## Orchestrator

Run the workflow in order: data validation, unit-safe daily aggregation, baseline/model evaluation, residual anomaly analysis, market-scope review, reliability critique, then reporting. Stop or downgrade any conclusion when an upstream status is `REJECT` or `INCONCLUSIVE`.

The orchestrator is the sole user-facing coordinator. It passes only named typed artifacts with a `run_id`, source/version references, and status to a specialist. It may not bypass a gate or revise a critic rejection.

## Data Quality Agent

Inspect source URLs, schema, date range, missing values, invalid numeric prices, duplicate records, lookup matches, units, geographic fields, and coverage. Record transformations and exclusions explicitly. Return only verified facts and one of `PASS`, `PASS_WITH_LIMITATIONS`, `REJECT`, or `INCONCLUSIVE`.

## Price Signal Agent

Compare out-of-sample observed daily median price with its baseline or selected model expectation. Report MAE, RMSE, configuration, residual, robust anomaly score, threshold, and coverage evidence. Never infer a cause or calculate metrics outside deterministic tooling.

## Market Scope Agent

Determine whether a qualified signal is isolated or corroborated according to configured transaction and distinct-premise thresholds. The output may say `INSUFFICIENT_COVERAGE`; it must not identify a merchant, assign motive, or declare a market-wide effect.

## Reliability Critic

Reject any result with unverified sources, invalid units, future leakage, random time splits, an absent baseline, tuning against the final test set, inadequate coverage, undocumented anomaly threshold, invented values, or unsupported claims. Return `PASS`, `PASS_WITH_LIMITATIONS`, `REJECT`, or `INCONCLUSIVE` with concise evidence references and approved/rejected claims.

## Reporter

Generate a concise evidence report from approved fields only. A permitted recommendation is: “Observed price is materially above the historical expectation and qualified coverage meets the configured threshold; conduct a human price-surveillance review.”
