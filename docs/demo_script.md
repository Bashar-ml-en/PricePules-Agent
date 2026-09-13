# RetailOps ML Pilot Protocol

## Pilot question

Can RetailOps ML identify qualified stockout or excess-inventory review cases
earlier or more consistently than the participating retailer's current process?

## Required setup

- One authorised retailer or distributor.
- Read-only access or exports for orders, products, locations, inventory, and
  available supplier lead-time data.
- A declared SKU/location cohort, historical period, forecast horizon, and
  existing comparison process.
- Named planner reviewers and an agreed non-automated review workflow.

## Measurements

Record forecast MAE/RMSE against a declared baseline, data coverage, qualified
cases, time to review, planner accept/override outcomes, stockout days, and
excess-inventory proxy where available. Do not attribute revenue or margin
change without an agreed counterfactual and evaluation method.

## Stop conditions

Stop or downgrade a pilot run when access is unauthorised, mappings are
unreproducible, inventories are stale, identity/unit compatibility fails,
history is insufficient, or a proposed action would bypass human approval.
