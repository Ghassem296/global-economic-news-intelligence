"""Safe, machine-classifiable application errors."""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    AUTHORIZATION_DENIED = "AUTHORIZATION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    STALE_VERSION = "STALE_VERSION"
    INVARIANT_VIOLATION = "INVARIANT_VIOLATION"
    IDEMPOTENCY_KEY_REUSE_CONFLICT = "IDEMPOTENCY_KEY_REUSE_CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    TIMEOUT_OUTCOME_UNKNOWN = "TIMEOUT_OUTCOME_UNKNOWN"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    RIGHTS_NOT_ALLOWED = "RIGHTS_NOT_ALLOWED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class GeniError(Exception):
    """An error safe to classify and return without exposing internals."""

    def __init__(
        self,
        code: ErrorCode,
        safe_message: str,
        *,
        correlation_id: str,
        retryable: bool = False,
    ) -> None:
        if not safe_message.strip():
            raise ValueError("safe_message must not be empty.")
        if not correlation_id.strip():
            raise ValueError("correlation_id must not be empty.")
        self.code = code
        self.safe_message = safe_message
        self.correlation_id = correlation_id
        self.retryable = retryable
        super().__init__(safe_message)

    def to_safe_dict(self) -> dict[str, str | bool]:
        """Return the public-safe error envelope; never include exception internals."""
        return {
            "code": self.code.value,
            "message": self.safe_message,
            "correlation_id": self.correlation_id,
            "retryable": self.retryable,
        }
