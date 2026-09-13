# RetailOps system blueprint

The control-room screen and `GET /system/blueprint` deliberately distinguish
the current foundation from the intended production operating model. They are
not a live-agent simulator and must not be described as one.

## What exists now

- The project constitution, lifecycle governance, connector contract, and
  deterministic agent decision contract.
- A FastAPI health endpoint, product brief, and versioned architecture
  blueprint endpoint.
- A React architecture explorer that can load the blueprint from the API and
  fall back to the same labelled local foundation data when the API is absent.
- Backend contract tests and a production frontend build.

## What must be implemented before a production claim

1. An authorised, tenant-scoped, read-only connector that creates immutable
   snapshots and a validated canonical retail dataset.
2. A time-safe feature job, a declared baseline, chronological validation,
   locked final test, model registry, and rollback-ready champion.
3. A job queue and durable audit storage that run specialist agents on the
   same evidence bundle and record their typed decisions.
4. A human review queue and outcome capture path. No agent may execute a
   purchase, transfer, pricing, or supplier action.
5. CI checks for code, contracts, data assumptions, and evaluation rules;
   followed by a release gate that packages only an approved version.
6. Production monitoring for schema, freshness, coverage, feature, and data
   drift plus realised forecast error. Drift proposes a retrain or rollback;
   it never changes the champion automatically.

## Parallel-agent rule

The data-contract, forecast-evaluation, inventory-risk, and impact-ranking
specialists may operate in parallel only after they receive the identical
versioned scope and evidence references. Their results converge at the Policy
Critic, which can return `REJECT` or `INCONCLUSIVE`. Action drafting occurs
only after that gate, and an authorised retail planner remains the sole
approver.

## Delivery sequence

Build the connector and snapshot contract first. Then implement baseline
backtesting, model registration, controlled scoring, review cases, and
monitoring in that order. Each stage must ship with its own tests, artifacts,
and documented acceptance criteria before the next is activated.
