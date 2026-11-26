from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.domain.processing_contracts import (
    CreateProcessingRun,
    TransitionProcessingRun,
)
from global_economic_news_intelligence.domain.workflows.lifecycle import ProcessingRunStatus


NOW = datetime(2026, 11, 26, 10, 0, tzinfo=UTC)


def create_run(**overrides: object) -> CreateProcessingRun:
    values: dict[str, object] = {
        "run_type": "article_revision_ingestion",
        "target_type": "source",
        "target_id": "source-1",
        "idempotency_key": "source-1:batch-1",
        "input_fingerprint": "fingerprint-1",
    }
    values.update(overrides)
    return CreateProcessingRun(**values)  # type: ignore[arg-type]


def transition(**overrides: object) -> TransitionProcessingRun:
    values: dict[str, object] = {
        "run_id": "run-1",
        "expected_version": "v1",
        "new_status": ProcessingRunStatus.RUNNING,
        "actor_reference": "worker-1",
        "occurred_at": NOW,
    }
    values.update(overrides)
    return TransitionProcessingRun(**values)  # type: ignore[arg-type]


def test_create_run_requires_stable_idempotency_and_input_identity() -> None:
    assert create_run().input_fingerprint == "fingerprint-1"
    with pytest.raises(ValueError, match="idempotency_key"):
        create_run(idempotency_key=" ")


def test_create_run_does_not_accept_server_owned_run_status() -> None:
    assert not hasattr(create_run(), "status")


def test_transition_run_uses_closed_status_type() -> None:
    assert transition().new_status is ProcessingRunStatus.RUNNING
    with pytest.raises(ValueError, match="ProcessingRunStatus"):
        transition(new_status="COMPLETED")  # type: ignore[arg-type]


def test_transition_requires_aware_server_time_and_actor() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        transition(occurred_at=datetime(2026, 11, 26, 10, 0))
    with pytest.raises(ValueError, match="actor_reference"):
        transition(actor_reference=" ")


@pytest.mark.parametrize(
    "status",
    (ProcessingRunStatus.FAILED, ProcessingRunStatus.CANCELLED),
)
def test_failure_and_cancellation_require_reason(status: ProcessingRunStatus) -> None:
    with pytest.raises(ValueError, match="reason_or_error_category"):
        transition(new_status=status)
    assert transition(
        new_status=status,
        reason_or_error_category="operator_requested",
    ).reason_or_error_category == "operator_requested"


def test_fencing_token_must_be_an_integer_not_a_boolean() -> None:
    assert transition(fencing_token=12).fencing_token == 12
    with pytest.raises(ValueError, match="integer"):
        transition(fencing_token=True)
    with pytest.raises(ValueError, match="integer"):
        transition(fencing_token=1.5)


def test_optional_reason_cannot_be_blank() -> None:
    with pytest.raises(ValueError, match="reason_or_error_category"):
        transition(reason_or_error_category=" ")
