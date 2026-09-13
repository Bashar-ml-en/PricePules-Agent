"""FastAPI entry point for PricePulse MY."""

import logging
from datetime import date
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas.contracts import AnalysisRequest, CatalogueItem, CatalogueResponse, HealthResponse
from app.services.data import DataSourceUnavailable, PriceCatcherLoader
from app.services.orchestrator import PricePulseOrchestrator
from app.services.storage import RunStore


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("pricepulse.api")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Evidence-first essential-goods price-surveillance API. "
        "Analysis endpoints are added only after the data pipeline is verified."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check() -> HealthResponse:
    """Return API readiness without pretending that source data is available."""

    logger.info("health_check status=ok")
    return HealthResponse(version=settings.app_version)


def get_loader() -> PriceCatcherLoader:
    return PriceCatcherLoader()


def get_orchestrator() -> PricePulseOrchestrator:
    return PricePulseOrchestrator()


def get_store() -> RunStore:
    return RunStore()


@app.get("/catalogue/items", response_model=CatalogueResponse, tags=["catalogue"])
def catalogue_items(loader: PriceCatcherLoader = Depends(get_loader)) -> CatalogueResponse:
    """Return only verified, unit-bearing official items for the selector."""

    try:
        items, _, sources = loader.load_lookups()
    except DataSourceUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    valid_items = items.loc[
        items["item_code"].notna()
        & (items["item_code"] > 0)
        & items["item"].notna()
        & items["unit"].notna()
        & items["unit"].astype("string").str.strip().ne("")
    ].copy()
    valid_items = valid_items.sort_values(["item_category", "item", "item_code"])
    return CatalogueResponse(
        source_url=sources[0].url,
        items=[
            CatalogueItem(
                item_code=int(row.item_code),
                item=str(row.item),
                unit=str(row.unit),
                item_group=_optional_text(row.item_group),
                item_category=_optional_text(row.item_category),
            )
            for row in valid_items.itertuples(index=False)
        ],
    )


@app.get("/catalogue/locations", tags=["catalogue"])
def catalogue_locations(
    geography_type: str = Query(pattern="^(state|district)$"),
    loader: PriceCatcherLoader = Depends(get_loader),
) -> dict[str, Any]:
    """Return verified geography labels without inventing a hierarchy."""

    try:
        _, premises, sources = loader.load_lookups()
    except DataSourceUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    column = geography_type
    values = sorted(
        value.strip()
        for value in premises[column].dropna().astype(str).unique()
        if value.strip()
    )
    return {"source_url": sources[1].url, "geography_type": geography_type, "values": values}


@app.get("/dataset/status", tags=["data"])
def dataset_status(
    month: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}$"),
    loader: PriceCatcherLoader = Depends(get_loader),
) -> dict[str, Any]:
    """Expose current provenance and validation state without a model claim."""

    selected_month = month or date.today().strftime("%Y-%m")
    try:
        raw = loader.load([selected_month])
    except DataSourceUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    from app.services.validation import validate_raw_data

    quality = validate_raw_data(raw)
    return quality.to_dict()


@app.post("/analysis/run", tags=["analysis"])
def run_analysis(
    request: AnalysisRequest,
    orchestrator: PricePulseOrchestrator = Depends(get_orchestrator),
    store: RunStore = Depends(get_store),
) -> dict[str, Any]:
    """Run the complete gated workflow and persist a concise audit artifact."""

    try:
        run = orchestrator.run(request)
    except (DataSourceUnavailable, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    payload = run.to_payload()
    store.save(payload)
    logger.info("analysis_complete run_id=%s critic=%s", payload["run_id"], payload["report"]["critic_status"])
    return payload


@app.get("/analysis/{run_id}", tags=["analysis"])
def get_analysis(
    run_id: str,
    store: RunStore = Depends(get_store),
) -> dict[str, Any]:
    """Retrieve a local persisted evidence artifact by its immutable run ID."""

    payload = store.get(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Analysis run was not found.")
    return payload


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
