from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from global_economic_news_intelligence.domain.duplicate_contracts import (
    AppendDuplicateCandidate,
    AppendDuplicateDecision,
    DuplicateDecisionOutcome,
)

NOW = datetime(2026, 11, 26, 10, 0, tzinfo=UTC)


def candidate(**overrides: object) -> AppendDuplicateCandidate:
    values: dict[str, object] = {
        "article_id_a": "article-a",
        "article_revision_id_a": "revision-a",
        "article_id_b": "article-b",
        "article_revision_id_b": "revision-b",
        "similarity_score": None,
        "matching_method": "policy-defined-method",
        "matching_policy_version": "policy-v1",
        "input_fingerprint": "fingerprint-1",
        "evaluated_at": NOW,
        "actor_reference": "actor-1",
        "authorization_reference": "authorization-1",
    }
    values.update(overrides)
    return AppendDuplicateCandidate(**values)  # type: ignore[arg-type]


def decision(**overrides: object) -> AppendDuplicateDecision:
    values: dict[str, object] = {
        "duplicate_candidate_id": "candidate-1",
        "outcome": DuplicateDecisionOutcome.REVIEW_REQUIRED,
        "decision_reason": "Insufficient independent evidence.",
        "decision_method": "policy-defined-method",
        "decision_policy_version": "policy-v1",
        "decision_confidence": None,
        "actor_reference": "actor-1",
        "authorization_reference": "authorization-1",
        "decided_at": NOW,
    }
    values.update(overrides)
    return AppendDuplicateDecision(**values)  # type: ignore[arg-type]


def test_candidate_preserves_unknown_similarity_as_none() -> None:
    assert candidate().similarity_score is None


def test_candidate_rejects_same_revision_on_both_sides() -> None:
    with pytest.raises(ValueError, match="cannot be compared with itself"):
        candidate(article_revision_id_b="revision-a")


def test_candidate_requires_non_empty_references() -> None:
    with pytest.raises(ValueError, match="actor_reference"):
        candidate(actor_reference=" ")


def test_candidate_requires_timezone_aware_evaluation_time() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        candidate(evaluated_at=datetime(2026, 11, 26, 10, 0))


def test_candidate_accepts_finite_decimal_score_without_inventing_scale() -> None:
    assert candidate(similarity_score=Decimal("0.82")).similarity_score == Decimal("0.82")


def test_candidate_rejects_non_finite_score() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        candidate(similarity_score=Decimal("NaN"))


def test_candidate_metadata_is_deeply_immutable() -> None:
    nested = {"labels": ["wire", "rates"]}
    item = candidate(metadata=nested)
    nested["labels"].append("changed")
    assert item.metadata is not None
    assert item.metadata["labels"] == ("wire", "rates")
    with pytest.raises(TypeError):
        item.metadata["new"] = "value"  # type: ignore[index]


def test_decision_uses_closed_outcome_vocabulary() -> None:
    assert decision(outcome=DuplicateDecisionOutcome.CONFIRMED_DUPLICATE).outcome is (
        DuplicateDecisionOutcome.CONFIRMED_DUPLICATE
    )
    with pytest.raises(ValueError, match="DuplicateDecisionOutcome"):
        decision(outcome="MAYBE")  # type: ignore[arg-type]


def test_decision_requires_valid_successor_reference_when_supplied() -> None:
    with pytest.raises(ValueError, match="supersedes_decision_id"):
        decision(supersedes_decision_id=" ")


def test_decision_keeps_unknown_confidence_null() -> None:
    assert decision().decision_confidence is None


def test_decision_requires_trusted_time_and_authorization() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        decision(decided_at=datetime(2026, 11, 26, 10, 0))
    with pytest.raises(ValueError, match="authorization_reference"):
        decision(authorization_reference="")
