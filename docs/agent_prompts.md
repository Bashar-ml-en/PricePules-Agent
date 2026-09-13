# RetailOps ML Agent Contracts

Specialists receive named, typed artifacts and return concise evidence. They do
not use hidden reasoning, browse customer systems directly, or write to a
customer system.

## Shared decision contract

~~~json
{
  "agent": "data_contract | forecast_evaluation | inventory_risk | impact_ranking | policy_critic | action_drafting",
  "run_id": "uuid",
  "status": "PASS | PASS_WITH_LIMITATIONS | REJECT | INCONCLUSIVE",
  "findings": [{"statement": "concise evidence-bound finding", "evidence_refs": ["artifact.field"]}],
  "limitations": [],
  "next_action": "named gate or stop"
}
~~~

## Specialist responsibilities

| Agent | Allowed inputs | Must stop when |
| --- | --- | --- |
| Data Contract | Connector metadata, mapping, validation, snapshot summary | Identity, unit, scope, or data provenance is unknown. |
| Forecast Evaluation | Approved demand series, feature/model configs, chronological metrics | A baseline is absent, a split leaks future data, or metrics are ineligible. |
| Inventory Risk | Forecast artifact, current inventory, inbound supply, lead-time policy | Inventory is stale, a required unit is incompatible, or lead-time evidence is missing. |
| Impact Ranking | Qualified risk cases and declared ranking assumptions | It would turn an estimate into a revenue or profit guarantee. |
| Policy Critic | All prior decisions and draft claims/actions | Any unsupported claim, unsafe action, missing evidence, or policy breach exists. |
| Action Drafting | Critic-approved case and human-review template | Critic status is not PASS or PASS_WITH_LIMITATIONS. |

## Optional language-model use

An LLM may turn a critic-approved artifact into a concise reviewer explanation.
It must receive labelled, bounded context and a fixed output schema. It may not
compute metrics, map columns autonomously, access connectors, or issue a
purchase or transfer action.
