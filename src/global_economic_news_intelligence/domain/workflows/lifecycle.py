"""Pure, deterministic lifecycle rules for the first GENI implementation slice.

These functions deliberately contain no persistence, I/O, clock, or provider logic.
Callers must persist transitions atomically with their associated audit records.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final, TypeVar


class TransitionError(ValueError):
    """Raised when a requested lifecycle transition violates domain policy."""


class ProcessingRunStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProcessingStepStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class EventMatchCaseStatus(StrEnum):
    OPEN = "OPEN"
    PENDING_REVIEW = "PENDING_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class EventMatchOutcome(StrEnum):
    MATCH = "MATCH"
    NEW_EVENT_CANDIDATE = "NEW_EVENT_CANDIDATE"
    NO_MATCH = "NO_MATCH"
    AMBIGUOUS = "AMBIGUOUS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class EventMatchCandidateStatus(StrEnum):
    GENERATED = "GENERATED"
    EVALUATED = "EVALUATED"
    INELIGIBLE = "INELIGIBLE"


class PublicationDecisionOutcome(StrEnum):
    PUBLISH = "PUBLISH"
    PUBLISH_WITH_CAVEATS = "PUBLISH_WITH_CAVEATS"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    REJECT = "REJECT"


class ExternalOperationStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


class ExternalAttemptType(StrEnum):
    EXECUTE = "EXECUTE"
    RECONCILE = "RECONCILE"


class ExternalAttemptOutcome(StrEnum):
    CONFIRMED_SUCCESS = "CONFIRMED_SUCCESS"
    CONFIRMED_FAILURE = "CONFIRMED_FAILURE"
    OUTCOME_UNKNOWN = "OUTCOME_UNKNOWN"
    RECONCILED_SUCCESS = "RECONCILED_SUCCESS"
    RECONCILED_NOT_APPLIED = "RECONCILED_NOT_APPLIED"


class ReviewStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ReviewAction(StrEnum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    REASSIGNED = "REASSIGNED"
    PRIORITY_CHANGED = "PRIORITY_CHANGED"
    STARTED = "STARTED"
    NOTE_ADDED = "NOTE_ADDED"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REOPENED = "REOPENED"


RUN_TRANSITIONS: Final[dict[ProcessingRunStatus, frozenset[ProcessingRunStatus]]] = {
    ProcessingRunStatus.PENDING: frozenset(
        {ProcessingRunStatus.RUNNING, ProcessingRunStatus.CANCELLED}
    ),
    ProcessingRunStatus.RUNNING: frozenset(
        {
            ProcessingRunStatus.PARTIALLY_COMPLETED,
            ProcessingRunStatus.COMPLETED,
            ProcessingRunStatus.FAILED,
            ProcessingRunStatus.CANCELLED,
        }
    ),
    ProcessingRunStatus.PARTIALLY_COMPLETED: frozenset(
        {ProcessingRunStatus.RUNNING, ProcessingRunStatus.CANCELLED}
    ),
    ProcessingRunStatus.COMPLETED: frozenset(),
    ProcessingRunStatus.FAILED: frozenset(),
    ProcessingRunStatus.CANCELLED: frozenset(),
}

STEP_TRANSITIONS: Final[dict[ProcessingStepStatus, frozenset[ProcessingStepStatus]]] = {
    ProcessingStepStatus.PENDING: frozenset(
        {
            ProcessingStepStatus.READY,
            ProcessingStepStatus.BLOCKED,
            ProcessingStepStatus.SKIPPED,
            ProcessingStepStatus.CANCELLED,
        }
    ),
    ProcessingStepStatus.READY: frozenset(
        {
            ProcessingStepStatus.RUNNING,
            ProcessingStepStatus.BLOCKED,
            ProcessingStepStatus.SKIPPED,
            ProcessingStepStatus.CANCELLED,
        }
    ),
    ProcessingStepStatus.RUNNING: frozenset(
        {
            ProcessingStepStatus.SUCCEEDED,
            ProcessingStepStatus.FAILED,
            ProcessingStepStatus.CANCELLED,
        }
    ),
    ProcessingStepStatus.FAILED: frozenset({ProcessingStepStatus.READY}),
    ProcessingStepStatus.BLOCKED: frozenset({ProcessingStepStatus.READY}),
    ProcessingStepStatus.SUCCEEDED: frozenset(),
    ProcessingStepStatus.SKIPPED: frozenset(),
    ProcessingStepStatus.CANCELLED: frozenset(),
}

CASE_TRANSITIONS: Final[dict[EventMatchCaseStatus, frozenset[EventMatchCaseStatus]]] = {
    EventMatchCaseStatus.OPEN: frozenset(
        {
            EventMatchCaseStatus.PENDING_REVIEW,
            EventMatchCaseStatus.RESOLVED,
            EventMatchCaseStatus.CLOSED,
            EventMatchCaseStatus.CANCELLED,
        }
    ),
    EventMatchCaseStatus.PENDING_REVIEW: frozenset(
        {
            EventMatchCaseStatus.OPEN,
            EventMatchCaseStatus.RESOLVED,
            EventMatchCaseStatus.CANCELLED,
        }
    ),
    EventMatchCaseStatus.RESOLVED: frozenset(
        {
            EventMatchCaseStatus.OPEN,
            EventMatchCaseStatus.PENDING_REVIEW,
            EventMatchCaseStatus.CLOSED,
        }
    ),
    EventMatchCaseStatus.CLOSED: frozenset(),
    EventMatchCaseStatus.CANCELLED: frozenset(),
}

CANDIDATE_TRANSITIONS: Final[
    dict[EventMatchCandidateStatus, frozenset[EventMatchCandidateStatus]]
] = {
    EventMatchCandidateStatus.GENERATED: frozenset(
        {EventMatchCandidateStatus.EVALUATED, EventMatchCandidateStatus.INELIGIBLE}
    ),
    EventMatchCandidateStatus.EVALUATED: frozenset(),
    EventMatchCandidateStatus.INELIGIBLE: frozenset(),
}

EXTERNAL_OPERATION_TRANSITIONS: Final[
    dict[ExternalOperationStatus, frozenset[ExternalOperationStatus]]
] = {
    ExternalOperationStatus.PENDING: frozenset(
        {ExternalOperationStatus.IN_PROGRESS, ExternalOperationStatus.CANCELLED}
    ),
    ExternalOperationStatus.IN_PROGRESS: frozenset(
        {
            ExternalOperationStatus.SUCCEEDED,
            ExternalOperationStatus.FAILED,
            ExternalOperationStatus.CANCELLED,
            ExternalOperationStatus.RECONCILIATION_REQUIRED,
        }
    ),
    ExternalOperationStatus.RECONCILIATION_REQUIRED: frozenset(
        {
            ExternalOperationStatus.SUCCEEDED,
            ExternalOperationStatus.PENDING,
            ExternalOperationStatus.FAILED,
        }
    ),
    ExternalOperationStatus.FAILED: frozenset(),
    ExternalOperationStatus.SUCCEEDED: frozenset(),
    ExternalOperationStatus.CANCELLED: frozenset(),
}

TStatus = TypeVar("TStatus", bound=StrEnum)


def _transition(
    current: TStatus,
    target: TStatus,
    transitions: dict[TStatus, frozenset[TStatus]],
    *,
    context: str,
) -> TStatus:
    """Validate a transition against a closed transition map."""
    if target not in transitions[current]:
        raise TransitionError(f"Invalid {context} transition: {current} -> {target}")
    return target


def transition_run(
    current: ProcessingRunStatus,
    target: ProcessingRunStatus,
) -> ProcessingRunStatus:
    return _transition(current, target, RUN_TRANSITIONS, context="ProcessingRun")


def transition_step(
    current: ProcessingStepStatus,
    target: ProcessingStepStatus,
    *,
    retry_authorized: bool = False,
    dependencies_satisfied: bool = False,
) -> ProcessingStepStatus:
    _transition(current, target, STEP_TRANSITIONS, context="ProcessingStep")
    if current is ProcessingStepStatus.FAILED and target is ProcessingStepStatus.READY:
        if not retry_authorized:
            raise TransitionError("A failed step requires an explicit retry authorization.")
    if current is ProcessingStepStatus.BLOCKED and target is ProcessingStepStatus.READY:
        if not dependencies_satisfied:
            raise TransitionError("A blocked step requires all dependencies to be satisfied.")
    return target


def aggregate_run_status(
    step_statuses: tuple[ProcessingStepStatus, ...],
) -> ProcessingRunStatus:
    """Derive a run projection from the complete, authoritative step set."""
    if not step_statuses:
        return ProcessingRunStatus.PENDING

    active = {\n        ProcessingStepStatus.PENDING,\n        ProcessingStepStatus.READY,\n        ProcessingStepStatus.RUNNING,\n    }
    if any(status in active for status in step_statuses):
        return ProcessingRunStatus.RUNNING

    successes = sum(
        status in {ProcessingStepStatus.SUCCEEDED, ProcessingStepStatus.SKIPPED}
        for status in step_statuses
    )
    failures = sum(
        status in {ProcessingStepStatus.FAILED, ProcessingStepStatus.BLOCKED}
        for status in step_statuses
    )
    cancellations = sum(status is ProcessingStepStatus.CANCELLED for status in step_statuses)

    if failures and successes:
        return ProcessingRunStatus.PARTIALLY_COMPLETED
    if failures:
        return ProcessingRunStatus.FAILED
    if cancellations and successes:
        return ProcessingRunStatus.PARTIALLY_COMPLETED
    if cancellations:
        return ProcessingRunStatus.CANCELLED
    return ProcessingRunStatus.COMPLETED


def transition_case(
    current: EventMatchCaseStatus,
    target: EventMatchCaseStatus,
    *,
    successor_decision_authorized: bool = False,
) -> EventMatchCaseStatus:
    _transition(current, target, CASE_TRANSITIONS, context="EventMatchCase")
    if current is EventMatchCaseStatus.RESOLVED and target is EventMatchCaseStatus.OPEN:
        if not successor_decision_authorized:
            raise TransitionError(
                "Reopening a resolved case requires an authorized successor decision."
            )
    return target


def case_status_for_decision(outcome: EventMatchOutcome) -> EventMatchCaseStatus:
    """Map an effective decision outcome to the case projection."""
    if outcome in {EventMatchOutcome.MATCH, EventMatchOutcome.NO_MATCH}:
        return EventMatchCaseStatus.RESOLVED
    if outcome is EventMatchOutcome.REVIEW_REQUIRED:
        return EventMatchCaseStatus.PENDING_REVIEW
    # A proposed new event must be created and matched in a successor decision;
    # ambiguity remains open for additional evidence or a later decision.
    return EventMatchCaseStatus.OPEN


def transition_candidate(
    current: EventMatchCandidateStatus,
    target: EventMatchCandidateStatus,
) -> EventMatchCandidateStatus:
    return _transition(current, target, CANDIDATE_TRANSITIONS, context="EventMatchCandidate")


def validate_decision_successor(
    current_effective_decision_id: str | None,
    supersedes_decision_id: str | None,
) -> None:
    """Enforce a single linear decision history for one aggregate."""
    if current_effective_decision_id != supersedes_decision_id:
        raise TransitionError(
            "A decision must supersede the current effective decision; "
            "concurrent branches are not permitted."
        )


@dataclass(frozen=True, slots=True)
class ExternalAttemptResult:
    attempt_type: ExternalAttemptType
    outcome: ExternalAttemptOutcome
    retry_authorized: bool = False


def external_operation_status_after_attempt(
    current: ExternalOperationStatus,
    result: ExternalAttemptResult,
) -> ExternalOperationStatus:
    """Map immutable attempt evidence to the operation's current-state projection."""
    if result.attempt_type is ExternalAttemptType.EXECUTE:
        if current is not ExternalOperationStatus.IN_PROGRESS:
            raise TransitionError("EXECUTE attempts require an IN_PROGRESS operation.")
        mapping = {
            ExternalAttemptOutcome.CONFIRMED_SUCCESS: ExternalOperationStatus.SUCCEEDED,
            ExternalAttemptOutcome.CONFIRMED_FAILURE: ExternalOperationStatus.FAILED,
            ExternalAttemptOutcome.OUTCOME_UNKNOWN: ExternalOperationStatus.RECONCILIATION_REQUIRED,
        }
        if result.outcome not in mapping:
            raise TransitionError("EXECUTE cannot use a reconciliation-only outcome.")
        return _transition(
            current,
            mapping[result.outcome],
            EXTERNAL_OPERATION_TRANSITIONS,
            context="ExternalOperation",
        )

    if current is not ExternalOperationStatus.RECONCILIATION_REQUIRED:
        raise TransitionError("RECONCILE attempts require RECONCILIATION_REQUIRED state.")
    if result.outcome is ExternalAttemptOutcome.RECONCILED_SUCCESS:
        return ExternalOperationStatus.SUCCEEDED
    if result.outcome is ExternalAttemptOutcome.RECONCILED_NOT_APPLIED:
        if result.retry_authorized:
            return ExternalOperationStatus.PENDING
        return ExternalOperationStatus.FAILED
    raise TransitionError("RECONCILE requires a reconciliation outcome.")


@dataclass(frozen=True, slots=True)
class ReviewProjection:
    status: ReviewStatus
    successor_required: bool = False


def project_review_action(
    current: ReviewStatus | None,
    action: ReviewAction,
) -> ReviewProjection:
    """Project one append-only review action; REOPENED creates a new task segment."""
    if current is None:
        if action is not ReviewAction.CREATED:
            raise TransitionError("The first review action must be CREATED.")
        return ReviewProjection(ReviewStatus.PENDING)

    if action is ReviewAction.CREATED:
        raise TransitionError("CREATED is valid only for a new review record.")
    if action is ReviewAction.REOPENED:
        if current not in {ReviewStatus.COMPLETED, ReviewStatus.CANCELLED}:
            raise TransitionError("Only a terminal review can be reopened.")
        return ReviewProjection(ReviewStatus.PENDING, successor_required=True)
    if action is ReviewAction.STARTED:
        if current is not ReviewStatus.PENDING:
            raise TransitionError("STARTED requires a PENDING review.")
        return ReviewProjection(ReviewStatus.IN_PROGRESS)
    if action is ReviewAction.COMPLETED:
        if current is not ReviewStatus.IN_PROGRESS:
            raise TransitionError("COMPLETED requires an IN_PROGRESS review.")
        return ReviewProjection(ReviewStatus.COMPLETED)
    if action is ReviewAction.CANCELLED:
        if current not in {ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS}:
            raise TransitionError("CANCELLED requires an active review.")
        return ReviewProjection(ReviewStatus.CANCELLED)

    if current not in {ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS}:
        raise TransitionError("Non-terminal review actions require an active review.")
    return ReviewProjection(current)
