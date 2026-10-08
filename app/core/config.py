from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://careerlens:careerlens@localhost:5432/careerlens"
    )
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    adzuna_app_id: str = os.getenv("ADZUNA_APP_ID", "")
    adzuna_app_key: str = os.getenv("ADZUNA_APP_KEY", "")
    adzuna_country: str = os.getenv("ADZUNA_COUNTRY", "us")
    gmail_client_secret_file: str = os.getenv("GMAIL_CLIENT_SECRET_FILE", "")
    demo_mode: bool = os.getenv("CAREERLENS_DEMO_MODE", "true").lower() == "true"
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "8"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def get_settings() -> Settings:
    return Settings()


def redact_secret(value: str) -> str:
    if not value:
        return ""
    return f"{value[:4]}...redacted"
