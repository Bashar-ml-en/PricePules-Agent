# PricePulse MY

PricePulse MY is an evidence-first prototype for identifying statistically unusual local price movements in essential goods in Malaysia. It supports human price-surveillance review; it is not a pricing, enforcement, or inflation system.

## What it does

- Use official PriceCatcher transaction data and official item/premise lookup tables.
- Analyse one official item code and its verified unit in a selected location.
- Calculate daily price evidence, a leakage-safe forecast, and qualified anomalies.
- Use deterministic specialist agents to validate data, scope the signal, and reject unsupported conclusions.
- Present source provenance, coverage, model evidence, anomalies, and limitations in one dashboard.

## Non-negotiable limits

- A price anomaly is not evidence of inflation, price gouging, wrongdoing, a supply shortage, or a cause of price change.
- Inadequate coverage produces `INCONCLUSIVE`, not an estimate or recommendation.
- Every displayed metric must come from a verified source field or deterministic calculation.
- No paid AI or external LLM API is required.

## Source data

The MVP uses the Malaysian government's official [PriceCatcher transactional records](https://data.gov.my/data-catalogue/pricecatcher), [item lookup](https://data.gov.my/data-catalogue/lookup_item), and [premise lookup](https://data.gov.my/data-catalogue/lookup_premise). See [the data contract](docs/data_contract.md) for verified schema, availability, and scope.

## Build status

The reproducible MVP is implemented and verified. It includes:

- Official-source ingestion with schema, provenance, unit, join, and date-continuity checks.
- An item-and-unit-safe daily series, chronology-safe baseline and eligible Ridge comparison, and MAD residual anomaly method.
- Four deterministic decision agents: Data Quality, Price Signal, Market Scope, and Reliability Critic; a deterministic reporter only presents their approved evidence.
- A FastAPI API with SQLite audit storage and a React analytical dashboard for running and inspecting reviews.

The latest local verification found 19 passing backend tests, a successful frontend production build, and a bounded live-data review that returned `PASS_WITH_LIMITATIONS` rather than inventing a conclusion. Read the [reliability audit](docs/reliability_audit.md), [constitution](docs/constitution.md), and [prompting standard](docs/prompting_standard.md) for the evidence rules and results.

The current stage-by-stage delivery and acceptance checklist is in the [build track](docs/build_track.md).

## Local development

Backend, from `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8000
```

Frontend, from `frontend/`:

```powershell
pnpm install
pnpm dev
```

Open `http://localhost:5173` after starting the backend at `http://localhost:8000`. The dashboard fetches the official source files at analysis time and may return `INCONCLUSIVE` when they are unavailable or insufficient for a qualified review.
