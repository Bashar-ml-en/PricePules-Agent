# RetailOps ML

RetailOps ML is a global, evidence-first decision-support foundation for
retailers and distributors. It helps human planners identify demand and
inventory cases that deserve review before a stockout or excess-stock decision
is made.

## The product answers four questions

| Question | RetailOps ML answer |
| --- | --- |
| Why is this worth solving? | Retail teams need a reliable way to prioritise stockout and excess-inventory risk from fragmented operational data. |
| What does it do? | It produces evidence-backed demand forecasts, inventory-risk cases, and reviewable action drafts per compatible SKU and location. |
| How does it work? | Authorised connector data is validated, versioned, forecast chronologically, reviewed by deterministic specialists, and presented for human approval. |
| What impact does it make? | A pilot measures forecast error, qualified cases found, planner response time, stockout days, and excess inventory. It does not promise outcomes before measurement. |

## Current status

This is a clean RetailOps ML foundation. It contains the product constitution,
retail connector contract, ML lifecycle governance, agent contracts, reusable
skill, reframed product-decision prompt, and a minimal local scaffold.

It intentionally has no live merchant connector, demand forecast, inventory
score, or autonomous purchasing capability yet. Those are upcoming validated
stages, not mocked features.

## Documentation

- [Constitution](docs/constitution.md)
- [Retail connector contract](docs/data_contract.md)
- [Agent contracts](docs/agent_prompts.md)
- [ML lifecycle governance](docs/lifecycle_governance.md)
- [Architecture](docs/architecture.md)
- [Inspectable system blueprint](docs/system_blueprint.md)
- [Build track](docs/build_track.md)
- [Product-decision prompt](docs/prompting_standard.md)

## Local development

Backend, from backend/:

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8000
~~~

Frontend, from frontend/:

~~~powershell
pnpm install
pnpm dev
~~~

Open http://localhost:5173 after starting the API at http://localhost:8000.

## Vercel deployment

The checked-in Vercel configuration builds the static React control room from
`frontend/` and serves `frontend/dist`. It explicitly installs development
build tooling, so a `NODE_ENV=production` project variable cannot omit Vite or
TypeScript during Vercel's build. The public control room uses its embedded,
explicitly labelled architecture blueprint unless an HTTPS API is configured
with `VITE_API_URL`.

A Vercel deployment makes the inspectable product surface available; it does
not by itself activate retail connectors, model training, agent workloads, or
operational decisions. Before connecting a production API, deploy it separately
with authenticated connector credentials held only on the server, explicit
CORS for the Vercel domain, durable audit storage, and the lifecycle gates in
`docs/system_blueprint.md`.
