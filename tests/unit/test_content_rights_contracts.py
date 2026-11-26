from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from global_economic_news_intelligence.domain.content_rights_contracts import (
    ContentPersistenceOutcome,
    ContentRetentionMode,
    ContentRetentionPolicy,
    RightsAssessment,
    RightsAssessmentStatus,
    RightsOperation,
    decide_content_persistence,
    is_rights_assessment_effective,
)


NOW = datetime(2026, 11, 26, 12, 0, tzinfo=UTC)
SCOPE = "a" * 64


def assessment(
    *,
    status: RightsAssessmentStatus = RightsAssessmentStatus.ALLOWED,
    operation: RightsOperation = RightsOperation.PERSISTENT_STORAGE,
    source_id: str = "source-1",
    fingerprint: str = SCOPE,
    assessed_at: datetime = NOW - timedelta(minutes=1),
    effective_from: datetime = NOW - timedelta(minutes=1),
    expires_at: datetime | None = NOW + timedelta(hours=1),
    policy_version: str = "rights-policy-v1",
) -> RightsAssessment:
    return RightsAssessment(
        assessment_reference="rights-assessment-1",
        source_id=source_id,
        content_scope_fingerprint=fingerprint,
        operation=operation,
        status=status,
        policy_version=policy_version,
        rights_profile_reference="rights-profile-1",
        assessed_at=assessed_at,
        effective_from=effective_from,
        expires_at=expires_at,
    )


def policy(
    mode: ContentRetentionMode = ContentRetentionMode.LIMITED_RETENTION,
) -> ContentRetentionPolicy:
    return ContentRetentionPolicy(mode=mode, policy_version="rights-policy-v1")


def test_exact_current_allowed_persistent_storage_assessment_is_effective() -> None:
    item = assessment()
    assert is_rights_assessment_effective(
        item,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=NOW,
    )


@pytest.mark.parametrize(
    "status",
    [
        RightsAssessmentStatus.DENIED,
        RightsAssessmentStatus.UNKNOWN,
        RightsAssessmentStatus.EXPIRED,
        RightsAssessmentStatus.REVOKED,
        RightsAssessmentStatus.REQUIRES_REVIEW,
    ],
)
def test_non_allowed_statuses_fail_closed(status: RightsAssessmentStatus) -> None:
    assert not is_rights_assessment_effective(
        assessment(status=status),
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=NOW,
    )


@pytest.mark.parametrize(
    ("source_id", "fingerprint", "operation"),
    [
        ("another-source", SCOPE, RightsOperation.PERSISTENT_STORAGE),
        ("source-1", "b" * 64, RightsOperation.PERSISTENT_STORAGE),
        ("source-1", SCOPE, RightsOperation.INTERNAL_ANALYSIS),
    ],
)
def test_assessment_cannot_be_reused_for_another_scope_or_operation(
    source_id: str,
    fingerprint: str,
    operation: RightsOperation,
) -> None:
    assert not is_rights_assessment_effective(
        assessment(),
        source_id=source_id,
        content_scope_fingerprint=fingerprint,
        operation=operation,
        at=NOW,
    )


def test_assessment_is_not_effective_before_recorded_or_effective_time() -> None:
    item = assessment(assessed_at=NOW + timedelta(minutes=1))
    assert not is_rights_assessment_effective(
        item,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=NOW,
    )

    item = assessment(effective_from=NOW + timedelta(minutes=1))
    assert not is_rights_assessment_effective(
        item,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=NOW,
    )


def test_expiration_is_an_exclusive_boundary() -> None:
    item = assessment(expires_at=NOW)
    assert not is_rights_assessment_effective(
        item,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=NOW,
    )


def test_missing_or_mismatched_assessment_keeps_metadata_only() -> None:
    assert decide_content_persistence(
        policy=policy(),
        assessment=None,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        at=NOW,
    ) is ContentPersistenceOutcome.METADATA_ONLY

    assert decide_content_persistence(
        policy=policy(),
        assessment=assessment(status=RightsAssessmentStatus.UNKNOWN),
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        at=NOW,
    ) is ContentPersistenceOutcome.METADATA_ONLY


@pytest.mark.parametrize(
    "mode",
    [
        ContentRetentionMode.NO_PERSISTENT_CONTENT,
        ContentRetentionMode.TEMPORARY_PROCESSING_ONLY,
    ],
)
def test_non_persistent_retention_modes_never_persist(
    mode: ContentRetentionMode,
) -> None:
    assert decide_content_persistence(
        policy=policy(mode),
        assessment=assessment(),
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        at=NOW,
    ) is ContentPersistenceOutcome.METADATA_ONLY


@pytest.mark.parametrize(
    "mode",
    [
        ContentRetentionMode.LIMITED_RETENTION,
        ContentRetentionMode.LICENSED_PERSISTENT_STORAGE,
        ContentRetentionMode.UNRESTRICTED_BY_DOCUMENTED_POLICY,
    ],
)
def test_persistent_modes_require_exact_current_persistent_storage_permission(
    mode: ContentRetentionMode,
) -> None:
    assert decide_content_persistence(
        policy=policy(mode),
        assessment=assessment(),
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        at=NOW,
    ) is ContentPersistenceOutcome.PERSIST_CONTENT


def test_policy_version_mismatch_fails_closed() -> None:
    item = assessment(policy_version="older-policy")
    assert decide_content_persistence(
        policy=policy(),
        assessment=item,
        source_id="source-1",
        content_scope_fingerprint=SCOPE,
        at=NOW,
    ) is ContentPersistenceOutcome.METADATA_ONLY


def test_assessment_rejects_invalid_scope_fingerprint() -> None:
    with pytest.raises(ValueError, match="SHA-256"):
        assessment(fingerprint="not-a-hash")


def test_assessment_rejects_naive_timestamps_and_invalid_expiry() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        assessment(assessed_at=datetime(2026, 11, 26, 12, 0))

    with pytest.raises(ValueError, match="later than effective_from"):
        assessment(
            effective_from=NOW,
            expires_at=NOW,
        )


def test_assessment_rejects_untyped_operation_and_status() -> None:
    with pytest.raises(TypeError, match="RightsOperation"):
        RightsAssessment(
            assessment_reference="assessment",
            source_id="source-1",
            content_scope_fingerprint=SCOPE,
            operation="PERSISTENT_STORAGE",  # type: ignore[arg-type]
            status=RightsAssessmentStatus.ALLOWED,
            policy_version="rights-policy-v1",
            rights_profile_reference="profile-1",
            assessed_at=NOW,
            effective_from=NOW,
        )
