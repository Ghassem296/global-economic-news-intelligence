"""Typed payload contracts for deterministic event-matching workflows.

Policy vocabularies, score calibration, authorization decisions, and persistence
remain outside these transport-neutral domain payloads.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType


class EventMatchOutcome(StrEnum):
    """Closed decision outcomes defined by GENI-IMPL-015."""

    MATCH = "MATCH"
    NEW_EVENT_CANDIDATE = "NEW_EVENT_CANDIDATE"
    NO_MATCH = "NO_MATCH"
    AMBIGUOUS = "AMBIGUOUS"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


def _required_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def _optional_score(value: object, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field_name} must be a finite Decimal or None.")


def _aware_instant(value: object, field_name: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")


def _metadata(value: Mapping[str, object] | None) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise TypeError("metadata must be a mapping.")
    copied = dict(value)
    for key in copied:
        _required_text(key, "metadata key")
    return MappingProxyType(copied)


@dataclass(frozen=True, slots=True)
class CreateEventMatchCase:
    """Create one independently scoped development case for an exact revision."""

    article_revision_id: str
    development_key: str
    scope_description: str
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in ("article_revision_id", "development_key", "scope_description"):
            _required_text(getattr(self, field_name), field_name)
        object.__setattr__(self, "metadata", _metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class EvaluateEventMatchCandidate:
    """Append one immutable candidate evaluation; this is not a match decision."""

    case_id: str
    candidate_event_id: str
    matching_method: str
    matching_policy_version: str
    candidate_input_fingerprint: str
    lexical_similarity: Decimal | None
    semantic_similarity: Decimal | None
    entity_overlap_score: Decimal | None
    temporal_compatibility_score: Decimal | None
    geographic_compatibility_score: Decimal | None
    overall_score: Decimal | None
    evaluation_reason: str

    def __post_init__(self) -> None:
        for field_name in (
            "case_id",
            "candidate_event_id",
            "matching_method",
            "matching_policy_version",
            "candidate_input_fingerprint",
            "evaluation_reason",
        ):
            _required_text(getattr(self, field_name), field_name)
        for field_name in (
            "lexical_similarity",
            "semantic_similarity",
            "entity_overlap_score",
            "temporal_compatibility_score",
            "geographic_compatibility_score",
            "overall_score",
        ):
            _optional_score(getattr(self, field_name), field_name)


@dataclass(frozen=True, slots=True)
class AppendEventMatchDecision:
    """Append a linear, immutable event-match decision for one case."""

    case_id: str
    outcome: EventMatchOutcome
    selected_candidate_id: str | None
    proposed_event_reference: str | None
    decision_method: str
    decision_confidence: Decimal | None
    decision_rationale: str
    matching_policy_version: str
    supersedes_decision_id: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "case_id",
            "decision_method",
            "decision_rationale",
            "matching_policy_version",
        ):
            _required_text(getattr(self, field_name), field_name)
        if not isinstance(self.outcome, EventMatchOutcome):
            raise ValueError("outcome must be an EventMatchOutcome.")
        if self.outcome is EventMatchOutcome.MATCH:
            _required_text(self.selected_candidate_id, "selected_candidate_id")
            if self.proposed_event_reference is not None:
                raise ValueError("MATCH cannot include proposed_event_reference.")
        elif self.outcome is EventMatchOutcome.NEW_EVENT_CANDIDATE:
            _required_text(self.proposed_event_reference, "proposed_event_reference")
            if self.selected_candidate_id is not None:
                raise ValueError("NEW_EVENT_CANDIDATE cannot select a candidate.")
        elif (
            self.selected_candidate_id is not None
            or self.proposed_event_reference is not None
        ):
            raise ValueError(
                "Non-MATCH outcomes cannot select a candidate or propose an Event."
            )
        if self.supersedes_decision_id is not None:
            _required_text(self.supersedes_decision_id, "supersedes_decision_id")
        _optional_score(self.decision_confidence, "decision_confidence")


@dataclass(frozen=True, slots=True)
class ActivateArticleEventLink:
    """Request activation strictly from the effective MATCH decision."""

    case_id: str
    event_match_decision_id: str
    expected_case_version: str
    relationship_type: str
    association_confidence: Decimal | None

    def __post_init__(self) -> None:
        for field_name in (
            "case_id",
            "event_match_decision_id",
            "expected_case_version",
            "relationship_type",
        ):
            _required_text(getattr(self, field_name), field_name)
        _optional_score(self.association_confidence, "association_confidence")


@dataclass(frozen=True, slots=True)
class DeactivateArticleEventLink:
    """Preserve and deactivate one link using its authorized successor decision."""

    case_id: str
    link_id: str
    successor_decision_id: str
    expected_case_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "case_id",
            "link_id",
            "successor_decision_id",
            "expected_case_version",
        ):
            _required_text(getattr(self, field_name), field_name)
