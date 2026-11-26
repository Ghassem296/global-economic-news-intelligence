from __future__ import annotations

import pytest

from global_economic_news_intelligence.domain.workflows.lifecycle import (
    EventMatchCandidateStatus,
    EventMatchCaseStatus,
    EventMatchOutcome,
    ExternalAttemptOutcome,
    ExternalAttemptResult,
    ExternalAttemptType,
    ExternalOperationStatus,
    ProcessingRunStatus,
    ProcessingStepStatus,
    PublicationDecisionOutcome,
    ReviewAction,
    ReviewStatus,
    TransitionError,
    aggregate_run_status,
    case_status_for_decision,
    cancel_external_operation,
    external_operation_status_after_attempt,
    project_review_action,
    transition_candidate,
    transition_case,
    transition_run,
    transition_step,
    validate_decision_successor,
)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ProcessingRunStatus.PENDING, ProcessingRunStatus.RUNNING),
        (ProcessingRunStatus.PENDING, ProcessingRunStatus.CANCELLED),
        (ProcessingRunStatus.RUNNING, ProcessingRunStatus.COMPLETED),
        (ProcessingRunStatus.RUNNING, ProcessingRunStatus.FAILED),
        (ProcessingRunStatus.RUNNING, ProcessingRunStatus.PARTIALLY_COMPLETED),
        (ProcessingRunStatus.PARTIALLY_COMPLETED, ProcessingRunStatus.RUNNING),
    ],
)
def test_valid_run_transitions(current: ProcessingRunStatus, target: ProcessingRunStatus) -> None:
    assert transition_run(current, target) is target


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ProcessingRunStatus.COMPLETED, ProcessingRunStatus.RUNNING),
        (ProcessingRunStatus.FAILED, ProcessingRunStatus.RUNNING),
        (ProcessingRunStatus.CANCELLED, ProcessingRunStatus.RUNNING),
        (ProcessingRunStatus.PENDING, ProcessingRunStatus.COMPLETED),
    ],
)
def test_invalid_run_transitions_are_rejected(
    current: ProcessingRunStatus, target: ProcessingRunStatus
) -> None:
    with pytest.raises(TransitionError):
        transition_run(current, target)


def test_failed_step_retry_requires_explicit_authorization() -> None:
    with pytest.raises(TransitionError):
        transition_step(ProcessingStepStatus.FAILED, ProcessingStepStatus.READY)
    assert (
        transition_step(
            ProcessingStepStatus.FAILED,
            ProcessingStepStatus.READY,
            retry_authorized=True,
        )
        is ProcessingStepStatus.READY
    )


def test_blocked_step_requires_satisfied_dependencies() -> None:
    with pytest.raises(TransitionError):
        transition_step(ProcessingStepStatus.BLOCKED, ProcessingStepStatus.READY)
    assert (
        transition_step(
            ProcessingStepStatus.BLOCKED,
            ProcessingStepStatus.READY,
            dependencies_satisfied=True,
        )
        is ProcessingStepStatus.READY
    )


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ((), ProcessingRunStatus.PENDING),
        ((ProcessingStepStatus.SUCCEEDED,), ProcessingRunStatus.COMPLETED),
        (
            (ProcessingStepStatus.SUCCEEDED, ProcessingStepStatus.SKIPPED),
            ProcessingRunStatus.COMPLETED,
        ),
        (
            (ProcessingStepStatus.RUNNING, ProcessingStepStatus.SUCCEEDED),
            ProcessingRunStatus.RUNNING,
        ),
        ((ProcessingStepStatus.FAILED,), ProcessingRunStatus.FAILED),
        ((ProcessingStepStatus.BLOCKED,), ProcessingRunStatus.FAILED),
        (
            (ProcessingStepStatus.SUCCEEDED, ProcessingStepStatus.FAILED),
            ProcessingRunStatus.PARTIALLY_COMPLETED,
        ),
        ((ProcessingStepStatus.CANCELLED,), ProcessingRunStatus.CANCELLED),
        (
            (ProcessingStepStatus.SUCCEEDED, ProcessingStepStatus.CANCELLED),
            ProcessingRunStatus.PARTIALLY_COMPLETED,
        ),
    ],
)
def test_run_status_aggregation(
    statuses: tuple[ProcessingStepStatus, ...], expected: ProcessingRunStatus
) -> None:
    assert aggregate_run_status(statuses) is expected


def test_case_decision_mapping() -> None:
    assert case_status_for_decision(EventMatchOutcome.MATCH) is EventMatchCaseStatus.RESOLVED
    assert case_status_for_decision(EventMatchOutcome.NO_MATCH) is EventMatchCaseStatus.RESOLVED
    assert (
        case_status_for_decision(EventMatchOutcome.REVIEW_REQUIRED)
        is EventMatchCaseStatus.PENDING_REVIEW
    )
    assert case_status_for_decision(EventMatchOutcome.AMBIGUOUS) is EventMatchCaseStatus.OPEN
    assert (
        case_status_for_decision(EventMatchOutcome.NEW_EVENT_CANDIDATE)
        is EventMatchCaseStatus.OPEN
    )


def test_resolved_case_reopen_requires_successor_decision() -> None:
    with pytest.raises(TransitionError):
        transition_case(EventMatchCaseStatus.RESOLVED, EventMatchCaseStatus.OPEN)
    assert (
        transition_case(
            EventMatchCaseStatus.RESOLVED,
            EventMatchCaseStatus.OPEN,
            successor_decision_authorized=True,
        )
        is EventMatchCaseStatus.OPEN
    )


def test_candidate_evaluation_is_immutable_after_terminal_evaluation() -> None:
    assert (
        transition_candidate(
            EventMatchCandidateStatus.GENERATED, EventMatchCandidateStatus.EVALUATED
        )
        is EventMatchCandidateStatus.EVALUATED
    )
    with pytest.raises(TransitionError):
        transition_candidate(
            EventMatchCandidateStatus.EVALUATED, EventMatchCandidateStatus.GENERATED
        )


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        (ExternalAttemptOutcome.CONFIRMED_SUCCESS, ExternalOperationStatus.SUCCEEDED),
        (ExternalAttemptOutcome.CONFIRMED_FAILURE, ExternalOperationStatus.FAILED),
        (
            ExternalAttemptOutcome.OUTCOME_UNKNOWN,
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
        ),
    ],
)
def test_execute_attempt_mapping(
    outcome: ExternalAttemptOutcome, expected: ExternalOperationStatus
) -> None:
    result = ExternalAttemptResult(ExternalAttemptType.EXECUTE, outcome)
    assert (
        external_operation_status_after_attempt(ExternalOperationStatus.IN_PROGRESS, result)
        is expected
    )


def test_external_operation_cancellation_requires_authorization_and_safe_state() -> None:
    with pytest.raises(TransitionError):
        cancel_external_operation(
            ExternalOperationStatus.PENDING, cancellation_authorized=False
        )
    assert (
        cancel_external_operation(
            ExternalOperationStatus.PENDING, cancellation_authorized=True
        )
        is ExternalOperationStatus.CANCELLED
    )
    with pytest.raises(TransitionError):
        cancel_external_operation(
            ExternalOperationStatus.IN_PROGRESS,
            cancellation_authorized=True,
            external_outcome_reconciled=True,
        )
    with pytest.raises(TransitionError):
        cancel_external_operation(
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
            cancellation_authorized=True,
        )
    assert (
        cancel_external_operation(
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
            cancellation_authorized=True,
            external_outcome_reconciled=True,
        )
        is ExternalOperationStatus.CANCELLED
    )
    with pytest.raises(TransitionError):
        cancel_external_operation(
            ExternalOperationStatus.SUCCEEDED, cancellation_authorized=True
        )


def test_unknown_external_outcome_must_be_reconciled_before_retry() -> None:
    with pytest.raises(TransitionError):
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
            ExternalAttemptResult(
                ExternalAttemptType.EXECUTE,
                ExternalAttemptOutcome.OUTCOME_UNKNOWN,
            ),
        )


def test_reconciled_not_applied_requires_retry_authorization() -> None:
    result = ExternalAttemptResult(
        ExternalAttemptType.RECONCILE, ExternalAttemptOutcome.RECONCILED_NOT_APPLIED
    )
    assert (
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED, result
        )
        is ExternalOperationStatus.FAILED
    )
    authorized = ExternalAttemptResult(
        ExternalAttemptType.RECONCILE,
        ExternalAttemptOutcome.RECONCILED_NOT_APPLIED,
        retry_authorized=True,
    )
    assert (
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED, authorized
        )
        is ExternalOperationStatus.PENDING
    )


def test_reconciliation_success_completes_operation() -> None:
    result = ExternalAttemptResult(
        ExternalAttemptType.RECONCILE, ExternalAttemptOutcome.RECONCILED_SUCCESS
    )
    assert (
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED, result
        )
        is ExternalOperationStatus.SUCCEEDED
    )


def test_effective_decision_history_is_linear() -> None:
    validate_decision_successor(None, None)
    validate_decision_successor("decision-1", "decision-1")
    with pytest.raises(TransitionError):
        validate_decision_successor("decision-2", "decision-1")


def test_review_creation_and_lifecycle() -> None:
    created = project_review_action(None, ReviewAction.CREATED)
    assert created.status is ReviewStatus.PENDING
    started = project_review_action(created.status, ReviewAction.STARTED)
    assert started.status is ReviewStatus.IN_PROGRESS
    completed = project_review_action(started.status, ReviewAction.COMPLETED)
    assert completed.status is ReviewStatus.COMPLETED


def test_review_reopen_creates_successor_segment() -> None:
    reopened = project_review_action(ReviewStatus.COMPLETED, ReviewAction.REOPENED)
    assert reopened.status is ReviewStatus.PENDING
    assert reopened.successor_required


def test_review_actions_cannot_reopen_nonterminal_tasks() -> None:
    with pytest.raises(TransitionError):
        project_review_action(ReviewStatus.IN_PROGRESS, ReviewAction.REOPENED)
    with pytest.raises(TransitionError):
        project_review_action(ReviewStatus.COMPLETED, ReviewAction.STARTED)


def test_publication_outcome_enum_remains_distinct_from_external_execution() -> None:
    assert PublicationDecisionOutcome.PUBLISH.value == "PUBLISH"
    assert PublicationDecisionOutcome.PUBLISH_WITH_CAVEATS.value == "PUBLISH_WITH_CAVEATS"

def test_resolved_case_can_require_review_after_authorized_successor_decision() -> None:
    assert (
        transition_case(
            EventMatchCaseStatus.RESOLVED,
            EventMatchCaseStatus.PENDING_REVIEW,
            successor_decision_authorized=True,
        )
        is EventMatchCaseStatus.PENDING_REVIEW
    )


def test_resolved_case_cannot_be_closed_without_explicit_transition_policy() -> None:
    assert (
        transition_case(EventMatchCaseStatus.RESOLVED, EventMatchCaseStatus.CLOSED)
        is EventMatchCaseStatus.CLOSED
    )


def test_cancelled_and_closed_cases_are_terminal() -> None:
    with pytest.raises(TransitionError):
        transition_case(EventMatchCaseStatus.CANCELLED, EventMatchCaseStatus.OPEN)
    with pytest.raises(TransitionError):
        transition_case(EventMatchCaseStatus.CLOSED, EventMatchCaseStatus.OPEN)


def test_external_reconciliation_rejects_execute_outcome() -> None:
    with pytest.raises(TransitionError):
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
            ExternalAttemptResult(
                ExternalAttemptType.RECONCILE,
                ExternalAttemptOutcome.OUTCOME_UNKNOWN,
            ),
        )


def test_review_metadata_actions_preserve_active_status() -> None:
    for action in (
        ReviewAction.ASSIGNED,
        ReviewAction.REASSIGNED,
        ReviewAction.PRIORITY_CHANGED,
        ReviewAction.NOTE_ADDED,
        ReviewAction.ESCALATED,
    ):
        assert project_review_action(ReviewStatus.PENDING, action).status is ReviewStatus.PENDING


def test_delivery_success_uses_delivered_terminal_state() -> None:
    result = ExternalAttemptResult(
        ExternalAttemptType.EXECUTE, ExternalAttemptOutcome.CONFIRMED_SUCCESS
    )
    assert (
        external_operation_status_after_attempt(
            ExternalOperationStatus.IN_PROGRESS,
            result,
            success_status=ExternalOperationStatus.DELIVERED,
        )
        is ExternalOperationStatus.DELIVERED
    )


def test_reconciled_delivery_success_uses_delivered_terminal_state() -> None:
    result = ExternalAttemptResult(
        ExternalAttemptType.RECONCILE, ExternalAttemptOutcome.RECONCILED_SUCCESS
    )
    assert (
        external_operation_status_after_attempt(
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
            result,
            success_status=ExternalOperationStatus.DELIVERED,
        )
        is ExternalOperationStatus.DELIVERED
    )


def test_resolved_case_requires_successor_for_review_reopen() -> None:
    with pytest.raises(TransitionError):
        transition_case(
            EventMatchCaseStatus.RESOLVED,
            EventMatchCaseStatus.PENDING_REVIEW,
        )

def test_delivery_outcome_is_not_a_processing_step_status() -> None:
    assert "DELIVERED" not in {status.value for status in ProcessingStepStatus}
    assert ExternalOperationStatus.DELIVERED.value == "DELIVERED"

def test_active_run_cancellation_requires_reconciled_external_outcomes() -> None:
    with pytest.raises(TransitionError):
        transition_run(ProcessingRunStatus.RUNNING, ProcessingRunStatus.CANCELLED)
    assert (
        transition_run(
            ProcessingRunStatus.RUNNING,
            ProcessingRunStatus.CANCELLED,
            external_outcomes_reconciled=True,
        )
        is ProcessingRunStatus.CANCELLED
    )
    with pytest.raises(TransitionError):
        transition_run(
            ProcessingRunStatus.PARTIALLY_COMPLETED,
            ProcessingRunStatus.CANCELLED,
        )


def test_running_step_cancellation_requires_reconciled_external_outcome() -> None:
    with pytest.raises(TransitionError):
        transition_step(ProcessingStepStatus.RUNNING, ProcessingStepStatus.CANCELLED)
    assert (
        transition_step(
            ProcessingStepStatus.RUNNING,
            ProcessingStepStatus.CANCELLED,
            external_outcome_reconciled=True,
        )
        is ProcessingStepStatus.CANCELLED
    )
