from __future__ import annotations

import hashlib
import os
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier, Event
from typing import Any

import psycopg
from article_revision_postgres_adapters import (
    PostgreSQLAuthorizationVerifier,
    PostgreSQLArticleRepository,
    PostgreSQLArticleRevisionRepository,
    PostgreSQLIdempotencyRepository,
    UUIDArticleIdGenerator,
)
from postgres_poc_uow import PostgreSQLUnitOfWorkFactory
from psycopg import sql

from global_economic_news_intelligence.application.article_revision_commands import (
    PersistArticleRevisionCommand,
    PersistArticleRevisionResult,
)
from global_economic_news_intelligence.application.article_revision_service import (
    ArticleRevisionService,
)
from global_economic_news_intelligence.domain.article_revision_contracts import (
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import CommandMetadata, UnitOfWork
from global_economic_news_intelligence.exceptions import ErrorCode, GeniError

DATABASE_URL = os.environ.get("GENI_POC_DATABASE_URL", "")
POSTGRES_CONTAINER_ID = os.environ.get("GENI_POC_POSTGRES_CONTAINER_ID", "")
MIGRATIONS = Path(__file__).parent / "migrations"
MIGRATION_NAMES = tuple(
    f"{number:03d}_{name}.sql"
    for number, name in (
        (1, "initial"),
        (2, "article_last_seen"),
        (3, "backup_payload"),
        (4, "domain_integrity"),
        (5, "deferred_article_revision_owner_fk"),
        (6, "atomic_idempotency_claims"),
        (7, "external_outcome_reconciliation"),
        (8, "automatic_external_outcome_transitions"),
        (9, "transaction_bound_authorization_and_rights"),
        (10, "article_revision_service_payload"),
        (11, "idempotency_result_payload"),
    )
)

NOW = datetime(2026, 11, 27, 12, 0, tzinfo=UTC)


class FixedClock:
    def now(self) -> datetime:
        return NOW


class AllowAuthorization:
    def __init__(self) -> None:
        self.calls: list[UnitOfWork | None] = []

    def is_authorized(
        self,
        metadata: CommandMetadata,
        *,
        action: str,
        resource_reference: str,
        uow: UnitOfWork | None = None,
    ) -> bool:
        self.calls.append(uow)
        return True


class AllowContentRights:
    def __init__(self) -> None:
        self.metadata_calls: list[UnitOfWork | None] = []
        self.storage_calls: list[UnitOfWork | None] = []

    def permits_metadata_retention(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
        uow: UnitOfWork | None = None,
    ) -> bool:
        self.metadata_calls.append(uow)
        return True

    def permits_persistent_storage(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
        uow: UnitOfWork | None = None,
    ) -> bool:
        self.storage_calls.append(uow)
        return True


def make_revision(title: str = "Central bank holds rates") -> PersistArticleRevision:
    return PersistArticleRevision(
        source_id="source-test",
        source_article_identity=SourceArticleIdentity(
            "publisher:article-123",
            "identity-v1",
            "https://example.test/articles/123",
        ),
        original_url="https://example.test/articles/123",
        external_id="article-123",
        normalized_title=title,
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
        summary="Synthetic policy summary",
        author="Test Author",
        language="en",
        published_at=None,
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=("metadata-rights-1",),
        metadata={"publisher": "Example Test", "tags": ["policy", "rates"]},
    )


def make_metadata(
    *,
    key: str = "request-1",
    expected_version: str | None = None,
) -> CommandMetadata:
    return CommandMetadata(
        command_id=f"command-{key}",
        schema_version="1",
        actor_reference="service:test-collector",
        authorization_reference="test-grant",
        correlation_id=f"correlation-{key}",
        idempotency_scope="article.revision.persist",
        idempotency_key=key,
        expected_aggregate_version=expected_version,
    )


@unittest.skipUnless(
    DATABASE_URL and POSTGRES_CONTAINER_ID,
    "PostgreSQL PoC database/container environment is not configured",
)
class ArticleRevisionPostgreSQLServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = f"article_revision_{uuid.uuid4().hex}"
        self.admin: psycopg.Connection[Any] | None = psycopg.connect(DATABASE_URL)
        migration_connection: psycopg.Connection[Any] | None = None
        try:
            self.admin.execute(
                sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
            )
            self.admin.commit()
            migration_connection = psycopg.connect(DATABASE_URL)
            migration_connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            migration_connection.commit()
            for migration_name in MIGRATION_NAMES:
                migration_sql = (MIGRATIONS / migration_name).read_text(
                    encoding="utf-8"
                )
                with migration_connection.transaction():
                    migration_connection.execute(migration_sql, prepare=False)
            migration_connection.execute(
                "INSERT INTO sources (source_id) VALUES ('source-test')"
            )
            migration_connection.commit()
            self.factory = PostgreSQLUnitOfWorkFactory(
                database_url=DATABASE_URL,
                schema=self.schema,
            )
            self.articles = PostgreSQLArticleRepository()
            self.revisions = PostgreSQLArticleRevisionRepository(self.factory)
            self.idempotency = PostgreSQLIdempotencyRepository()
            self.authorization = AllowAuthorization()
            self.rights = AllowContentRights()
            self.service = ArticleRevisionService(
                articles=self.articles,
                revisions=self.revisions,
                idempotency=self.idempotency,
                unit_of_work_factory=self.factory,
                authorization=self.authorization,
                content_rights=self.rights,
                article_ids=UUIDArticleIdGenerator(),
                clock=FixedClock(),
            )
        except BaseException:
            if migration_connection is not None:
                migration_connection.close()
            if self.admin is not None:
                self.admin.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                        sql.Identifier(self.schema)
                    )
                )
                self.admin.commit()
                self.admin.close()
                self.admin = None
            raise
        finally:
            if migration_connection is not None and not migration_connection.closed:
                migration_connection.close()

    def tearDown(self) -> None:
        if self.admin is None:
            return
        self.admin.execute(
            sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                sql.Identifier(self.schema)
            )
        )
        self.admin.commit()
        self.admin.close()

    def _counts(self) -> tuple[int, int, int]:
        row = self.admin.execute(
            sql.SQL(
                """
                SELECT
                    (SELECT count(*) FROM {}.articles),
                    (SELECT count(*) FROM {}.article_revisions),
                    (SELECT count(*) FROM {}.idempotency_records)
                """
            ).format(
                sql.Identifier(self.schema),
                sql.Identifier(self.schema),
                sql.Identifier(self.schema),
            )
        ).fetchone()
        return row

    def test_new_article_revision_and_idempotent_replay_use_postgres(self) -> None:
        command = PersistArticleRevisionCommand(make_metadata(), make_revision())

        first = self.service.execute(command)
        replay = self.service.execute(command)

        self.assertIsInstance(first, PersistArticleRevisionResult)
        self.assertTrue(first.created)
        self.assertEqual(replay, first)
        self.assertEqual(self._counts(), (1, 1, 1))
        self.assertEqual(first.article_version, "article-version-1")
        self.assertEqual(len(self.authorization.calls), 4)
        self.assertTrue(all(item is None for item in self.authorization.calls[::2]))
        self.assertTrue(all(item is not None for item in self.authorization.calls[1::2]))
        self.assertEqual(len(self.rights.metadata_calls), 4)
        self.assertEqual(self.rights.metadata_calls[0], None)
        self.assertIsNotNone(self.rights.metadata_calls[1])
        self.assertEqual(self.rights.metadata_calls[2], None)
        self.assertIsNotNone(self.rights.metadata_calls[3])

        revision = self.revisions.get_by_id(first.revision_id)
        self.assertIsNotNone(revision)
        self.assertEqual(revision.payload, make_revision())

    def test_existing_article_append_advances_aggregate_and_revision_numbers(self) -> None:
        first = self.service.execute(
            PersistArticleRevisionCommand(make_metadata(), make_revision())
        )
        changed = make_revision("Central bank cuts rates")
        second = self.service.execute(
            PersistArticleRevisionCommand(
                make_metadata(key="request-2", expected_version=first.article_version),
                changed,
                article_id=first.article_id,
            )
        )

        self.assertTrue(second.created)
        self.assertEqual(second.article_id, first.article_id)
        self.assertEqual(second.article_version, "article-version-2")
        self.assertEqual(self._counts(), (1, 2, 2))
        uow = self.factory.begin()
        try:
            current = self.revisions.get_current_for_article(first.article_id, uow)
        finally:
            uow.rollback()
        self.assertIsNotNone(current)
        self.assertEqual(current.revision_number, 2)

    def test_stale_article_version_is_rejected_without_partial_writes(self) -> None:
        first = self.service.execute(
            PersistArticleRevisionCommand(make_metadata(), make_revision())
        )
        command = PersistArticleRevisionCommand(
            make_metadata(key="stale-request", expected_version="article-version-9"),
            make_revision("A different headline"),
            article_id=first.article_id,
        )

        with self.assertRaises(GeniError) as exc:
            self.service.execute(command)

        self.assertIs(exc.exception.code, ErrorCode.STALE_VERSION)
        self.assertEqual(self._counts(), (1, 1, 1))

    def test_same_idempotency_key_with_changed_request_is_rejected(self) -> None:
        first = PersistArticleRevisionCommand(make_metadata(), make_revision())
        self.service.execute(first)
        changed = PersistArticleRevisionCommand(
            make_metadata(),
            make_revision("Changed title"),
        )

        with self.assertRaises(GeniError) as exc:
            self.service.execute(changed)

        self.assertIs(exc.exception.code, ErrorCode.IDEMPOTENCY_KEY_REUSE_CONFLICT)
        self.assertEqual(self._counts(), (1, 1, 1))

    def test_failure_after_idempotency_completion_rolls_back_entire_write_set(self) -> None:
        class FailingCompletionRepository(PostgreSQLIdempotencyRepository):
            def complete(self, **kwargs: Any) -> None:
                super().complete(**kwargs)
                raise RuntimeError("injected failure after completion")

        self.service._idempotency = FailingCompletionRepository()
        command = PersistArticleRevisionCommand(make_metadata(), make_revision())

        with self.assertRaisesRegex(RuntimeError, "injected failure"):
            self.service.execute(command)

        self.assertEqual(self._counts(), (0, 0, 0))

    def test_available_content_is_persisted_only_after_both_rights_checks(self) -> None:
        body = b"Synthetic full text for the PostgreSQL PoC."
        revision = replace(
            make_revision(),
            content_availability=ContentAvailability.AVAILABLE,
            content_reference="content://synthetic/article-123",
            content_hash=hashlib.sha256(body).hexdigest(),
            content_normalization_version="content-normalization-v1",
            rights_assessment_references=(
                "metadata-rights-1",
                "persistent-storage-rights-1",
            ),
        )

        result = self.service.execute(
            PersistArticleRevisionCommand(make_metadata(), revision)
        )

        self.assertTrue(result.created)
        self.assertEqual(len(self.rights.metadata_calls), 2)
        self.assertEqual(len(self.rights.storage_calls), 2)
        self.assertEqual(self._counts(), (1, 1, 1))
        restored = self.revisions.get_by_id(result.revision_id)
        self.assertEqual(restored.payload.content_hash, revision.content_hash)
        self.assertEqual(
            restored.payload.content_reference,
            revision.content_reference,
        )

    def test_concurrent_same_key_requests_create_one_service_effect(self) -> None:
        command = PersistArticleRevisionCommand(make_metadata(), make_revision())

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.service.execute, command)
                for _ in range(2)
            ]
            results = [future.result(timeout=15) for future in futures]

        self.assertEqual(results[0], results[1])
        self.assertTrue(results[0].created)
        self.assertEqual(self._counts(), (1, 1, 1))

    def test_canonical_url_collision_does_not_merge_distinct_source_identities(self) -> None:
        first = PersistArticleRevisionCommand(make_metadata(), make_revision())
        self.service.execute(first)
        other_identity = SourceArticleIdentity(
            "publisher:another-article",
            "identity-v1",
            "https://example.test/articles/123",
        )
        conflicting_revision = replace(
            make_revision("A different article"),
            source_article_identity=other_identity,
            original_url="https://example.test/articles/another",
            external_id="another-article",
        )

        with self.assertRaises(GeniError) as exc:
            self.service.execute(
                PersistArticleRevisionCommand(
                    make_metadata(key="request-2"),
                    conflicting_revision,
                )
            )

        self.assertIs(exc.exception.code, ErrorCode.CONFLICT)
        self.assertEqual(self._counts(), (1, 1, 1))

    def test_concurrent_new_articles_with_same_source_identity_have_one_winner(self) -> None:
        barrier = Barrier(2)

        class RacingArticleRepository(PostgreSQLArticleRepository):
            def find_by_source_identity(
                self,
                source_id: str,
                external_identity: SourceArticleIdentity,
                uow: UnitOfWork,
            ):
                result = super().find_by_source_identity(
                    source_id,
                    external_identity,
                    uow,
                )
                if result is None:
                    barrier.wait(timeout=10)
                return result

        self.service._articles = RacingArticleRepository()
        commands = [
            PersistArticleRevisionCommand(
                make_metadata(key=f"race-{index}"),
                make_revision(),
            )
            for index in range(2)
        ]

        successes = []
        conflicts = []
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.service.execute, command)
                for command in commands
            ]
            for future in futures:
                try:
                    successes.append(future.result(timeout=20))
                except GeniError as exc:
                    conflicts.append(exc)

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(conflicts), 1)
        self.assertIs(conflicts[0].code, ErrorCode.DUPLICATE_IDENTITY)
        self.assertEqual(self._counts(), (1, 1, 1))

    def _insert_authorization_grant(
        self,
        command: PersistArticleRevisionCommand,
        *,
        status: str = "ACTIVE",
    ) -> None:
        resource_reference = ArticleRevisionService._resource_reference(command)
        self.admin.execute(
            sql.SQL(
                """
                INSERT INTO {}.poc_authorization_grants (
                    grant_reference, actor_reference, action, resource_reference,
                    status, effective_from, expires_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, NULL)
                """
            ).format(sql.Identifier(self.schema)),
            (
                command.metadata.authorization_reference,
                command.metadata.actor_reference,
                ArticleRevisionService.ACTION,
                resource_reference,
                status,
                NOW - timedelta(minutes=1),
            ),
        )
        self.admin.commit()

    def test_postgres_authorization_verifier_fails_closed_without_exact_grant(self) -> None:
        self.service._authorization = PostgreSQLAuthorizationVerifier(
            self.factory,
            FixedClock(),
        )
        command = PersistArticleRevisionCommand(make_metadata(), make_revision())

        with self.assertRaises(GeniError) as exc:
            self.service.execute(command)

        self.assertIs(exc.exception.code, ErrorCode.AUTHORIZATION_DENIED)
        self.assertEqual(self._counts(), (0, 0, 0))

    def test_postgres_authorization_grant_lock_serializes_revocation_after_commit(self) -> None:
        command = PersistArticleRevisionCommand(make_metadata(), make_revision())
        self._insert_authorization_grant(command)
        self.service._authorization = PostgreSQLAuthorizationVerifier(
            self.factory,
            FixedClock(),
        )
        append_entered = Event()
        allow_commit = Event()
        revocation_started = Event()
        revocation_completed = Event()

        class BlockingRevisionRepository(PostgreSQLArticleRevisionRepository):
            def append_revision(
                self,
                article_id: str,
                revision: PersistArticleRevision,
                expected_article_version: str | None,
                uow: UnitOfWork,
            ):
                record = super().append_revision(
                    article_id,
                    revision,
                    expected_article_version,
                    uow,
                )
                append_entered.set()
                if not allow_commit.wait(timeout=10):
                    raise TimeoutError("Test did not release the ArticleRevision transaction.")
                return record

        def revoke_grant() -> None:
            connection = psycopg.connect(DATABASE_URL)
            try:
                connection.execute(
                    sql.SQL("SET search_path TO {}").format(
                        sql.Identifier(self.schema)
                    )
                )
                revocation_started.set()
                connection.execute(
                    """
                    UPDATE poc_authorization_grants
                    SET status = 'REVOKED', version = version + 1
                    WHERE grant_reference = 'test-grant'
                    """
                )
                connection.commit()
            finally:
                connection.close()
                revocation_completed.set()

        self.service._revisions = BlockingRevisionRepository(self.factory)
        with ThreadPoolExecutor(max_workers=2) as executor:
            service_future = executor.submit(self.service.execute, command)
            self.assertTrue(append_entered.wait(timeout=10))
            revocation_future = executor.submit(revoke_grant)
            try:
                self.assertTrue(revocation_started.wait(timeout=5))
                self.assertFalse(revocation_completed.wait(timeout=0.25))
            finally:
                allow_commit.set()
            result = service_future.result(timeout=15)
            revocation_future.result(timeout=15)

        self.assertTrue(result.created)
        self.assertTrue(revocation_completed.is_set())
        row = self.admin.execute(
            sql.SQL(
                "SELECT status FROM {}.poc_authorization_grants WHERE grant_reference = %s"
            ).format(sql.Identifier(self.schema)),
            ("test-grant",),
        ).fetchone()
        self.assertEqual(row[0], "REVOKED")
        self.assertEqual(self._counts(), (1, 1, 1))

