"""Public response shapes for the PricePulse API."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HealthResponse(BaseModel):
    """Readiness response that contains no inferred analysis information."""

    status: Literal["ok"] = "ok"
    service: str = "PricePulse MY API"
    version: str = Field(description="Backend application version.")


class AnalysisRequest(BaseModel):
    """A bounded, unit-safe request for one PricePulse analysis run."""

    item_code: int = Field(gt=0)
    geography_type: Literal["national", "state", "district"]
    geography_value: str | None = Field(default=None, max_length=120)
    start_date: date
    end_date: date
    min_transactions: int = Field(default=3, ge=1, le=10_000)
    min_premises: int = Field(default=2, ge=1, le=10_000)
    anomaly_threshold: float = Field(default=3.5, gt=0, le=20)

    @model_validator(mode="after")
    def validate_scope(self) -> "AnalysisRequest":
        if self.start_date > self.end_date:
            raise ValueError("start_date must not be after end_date")
        if (self.end_date - self.start_date).days > 366:
            raise ValueError("Analysis windows may not exceed 366 days")
        if self.geography_type == "national" and self.geography_value:
            raise ValueError("national analysis must not include geography_value")
        if self.geography_type != "national" and not self.geography_value:
            raise ValueError(f"{self.geography_type} analysis requires geography_value")
        return self


class CatalogueItem(BaseModel):
    item_code: int
    item: str
    unit: str
    item_group: str | None = None
    item_category: str | None = None


class CatalogueResponse(BaseModel):
    source_url: str
    items: list[CatalogueItem]
