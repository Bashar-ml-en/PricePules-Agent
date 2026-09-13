# PricePulse MY Build Track

**Purpose:** this is the single practical checklist for building, changing, testing, and accepting PricePulse MY. Work moves from top to bottom; a failed gate stops the work until it is fixed or explicitly recorded as `INCONCLUSIVE`.

## Operating rule

Before changing a workflow, model, agent, API, or claim, read the [constitution](constitution.md), [data contract](data_contract.md), and [prompting standard](prompting_standard.md). Use the `pricepulse-spectrum` skill to select the smallest applicable stage, then add or update the matching test before changing the dashboard.

## Build board

| Stage | Deliverable | Status | Completion proof |
| --- | --- | --- | --- |
| 0. Foundation | Official-source contract, product limits, architecture, agent contracts | Complete | `AGENTS.md`, `docs/data_contract.md`, `docs/architecture.md`, and `docs/agent_prompts.md` |
| 1. Scaffold | FastAPI, React/Vite, typed requests, health check, local configuration | Complete | Health API and health test |
| 2. Ingestion | Official monthly loader, cache, provenance, schema and quality checks | Complete | Validation fixture tests and live-source smoke check |
| 3. Series | Single-item, verified-unit daily price series and historical baseline | Complete | Unit, median, coverage, and no-future-leakage tests |
| 4. Forecast | Chronological baseline/Ridge comparison and out-of-sample MAD anomalies | Complete | Split, model selection, leakage, and anomaly tests |
| 5. Agents | Four deterministic decision agents and one controlled reporter | Complete | End-to-end pass, limitation, and rejected-claim tests |
| 6. API and audit store | Analysis endpoints, catalogue endpoints, SQLite run evidence | Complete | API-contract and persistence tests |
| 7. Dashboard | Evidence-bound review dashboard and responsive states | Build complete; manual acceptance pending | TypeScript production build passed; browser QA remains |
| 8. Reliability audit | Provenance, safety, leakage, secret, and build checks | Audit complete; final acceptance pending Stage 7 QA | [Reliability audit](reliability_audit.md) records the results |

## Workflow for every analysis run

```text
User chooses one item, geography, and date window
  -> G0 official source and schema verification
  -> G1 data-quality decision
  -> G2 verified-unit and coverage-qualified daily series
  -> G3 chronological baseline / eligible model evaluation
  -> G4 out-of-sample residual and market-scope review
  -> G5 Reliability Critic decision
  -> G6 evidence report, or safe stop with limitations
```

Only `PASS` or `PASS_WITH_LIMITATIONS` may advance a required gate. A `REJECT` or `INCONCLUSIVE` result ends that run without a speculative conclusion.

## Next work item: local acceptance run

**Owner:** product reviewer (you), with implementation support from Codex.

1. Install the dependencies and run the backend and frontend using the [README](../README.md).
2. Open the dashboard and select an official item, geography, and historical date window.
3. Confirm that the page shows the source status, unit, daily evidence, model comparison, limitations, and agent trail.
4. Try an intentionally too-short or low-coverage request. It must return `INCONCLUSIVE` or a visible limitation, never a fabricated result.
5. Check the dashboard at desktop and mobile widths, keyboard navigation, focus visibility, and contrast. Record defects here or in the next issue/task.

## Change workflow after acceptance

For any new capability, create one work item with this template:

```text
Title: <small, evidence-bounded capability>
Why: <human-review problem it solves>
Affected gate: G0-G6
Permitted inputs: <official fields / typed artifacts only>
Non-goals: <claims or actions it must not make>
Acceptance tests: <positive case, failure case, safety boundary>
UI effect: <which API-backed components change>
Audit impact: <contract, threshold, model, or critic rule to revisit>
```

Do not start a new feature until its affected gate, evidence boundary, and acceptance tests are written. The default next feature is not a more complex model; it is completing manual dashboard acceptance and recording the findings.
