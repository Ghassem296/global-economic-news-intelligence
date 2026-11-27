"""Typed payload contracts for deterministic event-matching workflows.

Policy vocabularies, score calibration, authorization decisions, and persistence
remain outside these transport-neutral domain payloads.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from types import MappingProxyType

from global_economic_news_intelligence.domain.validation import (
    require_optional_finite_decimal,
    require_text,
)
from global_economic_news_intelligence.domain.workflows.lifecycle import EventMatchOutcome


def _freeze_json(value: object, field_name: str) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_name} cannot contain a non-finite number.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, object] = {}
        for key, item in value.items():
            require_text(key, f"{field_name} key")
            frozen[key] = _freeze_json(item, field_name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item, field_name) for item in value)
    raise TypeError(f"{field_name} must contain JSON-compatible values.")


def _metadata(value: Mapping[str, object] | None) -> Mapping[str, object] | None:
    if value is None:
        return None
    frozen = _freeze_json(value, "metadata")
    if not isinstance(frozen, Mapping):
        raise TypeError("metadata must be a mapping.")
    return frozen


@dataclass(frozen=True, slots=True)
class CreateEventMatchCase:
    """Create one independently scoped development case for an exact revision."""

    article_revision_id: str
    development_key: str
    scope_description: str
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in ("article_revision_id", "development_key", "scope_description"):
            require_text(getattr(self, field_name), field_name)
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
            require_text(getattr(self, field_name), field_name)
        for field_name in (
            "lexical_similarity",
            "semantic_similarity",
            "entity_overlap_score",
            "temporal_compatibility_score",
            "geographic_compatibility_score",
            "overall_score",
        ):
            require_optional_finite_decimal(getattr(self, field_name), field_name)


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
            require_text(getattr(self, field_name), field_name)
        if not isinstance(self.outcome, EventMatchOutcome):
            raise ValueError("outcome must be an EventMatchOutcome.")
        if self.outcome is EventMatchOutcome.MATCH:
            require_text(self.selected_candidate_id, "selected_candidate_id")
            if self.proposed_event_reference is not None:
                raise ValueError("MATCH cannot include proposed_event_reference.")
        elif self.outcome is EventMatchOutcome.NEW_EVENT_CANDIDATE:
            require_text(self.proposed_event_reference, "proposed_event_reference")
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
            require_text(self.supersedes_decision_id, "supersedes_decision_id")
        require_optional_finite_decimal(self.decision_confidence, "decision_confidence")


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
            require_text(getattr(self, field_name), field_name)
        require_optional_finite_decimal(self.association_confidence, "association_confidence")


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
            require_text(getattr(self, field_name), field_name)
