"""Typed, immutable contracts for pairwise article deduplication.

The contracts intentionally preserve policy-governed vocabularies and numeric
semantics as opaque values. They do not implement matching, clustering, or
persistence.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType

type JsonScalar = str | int | float | bool | None
type FrozenJson = JsonScalar | tuple[FrozenJson, ...] | Mapping[str, FrozenJson]


class DuplicateDecisionOutcome(StrEnum):
    """Closed outcome vocabulary from GENI-IMPL-015 §10.16.2."""

    CONFIRMED_DUPLICATE = "CONFIRMED_DUPLICATE"
    NOT_DUPLICATE = "NOT_DUPLICATE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


def _required_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def _optional_decimal(value: object, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field_name} must be a finite Decimal or None.")


def _trusted_instant(value: object, field_name: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")


def _freeze_json(value: object, field_name: str) -> FrozenJson:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_name} cannot contain a non-finite number.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJson] = {}
        for key, item in value.items():
            _required_text(key, f"{field_name} key")
            frozen[key] = _freeze_json(item, field_name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item, field_name) for item in value)
    raise TypeError(f"{field_name} must contain JSON-compatible values.")


def _freeze_metadata(value: Mapping[str, object] | None) -> Mapping[str, FrozenJson] | None:
    if value is None:
        return None
    frozen = _freeze_json(value, "metadata")
    if not isinstance(frozen, Mapping):
        raise TypeError("metadata must be a mapping.")
    return frozen


@dataclass(frozen=True, slots=True)
class AppendDuplicateCandidate:
    """Immutable pairwise candidate-evaluation payload.

    Canonical pair ordering, matching-method vocabulary, score scale, and
    fingerprint serialization remain policy decisions and are not guessed here.
    """

    article_id_a: str
    article_revision_id_a: str
    article_id_b: str
    article_revision_id_b: str
    similarity_score: Decimal | None
    matching_method: str
    matching_policy_version: str
    input_fingerprint: str
    evaluated_at: datetime
    actor_reference: str
    authorization_reference: str
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "article_id_a",
            "article_revision_id_a",
            "article_id_b",
            "article_revision_id_b",
            "matching_method",
            "matching_policy_version",
            "input_fingerprint",
            "actor_reference",
            "authorization_reference",
        ):
            _required_text(getattr(self, field_name), field_name)
        if self.article_revision_id_a == self.article_revision_id_b:
            raise ValueError("A revision cannot be compared with itself.")
        _optional_decimal(self.similarity_score, "similarity_score")
        _trusted_instant(self.evaluated_at, "evaluated_at")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class AppendDuplicateDecision:
    """Immutable pairwise decision payload with explicit successor lineage."""

    duplicate_candidate_id: str
    outcome: DuplicateDecisionOutcome
    decision_reason: str
    decision_method: str
    decision_policy_version: str
    decision_confidence: Decimal | None
    actor_reference: str
    authorization_reference: str
    decided_at: datetime
    supersedes_decision_id: str | None = None
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "duplicate_candidate_id",
            "decision_reason",
            "decision_method",
            "decision_policy_version",
            "actor_reference",
            "authorization_reference",
        ):
            _required_text(getattr(self, field_name), field_name)
        if not isinstance(self.outcome, DuplicateDecisionOutcome):
            raise ValueError("outcome must be a DuplicateDecisionOutcome.")
        if self.supersedes_decision_id is not None:
            _required_text(self.supersedes_decision_id, "supersedes_decision_id")
        _optional_decimal(self.decision_confidence, "decision_confidence")
        _trusted_instant(self.decided_at, "decided_at")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))
