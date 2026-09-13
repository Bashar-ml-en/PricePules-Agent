"""Official PriceCatcher retrieval with explicit provenance artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CACHE_DIR = ROOT_DIR / "data" / "cache"
BASE_URL = "https://storage.data.gov.my/pricecatcher"
ITEM_LOOKUP_URL = f"{BASE_URL}/lookup_item.csv"
PREMISE_LOOKUP_URL = f"{BASE_URL}/lookup_premise.csv"


class DataSourceUnavailable(RuntimeError):
    """Raised only when no usable transaction source is available for a run."""


@dataclass(frozen=True)
class SourceArtifact:
    """A retrievable, audit-friendly record of one source access attempt."""

    name: str
    url: str
    retrieved_at: str
    status: str
    row_count: int | None = None
    cache_path: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class RawPriceCatcherData:
    """Raw source frames kept separate from qualification and modelling data."""

    transactions: pd.DataFrame
    items: pd.DataFrame
    premises: pd.DataFrame
    sources: tuple[SourceArtifact, ...]


def monthly_url(month: str) -> str:
    """Return the official transaction URL for a validated `YYYY-MM` month."""

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError as error:
        raise ValueError("month must use YYYY-MM format") from error
    return f"{BASE_URL}/pricecatcher_{month}.csv"


def month_sequence(start_month: str, end_month: str) -> list[str]:
    """Return inclusive months without silently assuming a source file exists."""

    try:
        start = datetime.strptime(start_month, "%Y-%m")
        end = datetime.strptime(end_month, "%Y-%m")
    except ValueError as error:
        raise ValueError("months must use YYYY-MM format") from error
    if start > end:
        raise ValueError("start_month must not be after end_month")

    months: list[str] = []
    current = start
    while current <= end:
        months.append(current.strftime("%Y-%m"))
        year = current.year + (current.month == 12)
        month = 1 if current.month == 12 else current.month + 1
        current = current.replace(year=year, month=month)
    return months


class PriceCatcherLoader:
    """Fetch official CSVs, cache successful responses, and preserve failures."""

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, timeout_seconds: int = 60):
        self.cache_dir = cache_dir
        self.timeout_seconds = timeout_seconds

    def load(self, months: Iterable[str]) -> RawPriceCatcherData:
        """Load lookup tables and every requested monthly transaction file.

        A missing month remains a source artifact. It is never replaced by an
        invented file or silently ignored.
        """

        item_frame, item_source = self._fetch_csv("lookup_item", ITEM_LOOKUP_URL)
        premise_frame, premise_source = self._fetch_csv(
            "lookup_premise", PREMISE_LOOKUP_URL
        )

        transaction_frames: list[pd.DataFrame] = []
        source_artifacts = [item_source, premise_source]
        for month in months:
            url = monthly_url(month)
            frame, artifact = self._fetch_csv(f"pricecatcher_{month}", url)
            source_artifacts.append(artifact)
            if not frame.empty:
                transaction_frames.append(frame)

        if not transaction_frames:
            raise DataSourceUnavailable(
                "No requested official PriceCatcher transaction file could be loaded."
            )

        return RawPriceCatcherData(
            transactions=pd.concat(transaction_frames, ignore_index=True),
            items=item_frame,
            premises=premise_frame,
            sources=tuple(source_artifacts),
        )

    def load_lookups(self) -> tuple[pd.DataFrame, pd.DataFrame, tuple[SourceArtifact, ...]]:
        """Load only catalogue data for selectors without forcing a large run."""

        items, item_source = self._fetch_csv("lookup_item", ITEM_LOOKUP_URL)
        premises, premise_source = self._fetch_csv("lookup_premise", PREMISE_LOOKUP_URL)
        if items.empty or premises.empty:
            raise DataSourceUnavailable("Official PriceCatcher lookup data is unavailable.")
        return items, premises, (item_source, premise_source)

    def _fetch_csv(self, name: str, url: str) -> tuple[pd.DataFrame, SourceArtifact]:
        cache_path = self.cache_dir / f"{name}.csv"
        retrieved_at = datetime.now(UTC).isoformat()

        try:
            request = Request(url, headers={"User-Agent": "PricePulseMY/0.1"})
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read()

            frame = pd.read_csv(BytesIO(payload))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(payload)
            return frame, SourceArtifact(
                name=name,
                url=url,
                retrieved_at=retrieved_at,
                status="LIVE",
                row_count=len(frame),
                cache_path=str(cache_path),
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            if cache_path.exists():
                cached_frame = pd.read_csv(cache_path)
                return cached_frame, SourceArtifact(
                    name=name,
                    url=url,
                    retrieved_at=retrieved_at,
                    status="CACHED",
                    row_count=len(cached_frame),
                    cache_path=str(cache_path),
                    error=f"Live retrieval failed: {error}",
                )

            return pd.DataFrame(), SourceArtifact(
                name=name,
                url=url,
                retrieved_at=retrieved_at,
                status="UNAVAILABLE",
                error=str(error),
            )
