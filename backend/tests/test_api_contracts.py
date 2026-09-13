"""Request-boundary tests that do not require the live government source."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.contracts import AnalysisRequest


def test_analysis_request_requires_geography_value_for_state() -> None:
    with pytest.raises(ValidationError, match="requires geography_value"):
        AnalysisRequest(
            item_code=1,
            geography_type="state",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
        )


def test_analysis_request_rejects_a_window_over_one_year() -> None:
    with pytest.raises(ValidationError, match="may not exceed 366 days"):
        AnalysisRequest(
            item_code=1,
            geography_type="national",
            start_date=date(2025, 1, 1),
            end_date=date(2026, 1, 3),
        )
