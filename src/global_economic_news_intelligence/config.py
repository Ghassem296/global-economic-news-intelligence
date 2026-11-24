"""Validated, minimal application configuration.

Provider and persistence credentials are intentionally not loaded until their ADR
and operation-specific authorization gates are satisfied.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TEST = "test"
    EVALUATION = "evaluation"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class ConfigurationError(ValueError):
    """Raised when an application setting is missing or invalid."""


@dataclass(frozen=True, slots=True)
class Settings:
    environment: Environment
    log_level: LogLevel

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Settings:
        values = os.environ if environ is None else environ

        raw_environment = values.get("GENI_ENV", Environment.DEVELOPMENT.value).strip().lower()
        raw_log_level = values.get("GENI_LOG_LEVEL", LogLevel.INFO.value).strip().upper()

        try:
            environment = Environment(raw_environment)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in Environment)
            raise ConfigurationError(
                f"GENI_ENV must be one of: {allowed}."
            ) from exc

        try:
            log_level = LogLevel(raw_log_level)
        except ValueError as exc:
            allowed = ", ".join(item.value for item in LogLevel)
            raise ConfigurationError(
                f"GENI_LOG_LEVEL must be one of: {allowed}."
            ) from exc

        return cls(environment=environment, log_level=log_level)
