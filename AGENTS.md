# RetailOps ML — Project Constitution

## Mission

Build an evidence-first decision-support system for retailers and distributors.
It identifies demand, inventory, and replenishment cases that merit human
review. The product scope is a merchant's authorised operational data, not a
country-specific public dataset.

The governing documents are the constitution, retail connector contract, agent
contracts, lifecycle governance, and product-decision prompt in docs/. Read the
relevant document before changing a workflow, model, agent, claim, or API
contract.

## Product boundary

- The product supports human planners; it does not autonomously buy stock,
  transfer inventory, alter prices, or contact suppliers.
- A forecast, risk score, or draft action is an estimate, not a guarantee of
  sales, profit, availability, or business impact.
- Demo, synthetic, and public benchmark data must be visibly labelled. A
  production claim needs authorised customer data and a declared evaluation.
- If identity, unit, stock coverage, lead time, or forecasting evidence is
  insufficient, return INCONCLUSIVE and do not create an action draft.

## Data and modelling rules

- Accept only authorised connector data or explicitly labelled fixtures.
- Analyse only compatible SKU, location, and quantity-unit scopes. Record
  exclusions; never silently repair source records.
- Version every input snapshot, mapping, feature definition, model
  configuration, metric, and decision artifact.
- Use chronological splits and historical-only features. Establish a baseline
  before an ML candidate and lock the final test period.
- Promote a model only when it improves declared validation criteria; retain a
  rollback-ready champion and monitor realised error and drift.

## Agent rules

Agents are typed, deterministic components by default. They receive named
artifacts and return concise decisions, evidence references, limitations, and
the next action. They do not retrieve unapproved data, calculate metrics
mentally, or write to a customer system.

The fixed specialists are Data Contract, Forecast Evaluation, Inventory Risk,
Impact Ranking, Policy Critic, and Action Drafting. The Policy Critic may
return only PASS, PASS_WITH_LIMITATIONS, REJECT, or INCONCLUSIVE and has veto
authority over unsupported actions.

An optional LLM may explain critic-approved evidence. It may not create
numbers, map data without approval, choose a model, or submit an action.

## Engineering and assurance

- Use Python, FastAPI, pandas, scikit-learn, React, Vite, and TypeScript.
- Keep credentials and operational data server-side; use read-only,
  least-privilege connectors by default.
- Record concise audit artifacts, never hidden reasoning or unnecessary
  customer data.
- A connector, model, threshold, agent contract, or action-policy change needs
  fixture-based success, failure, and safety-boundary tests.
- Before release, run relevant tests, frontend build, lifecycle audit, and the
  four product questions: why, what, how, and measured impact.
