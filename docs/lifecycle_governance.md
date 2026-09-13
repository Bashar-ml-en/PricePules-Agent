# RetailOps ML Lifecycle Governance

## Lifecycle

1. Acquire a read-only, authorised connector snapshot.
2. Validate and version the canonical retail dataset.
3. Build only historical features for each compatible SKU-location-unit scope.
4. Evaluate a transparent baseline and eligible candidate models with
   chronological validation; keep a locked test period.
5. Register the champion model, data snapshot, feature version, configuration,
   metrics, and rollback candidate.
6. Score eligible future demand and inventory-risk cases.
7. Record actual demand when it becomes known; measure realised error, coverage,
   drift, and reviewer outcomes.
8. Propose retraining or rollback only through declared criteria and audit it.

## Minimum registered artifacts

| Artifact | Required fields |
| --- | --- |
| Dataset snapshot | tenant, retrieval time, connector/mapping version, schema hash, scope, row counts |
| Feature set | version, horizon, lookback, availability rules, source snapshot IDs |
| Model run | algorithm/configuration, split dates, baseline metrics, candidate metrics, selection result |
| Production score | model version, score timestamp, input snapshot ID, confidence and limitations |
| Review case | risk evidence, critic status, reviewer decision, approved action draft if any |
| Monitoring event | realised error, data-quality change, drift signal, retrain/rollback decision |

## Promotion and monitoring rules

- The baseline is always evaluated and is the fallback champion.
- A candidate is promoted only on predeclared validation criteria, never because
  it produces a more attractive chart.
- The final test partition remains untouched until after selection.
- Alert on schema drift, missing data, SKU/location coverage collapse, stale
  inventory, prediction-error deterioration, and feature availability changes.
- Reviewer feedback informs product prioritisation and policy evaluation. It is
  not automatically a ground-truth label for causality or profit.
