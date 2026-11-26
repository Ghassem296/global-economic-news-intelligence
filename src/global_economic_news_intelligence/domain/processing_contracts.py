"""Typed payload contracts for durable processing-run commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from global_economic_news_intelligence.domain.workflows.lifecycle import ProcessingRunStatus


def _required_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def _aware_instant(value: object, field_name: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")


@dataclass(frozen=True, slots=True)
class CreateProcessingRun:
    """Create a logical run; identity and initial status are server-assigned."""

    run_type: str
    target_type: str
    target_id: str
    idempotency_key: str
    input_fingerprint: str

    def __post_init__(self) -> None:
        for field_name in (
            "run_type",
            "target_type",
            "target_id",
            "idempotency_key",
            "input_fingerprint",
        ):
            _required_text(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class TransitionProcessingRun:
    """Request one authorized, version-checked ProcessingRun transition."""

    run_id: str
    expected_version: str
    new_status: ProcessingRunStatus
    actor_reference: str
    occurred_at: datetime
    fencing_token: int | None = None
    reason_or_error_category: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "run_id",
            "expected_version",
            "actor_reference",
        ):
            _required_text(getattr(self, field_name), field_name)
        if not isinstance(self.new_status, ProcessingRunStatus):
            raise ValueError("new_status must be a ProcessingRunStatus.")
        _aware_instant(self.occurred_at, "occurred_at")
        if self.fencing_token is not None and (
            isinstance(self.fencing_token, bool) or not isinstance(self.fencing_token, int)
        ):
            raise ValueError("fencing_token must be an integer when supplied.")
        if self.reason_or_error_category is not None:
            _required_text(self.reason_or_error_category, "reason_or_error_category")
        if (
            self.new_status in {ProcessingRunStatus.FAILED, ProcessingRunStatus.CANCELLED}
            and self.reason_or_error_category is None
        ):
            raise ValueError(
                "reason_or_error_category is required for FAILED or CANCELLED transitions."
            )
