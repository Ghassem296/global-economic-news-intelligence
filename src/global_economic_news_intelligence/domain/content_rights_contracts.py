"""Fail-closed, operation- and content-scope-specific rights policy contracts.

These pure contracts evaluate recorded rights assessments. They do not determine
whether a license is legally sufficient, refresh source profiles, or perform
storage, deletion, or external-processing operations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RightsOperation(StrEnum):
    DISCOVERY = "DISCOVERY"
    METADATA_ACCESS = "METADATA_ACCESS"
    FULL_TEXT_ACCESS = "FULL_TEXT_ACCESS"
    TEMPORARY_PROCESSING = "TEMPORARY_PROCESSING"
    PERSISTENT_STORAGE = "PERSISTENT_STORAGE"
    INTERNAL_ANALYSIS = "INTERNAL_ANALYSIS"
    EXTERNAL_LLM_PROCESSING = "EXTERNAL_LLM_PROCESSING"
    DERIVED_OUTPUT_GENERATION = "DERIVED_OUTPUT_GENERATION"
    TRANSLATION = "TRANSLATION"
    EMBEDDING_GENERATION = "EMBEDDING_GENERATION"
    QUOTATION = "QUOTATION"
    AUDIO_TRANSFORMATION = "AUDIO_TRANSFORMATION"
    VIDEO_TRANSFORMATION = "VIDEO_TRANSFORMATION"
    CUSTOMER_DISTRIBUTION = "CUSTOMER_DISTRIBUTION"
    CONTENT_REPUBLICATION = "CONTENT_REPUBLICATION"


class RightsAssessmentStatus(StrEnum):
    ALLOWED = "ALLOWED"
    DENIED = "DENIED"
    UNKNOWN = "UNKNOWN"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class ContentRetentionMode(StrEnum):
    NO_PERSISTENT_CONTENT = "NO_PERSISTENT_CONTENT"
    TEMPORARY_PROCESSING_ONLY = "TEMPORARY_PROCESSING_ONLY"
    LIMITED_RETENTION = "LIMITED_RETENTION"
    LICENSED_PERSISTENT_STORAGE = "LICENSED_PERSISTENT_STORAGE"
    UNRESTRICTED_BY_DOCUMENTED_POLICY = "UNRESTRICTED_BY_DOCUMENTED_POLICY"


class ContentPersistenceOutcome(StrEnum):
    PERSIST_CONTENT = "PERSIST_CONTENT"
    METADATA_ONLY = "METADATA_ONLY"


@dataclass(frozen=True, slots=True)
class RightsAssessment:
    """Immutable assessment for one operation and one exact content scope."""

    assessment_reference: str
    source_id: str
    content_scope_fingerprint: str
    operation: RightsOperation
    status: RightsAssessmentStatus
    policy_version: str
    rights_profile_reference: str
    assessed_at: datetime
    effective_from: datetime
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "assessment_reference",
            "source_id",
            "policy_version",
            "rights_profile_reference",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")

        if not isinstance(self.operation, RightsOperation):
            raise TypeError("operation must be a RightsOperation.")
        if not isinstance(self.status, RightsAssessmentStatus):
            raise TypeError("status must be a RightsAssessmentStatus.")
        if not isinstance(self.content_scope_fingerprint, str) or not _SHA256_RE.fullmatch(
            self.content_scope_fingerprint
        ):
            raise ValueError(
                "content_scope_fingerprint must be a lowercase SHA-256 hex digest."
            )

        for field_name in ("assessed_at", "effective_from"):
            value = getattr(self, field_name)
            if not isinstance(value, datetime) or value.utcoffset() is None:
                raise ValueError(f"{field_name} must be a timezone-aware datetime.")

        if self.expires_at is not None:
            if not isinstance(self.expires_at, datetime) or self.expires_at.utcoffset() is None:
                raise ValueError("expires_at must be a timezone-aware datetime.")
            if self.expires_at <= self.effective_from:
                raise ValueError("expires_at must be later than effective_from.")


@dataclass(frozen=True, slots=True)
class ContentRetentionPolicy:
    """Source/content-specific retention mode; no universal duration is assumed."""

    mode: ContentRetentionMode
    policy_version: str

    def __post_init__(self) -> None:
        if not isinstance(self.mode, ContentRetentionMode):
            raise TypeError("mode must be a ContentRetentionMode.")
        if not isinstance(self.policy_version, str) or not self.policy_version.strip():
            raise ValueError("policy_version must be a non-empty string.")


def is_rights_assessment_effective(
    assessment: RightsAssessment,
    *,
    source_id: str,
    content_scope_fingerprint: str,
    operation: RightsOperation,
    at: datetime,
) -> bool:
    """Return true only for an ALLOWED assessment matching the exact request scope."""

    if not isinstance(assessment, RightsAssessment):
        raise TypeError("assessment must be a RightsAssessment.")
    if not isinstance(operation, RightsOperation):
        raise TypeError("operation must be a RightsOperation.")
    if not isinstance(at, datetime) or at.utcoffset() is None:
        raise ValueError("at must be a timezone-aware datetime.")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("source_id must be a non-empty string.")
    if not isinstance(content_scope_fingerprint, str) or not _SHA256_RE.fullmatch(
        content_scope_fingerprint
    ):
        raise ValueError("content_scope_fingerprint must be a lowercase SHA-256 hex digest.")

    if (
        assessment.status is not RightsAssessmentStatus.ALLOWED
        or assessment.source_id != source_id
        or assessment.content_scope_fingerprint != content_scope_fingerprint
        or assessment.operation is not operation
        or at < assessment.effective_from
        or (assessment.expires_at is not None and at >= assessment.expires_at)
    ):
        return False
    return True


def decide_content_persistence(
    *,
    policy: ContentRetentionPolicy,
    assessment: RightsAssessment | None,
    source_id: str,
    content_scope_fingerprint: str,
    at: datetime,
) -> ContentPersistenceOutcome:
    """Choose persistence or metadata-only; missing/invalid rights always fail closed."""

    if not isinstance(policy, ContentRetentionPolicy):
        raise TypeError("policy must be a ContentRetentionPolicy.")
    if not isinstance(at, datetime) or at.utcoffset() is None:
        raise ValueError("at must be a timezone-aware datetime.")

    if policy.mode is ContentRetentionMode.NO_PERSISTENT_CONTENT:
        return ContentPersistenceOutcome.METADATA_ONLY

    if assessment is None:
        return ContentPersistenceOutcome.METADATA_ONLY

    allowed = is_rights_assessment_effective(
        assessment,
        source_id=source_id,
        content_scope_fingerprint=content_scope_fingerprint,
        operation=RightsOperation.PERSISTENT_STORAGE,
        at=at,
    )
    if not allowed:
        return ContentPersistenceOutcome.METADATA_ONLY

    if policy.mode in {
        ContentRetentionMode.TEMPORARY_PROCESSING_ONLY,
        ContentRetentionMode.LIMITED_RETENTION,
        ContentRetentionMode.LICENSED_PERSISTENT_STORAGE,
        ContentRetentionMode.UNRESTRICTED_BY_DOCUMENTED_POLICY,
    }:
        return ContentPersistenceOutcome.PERSIST_CONTENT

    return ContentPersistenceOutcome.METADATA_ONLY
