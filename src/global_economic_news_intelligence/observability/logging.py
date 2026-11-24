"""Structured JSON logging with an explicit field allowlist."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any


_ALLOWED_FIELDS = (
    "event_name",
    "correlation_id",
    "causation_id",
    "workflow_name",
    "component",
    "outcome",
    "duration_ms",
    "error_code",
)


class SafeJsonFormatter(logging.Formatter):
    """Serialize only approved metadata; omit free-form messages and exception text."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
        }
        for field in _ALLOWED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger with a safe structured formatter."""
    normalized = level.strip().upper()
    numeric_level = logging.getLevelName(normalized)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {level}")

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(numeric_level)

    handler = logging.StreamHandler()
    handler.setFormatter(SafeJsonFormatter())
    root.addHandler(handler)
