"""PoC-only, fail-closed backup retention planning.

This module never deletes backups or defines GENI production retention periods.
A production policy must be explicitly approved and enforced by a separate,
audited operational workflow.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


def _require_aware(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime")


@dataclass(frozen=True, slots=True)
class BackupArtifact:
    artifact_id: str
    created_at: datetime
    verified: bool
    legal_hold: bool = False
    immutable_until: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.artifact_id, str) or not self.artifact_id.strip():
            raise ValueError("artifact_id must be a non-empty string")
        _require_aware(self.created_at, "created_at")
        if not isinstance(self.verified, bool):
            raise ValueError("verified must be a boolean")
        if not isinstance(self.legal_hold, bool):
            raise ValueError("legal_hold must be a boolean")
        if self.immutable_until is not None:
            _require_aware(self.immutable_until, "immutable_until")
            if self.immutable_until < self.created_at:
                raise ValueError("immutable_until cannot precede created_at")


@dataclass(frozen=True, slots=True)
class BackupRetentionPolicy:
    retention_period: timedelta
    minimum_successful_backups: int

    def __post_init__(self) -> None:
        if not isinstance(self.retention_period, timedelta) or self.retention_period <= timedelta(0):
            raise ValueError("retention_period must be a positive timedelta")
        if (
            isinstance(self.minimum_successful_backups, bool)
            or not isinstance(self.minimum_successful_backups, int)
            or self.minimum_successful_backups < 1
        ):
            raise ValueError("minimum_successful_backups must be a positive integer")


def plan_backup_deletions(
    artifacts: tuple[BackupArtifact, ...],
    policy: BackupRetentionPolicy | None,
    now: datetime,
) -> tuple[str, ...]:
    """Return eligible IDs only; never perform deletion or storage mutation."""
    if not isinstance(policy, BackupRetentionPolicy):
        raise ValueError("an explicit valid retention policy is required")
    _require_aware(now, "now")
    if not isinstance(artifacts, tuple):
        raise ValueError("artifacts must be an immutable tuple")
    if any(not isinstance(artifact, BackupArtifact) for artifact in artifacts):
        raise ValueError("all entries must be validated BackupArtifact instances")

    artifact_ids = [artifact.artifact_id for artifact in artifacts]
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError("artifact IDs must be unique")
    if any(artifact.created_at > now for artifact in artifacts):
        raise ValueError("future-dated backup artifacts are not eligible for planning")

    verified = sorted(
        (artifact for artifact in artifacts if artifact.verified),
        key=lambda artifact: (artifact.created_at, artifact.artifact_id),
        reverse=True,
    )
    keep_ids = {
        artifact.artifact_id
        for artifact in verified[: policy.minimum_successful_backups]
    }

    candidates: list[BackupArtifact] = []
    for artifact in artifacts:
        if not artifact.verified or artifact.legal_hold:
            continue
        if artifact.artifact_id in keep_ids:
            continue
        if artifact.immutable_until is not None and artifact.immutable_until > now:
            continue
        if now - artifact.created_at >= policy.retention_period:
            candidates.append(artifact)

    candidates.sort(key=lambda artifact: (artifact.created_at, artifact.artifact_id))
    return tuple(artifact.artifact_id for artifact in candidates)
