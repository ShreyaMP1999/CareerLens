from __future__ import annotations

import logging
from typing import Any

SENSITIVE_KEYS = {"api_key", "authorization", "token", "password", "secret"}


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def redact_mapping(payload: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if any(part in key.lower() for part in SENSITIVE_KEYS):
            redacted[key] = "***redacted***"
        elif isinstance(value, dict):
            redacted[key] = redact_mapping(value)
        else:
            redacted[key] = value
    return redacted

