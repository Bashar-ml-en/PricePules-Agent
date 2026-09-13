"""Application configuration with deliberately small, local defaults."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Runtime settings that never contain client-visible secrets."""

    app_name: str = "PricePulse MY"
    app_version: str = "0.1.0"
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )

    @classmethod
    def from_environment(cls) -> "Settings":
        raw_origins = os.getenv("PRICEPULSE_CORS_ORIGINS")
        if not raw_origins:
            return cls()

        origins = tuple(
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        )
        return cls(cors_origins=origins or cls().cors_origins)


settings = Settings.from_environment()
