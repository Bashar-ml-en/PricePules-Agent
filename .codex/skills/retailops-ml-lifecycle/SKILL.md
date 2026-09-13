---
name: retailops-ml-lifecycle
description: Build or extend RetailOps ML, an evidence-first retail demand, inventory, and replenishment decision system with authorised connectors, controlled ML lifecycle, and human-approved actions.
---

# RetailOps ML Lifecycle

Use this skill for RetailOps ML product decisions, retail-data connectors,
forecast lifecycle work, deterministic agents, review workflows, or dashboard
evidence. Do not use it for generic ecommerce sites, autonomous purchasing, or
unrelated analytics.

## Product boundary

RetailOps ML supports a human planner by identifying reviewable demand and
inventory cases for compatible SKU, location, and unit scopes. It never submits
a purchase order, transfers stock, changes a price, or guarantees business
outcomes.

Use only authorised connector data or fixtures visibly labelled as demo,
synthetic, or public benchmark data. Missing identity, inventory state, lead
time, coverage, or model proof must produce INCONCLUSIVE or REJECT, not an
action draft.

## Workflow routing

- For a product idea, pilot, or new capability, read
  [the product-decision prompt](references/product-decision-prompt.md).
- For CSV, commerce, inventory, or supplier integrations, read
  [the connector contract](references/connector-contract.md).
- For forecasting, model promotion, drift, retraining, or audit work, read
  [lifecycle governance](references/lifecycle-governance.md).

## Operating rules

- Version input snapshots, mappings, features, models, metrics, and decisions.
- Use chronological evaluation, compare a baseline first, keep the final test
  period locked, and retain a rollback-ready champion.
- Use deterministic typed specialists for data contract, forecast evaluation,
  inventory risk, impact ranking, policy critique, and action drafting.
- Let the Policy Critic veto unsupported claims and unsafe drafts. Humans alone
  approve operational actions.
- Never log hidden reasoning, credentials, or unnecessary customer data.

## Completion gate

Run relevant tests and document why, what, how, and measured impact. Before a
release, run the lifecycle audit and frontend production build. Report missing
customer evidence or a blocked integration plainly.
