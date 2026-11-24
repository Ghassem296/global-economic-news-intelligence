import pytest

from global_economic_news_intelligence.exceptions import ErrorCode, GeniError


def test_safe_error_envelope_contains_only_approved_fields() -> None:
    error = GeniError(
        ErrorCode.CONFLICT,
        "The resource changed. Reload and retry.",
        correlation_id="corr-123",
    )
    assert error.to_safe_dict() == {
        "code": "CONFLICT",
        "message": "The resource changed. Reload and retry.",
        "correlation_id": "corr-123",
        "retryable": False,
    }


def test_safe_error_rejects_empty_message_or_correlation() -> None:
    with pytest.raises(ValueError):
        GeniError(ErrorCode.INTERNAL_ERROR, " ", correlation_id="corr")
    with pytest.raises(ValueError):
        GeniError(ErrorCode.INTERNAL_ERROR, "Safe message", correlation_id=" ")


def test_unknown_external_outcome_is_not_marked_retryable() -> None:
    error = GeniError(
        ErrorCode.TIMEOUT_OUTCOME_UNKNOWN,
        "The external result is unknown and must be reconciled.",
        correlation_id="corr-456",
    )
    assert not error.retryable
