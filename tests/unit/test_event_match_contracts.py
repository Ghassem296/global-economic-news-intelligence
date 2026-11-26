from __future__ import annotations

from decimal import Decimal

import pytest

from global_economic_news_intelligence.domain.event_match_contracts import (
    ActivateArticleEventLink,
    AppendEventMatchDecision,
    CreateEventMatchCase,
    DeactivateArticleEventLink,
    EvaluateEventMatchCandidate,
    EventMatchOutcome,
)


def evaluation(**overrides: object) -> EvaluateEventMatchCandidate:
    values: dict[str, object] = {
        "case_id": "case-1",
        "candidate_event_id": "event-1",
        "matching_method": "policy-defined",
        "matching_policy_version": "match-v1",
        "candidate_input_fingerprint": "fingerprint-1",
        "lexical_similarity": None,
        "semantic_similarity": None,
        "entity_overlap_score": None,
        "temporal_compatibility_score": None,
        "geographic_compatibility_score": None,
        "overall_score": None,
        "evaluation_reason": "No scoring signal was evaluated.",
    }
    values.update(overrides)
    return EvaluateEventMatchCandidate(**values)  # type: ignore[arg-type]


def match_decision(**overrides: object) -> AppendEventMatchDecision:
    values: dict[str, object] = {
        "case_id": "case-1",
        "outcome": EventMatchOutcome.MATCH,
        "selected_candidate_id": "candidate-1",
        "proposed_event_reference": None,
        "decision_method": "policy-defined",
        "decision_confidence": None,
        "decision_rationale": "The selected candidate satisfies the approved policy.",
        "matching_policy_version": "match-v1",
    }
    values.update(overrides)
    return AppendEventMatchDecision(**values)  # type: ignore[arg-type]


def test_case_requires_exact_revision_and_development_scope() -> None:
    case = CreateEventMatchCase(
        article_revision_id="revision-1",
        development_key="development-1",
        scope_description="Central bank rate decision",
    )
    assert case.article_revision_id == "revision-1"
    with pytest.raises(ValueError, match="development_key"):
        CreateEventMatchCase("revision-1", " ", "Development")


def test_case_metadata_is_copied_and_read_only() -> None:
    source = {"fixture": "synthetic"}
    case = CreateEventMatchCase("revision-1", "dev-1", "Scope", source)
    source["fixture"] = "changed"
    assert case.metadata is not None
    assert case.metadata["fixture"] == "synthetic"
    with pytest.raises(TypeError):
        case.metadata["new"] = "value"  # type: ignore[index]


def test_candidate_evaluation_keeps_unevaluated_scores_null() -> None:
    result = evaluation()
    assert result.semantic_similarity is None
    assert result.overall_score is None


def test_candidate_evaluation_accepts_decimal_scores_without_assuming_scale() -> None:
    result = evaluation(lexical_similarity=Decimal("0.73"))
    assert result.lexical_similarity == Decimal("0.73")


def test_candidate_evaluation_rejects_non_finite_scores() -> None:
    with pytest.raises(ValueError, match="finite Decimal"):
        evaluation(overall_score=Decimal("Infinity"))


def test_match_requires_exactly_one_selected_candidate() -> None:
    assert match_decision().selected_candidate_id == "candidate-1"
    with pytest.raises(ValueError, match="selected_candidate_id"):
        match_decision(selected_candidate_id=None)


def test_new_event_candidate_requires_reference_but_does_not_create_event() -> None:
    decision = match_decision(
        outcome=EventMatchOutcome.NEW_EVENT_CANDIDATE,
        selected_candidate_id=None,
        proposed_event_reference="preassigned-event-1",
    )
    assert decision.proposed_event_reference == "preassigned-event-1"


@pytest.mark.parametrize(
    "outcome",
    (
        EventMatchOutcome.NO_MATCH,
        EventMatchOutcome.AMBIGUOUS,
        EventMatchOutcome.REVIEW_REQUIRED,
    ),
)
def test_non_match_outcomes_cannot_select_candidate_or_propose_event(
    outcome: EventMatchOutcome,
) -> None:
    with pytest.raises(ValueError, match="Non-MATCH outcomes"):
        match_decision(
            outcome=outcome,
            selected_candidate_id="candidate-1",
        )


def test_non_match_outcomes_accept_no_selection() -> None:
    decision = match_decision(
        outcome=EventMatchOutcome.REVIEW_REQUIRED,
        selected_candidate_id=None,
    )
    assert decision.selected_candidate_id is None


def test_link_activation_requires_case_version_and_decision_reference() -> None:
    request = ActivateArticleEventLink(
        "case-1", "decision-1", "v3", "INITIAL_REPORT", None
    )
    assert request.association_confidence is None
    with pytest.raises(ValueError, match="expected_case_version"):
        ActivateArticleEventLink("case-1", "decision-1", " ", "INITIAL_REPORT", None)


def test_link_deactivation_requires_successor_and_link_identity() -> None:
    request = DeactivateArticleEventLink("case-1", "link-1", "decision-2", "v4")
    assert request.successor_decision_id == "decision-2"
    with pytest.raises(ValueError, match="successor_decision_id"):
        DeactivateArticleEventLink("case-1", "link-1", " ", "v4")
