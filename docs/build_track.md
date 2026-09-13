# RetailOps ML Build Track

Work sequentially. A stage is complete only when its acceptance checks pass.

| Stage | Deliverable | Acceptance |
| --- | --- | --- |
| 0. Product decision | Defined buyer, workflow, four-question case, pilot metric | Prompt review returns PROCEED or a documented REFINE. |
| 1. Foundation | Constitution, connector contract, agent contracts, API/UI scaffold | No legacy domain wording; health/API and frontend build pass. |
| 2. CSV connector | Versioned CSV import and deterministic mapping validation | Valid, malformed, duplicate, unknown-SKU, and missing-inventory fixtures pass. |
| 3. Demand baseline | SKU-location daily demand series and chronology-safe baseline | No leakage; baseline metrics and insufficient-history path tested. |
| 4. Model lifecycle | Candidate comparison, registry, monitoring artifacts, rollback policy | Candidate cannot replace baseline without declared validation success. |
| 5. Risk and review | Inventory-risk cases, policy critic, reviewer queue, action drafts | Stale/missing inventory and unsupported actions stop safely. |
| 6. Production pilot | Read-only connector, access controls, scheduled jobs, observability | One authorised pilot measures declared metrics against baseline. |

The immediate next implementation stage is Stage 2. Do not implement an
inventory-risk recommendation before the connector contract is validated.
