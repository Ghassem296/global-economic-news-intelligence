from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from retention_policy import BackupArtifact, BackupRetentionPolicy, plan_backup_deletions


class BackupRetentionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 11, 27, 12, 0, tzinfo=UTC)
        self.policy = BackupRetentionPolicy(
            retention_period=timedelta(days=7),
            minimum_successful_backups=2,
        )

    def test_poc_21_retention_planner_preserves_minimum_holds_and_immutability(self) -> None:
        artifacts = (
            BackupArtifact("expired", self.now - timedelta(days=30), True),
            BackupArtifact("boundary", self.now - timedelta(days=7), True),
            BackupArtifact("recent-older", self.now - timedelta(days=2), True),
            BackupArtifact("recent-newest", self.now - timedelta(days=1), True),
            BackupArtifact("legal-hold", self.now - timedelta(days=90), True, legal_hold=True),
            BackupArtifact(
                "immutable-active",
                self.now - timedelta(days=90),
                True,
                immutable_until=self.now + timedelta(seconds=1),
            ),
            BackupArtifact(
                "immutable-expired",
                self.now - timedelta(days=90),
                True,
                immutable_until=self.now,
            ),
            BackupArtifact("unverified", self.now - timedelta(days=90), False),
        )
        self.assertEqual(
            plan_backup_deletions(artifacts, self.policy, self.now),
            ("expired", "immutable-expired", "boundary"),
        )

    def test_retention_planner_fails_closed_and_rejects_invalid_policy(self) -> None:
        artifact = BackupArtifact("backup", self.now - timedelta(days=30), True)
        with self.assertRaises(ValueError):
            plan_backup_deletions((artifact,), None, self.now)
        with self.assertRaises(ValueError):
            plan_backup_deletions((artifact,), self.policy, datetime(2026, 11, 27))
        with self.assertRaises(ValueError):
            plan_backup_deletions([artifact], self.policy, self.now)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            plan_backup_deletions((artifact, artifact), self.policy, self.now)
        with self.assertRaises(ValueError):
            BackupRetentionPolicy(timedelta(0), 1)
        with self.assertRaises(ValueError):
            BackupRetentionPolicy(timedelta(days=7), 0)
        with self.assertRaises(ValueError):
            BackupRetentionPolicy(timedelta(days=7), True)  # type: ignore[arg-type]

    def test_retention_planner_rejects_invalid_artifact_metadata_and_future_dates(self) -> None:
        with self.assertRaises(ValueError):
            BackupArtifact("  ", self.now, True)
        with self.assertRaises(ValueError):
            BackupArtifact("naive", datetime(2026, 11, 27), True)
        with self.assertRaises(ValueError):
            BackupArtifact(
                "bad-immutability",
                self.now,
                True,
                immutable_until=self.now - timedelta(seconds=1),
            )
        future = BackupArtifact("future", self.now + timedelta(seconds=1), True)
        with self.assertRaises(ValueError):
            plan_backup_deletions((future,), self.policy, self.now)

    def test_retention_planner_is_deterministic_and_keeps_all_when_below_minimum(self) -> None:
        tied = self.now - timedelta(days=30)
        artifacts = (
            BackupArtifact("z-old", tied, True),
            BackupArtifact("a-old", tied, True),
        )
        self.assertEqual(plan_backup_deletions(artifacts, self.policy, self.now), ())
        enough = artifacts + (
            BackupArtifact("newest-1", self.now - timedelta(days=1), True),
            BackupArtifact("newest-2", self.now - timedelta(days=2), True),
        )
        self.assertEqual(
            plan_backup_deletions(enough, self.policy, self.now),
            ("a-old", "z-old"),
        )


if __name__ == "__main__":
    unittest.main()
