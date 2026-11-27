"""PoC-only, fail-closed backup retention planning.

This module does not delete backups or define GENI production retention periods.
A production policy must supply owner-approved values explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class BackupArtifact:
    artifact_id: str
    created_at: datetime
    verified: bool
    legal_hold: bool = False
    immutable_until: datetime | None = None

    def __post_init__(self) -> None:
        if not self.artifact_id.strip():
            raise ValueError("artifact_id must not be empty")
        _require_aware(self.created_at, "created_at")
        if self.immutable_until is not None:
            _require_aware(self.immutable_until, "immutable_until")


@dataclass(frozen=True, slots=True)
class BackupRetentionPolicy:
    retention_period: timedelta
    minimum_successful_backups: int

    def __post_init__(self) -> None:
        if self.retention_period <= timedelta(0):
            raise ValueError("retention_period must be positive")
        if self.minimum_successful_backups < 1:
            raise ValueError("minimum_successful_backups must be at least one")


def plan_backup_deletions(
    artifacts: tuple[BackupArtifact, ...],
    policy: BackupRetentionPolicy | None,
    now: datetime,
) -> tuple[str, ...]:
    """Return eligible IDs only; never perform deletion or storage mutation."""
    if policy is None:
        raise ValueError("an explicit owner-approved retention policy is required")
    _require_aware(now, "now")

    artifact_ids = [artifact.artifact_id for artifact in artifacts]
    if len(artifact_ids) != len(set(artifact_ids)):
        raise ValueError("artifact IDs must be unique")

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
