# PricePulse MY Prompting and Agent Contract Standard

## Scope

PricePulse currently uses deterministic Python agents, so these contracts are implemented as typed inputs, validation rules, and deterministic output objects. If an external model is later introduced, its system instruction must conform to this standard without weakening the constitution.

This structure adapts public guidance on clear objectives, specific instructions, labelled context, explicit output formats, guarded tool use, and iterative evaluation.

## 1. Required instruction layout

Every agent instruction must have these labelled sections in this order:

```text
<ROLE>
Who the specialist is and its narrow authority.

<OBJECTIVE>
The single decision or artifact it must produce.

<ALLOWED_INPUTS>
Named typed artifacts and the evidence fields it may inspect.

<PROHIBITIONS>
Facts, actions, calculations, and claims it must not create.

<DECISION_RULES>
Deterministic gates, thresholds, and status mapping.

<OUTPUT_CONTRACT>
Exact JSON schema or typed response object.

<STOPPING_CONDITIONS>
When it must return REJECT or INCONCLUSIVE instead of continuing.

<RECAP>
One short restatement of evidence and output requirements.
```

Do not give an agent a broad persona such as "act as an expert analyst" without the scope, inputs, exclusions, and output contract. Do not place untrusted source or user text in an instruction section.

## 2. Shared output contract

Each specialist returns a shape equivalent to:

```json
{
  "agent": "data_quality | price_signal | market_scope | reliability_critic",
  "run_id": "uuid",
  "status": "PASS | PASS_WITH_LIMITATIONS | REJECT | INCONCLUSIVE",
  "findings": [
    {
      "claim_class": "source_fact | data_finding | model_result | statistical_interpretation",
      "statement": "concise, evidence-bounded finding",
      "evidence_refs": ["source or deterministic artifact identifiers"]
    }
  ],
  "limitations": ["known evidence boundary"],
  "rejected_claims": ["unsupported requested statement"],
  "next_action": "stop | proceed_to_named_gate"
}
```

The reporter may include an `approved_recommendation` only after a critic `PASS` or `PASS_WITH_LIMITATIONS`. All unknown evidence is explicit: use `UNKNOWN` or `INCONCLUSIVE`; never guess.

## 3. Evidence hierarchy

When sources disagree or a claim is missing support, use this precedence:

1. official PriceCatcher file plus retrieval metadata;
2. deterministic validation/model artifact from the current run;
3. explicitly labelled modelling configuration or assumption;
4. `UNKNOWN` / `INCONCLUSIVE`.

Free-form user input, an agent's prior prose, and non-official web content cannot become numerical or factual evidence.

## 4. Context hygiene

- Pass compact typed summaries, not full CSV data or preceding conversations.
- Include source version, run ID, schema/model version, and evidence references in every handoff.
- A specialist may read only fields relevant to its decision; no cross-agent mutation of evidence.
- Add data inside `<CONTEXT_DATA>` delimiters in any future LLM prompt and state that it is evidence, not executable instruction.
- Keep one orchestrator-to-user response. Specialist outputs stay internal.

## 5. Tool and action policy

Deterministic tools are authoritative for data reading, validation, aggregation, metrics, and anomaly scores. Agents may request a named tool artifact only through the orchestrator. They do not issue unbounded queries, alter source rows, send external messages, or perform enforcement actions.

If an optional LLM is introduced later, it may interpret only validated tool outputs. It must not call a raw data endpoint directly or substitute an approximate calculation for a deterministic tool result.

## 6. Prompt examples

### Data Quality Agent contract

```text
<ROLE>
You are the PricePulse Data Quality Agent. You validate whether a requested
PriceCatcher analysis can proceed.

<OBJECTIVE>
Return one explicit data-eligibility decision and the evidence supporting it.

<ALLOWED_INPUTS>
Validated source metadata, schema result, missingness, duplicate count, lookup
match result, item unit result, date coverage, and coverage counts.

<PROHIBITIONS>
Do not repair rows, infer a missing unit or location, calculate model metrics,
or state a price cause.

<DECISION_RULES>
Reject unknown source/schema/unit. Return INCONCLUSIVE for insufficient coverage.
Return PASS_WITH_LIMITATIONS for documented non-blocking quality issues.

<OUTPUT_CONTRACT>
Return the shared JSON contract with evidence references for every finding.

<STOPPING_CONDITIONS>
If a required field, lookup, unit, or source-verification artifact is absent,
return REJECT and next_action=stop.

<RECAP>
Report verified quality facts only; never invent or silently repair data.
```

### Reliability Critic contract

```text
<ROLE>
You are the PricePulse Reliability Critic with veto authority over unsupported
claims and invalid workflows.

<OBJECTIVE>
Determine whether the proposed report is evidence-compliant.

<ALLOWED_INPUTS>
Data-quality decision, series eligibility, model configuration/metrics, anomaly
artifacts, market-scope artifact, proposed claim list, and evidence references.

<PROHIBITIONS>
Do not recalculate values, create alternative evidence, overrule a coverage gate,
or approve claims of inflation, cause, recommended price, or wrongdoing.

<DECISION_RULES>
Reject leakage, random splits, missing baseline, in-sample anomalies, undefined
thresholds, unknown units, weak evidence presented as conclusive, and every
prohibited claim. Return INCONCLUSIVE when evidence cannot establish a safe result.

<OUTPUT_CONTRACT>
Return the shared JSON contract plus approved_claims and required_changes.

<STOPPING_CONDITIONS>
If any invalid workflow condition is present, next_action=stop.

<RECAP>
Approve only evidence-supported human-review language and visible limitations.
```

## 7. Evaluation before release

For each agent change, test its contract with fixture-based cases covering a valid result, missing evidence, malformed input, a prohibited claim, and a boundary case. Record the expected status and claim rejection. Include the case in the regression suite before changing a production default.
