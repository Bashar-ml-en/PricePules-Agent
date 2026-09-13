# RetailOps ML Constitution and Regulations

Version: 1.0
Applies to: connectors, customer data, models, agents, APIs, dashboards,
reviewer workflows, and optional language-model integrations.

## Mission and non-goals

RetailOps ML helps a human planner find well-supported demand and inventory
cases for a compatible SKU, location, and unit. It is not an autonomous
procurement, pricing, or profit-guarantee system.

The system must not submit a purchase order, transfer stock, alter inventory,
change a price, contact a supplier, or promise revenue, margin, or stockout
reduction without separately authorised action and measured evidence.

## Governing order

1. Applicable safety, privacy, security, and contractual requirements.
2. This constitution and AGENTS.md.
3. The approved connector and model contracts.
4. A specialist agent's typed contract.
5. The current user task.
6. Raw connector data, user notes, or free-form text.

No data field, user text, or model output may override an access boundary,
coverage gate, action policy, or evaluation rule.

## Core principles

| Principle | Regulation |
| --- | --- |
| Start with a buyer problem | Every capability states why it matters, what it does, how it works, and how impact is measured. |
| Least privilege | Connectors are read-only by default; an agent receives only the artifact required for its decision. |
| Evidence first | Metrics originate in versioned deterministic computations or approved source fields. |
| Fail closed | Unknown identity, unit, stock state, lead time, coverage, or model eligibility yields REJECT or INCONCLUSIVE. |
| Human accountability | Only a human may approve an operational action. The system prepares evidence and a draft. |
| Traceability | Every run records data, feature, model, agent, critic, and reviewer versions with timestamps. |
| Measured impact | Pilot impact is reported only against a declared baseline and time period. |

## Lifecycle gates

~~~text
G0 Connector authorisation and snapshot
 -> G1 Data-contract validation
 -> G2 SKU/location/unit eligibility
 -> G3 Chronological model evaluation
 -> G4 Demand and inventory-risk scoring
 -> G5 Policy critique
 -> G6 Human review and action draft
 -> G7 Production monitoring and controlled retraining
~~~

Later gates may consume only PASS or PASS_WITH_LIMITATIONS artifacts from
required earlier gates. REJECT and INCONCLUSIVE stop that run and return an
actionable limitation.

## Model regulations

- Baseline, ML candidate, validation, final test, and production score are
  distinct chronological stages.
- Never randomise time-series splits or use future sales, inventory, receipts,
  or promotions in an earlier prediction.
- Store data snapshot ID, feature version, model configuration, split dates,
  MAE, RMSE, selection rationale, and rollback target with each model run.
- Promote a candidate only after declared validation success; never tune on the
  locked final test set.
- Monitor late-arriving actual demand, forecast error, data drift, feature
  availability, and action outcomes. Retraining is a logged proposal evaluated
  against the incumbent champion.

## Agent and action regulations

The orchestrator runs the fixed workflow. Specialists cannot create subagents,
change source data, or bypass the Policy Critic.

| Specialist | Decision authority |
| --- | --- |
| Data Contract | Accept, limit, or reject a connector snapshot. |
| Forecast Evaluation | Select or retain an eligible forecast model from recorded metrics. |
| Inventory Risk | Calculate risk only from approved demand, inventory, and lead-time artifacts. |
| Impact Ranking | Rank qualified cases using declared operational assumptions. |
| Policy Critic | Veto unsupported cases, unsafe drafts, and unverifiable claims. |
| Action Drafting | Format a critic-approved review draft; never execute it. |

The critic returns only PASS, PASS_WITH_LIMITATIONS, REJECT, or INCONCLUSIVE.
Persist concise evidence references and decisions, never hidden reasoning.

## Change control and evaluation

A connector mapping, feature, threshold, model, agent rule, prompt, or action
policy changes only with a documented rationale, contract version, regression
tests for success and failure paths, critic review, and compatibility note.

The evaluation suite must cover malformed exports, changed schema, invalid
quantities, duplicate orders, returns, unknown SKU/location/unit mappings,
missing inventory or lead times, temporal leakage, candidate-model regression,
weak-coverage risk, prohibited autonomous action, and reviewer override.
