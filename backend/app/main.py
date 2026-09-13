"""Minimal RetailOps ML API foundation.

The API intentionally exposes product context only. Connector ingestion,
forecasting, risk scoring, and action drafting begin in the validated build
stages documented in docs/build_track.md.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.system_blueprint import build_system_blueprint


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Evidence-first retail demand and inventory decision support.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@app.get("/product/brief", tags=["product"])
def product_brief() -> dict[str, object]:
    return {
        "product": settings.app_name,
        "status": "foundation",
        "why": "Help retail planners prioritise demand and inventory decisions from authorised operational data.",
        "what": "A future workflow for evidence-backed forecast, inventory-risk, and human-review cases.",
        "how": [
            "Validate versioned connector snapshots.",
            "Evaluate chronology-safe baselines and ML candidates.",
            "Pass typed evidence through deterministic specialist agents.",
            "Require human approval before any operational action.",
        ],
        "impact_measurement": [
            "forecast error against a declared baseline",
            "qualified review cases",
            "planner response time",
            "stockout days and excess-inventory measures when available",
        ],
        "non_goals": [
            "autonomous purchasing",
            "inventory transfer",
            "price changes",
            "unmeasured business guarantees",
        ],
    }


@app.get("/system/blueprint", tags=["system"])
def system_blueprint() -> dict[str, object]:
    """Expose the inspectable architecture without claiming a live workload."""

    return build_system_blueprint()
