from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import secrets
import stat
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.errors import (
    CheckViolation,
    ForeignKeyViolation,
    InsufficientPrivilege,
    LockNotAvailable,
    QueryCanceled,
    UndefinedTable,
    UniqueViolation,
)

DATABASE_URL = os.environ.get("GENI_POC_DATABASE_URL", "")
POSTGRES_CONTAINER_ID = os.environ.get("GENI_POC_POSTGRES_CONTAINER_ID", "")
MIGRATIONS = Path(__file__).parent / "migrations"


async def connect_to_schema(database_url: str, schema: str) -> psycopg.AsyncConnection[Any]:
    connection = await psycopg.AsyncConnection.connect(database_url)
    await connection.execute(
        sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))
    )
    await connection.commit()
    return connection


async def apply_migration_sql(
    connection: psycopg.AsyncConnection[Any],
    migration_name: str,
    migration_sql: str,
) -> bool:
    """Apply one migration atomically under a schema-scoped transaction lock.

    The lock is acquired before checking migration history, so concurrent runners
    cannot both decide that the same migration is pending. The complete SQL file
    is sent through psycopg's simple-query path; splitting on semicolons is unsafe
    for PL/pgSQL bodies and quoted literals.
    """
    async with connection.transaction():
        await connection.execute(
            "SELECT pg_advisory_xact_lock(hashtextextended(current_schema(), 0))"
        )
        bootstrap = await connection.execute(
            "SELECT to_regclass('schema_migrations')"
        )
        migration_table = await bootstrap.fetchone()
        if migration_table is not None and migration_table[0] is not None:
            applied = await connection.execute(
                "SELECT 1 FROM schema_migrations WHERE version = %s",
                (migration_name,),
            )
            if await applied.fetchone():
                return False

        await connection.execute(migration_sql, prepare=False)
        await connection.execute(
            "INSERT INTO schema_migrations (version) VALUES (%s)",
            (migration_name,),
        )
    return True

async def apply_migrations(
    connection: psycopg.AsyncConnection[Any],
    migration_names: tuple[str, ...],
) -> None:
    for migration_name in migration_names:
        migration_sql = (MIGRATIONS / migration_name).read_text(encoding="utf-8")
        await apply_migration_sql(connection, migration_name, migration_sql)

async def claim_idempotency(
    connection: psycopg.AsyncConnection[Any],
    *,
    operation_scope: str,
    idempotency_key: str,
    request_fingerprint: str,
) -> tuple[str, uuid.UUID | None]:
    """Claim a key in the current transaction or return its durable outcome.

    A concurrent insert on the same key is serialized by the primary key. The
    caller must complete a newly claimed record in this same transaction.
    """
    inserted = await connection.execute(
        """
        INSERT INTO idempotency_records
            (operation_scope, idempotency_key, request_fingerprint, state, completed_at)
        VALUES (%s, %s, %s, 'CLAIMED', NULL)
        ON CONFLICT (operation_scope, idempotency_key) DO NOTHING
        RETURNING operation_scope
        """,
        (operation_scope, idempotency_key, request_fingerprint),
    )
    if await inserted.fetchone() is not None:
        return "claimed", None

    existing = await connection.execute(
        """
        SELECT request_fingerprint, state, result_id
        FROM idempotency_records
        WHERE operation_scope = %s AND idempotency_key = %s
        FOR UPDATE
        """,
        (operation_scope, idempotency_key),
    )
    row = await existing.fetchone()
    if row is None:
        raise AssertionError("Conflicting idempotency row disappeared.")
    stored_fingerprint, state, result_id = row
    if stored_fingerprint != request_fingerprint:
        return "conflict", None
    if state != "COMPLETED" or result_id is None:
        return "in_progress", None
    return "replay", result_id


async def complete_idempotency(
    connection: psycopg.AsyncConnection[Any],
    *,
    operation_scope: str,
    idempotency_key: str,
    request_fingerprint: str,
    result_id: uuid.UUID,
) -> None:
    updated = await connection.execute(
        """
        UPDATE idempotency_records
        SET state = 'COMPLETED', result_id = %s, completed_at = clock_timestamp()
        WHERE operation_scope = %s AND idempotency_key = %s
          AND request_fingerprint = %s AND state = 'CLAIMED'
        """,
        (result_id, operation_scope, idempotency_key, request_fingerprint),
    )
    if updated.rowcount != 1:
        raise AssertionError("Idempotency completion must update exactly one claimed row.")


@unittest.skipUnless(
    DATABASE_URL and POSTGRES_CONTAINER_ID,
    "PostgreSQL PoC database/container environment is not configured",
)
class PostgreSQLPersistencePoCTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.schema = f"poc_{uuid.uuid4().hex}"
        self.admin = await psycopg.AsyncConnection.connect(DATABASE_URL)
        await self.admin.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
        )
        await self.admin.commit()

        self.connection = await connect_to_schema(DATABASE_URL, self.schema)
        await apply_migrations(
            self.connection,
            ("001_initial.sql", "002_article_last_seen.sql", "003_backup_payload.sql", "004_domain_integrity.sql", "005_deferred_article_revision_owner_fk.sql", "006_atomic_idempotency_claims.sql", "007_external_outcome_reconciliation.sql", "008_automatic_external_outcome_transitions.sql", "009_transaction_bound_authorization_and_rights.sql", "010_article_revision_service_payload.sql", "011_idempotency_result_payload.sql"),
        )
        self.source_id = "source-test"
        self.article_id = uuid.uuid4()
        self.event_id = uuid.uuid4()
        self.analysis_id = uuid.uuid4()
        self.report_id = uuid.uuid4()
        self.case_id = uuid.uuid4()
        await self.connection.execute(
            "INSERT INTO sources (source_id) VALUES (%s)",
            (self.source_id,),
        )
        await self.connection.execute(
            """
            INSERT INTO articles (article_id, source_id, external_identity)
            VALUES (%s, %s, %s)
            """,
            (self.article_id, self.source_id, "publisher:article-1"),
        )
        await self.connection.execute(
            "INSERT INTO events (event_id) VALUES (%s)",
            (self.event_id,),
        )
        await self.connection.execute(
            "INSERT INTO analyses (analysis_id) VALUES (%s)",
            (self.analysis_id,),
        )
        await self.connection.execute(
            "INSERT INTO reports (report_id) VALUES (%s)",
            (self.report_id,),
        )
        await self.connection.execute(
            "INSERT INTO decision_cases (case_id) VALUES (%s)",
            (self.case_id,),
        )
        await self.connection.execute(
            "INSERT INTO counters (counter_name, value) VALUES ('writes', 0)"
        )
        await self.connection.commit()

    async def asyncTearDown(self) -> None:
        if getattr(self, "connection", None) is not None:
            await self.connection.close()
        if getattr(self, "admin", None) is not None:
            await self.admin.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(self.schema)
                )
            )
            await self.admin.commit()
            await self.admin.close()

    async def test_poc_01_foreign_key_rejects_invalid_reference(self) -> None:
        with self.assertRaises(ForeignKeyViolation):
            await self.connection.execute(
                """
                INSERT INTO articles (article_id, source_id, external_identity)
                VALUES (%s, 'missing-source', 'publisher:invalid')
                """,
                (uuid.uuid4(),),
            )
        await self.connection.rollback()

    async def test_poc_02_idempotency_replay_and_fingerprint_conflict(self) -> None:
        result_id = uuid.uuid4()
        async with self.connection.transaction():
            state, existing_result = await claim_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key="key-1",
                request_fingerprint="fingerprint-a",
            )
            self.assertEqual(state, "claimed")
            self.assertIsNone(existing_result)
            await complete_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key="key-1",
                request_fingerprint="fingerprint-a",
                result_id=result_id,
            )

        async with self.connection.transaction():
            replay_state, replayed_result = await claim_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key="key-1",
                request_fingerprint="fingerprint-a",
            )
            conflict_state, conflict_result = await claim_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key="key-1",
                request_fingerprint="fingerprint-b",
            )

        self.assertEqual(replay_state, "replay")
        self.assertEqual(replayed_result, result_id)
        self.assertEqual(conflict_state, "conflict")
        self.assertIsNone(conflict_result)

    async def test_poc_03_successor_chain_allows_only_one_direct_successor(self) -> None:
        predecessor_id = uuid.uuid4()
        case_id = self.case_id
        await self.connection.execute(
            """
            INSERT INTO decision_records (decision_id, case_id, outcome)
            VALUES (%s, %s, 'OPEN')
            """,
            (predecessor_id, case_id),
        )
        await self.connection.commit()

        async def append_successor(outcome: str) -> str:
            connection = await connect_to_schema(DATABASE_URL, self.schema)
            try:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO decision_records
                            (decision_id, case_id, predecessor_decision_id, outcome)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (uuid.uuid4(), self.case_id, predecessor_id, outcome),
                    )
                return "committed"
            except UniqueViolation:
                await connection.rollback()
                return "conflict"
            finally:
                await connection.close()

        outcomes = await asyncio.gather(
            append_successor("MATCH"),
            append_successor("NO_MATCH"),
        )
        self.assertCountEqual(outcomes, ["committed", "conflict"])

    async def test_poc_04_decision_and_event_link_rollback_atomically(self) -> None:
        decision_id = uuid.uuid4()
        with self.assertRaises(ForeignKeyViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO decision_records (decision_id, case_id, outcome)
                    VALUES (%s, %s, 'MATCH')
                    """,
                    (decision_id, self.case_id),
                )
                await self.connection.execute(
                    """
                    INSERT INTO article_event_links
                        (link_id, decision_id, article_id, event_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (uuid.uuid4(), decision_id, self.article_id, uuid.uuid4()),
                )
        result = await self.connection.execute(
            "SELECT 1 FROM decision_records WHERE decision_id = %s",
            (decision_id,),
        )
        self.assertIsNone(await result.fetchone())

    async def test_poc_05_parent_provenance_write_set_rolls_back_atomically(self) -> None:
        location_id = uuid.uuid4()
        input_id = uuid.uuid4()
        with self.assertRaises(ForeignKeyViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO evidence_locations (location_id, evidence_id, uri)
                    VALUES (%s, 'evidence-1', 'https://example.invalid/evidence/1')
                    """,
                    (location_id,),
                )
                await self.connection.execute(
                    "INSERT INTO analysis_inputs (analysis_id, input_id) VALUES (%s, %s)",
                    (self.analysis_id, input_id),
                )
                await self.connection.execute(
                    """
                    INSERT INTO analysis_evidence_links
                        (analysis_id, input_id, evidence_location_id)
                    VALUES (%s, %s, %s)
                    """,
                    (self.analysis_id, input_id, location_id),
                )
                await self.connection.execute(
                    """
                    INSERT INTO report_provenance_links (report_id, evidence_location_id)
                    VALUES (%s, %s)
                    """,
                    (uuid.uuid4(), location_id),
                )

        result = await self.connection.execute(
            "SELECT 1 FROM evidence_locations WHERE location_id = %s",
            (location_id,),
        )
        self.assertIsNone(await result.fetchone())
        result = await self.connection.execute(
            "SELECT 1 FROM analysis_inputs WHERE analysis_id = %s AND input_id = %s",
            (self.analysis_id, input_id),
        )
        self.assertIsNone(await result.fetchone())

    async def test_poc_06_optimistic_concurrency_rejects_stale_writer(self) -> None:
        first = await self.connection.execute(
            """
            UPDATE articles SET version = version + 1
            WHERE article_id = %s AND version = 1
            """,
            (self.article_id,),
        )
        stale = await self.connection.execute(
            """
            UPDATE articles SET version = version + 1
            WHERE article_id = %s AND version = 1
            """,
            (self.article_id,),
        )
        await self.connection.commit()
        self.assertEqual(first.rowcount, 1)
        self.assertEqual(stale.rowcount, 0)

    async def test_poc_07_competing_lease_acquisition_has_one_owner(self) -> None:
        barrier = asyncio.Event()
        ready = 0
        ready_lock = asyncio.Lock()

        async def acquire(owner: str) -> tuple[str, int] | None:
            nonlocal ready
            connection = await connect_to_schema(DATABASE_URL, self.schema)
            try:
                async with ready_lock:
                    ready += 1
                    if ready == 2:
                        barrier.set()
                await barrier.wait()
                cursor = await connection.execute(
                    """
                    INSERT INTO execution_leases
                        (resource_id, owner_id, fencing_token, expires_at)
                    VALUES ('run-1', %s, 1, clock_timestamp() + interval '5 minutes')
                    ON CONFLICT (resource_id) DO UPDATE
                    SET owner_id = EXCLUDED.owner_id,
                        fencing_token = execution_leases.fencing_token + 1,
                        expires_at = EXCLUDED.expires_at
                    WHERE execution_leases.expires_at <= clock_timestamp()
                    RETURNING owner_id, fencing_token
                    """,
                    (owner,),
                )
                row = await cursor.fetchone()
                await connection.commit()
                return row
            finally:
                await connection.close()

        owners = await asyncio.gather(acquire("worker-a"), acquire("worker-b"))
        winners = [owner for owner in owners if owner is not None]
        self.assertEqual(len(winners), 1)
        self.assertIn(winners[0][0], {"worker-a", "worker-b"})

    async def test_poc_08_stale_fencing_token_cannot_write_protected_state(self) -> None:
        await self.connection.execute(
            """
            INSERT INTO execution_leases
                (resource_id, owner_id, fencing_token, expires_at)
            VALUES ('resource-1', 'worker-new', 2, clock_timestamp() + interval '5 minutes')
            """
        )
        await self.connection.execute(
            """
            INSERT INTO protected_state (resource_id, fencing_token, value)
            VALUES ('resource-1', 2, 'current')
            """
        )
        stale = await self.connection.execute(
            """
            UPDATE protected_state SET value = 'stale-write'
            WHERE resource_id = 'resource-1' AND fencing_token = 1
              AND EXISTS (
                  SELECT 1 FROM execution_leases
                  WHERE resource_id = 'resource-1'
                    AND owner_id = 'worker-old' AND fencing_token = 1
              )
            """
        )
        current = await self.connection.execute(
            """
            UPDATE protected_state SET value = 'current-write'
            WHERE resource_id = 'resource-1' AND fencing_token = 2
              AND EXISTS (
                  SELECT 1 FROM execution_leases
                  WHERE resource_id = 'resource-1'
                    AND owner_id = 'worker-new' AND fencing_token = 2
              )
            """
        )
        await self.connection.commit()
        self.assertEqual(stale.rowcount, 0)
        self.assertEqual(current.rowcount, 1)

    async def test_poc_09_connection_loss_rolls_back_uncommitted_transaction(self) -> None:
        transient_id = uuid.uuid4()
        connection = await connect_to_schema(DATABASE_URL, self.schema)
        await connection.execute(
            """
            INSERT INTO articles (article_id, source_id, external_identity)
            VALUES (%s, %s, 'publisher:uncommitted')
            """,
            (transient_id, self.source_id),
        )
        await connection.close()

        result = await self.connection.execute(
            "SELECT 1 FROM articles WHERE article_id = %s",
            (transient_id,),
        )
        self.assertIsNone(await result.fetchone())

    async def test_poc_10_commit_before_lost_ack_replays_existing_result(self) -> None:
        await self.connection.commit()
        key = f"ack-{uuid.uuid4()}"
        result_id = uuid.uuid4()
        revision_id = uuid.uuid4()
        connection = await connect_to_schema(DATABASE_URL, self.schema)
        async with connection.transaction():
            state, existing = await claim_idempotency(
                connection,
                operation_scope="article.persist",
                idempotency_key=key,
                request_fingerprint="same-request",
            )
            self.assertEqual(state, "claimed")
            self.assertIsNone(existing)
            await connection.execute(
                """
                INSERT INTO article_revisions
                    (revision_id, article_id, revision_number, fingerprint)
                VALUES (%s, %s, 1, 'lost-ack-fingerprint')
                """,
                (revision_id, self.article_id),
            )
            await complete_idempotency(
                connection,
                operation_scope="article.persist",
                idempotency_key=key,
                request_fingerprint="same-request",
                result_id=result_id,
            )
        await connection.close()

        async with self.connection.transaction():
            replay_state, replayed_id = await claim_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key=key,
                request_fingerprint="same-request",
            )
        self.assertEqual(replay_state, "replay")
        self.assertEqual(replayed_id, result_id)
        count = await self.connection.execute(
            "SELECT count(*) FROM article_revisions WHERE article_id = %s AND revision_number = 1",
            (self.article_id,),
        )
        self.assertEqual((await count.fetchone())[0], 1)


    async def test_poc_31_concurrent_same_key_claims_create_one_domain_effect(self) -> None:
        await self.connection.commit()
        key = f"concurrent-{uuid.uuid4()}"
        barrier = asyncio.Event()
        ready = 0
        ready_lock = asyncio.Lock()

        async def execute_once() -> tuple[str, uuid.UUID | None]:
            nonlocal ready
            connection = await connect_to_schema(DATABASE_URL, self.schema)
            try:
                async with ready_lock:
                    ready += 1
                    if ready == 2:
                        barrier.set()
                await barrier.wait()
                async with connection.transaction():
                    state, result_id = await claim_idempotency(
                        connection,
                        operation_scope="article.persist",
                        idempotency_key=key,
                        request_fingerprint="identical-request",
                    )
                    if state == "claimed":
                        result_id = uuid.uuid4()
                        await connection.execute(
                            "UPDATE counters SET value = value + 1 WHERE counter_name = 'writes'"
                        )
                        await complete_idempotency(
                            connection,
                            operation_scope="article.persist",
                            idempotency_key=key,
                            request_fingerprint="identical-request",
                            result_id=result_id,
                        )
                    return state, result_id
            finally:
                await connection.close()

        outcomes = await asyncio.gather(execute_once(), execute_once())
        self.assertCountEqual([state for state, _ in outcomes], ["claimed", "replay"])
        result_ids = {result_id for _, result_id in outcomes}
        self.assertEqual(len(result_ids), 1)
        self.assertIsNotNone(next(iter(result_ids)))
        count = await self.connection.execute(
            "SELECT value FROM counters WHERE counter_name = 'writes'"
        )
        self.assertEqual((await count.fetchone())[0], 1)
        record = await self.connection.execute(
            """
            SELECT state, request_fingerprint, result_id
            FROM idempotency_records
            WHERE operation_scope = 'article.persist' AND idempotency_key = %s
            """,
            (key,),
        )
        state, fingerprint, result_id = await record.fetchone()
        self.assertEqual(state, "COMPLETED")
        self.assertEqual(fingerprint, "identical-request")
        self.assertEqual(result_id, next(iter(result_ids)))


    async def test_poc_32_interrupted_idempotency_claim_rolls_back_for_safe_retry(self) -> None:
        await self.connection.commit()
        key = f"interrupted-{uuid.uuid4()}"
        interrupted = await connect_to_schema(DATABASE_URL, self.schema)
        state, result_id = await claim_idempotency(
            interrupted,
            operation_scope="article.persist",
            idempotency_key=key,
            request_fingerprint="same-request",
        )
        self.assertEqual(state, "claimed")
        self.assertIsNone(result_id)
        await interrupted.execute(
            "UPDATE counters SET value = value + 1 WHERE counter_name = 'writes'"
        )
        # Closing before COMMIT simulates process loss: both claim and local effect roll back.
        await interrupted.close()

        absent = await self.connection.execute(
            """
            SELECT 1 FROM idempotency_records
            WHERE operation_scope = 'article.persist' AND idempotency_key = %s
            """,
            (key,),
        )
        self.assertIsNone(await absent.fetchone())

        result_id = uuid.uuid4()
        async with self.connection.transaction():
            retry_state, retry_result = await claim_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key=key,
                request_fingerprint="same-request",
            )
            self.assertEqual(retry_state, "claimed")
            self.assertIsNone(retry_result)
            await self.connection.execute(
                "UPDATE counters SET value = value + 1 WHERE counter_name = 'writes'"
            )
            await complete_idempotency(
                self.connection,
                operation_scope="article.persist",
                idempotency_key=key,
                request_fingerprint="same-request",
                result_id=result_id,
            )

        count = await self.connection.execute(
            "SELECT value FROM counters WHERE counter_name = 'writes'"
        )
        self.assertEqual((await count.fetchone())[0], 1)

    async def test_poc_33_expired_lease_takeover_increments_fence_and_rejects_stale_worker(
        self,
    ) -> None:
        resource_id = f"lease-{uuid.uuid4()}"
        await self.connection.execute(
            """
            INSERT INTO execution_leases
                (resource_id, owner_id, fencing_token, expires_at)
            VALUES (%s, 'worker-old', 1, clock_timestamp() - interval '1 second')
            """,
            (resource_id,),
        )
        await self.connection.execute(
            """
            INSERT INTO protected_state (resource_id, fencing_token, value)
            VALUES (%s, 1, 'old-state')
            """,
            (resource_id,),
        )

        takeover = await self.connection.execute(
            """
            INSERT INTO execution_leases
                (resource_id, owner_id, fencing_token, expires_at)
            VALUES (%s, 'worker-new', 1, clock_timestamp() + interval '5 minutes')
            ON CONFLICT (resource_id) DO UPDATE
            SET owner_id = EXCLUDED.owner_id,
                fencing_token = execution_leases.fencing_token + 1,
                expires_at = EXCLUDED.expires_at
            WHERE execution_leases.expires_at <= clock_timestamp()
            RETURNING owner_id, fencing_token
            """,
            (resource_id,),
        )
        self.assertEqual(await takeover.fetchone(), ("worker-new", 2))

        stale = await self.connection.execute(
            """
            UPDATE protected_state SET value = 'stale-write'
            WHERE resource_id = %s AND fencing_token = 1
              AND EXISTS (
                  SELECT 1 FROM execution_leases
                  WHERE resource_id = %s
                    AND owner_id = 'worker-old' AND fencing_token = 1
              )
            """,
            (resource_id, resource_id),
        )
        current = await self.connection.execute(
            """
            UPDATE protected_state SET fencing_token = 2, value = 'new-state'
            WHERE resource_id = %s AND fencing_token < 2
              AND EXISTS (
                  SELECT 1 FROM execution_leases
                  WHERE resource_id = %s
                    AND owner_id = 'worker-new' AND fencing_token = 2
              )
            """,
            (resource_id, resource_id),
        )
        await self.connection.commit()
        self.assertEqual(stale.rowcount, 0)
        self.assertEqual(current.rowcount, 1)
        result = await self.connection.execute(
            "SELECT value FROM protected_state WHERE resource_id = %s",
            (resource_id,),
        )
        self.assertEqual((await result.fetchone())[0], "new-state")


    async def test_poc_34_unknown_external_outcome_blocks_retry_until_reconciled(self) -> None:
        operation_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO external_operations (operation_id, operation_kind, status)
            VALUES (%s, 'PUBLICATION', 'PENDING')
            """,
            (operation_id,),
        )
        await self.connection.execute(
            """
            UPDATE external_operations
            SET status = 'IN_PROGRESS', version = version + 1
            WHERE operation_id = %s AND status = 'PENDING'
            """,
            (operation_id,),
        )
        await self.connection.execute(
            """
            INSERT INTO external_attempts
                (attempt_id, operation_id, attempt_number, attempt_type, outcome)
            VALUES (%s, %s, 1, 'EXECUTE', 'OUTCOME_UNKNOWN')
            """,
            (uuid.uuid4(), operation_id),
        )

        state = await self.connection.execute(
            "SELECT status FROM external_operations WHERE operation_id = %s",
            (operation_id,),
        )
        self.assertEqual((await state.fetchone())[0], "RECONCILIATION_REQUIRED")

        with self.assertRaises(CheckViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO external_attempts
                        (attempt_id, operation_id, attempt_number, attempt_type, outcome)
                    VALUES (%s, %s, 2, 'EXECUTE', 'CONFIRMED_SUCCESS')
                    """,
                    (uuid.uuid4(), operation_id),
                )

        await self.connection.execute(
            """
            INSERT INTO external_attempts
                (attempt_id, operation_id, attempt_number, attempt_type, outcome)
            VALUES (%s, %s, 2, 'RECONCILE', 'RECONCILED_SUCCESS')
            """,
            (uuid.uuid4(), operation_id),
        )
        state = await self.connection.execute(
            "SELECT status FROM external_operations WHERE operation_id = %s",
            (operation_id,),
        )
        self.assertEqual((await state.fetchone())[0], "SUCCEEDED")

        with self.assertRaises(CheckViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO external_attempts
                        (attempt_id, operation_id, attempt_number, attempt_type, outcome)
                    VALUES (%s, %s, 3, 'EXECUTE', 'CONFIRMED_SUCCESS')
                    """,
                    (uuid.uuid4(), operation_id),
                )
        await self.connection.commit()

        attempts = await self.connection.execute(
            """
            SELECT attempt_type, outcome FROM external_attempts
            WHERE operation_id = %s ORDER BY attempt_number
            """,
            (operation_id,),
        )
        self.assertEqual(
            await attempts.fetchall(),
            [("EXECUTE", "OUTCOME_UNKNOWN"), ("RECONCILE", "RECONCILED_SUCCESS")],
        )


    async def test_poc_11_concurrent_atomic_updates_have_no_lost_increments(self) -> None:
        async def increment() -> None:
            connection = await connect_to_schema(DATABASE_URL, self.schema)
            try:
                await connection.execute(
                    "UPDATE counters SET value = value + 1 WHERE counter_name = 'writes'"
                )
                await connection.commit()
            finally:
                await connection.close()

        await asyncio.gather(*(increment() for _ in range(24)))
        result = await self.connection.execute(
            "SELECT value FROM counters WHERE counter_name = 'writes'"
        )
        self.assertEqual((await result.fetchone())[0], 24)

    async def test_poc_12_async_query_cancellation_keeps_event_loop_responsive(self) -> None:
        connection = await connect_to_schema(DATABASE_URL, self.schema)
        ticks = 0
        running = True

        async def heartbeat() -> None:
            nonlocal ticks
            while running:
                ticks += 1
                await asyncio.sleep(0.005)

        heartbeat_task = asyncio.create_task(heartbeat())
        query_task = asyncio.create_task(connection.execute("SELECT pg_sleep(5)"))
        await asyncio.sleep(0.05)
        await connection.cancel_safe(timeout=3)
        with self.assertRaises(QueryCanceled):
            await query_task
        running = False
        await heartbeat_task
        await connection.rollback()
        await connection.close()
        self.assertGreater(ticks, 2)

    async def test_poc_13_clean_install_applies_all_versioned_migrations(self) -> None:
        result = await self.connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        versions = [row[0] for row in await result.fetchall()]
        self.assertEqual(versions, ["001_initial.sql", "002_article_last_seen.sql", "003_backup_payload.sql", "004_domain_integrity.sql", "005_deferred_article_revision_owner_fk.sql", "006_atomic_idempotency_claims.sql", "007_external_outcome_reconciliation.sql", "008_automatic_external_outcome_transitions.sql", "009_transaction_bound_authorization_and_rights.sql"])
        result = await self.connection.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = %s AND table_name = 'articles'
            """,
            (self.schema,),
        )
        columns = {row[0] for row in await result.fetchall()}
        self.assertIn("source_last_seen_at", columns)

    async def test_poc_14_upgrade_preserves_existing_rows(self) -> None:
        upgrade_schema = f"upgrade_{uuid.uuid4().hex}"
        await self.admin.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(upgrade_schema))
        )
        await self.admin.commit()
        connection = await connect_to_schema(DATABASE_URL, upgrade_schema)
        try:
            await apply_migrations(connection, ("001_initial.sql",))
            source_id = "upgrade-source"
            article_id = uuid.uuid4()
            legacy_case_id = uuid.uuid4()
            legacy_decision_id = uuid.uuid4()
            await connection.execute(
                "INSERT INTO sources (source_id) VALUES (%s)",
                (source_id,),
            )
            await connection.execute(
                """
                INSERT INTO articles (article_id, source_id, external_identity)
                VALUES (%s, %s, 'legacy-article')
                """,
                (article_id, source_id),
            )
            await connection.execute(
                """
                INSERT INTO decision_records (decision_id, case_id, outcome)
                VALUES (%s, %s, 'OPEN')
                """,
                (legacy_decision_id, legacy_case_id),
            )
            await connection.commit()
            await apply_migrations(connection, ("002_article_last_seen.sql", "003_backup_payload.sql", "004_domain_integrity.sql", "005_deferred_article_revision_owner_fk.sql", "006_atomic_idempotency_claims.sql", "007_external_outcome_reconciliation.sql", "008_automatic_external_outcome_transitions.sql", "009_transaction_bound_authorization_and_rights.sql"))
            result = await connection.execute(
                """
                SELECT external_identity, source_last_seen_at
                FROM articles WHERE article_id = %s
                """,
                (article_id,),
            )
            identity, last_seen = await result.fetchone()
            self.assertEqual(identity, "legacy-article")
            self.assertIsNone(last_seen)
            result = await connection.execute(
                "SELECT current_revision_id FROM articles WHERE article_id = %s",
                (article_id,),
            )
            self.assertIsNone((await result.fetchone())[0])
            result = await connection.execute(
                "SELECT case_id FROM decision_cases WHERE case_id = %s",
                (legacy_case_id,),
            )
            self.assertEqual((await result.fetchone())[0], legacy_case_id)
            result = await connection.execute(
                "SELECT case_id FROM decision_records WHERE decision_id = %s",
                (legacy_decision_id,),
            )
            self.assertEqual((await result.fetchone())[0], legacy_case_id)
        finally:
            await connection.close()
            await self.admin.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(upgrade_schema)
                )
            )
            await self.admin.commit()

    async def test_poc_15_backup_restores_schema_and_application_rows(self) -> None:
        restore_database = f"restore_{uuid.uuid4().hex[:12]}"
        admin_url = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
        admin = await psycopg.AsyncConnection.connect(admin_url, autocommit=True)
        restored: psycopg.AsyncConnection[Any] | None = None
        backup_process: asyncio.subprocess.Process | None = None
        remote_backup = f"/tmp/{restore_database}.dump"
        concurrent_article_id = uuid.uuid4()

        async def docker(*arguments: str) -> subprocess.CompletedProcess[str]:
            return await asyncio.to_thread(
                subprocess.run,
                ["docker", *arguments],
                check=True,
                capture_output=True,
                text=True,
            )

        try:
            with tempfile.TemporaryDirectory() as temporary_directory:
                local_backup = Path(temporary_directory) / "geni-poc.dump"
                await self.connection.execute(
                    """
                    INSERT INTO backup_payload (payload)
                    SELECT repeat('x', 256) FROM generate_series(1, 50000)
                    """
                )
                await self.connection.commit()

                backup_process = await asyncio.create_subprocess_exec(
                    "docker",
                    "exec",
                    "-e",
                    "PGAPPNAME=geni_poc_backup",
                    POSTGRES_CONTAINER_ID,
                    "sh",
                    "-c",
                    'umask 077 && exec pg_dump -U postgres -d geni_poc -Fc -f "$1"',
                    "sh",
                    remote_backup,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                backup_active = False
                for _ in range(500):
                    activity = await self.connection.execute(
                        """
                        SELECT 1 FROM pg_stat_activity
                        WHERE application_name = 'geni_poc_backup'
                          AND state = 'active'
                        LIMIT 1
                        """
                    )
                    backup_active = await activity.fetchone() is not None
                    await self.connection.commit()
                    if backup_active:
                        break
                    if backup_process.returncode is not None:
                        break
                    await asyncio.sleep(0.01)
                self.assertTrue(
                    backup_active,
                    "Could not observe pg_dump while active; concurrent-write backup was not exercised.",
                )

                writer = await connect_to_schema(DATABASE_URL, self.schema)
                try:
                    await writer.execute(
                        """
                        INSERT INTO articles (article_id, source_id, external_identity)
                        VALUES (%s, %s, 'publisher:concurrent-backup-write')
                        """,
                        (concurrent_article_id, self.source_id),
                    )
                    await writer.commit()
                finally:
                    await writer.close()

                _, backup_stderr = await backup_process.communicate()
                self.assertEqual(
                    backup_process.returncode,
                    0,
                    backup_stderr.decode(errors="replace"),
                )
                remote_mode = await docker(
                    "exec", POSTGRES_CONTAINER_ID, "stat", "-c", "%a", remote_backup
                )
                self.assertEqual(remote_mode.stdout.strip(), "600")
                await docker(
                    "cp",
                    f"{POSTGRES_CONTAINER_ID}:{remote_backup}",
                    str(local_backup),
                )

                # PoC-only envelope: encrypted backup plus an independent
                # authentication tag. Production key custody/rotation remains
                # outside this experiment and requires an approved KMS design.
                os.chmod(local_backup, 0o600)
                self.assertEqual(stat.S_IMODE(local_backup.stat().st_mode), 0o600)
                passphrase = secrets.token_urlsafe(48)
                encryption_environment = os.environ.copy()
                encryption_environment["GENI_POC_BACKUP_PASSPHRASE"] = passphrase
                encrypted_backup = local_backup.with_suffix(".dump.enc")
                subprocess.run(
                    [
                        "openssl", "enc", "-aes-256-cbc", "-salt",
                        "-pbkdf2", "-iter", "200000", "-md", "sha256",
                        "-in", str(local_backup), "-out", str(encrypted_backup),
                        "-pass", "env:GENI_POC_BACKUP_PASSPHRASE",
                    ],
                    check=True,
                    capture_output=True,
                    env=encryption_environment,
                )
                os.chmod(encrypted_backup, 0o600)
                ciphertext = encrypted_backup.read_bytes()
                authentication_key = hmac.new(
                    passphrase.encode("utf-8"),
                    b"GENI-PoC-backup-authentication-v1",
                    hashlib.sha256,
                ).digest()
                authentication_tag = hmac.new(
                    authentication_key, ciphertext, hashlib.sha256
                ).hexdigest()
                tag_file = encrypted_backup.with_suffix(".hmac")
                tag_file.write_text(authentication_tag, encoding="ascii")
                os.chmod(tag_file, 0o600)
                self.assertEqual(stat.S_IMODE(encrypted_backup.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(tag_file.stat().st_mode), 0o600)

                wrong_key = hmac.new(
                    b"incorrect-ephemeral-passphrase",
                    b"GENI-PoC-backup-authentication-v1",
                    hashlib.sha256,
                ).digest()
                wrong_tag = hmac.new(
                    wrong_key, ciphertext, hashlib.sha256
                ).hexdigest()
                self.assertFalse(hmac.compare_digest(authentication_tag, wrong_tag))

                tampered_ciphertext = bytearray(ciphertext)
                tampered_ciphertext[-1] ^= 0x01
                tampered_tag = hmac.new(
                    authentication_key, tampered_ciphertext, hashlib.sha256
                ).hexdigest()
                self.assertFalse(
                    hmac.compare_digest(authentication_tag, tampered_tag),
                    "Modified backup ciphertext must fail authentication.",
                )

                authenticated_backup = local_backup.with_name("authenticated.dump")
                verified_tag = hmac.new(
                    authentication_key, ciphertext, hashlib.sha256
                ).hexdigest()
                stored_tag = tag_file.read_text(encoding="ascii")
                self.assertTrue(hmac.compare_digest(stored_tag, verified_tag))
                subprocess.run(
                    [
                        "openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2",
                        "-iter", "200000", "-md", "sha256",
                        "-in", str(encrypted_backup), "-out", str(authenticated_backup),
                        "-pass", "env:GENI_POC_BACKUP_PASSPHRASE",
                    ],
                    check=True,
                    capture_output=True,
                    env=encryption_environment,
                )
                os.chmod(authenticated_backup, 0o600)
                self.assertEqual(
                    hashlib.sha256(authenticated_backup.read_bytes()).digest(),
                    hashlib.sha256(local_backup.read_bytes()).digest(),
                )
                local_backup.unlink()

                await admin.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(restore_database)
                    )
                )
                await docker(
                    "cp",
                    str(authenticated_backup),
                    f"{POSTGRES_CONTAINER_ID}:{remote_backup}",
                )
                await docker(
                    "exec",
                    POSTGRES_CONTAINER_ID,
                    "pg_restore",
                    "-U",
                    "postgres",
                    "-d",
                    restore_database,
                    "--no-owner",
                    "--no-acl",
                    "--exit-on-error",
                    remote_backup,
                )
                restored_url = DATABASE_URL.rsplit("/", 1)[0] + f"/{restore_database}"
                restored = await connect_to_schema(restored_url, self.schema)
                result = await restored.execute(
                    "SELECT count(*) FROM articles WHERE article_id = %s",
                    (self.article_id,),
                )
                self.assertEqual((await result.fetchone())[0], 1)
                result = await restored.execute(
                    "SELECT count(*) FROM backup_payload"
                )
                self.assertEqual((await result.fetchone())[0], 50000)
                result = await restored.execute(
                    """
                    SELECT source_id, external_identity, version
                    FROM articles WHERE article_id = %s
                    """,
                    (concurrent_article_id,),
                )
                concurrent_row = await result.fetchone()
                # pg_dump uses one MVCC snapshot. A write committed after
                # that snapshot is correctly absent; if visible, it must be
                # complete and internally consistent rather than partially copied.
                if concurrent_row is not None:
                    self.assertEqual(
                        concurrent_row,
                        (self.source_id, "publisher:concurrent-backup-write", 1),
                    )
                result = await restored.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                )
                self.assertEqual(
                    [row[0] for row in await result.fetchall()],
                    [
                        "001_initial.sql",
                        "002_article_last_seen.sql",
                        "003_backup_payload.sql",
                        "004_domain_integrity.sql",
                        "005_deferred_article_revision_owner_fk.sql",
                        "006_atomic_idempotency_claims.sql",
                        "007_external_outcome_reconciliation.sql",
                        "008_automatic_external_outcome_transitions.sql",
                        "009_transaction_bound_authorization_and_rights.sql",
                    ],
                )
        finally:
            if backup_process is not None and backup_process.returncode is None:
                backup_process.terminate()
                await backup_process.wait()
            if restored is not None:
                await restored.close()
            await admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                    sql.Identifier(restore_database)
                )
            )
            await admin.close()
            await docker("exec", POSTGRES_CONTAINER_ID, "rm", "-f", remote_backup)

    async def test_poc_17_least_privilege_role_cannot_write(self) -> None:
        role_name = f"poc_reader_{uuid.uuid4().hex[:12]}"
        role = sql.Identifier(role_name)
        role_created = False
        try:
            await self.admin.execute(
                sql.SQL("CREATE ROLE {} NOLOGIN").format(role)
            )
            role_created = True
            await self.admin.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                    sql.Identifier(self.schema), role
                )
            )
            await self.admin.execute(
                sql.SQL("GRANT SELECT ON TABLE {}.articles TO {}").format(
                    sql.Identifier(self.schema), role
                )
            )
            await self.admin.commit()

            await self.connection.execute(sql.SQL("SET ROLE {}").format(role))
            result = await self.connection.execute(
                "SELECT article_id FROM articles WHERE article_id = %s",
                (self.article_id,),
            )
            self.assertEqual((await result.fetchone())[0], self.article_id)

            with self.assertRaises(InsufficientPrivilege):
                await self.connection.execute(
                    """
                    INSERT INTO articles (article_id, source_id, external_identity)
                    VALUES (%s, %s, 'poc-reader-must-not-write')
                    """,
                    (uuid.uuid4(), self.source_id),
                )
            await self.connection.rollback()
        finally:
            if role_created:
                await self.admin.execute(
                    sql.SQL("REVOKE ALL ON TABLE {}.articles FROM {}").format(
                        sql.Identifier(self.schema), role
                    )
                )
                await self.admin.execute(
                    sql.SQL("REVOKE ALL ON SCHEMA {} FROM {}").format(
                        sql.Identifier(self.schema), role
                    )
                )
                await self.admin.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(role)
                )
                await self.admin.commit()

    async def test_poc_16_new_process_observes_committed_operation_after_restart(self) -> None:
        record_id = uuid.uuid4()
        child_environment = os.environ.copy()
        child_environment["GENI_POC_SCHEMA"] = self.schema
        child_environment["GENI_POC_RECORD_ID"] = str(record_id)
        child_environment["GENI_POC_CASE_ID"] = str(self.case_id)
        child_script = """
import asyncio
import os
import uuid
import psycopg

async def main():
    connection = await psycopg.AsyncConnection.connect(
        os.environ["GENI_POC_DATABASE_URL"]
    )
    schema = os.environ["GENI_POC_SCHEMA"]
    await connection.execute(f'SET search_path TO "{schema}"')
    await connection.execute(
        "INSERT INTO decision_records (decision_id, case_id, outcome) "
        "VALUES (%s, %s, 'OPEN')",
        (uuid.UUID(os.environ["GENI_POC_RECORD_ID"]), uuid.UUID(os.environ["GENI_POC_CASE_ID"])),
    )
    await connection.commit()
    await connection.close()

asyncio.run(main())
"""
        await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-c", child_script],
            check=True,
            capture_output=True,
            text=True,
            env=child_environment,
        )

        recovered = await connect_to_schema(DATABASE_URL, self.schema)
        try:
            result = await recovered.execute(
                "SELECT outcome FROM decision_records WHERE decision_id = %s",
                (record_id,),
            )
            self.assertEqual((await result.fetchone())[0], "OPEN")
        finally:
            await recovered.close()



    async def test_poc_20_least_privilege_backup_role_can_dump_without_write_access(self) -> None:
        role_name = f"poc_backup_{uuid.uuid4().hex[:12]}"
        restore_role_name = f"poc_restore_{uuid.uuid4().hex[:12]}"
        restore_database = f"restore_backup_{uuid.uuid4().hex[:12]}"
        remote_backup = f"/tmp/{restore_database}.dump"
        password = secrets.token_urlsafe(32)
        restore_password = secrets.token_urlsafe(32)
        role = sql.Identifier(role_name)
        restore_role = sql.Identifier(restore_role_name)
        admin_url = DATABASE_URL.rsplit("/", 1)[0] + "/postgres"
        admin = await psycopg.AsyncConnection.connect(admin_url, autocommit=True)
        backup_connection: psycopg.AsyncConnection[Any] | None = None
        restore_probe: psycopg.AsyncConnection[Any] | None = None
        restored: psycopg.AsyncConnection[Any] | None = None
        backup_role_created = False
        restore_role_created = False
        database_created = False

        async def docker(*arguments: str) -> subprocess.CompletedProcess[str]:
            return await asyncio.to_thread(
                subprocess.run,
                ["docker", *arguments],
                check=True,
                capture_output=True,
                text=True,
            )

        try:
            await self.admin.execute(
                sql.SQL("CREATE ROLE {} LOGIN INHERIT PASSWORD {}").format(
                    role, sql.Literal(password)
                )
            )
            await self.admin.execute(
                sql.SQL("CREATE ROLE {} LOGIN INHERIT PASSWORD {}").format(
                    restore_role, sql.Literal(restore_password)
                )
            )
            await self.admin.execute(
                sql.SQL("GRANT pg_read_all_data TO {}").format(role)
            )
            await self.admin.commit()
            backup_role_created = True
            restore_role_created = True

            backup_connection = await psycopg.AsyncConnection.connect(
                DATABASE_URL,
                user=role_name,
                password=password,
            )
            await backup_connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            with self.assertRaises(InsufficientPrivilege):
                await backup_connection.execute(
                    """
                    INSERT INTO articles (article_id, source_id, external_identity)
                    VALUES (%s, %s, 'backup-role-must-not-write')
                    """,
                    (uuid.uuid4(), self.source_id),
                )
            await backup_connection.rollback()
            await backup_connection.close()
            backup_connection = None

            await self.admin.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                    sql.Identifier(self.schema), restore_role
                )
            )
            await self.admin.commit()
            restore_probe = await psycopg.AsyncConnection.connect(
                DATABASE_URL,
                user=restore_role_name,
                password=restore_password,
            )
            await restore_probe.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            with self.assertRaises(InsufficientPrivilege):
                await restore_probe.execute(
                    """
                    INSERT INTO articles (article_id, source_id, external_identity)
                    VALUES (%s, %s, 'restore-role-must-not-write-source')
                    """,
                    (uuid.uuid4(), self.source_id),
                )
            await restore_probe.rollback()
            await restore_probe.close()
            restore_probe = None

            role_attributes = await self.admin.execute(
                """
                SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolcanlogin
                FROM pg_roles WHERE rolname IN (%s, %s)
                ORDER BY rolname
                """,
                (role_name, restore_role_name),
            )
            self.assertEqual(
                await role_attributes.fetchall(),
                [
                    (role_name, False, False, False, True),
                    (restore_role_name, False, False, False, True),
                ],
            )

            await docker(
                "exec",
                "-e",
                f"PGPASSWORD={password}",
                POSTGRES_CONTAINER_ID,
                "sh",
                "-c",
                'umask 077 && exec pg_dump -h 127.0.0.1 -U "$1" -d geni_poc -Fc -f "$2"',
                "sh",
                role_name,
                remote_backup,
            )
            backup_mode = await docker(
                "exec", POSTGRES_CONTAINER_ID, "stat", "-c", "%a", remote_backup
            )
            self.assertEqual(backup_mode.stdout.strip(), "600")

            await admin.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(restore_database)
                )
            )
            database_created = True
            await admin.execute(
                sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
                    sql.Identifier(restore_database), restore_role
                )
            )
            await docker(
                "exec",
                "-e",
                f"PGPASSWORD={restore_password}",
                POSTGRES_CONTAINER_ID,
                "pg_restore",
                "-h",
                "127.0.0.1",
                "-U",
                restore_role_name,
                "-d",
                restore_database,
                "--no-owner",
                "--no-acl",
                "--exit-on-error",
                remote_backup,
            )
            restored_url = DATABASE_URL.rsplit("/", 1)[0] + f"/{restore_database}"
            restored = await psycopg.AsyncConnection.connect(
                restored_url,
                user=restore_role_name,
                password=restore_password,
            )
            await restored.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            result = await restored.execute(
                "SELECT count(*) FROM articles WHERE article_id = %s",
                (self.article_id,),
            )
            self.assertEqual((await result.fetchone())[0], 1)
            result = await restored.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
            self.assertEqual(
                [row[0] for row in await result.fetchall()],
                [
                    "001_initial.sql",
                    "002_article_last_seen.sql",
                    "003_backup_payload.sql",
                    "004_domain_integrity.sql",
                    "005_deferred_article_revision_owner_fk.sql",
                    "006_atomic_idempotency_claims.sql",
                    "007_external_outcome_reconciliation.sql",
                    "008_automatic_external_outcome_transitions.sql",
                    "009_transaction_bound_authorization_and_rights.sql",
                ],
            )
            owner = await restored.execute(
                """
                SELECT pg_get_userbyid(class.relowner)
                FROM pg_class class
                JOIN pg_namespace namespace ON namespace.oid = class.relnamespace
                WHERE namespace.nspname = %s AND class.relname = 'articles'
                """,
                (self.schema,),
            )
            self.assertEqual((await owner.fetchone())[0], restore_role_name)
        finally:
            if backup_connection is not None:
                await backup_connection.close()
            if restore_probe is not None:
                await restore_probe.close()
            if restored is not None:
                await restored.close()
            await self.admin.rollback()
            if database_created:
                await admin.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(
                        sql.Identifier(restore_database)
                    )
                )
            if backup_role_created:
                await admin.execute(
                    sql.SQL("REVOKE pg_read_all_data FROM {}").format(role)
                )
                await admin.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(role)
                )
            if restore_role_created:
                await self.admin.execute(
                    sql.SQL("REVOKE ALL ON SCHEMA {} FROM {}").format(
                        sql.Identifier(self.schema), restore_role
                    )
                )
                await self.admin.commit()
                await admin.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(restore_role)
                )
            await admin.close()
            await asyncio.to_thread(
                subprocess.run,
                ["docker", "exec", POSTGRES_CONTAINER_ID, "rm", "-f", remote_backup],
                check=False,
                capture_output=True,
                text=True,
            )

    async def test_poc_19_cluster_global_roles_restore_into_clean_instance(self) -> None:
        image_digest = os.environ.get("GENI_POC_POSTGRES_IMAGE_DIGEST", "")
        self.assertIn(
            "@sha256:",
            image_digest,
            "A pinned PostgreSQL image digest is required for isolated globals restore.",
        )
        suffix = uuid.uuid4().hex[:12]
        parent_role = f"poc_restore_parent_{suffix}"
        member_role = f"poc_restore_member_{suffix}"
        target_container = f"geni-poc-globals-{suffix}"
        target_started = False
        source_roles_created = False
        target_connection: psycopg.AsyncConnection[Any] | None = None

        async def docker(*arguments: str) -> subprocess.CompletedProcess[str]:
            return await asyncio.to_thread(
                subprocess.run,
                ["docker", *arguments],
                check=True,
                capture_output=True,
                text=True,
            )

        try:
            await self.admin.execute(
                sql.SQL("CREATE ROLE {} NOLOGIN INHERIT").format(
                    sql.Identifier(parent_role)
                )
            )
            await self.admin.execute(
                sql.SQL("CREATE ROLE {} NOLOGIN INHERIT").format(
                    sql.Identifier(member_role)
                )
            )
            await self.admin.execute(
                sql.SQL("GRANT {} TO {}").format(
                    sql.Identifier(parent_role), sql.Identifier(member_role)
                )
            )
            await self.admin.commit()
            source_roles_created = True

            with tempfile.TemporaryDirectory() as temporary_directory:
                globals_dump = Path(temporary_directory) / "cluster-globals.sql"
                dump = await docker(
                    "exec",
                    POSTGRES_CONTAINER_ID,
                    "pg_dumpall",
                    "-U",
                    "postgres",
                    "--globals-only",
                    "--no-role-passwords",
                )
                os.chmod(temporary_directory, 0o700)
                # The destination cluster already bootstraps its postgres
                # administrator. Keep that destination-owned identity and
                # restore all other cluster-global roles and memberships.
                restore_sql = "\n".join(
                    line for line in dump.stdout.splitlines()
                    if line != "CREATE ROLE postgres;"
                    and not line.startswith("ALTER ROLE postgres ")
                ) + "\n"
                globals_dump.write_text(restore_sql, encoding="utf-8")
                os.chmod(globals_dump, 0o600)
                self.assertGreater(globals_dump.stat().st_size, 0)
                self.assertIn(f"CREATE ROLE {parent_role};", restore_sql)
                self.assertIn(f"GRANT {parent_role} TO {member_role} WITH INHERIT TRUE", restore_sql)
                self.assertNotIn("PASSWORD", restore_sql.upper())

                await docker(
                    "run",
                    "--detach",
                    "--rm",
                    "--name",
                    target_container,
                    "--publish",
                    "127.0.0.1::5432",
                    "--env",
                    "POSTGRES_PASSWORD=poc_restore_ephemeral",
                    image_digest,
                )
                target_started = True

                ready = False
                for _ in range(60):
                    probe = await asyncio.to_thread(
                        subprocess.run,
                        [
                            "docker",
                            "exec",
                            target_container,
                            "pg_isready",
                            "-U",
                            "postgres",
                            "-d",
                            "postgres",
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    if probe.returncode == 0:
                        ready = True
                        break
                    await asyncio.sleep(1)
                self.assertTrue(ready, "Clean PostgreSQL restore instance did not become ready.")

                restore = await asyncio.to_thread(
                    subprocess.run,
                    [
                        "docker",
                        "exec",
                        "-i",
                        target_container,
                        "psql",
                        "-U",
                        "postgres",
                        "-d",
                        "postgres",
                        "--set",
                        "ON_ERROR_STOP=1",
                    ],
                    input=globals_dump.read_text(encoding="utf-8"),
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    restore.returncode,
                    0,
                    f"Cluster-global role restore failed: {restore.stderr}",
                )
                self.assertNotIn("ERROR", restore.stderr.upper())

                port_result = await docker(
                    "port", target_container, "5432/tcp"
                )
                host_port = port_result.stdout.strip().rsplit(":", 1)[1]
                target_url = (
                    "postgresql://postgres:poc_restore_ephemeral@"
                    f"127.0.0.1:{host_port}/postgres"
                )
                target_connection = await psycopg.AsyncConnection.connect(
                    target_url,
                    connect_timeout=10,
                )
                roles = await target_connection.execute(
                    """
                    SELECT rolname, rolcanlogin, rolinherit
                    FROM pg_roles
                    WHERE rolname IN (%s, %s)
                    ORDER BY rolname
                    """,
                    (parent_role, member_role),
                )
                self.assertEqual(
                    await roles.fetchall(),
                    [
                        (member_role, False, True),
                        (parent_role, False, True),
                    ],
                )
                restored_superuser = await target_connection.execute(
                    "SELECT rolsuper FROM pg_roles WHERE rolname = 'postgres'"
                )
                self.assertTrue((await restored_superuser.fetchone())[0])
                membership = await target_connection.execute(
                    """
                    SELECT count(*)
                    FROM pg_auth_members membership
                    JOIN pg_roles granted ON granted.oid = membership.roleid
                    JOIN pg_roles member ON member.oid = membership.member
                    WHERE granted.rolname = %s AND member.rolname = %s
                    """,
                    (parent_role, member_role),
                )
                self.assertEqual((await membership.fetchone())[0], 1)
        finally:
            if target_connection is not None:
                await target_connection.close()
            if target_started:
                await asyncio.to_thread(
                    subprocess.run,
                    ["docker", "rm", "--force", target_container],
                    check=False,
                    capture_output=True,
                    text=True,
                )
            if source_roles_created:
                await self.admin.execute(
                    sql.SQL("REVOKE {} FROM {}").format(
                        sql.Identifier(parent_role), sql.Identifier(member_role)
                    )
                )
                await self.admin.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(
                        sql.Identifier(member_role)
                    )
                )
                await self.admin.execute(
                    sql.SQL("DROP ROLE IF EXISTS {}").format(
                        sql.Identifier(parent_role)
                    )
                )
                await self.admin.commit()

    async def test_poc_22_failed_migration_rolls_back_schema_and_history(self) -> None:
        migration_name = "poc_22_intentionally_failed.sql"
        migration_sql = """
        CREATE TABLE migration_rollback_probe (id INTEGER PRIMARY KEY);
        INSERT INTO migration_rollback_probe (id) VALUES (1);
        SELECT * FROM missing_migration_dependency;
        """

        with self.assertRaises(UndefinedTable):
            await apply_migration_sql(
                self.connection,
                migration_name,
                migration_sql,
            )
        await self.connection.rollback()

        result = await self.connection.execute(
            "SELECT to_regclass('migration_rollback_probe')"
        )
        self.assertIsNone((await result.fetchone())[0])
        result = await self.connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = %s",
            (migration_name,),
        )
        self.assertIsNone(await result.fetchone())
        await self.connection.commit()

    async def test_poc_18_read_path_exposes_machine_readable_query_plan(self) -> None:
        result = await self.connection.execute(
            """
            EXPLAIN (FORMAT JSON)
            SELECT article_id FROM articles
            WHERE source_id = %s AND external_identity = %s
            """,
            (self.source_id, "publisher:article-1"),
        )
        plan = (await result.fetchone())[0]
        self.assertIsInstance(plan, list)
        self.assertIn("Plan", plan[0])


    async def test_poc_23_reapplying_migrations_is_idempotent(self) -> None:
        migration_names = (
            "001_initial.sql",
            "002_article_last_seen.sql",
            "003_backup_payload.sql",
            "004_domain_integrity.sql",
            "005_deferred_article_revision_owner_fk.sql",
            "006_atomic_idempotency_claims.sql",
            "007_external_outcome_reconciliation.sql",
            "008_automatic_external_outcome_transitions.sql",
            "009_transaction_bound_authorization_and_rights.sql",
        )
        before = await self.connection.execute(
            "SELECT version, applied_at FROM schema_migrations ORDER BY version"
        )
        before_rows = await before.fetchall()
        self.assertEqual(len(before_rows), len(migration_names))

        await apply_migrations(self.connection, migration_names)

        after = await self.connection.execute(
            "SELECT version, applied_at FROM schema_migrations ORDER BY version"
        )
        after_rows = await after.fetchall()
        self.assertEqual(after_rows, before_rows)
        self.assertEqual(len(after_rows), len(migration_names))
        await self.connection.commit()



    async def test_poc_24_concurrent_migration_runners_serialize_and_execute_full_sql(self) -> None:
        migration_name = "poc_24_concurrent_runner.sql"
        migration_sql = """
        CREATE FUNCTION migration_runner_probe() RETURNS integer
        LANGUAGE plpgsql
        AS $migration$
        BEGIN
            RETURN 1;
        END;
        $migration$;

        CREATE TABLE migration_runner_probe_table (id INTEGER PRIMARY KEY);
        """
        second = await connect_to_schema(DATABASE_URL, self.schema)
        try:
            results = await asyncio.gather(
                apply_migration_sql(self.connection, migration_name, migration_sql),
                apply_migration_sql(second, migration_name, migration_sql),
            )
            self.assertCountEqual(results, [True, False])
            function = await self.connection.execute(
                "SELECT migration_runner_probe()"
            )
            self.assertEqual((await function.fetchone())[0], 1)
            table = await self.connection.execute(
                "SELECT to_regclass('migration_runner_probe_table')"
            )
            self.assertIsNotNone((await table.fetchone())[0])
            history = await self.connection.execute(
                "SELECT count(*) FROM schema_migrations WHERE version = %s",
                (migration_name,),
            )
            self.assertEqual((await history.fetchone())[0], 1)
        finally:
            await second.close()


    async def test_poc_25_article_current_revision_must_belong_to_same_article(self) -> None:
        revision_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO article_revisions
                (revision_id, article_id, revision_number, fingerprint)
            VALUES (%s, %s, 1, 'fingerprint-1')
            """,
            (revision_id, self.article_id),
        )
        other_article_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO articles (article_id, source_id, external_identity)
            VALUES (%s, %s, 'publisher:article-2')
            """,
            (other_article_id, self.source_id),
        )
        await self.connection.commit()

        await self.connection.execute("SET CONSTRAINTS articles_current_revision_fk IMMEDIATE")
        with self.assertRaises(ForeignKeyViolation):
            await self.connection.execute(
                "UPDATE articles SET current_revision_id = %s WHERE article_id = %s",
                (revision_id, other_article_id),
            )
        await self.connection.rollback()

        result = await self.connection.execute(
            "SELECT current_revision_id FROM articles WHERE article_id = %s",
            (other_article_id,),
        )
        self.assertIsNone((await result.fetchone())[0])

    async def test_poc_26_decision_case_and_outcome_are_constrained(self) -> None:
        with self.assertRaises(ForeignKeyViolation):
            await self.connection.execute(
                """
                INSERT INTO decision_records (decision_id, case_id, outcome)
                VALUES (%s, %s, 'OPEN')
                """,
                (uuid.uuid4(), uuid.uuid4()),
            )
        await self.connection.rollback()

        with self.assertRaises(CheckViolation):
            await self.connection.execute(
                """
                INSERT INTO decision_records (decision_id, case_id, outcome)
                VALUES (%s, %s, 'MAYBE')
                """,
                (uuid.uuid4(), self.case_id),
            )
        await self.connection.rollback()


    async def test_poc_27_source_identity_has_one_unique_lookup_index(self) -> None:
        result = await self.connection.execute(
            """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = 'articles'
              AND position('(source_id, external_identity)' in indexdef) > 0
            ORDER BY indexname
            """,
            (self.schema,),
        )
        indexes = await result.fetchall()
        self.assertEqual(len(indexes), 1)
        self.assertIn("UNIQUE", indexes[0][1].upper())
        self.assertNotEqual(indexes[0][0], "articles_source_identity_idx")

    async def test_poc_28_legacy_article_revision_backfill_is_atomic(self) -> None:
        legacy_article_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO articles (article_id, source_id, external_identity)
            VALUES (%s, %s, 'publisher:legacy-article')
            """,
            (legacy_article_id, self.source_id),
        )
        await self.connection.commit()

        legacy = await self.connection.execute(
            "SELECT current_revision_id FROM articles WHERE article_id = %s",
            (legacy_article_id,),
        )
        self.assertIsNone((await legacy.fetchone())[0])

        revision_id = uuid.uuid4()
        invalid_pointer = uuid.uuid4()
        with self.assertRaises(ForeignKeyViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO article_revisions
                        (revision_id, article_id, revision_number, fingerprint)
                    VALUES (%s, %s, 1, 'legacy-backfill-fingerprint')
                    """,
                    (revision_id, legacy_article_id),
                )
                await self.connection.execute(
                    "UPDATE articles SET current_revision_id = %s WHERE article_id = %s",
                    (invalid_pointer, legacy_article_id),
                )
                await self.connection.execute(
                    "SET CONSTRAINTS articles_current_revision_fk IMMEDIATE"
                )

        after_failure = await self.connection.execute(
            """
            SELECT a.current_revision_id,
                   (SELECT COUNT(*) FROM article_revisions r
                    WHERE r.revision_id = %s AND r.article_id = a.article_id)
            FROM articles a
            WHERE a.article_id = %s
            """,
            (revision_id, legacy_article_id),
        )
        current_revision_id, revision_count = await after_failure.fetchone()
        self.assertIsNone(current_revision_id)
        self.assertEqual(revision_count, 0)

        async with self.connection.transaction():
            await self.connection.execute(
                """
                INSERT INTO article_revisions
                    (revision_id, article_id, revision_number, fingerprint)
                VALUES (%s, %s, 1, 'legacy-backfill-fingerprint')
                """,
                (revision_id, legacy_article_id),
            )
            updated = await self.connection.execute(
                "UPDATE articles SET current_revision_id = %s WHERE article_id = %s",
                (revision_id, legacy_article_id),
            )
            self.assertEqual(updated.rowcount, 1)

        completed = await self.connection.execute(
            """
            SELECT a.current_revision_id, r.revision_number
            FROM articles a
            JOIN article_revisions r
              ON r.article_id = a.article_id
             AND r.revision_id = a.current_revision_id
            WHERE a.article_id = %s
            """,
            (legacy_article_id,),
        )
        self.assertEqual(await completed.fetchone(), (revision_id, 1))


    async def test_poc_29_concurrent_article_revision_appends_are_atomic(self) -> None:
        initial_revision_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO article_revisions
                (revision_id, article_id, revision_number, fingerprint)
            VALUES (%s, %s, 1, 'initial-article-revision')
            """,
            (initial_revision_id, self.article_id),
        )
        await self.connection.execute(
            """
            UPDATE articles
            SET current_revision_id = %s
            WHERE article_id = %s
            """,
            (initial_revision_id, self.article_id),
        )
        await self.connection.commit()

        barrier = asyncio.Event()
        ready = 0
        ready_lock = asyncio.Lock()

        class StaleArticleVersion(Exception):
            pass

        async def append_revision(
            revision_number: int,
            fingerprint: str,
        ) -> tuple[str, uuid.UUID]:
            nonlocal ready
            connection = await connect_to_schema(DATABASE_URL, self.schema)
            revision_id = uuid.uuid4()
            try:
                async with ready_lock:
                    ready += 1
                    if ready == 2:
                        barrier.set()
                await barrier.wait()

                try:
                    async with connection.transaction():
                        await connection.execute(
                            """
                            INSERT INTO article_revisions
                                (revision_id, article_id, revision_number, fingerprint)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (
                                revision_id,
                                self.article_id,
                                revision_number,
                                fingerprint,
                            ),
                        )
                        updated = await connection.execute(
                            """
                            UPDATE articles
                            SET current_revision_id = %s, version = version + 1
                            WHERE article_id = %s AND version = 1
                            """,
                            (revision_id, self.article_id),
                        )
                        if updated.rowcount != 1:
                            raise StaleArticleVersion
                    return ("committed", revision_id)
                except StaleArticleVersion:
                    return ("conflict", revision_id)
            finally:
                await connection.close()

        outcomes = await asyncio.gather(
            append_revision(2, "concurrent-revision-a"),
            append_revision(3, "concurrent-revision-b"),
        )
        self.assertCountEqual([outcome[0] for outcome in outcomes], ["committed", "conflict"])

        current = await self.connection.execute(
            """
            SELECT a.version, a.current_revision_id, r.revision_number,
                   (SELECT COUNT(*) FROM article_revisions all_revisions
                    WHERE all_revisions.article_id = a.article_id)
            FROM articles a
            JOIN article_revisions r
              ON r.article_id = a.article_id
             AND r.revision_id = a.current_revision_id
            WHERE a.article_id = %s
            """,
            (self.article_id,),
        )
        version, current_revision_id, revision_number, revision_count = (
            await current.fetchone()
        )
        self.assertEqual(version, 2)
        self.assertEqual(revision_count, 2)
        self.assertEqual(revision_number, 2 if outcomes[0][0] == "committed" else 3)
        self.assertIn(
            current_revision_id,
            {outcome[1] for outcome in outcomes if outcome[0] == "committed"},
        )


    async def test_poc_30_new_article_revision_and_projection_commit_atomically(self) -> None:
        article_id = uuid.uuid4()
        revision_id = uuid.uuid4()

        # The application service appends the revision before saving a new
        # Article projection. The owner FK must therefore be deferred until
        # the shared UnitOfWork commits.
        async with self.connection.transaction():
            await self.connection.execute(
                """
                INSERT INTO article_revisions
                    (revision_id, article_id, revision_number, fingerprint)
                VALUES (%s, %s, 1, 'new-article-fingerprint')
                """,
                (revision_id, article_id),
            )
            await self.connection.execute(
                """
                INSERT INTO articles
                    (article_id, source_id, external_identity, current_revision_id)
                VALUES (%s, %s, 'publisher:new-article', %s)
                """,
                (article_id, self.source_id, revision_id),
            )

        result = await self.connection.execute(
            """
            SELECT a.current_revision_id, r.revision_id
            FROM articles a
            JOIN article_revisions r
              ON r.article_id = a.article_id
             AND r.revision_id = a.current_revision_id
            WHERE a.article_id = %s
            """,
            (article_id,),
        )
        self.assertEqual(await result.fetchone(), (revision_id, revision_id))
        await self.connection.commit()

        orphan_revision_id = uuid.uuid4()
        missing_article_id = uuid.uuid4()
        with self.assertRaises(ForeignKeyViolation):
            async with self.connection.transaction():
                await self.connection.execute(
                    """
                    INSERT INTO article_revisions
                        (revision_id, article_id, revision_number, fingerprint)
                    VALUES (%s, %s, 1, 'orphan-fingerprint')
                    """,
                    (orphan_revision_id, missing_article_id),
                )

        result = await self.connection.execute(
            "SELECT 1 FROM article_revisions WHERE revision_id = %s",
            (orphan_revision_id,),
        )
        self.assertIsNone(await result.fetchone())


    async def test_poc_35_authorization_revocation_serializes_after_protected_commit(self) -> None:
        now = "2026-11-27T12:00:00+00:00"
        await self.connection.execute(
            """
            INSERT INTO poc_authorization_grants
                (grant_reference, actor_reference, action, resource_reference, status, effective_from)
            VALUES ('grant-1', 'service:collector', 'article.revision.persist',
                    'source:source-test', 'ACTIVE', %s)
            """,
            (now,),
        )
        await self.connection.commit()
        checker = await connect_to_schema(DATABASE_URL, self.schema)
        revoker = await connect_to_schema(DATABASE_URL, self.schema)
        try:
            await revoker.execute("SET lock_timeout = '100ms'")
            await revoker.commit()
            async with checker.transaction():
                grant = await checker.execute(
                    """
                    SELECT status, version FROM poc_authorization_grants
                    WHERE grant_reference = 'grant-1'
                      AND actor_reference = 'service:collector'
                      AND action = 'article.revision.persist'
                      AND resource_reference = 'source:source-test'
                      AND effective_from <= %s
                    FOR SHARE
                    """,
                    (now,),
                )
                self.assertEqual(await grant.fetchone(), ("ACTIVE", 1))
                await checker.execute(
                    """
                    INSERT INTO protected_state (resource_id, fencing_token, value)
                    VALUES ('authorization-protected-write', 1, 'committed-before-revoke')
                    """
                )
                with self.assertRaises(LockNotAvailable):
                    async with revoker.transaction():
                        await revoker.execute(
                            """
                            UPDATE poc_authorization_grants
                            SET status = 'REVOKED', version = version + 1
                            WHERE grant_reference = 'grant-1'
                            """
                        )
            async with revoker.transaction():
                await revoker.execute(
                    """
                    UPDATE poc_authorization_grants
                    SET status = 'REVOKED', version = version + 1
                    WHERE grant_reference = 'grant-1'
                    """
                )
            persisted = await self.connection.execute(
                "SELECT value FROM protected_state WHERE resource_id = 'authorization-protected-write'"
            )
            self.assertEqual((await persisted.fetchone())[0], "committed-before-revoke")
            revoked = await self.connection.execute(
                """
                SELECT status, version FROM poc_authorization_grants
                WHERE grant_reference = 'grant-1'
                """
            )
            self.assertEqual(await revoked.fetchone(), ("REVOKED", 2))
        finally:
            await checker.close()
            await revoker.close()

    async def test_poc_36_authorization_revocation_committed_before_check_is_denied(self) -> None:
        now = "2026-11-27T12:00:00+00:00"
        await self.connection.execute(
            """
            INSERT INTO poc_authorization_grants
                (grant_reference, actor_reference, action, resource_reference, status, effective_from)
            VALUES ('grant-2', 'service:collector', 'article.revision.persist',
                    'source:source-test', 'ACTIVE', %s)
            """,
            (now,),
        )
        await self.connection.commit()
        await self.connection.execute(
            """
            UPDATE poc_authorization_grants
            SET status = 'REVOKED', version = version + 1
            WHERE grant_reference = 'grant-2'
            """
        )
        await self.connection.commit()
        async with self.connection.transaction():
            result = await self.connection.execute(
                """
                SELECT status, version FROM poc_authorization_grants
                WHERE grant_reference = 'grant-2'
                FOR SHARE
                """
            )
            self.assertEqual(await result.fetchone(), ("REVOKED", 2))

    async def test_poc_37_content_rights_revocation_serializes_after_protected_commit(self) -> None:
        now = "2026-11-27T12:00:00+00:00"
        fingerprint = "a" * 64
        await self.connection.execute(
            """
            INSERT INTO poc_content_rights_assessments
                (assessment_reference, source_id, content_scope_fingerprint, operation,
                 policy_version, rights_profile_reference, status, effective_from)
            VALUES ('rights-1', %s, %s, 'PERSISTENT_STORAGE', 'policy-v1',
                    'profile-v1', 'ALLOWED', %s)
            """,
            (self.source_id, fingerprint, now),
        )
        await self.connection.commit()
        checker = await connect_to_schema(DATABASE_URL, self.schema)
        revoker = await connect_to_schema(DATABASE_URL, self.schema)
        try:
            await revoker.execute("SET lock_timeout = '100ms'")
            await revoker.commit()
            async with checker.transaction():
                assessment = await checker.execute(
                    """
                    SELECT status, policy_version, version
                    FROM poc_content_rights_assessments
                    WHERE assessment_reference = 'rights-1'
                      AND source_id = %s
                      AND content_scope_fingerprint = %s
                      AND operation = 'PERSISTENT_STORAGE'
                      AND effective_from <= %s
                    FOR SHARE
                    """,
                    (self.source_id, fingerprint, now),
                )
                self.assertEqual(await assessment.fetchone(), ("ALLOWED", "policy-v1", 1))
                await checker.execute(
                    """
                    INSERT INTO protected_state (resource_id, fencing_token, value)
                    VALUES ('rights-protected-write', 1, 'stored-before-revocation')
                    """
                )
                with self.assertRaises(LockNotAvailable):
                    async with revoker.transaction():
                        await revoker.execute(
                            """
                            UPDATE poc_content_rights_assessments
                            SET status = 'REVOKED', version = version + 1
                            WHERE assessment_reference = 'rights-1'
                            """
                        )
            async with revoker.transaction():
                await revoker.execute(
                    """
                    UPDATE poc_content_rights_assessments
                    SET status = 'REVOKED', version = version + 1
                    WHERE assessment_reference = 'rights-1'
                    """
                )
            persisted = await self.connection.execute(
                "SELECT value FROM protected_state WHERE resource_id = 'rights-protected-write'"
            )
            self.assertEqual((await persisted.fetchone())[0], "stored-before-revocation")
            revoked = await self.connection.execute(
                """
                SELECT status, version FROM poc_content_rights_assessments
                WHERE assessment_reference = 'rights-1'
                """
            )
            self.assertEqual(await revoked.fetchone(), ("REVOKED", 2))
        finally:
            await checker.close()
            await revoker.close()

    async def test_poc_38_content_rights_revocation_committed_before_check_is_denied(self) -> None:
        now = "2026-11-27T12:00:00+00:00"
        await self.connection.execute(
            """
            INSERT INTO poc_content_rights_assessments
                (assessment_reference, source_id, content_scope_fingerprint, operation,
                 policy_version, rights_profile_reference, status, effective_from)
            VALUES ('rights-2', %s, %s, 'PERSISTENT_STORAGE', 'policy-v1',
                    'profile-v1', 'ALLOWED', %s)
            """,
            (self.source_id, "b" * 64, now),
        )
        await self.connection.commit()
        await self.connection.execute(
            """
            UPDATE poc_content_rights_assessments
            SET status = 'REVOKED', version = version + 1
            WHERE assessment_reference = 'rights-2'
            """
        )
        await self.connection.commit()
        async with self.connection.transaction():
            result = await self.connection.execute(
                """
                SELECT status, version FROM poc_content_rights_assessments
                WHERE assessment_reference = 'rights-2'
                FOR SHARE
                """
            )
            self.assertEqual(await result.fetchone(), ("REVOKED", 2))

    async def test_poc_39_article_revision_payload_schema_preserves_typed_json(self) -> None:
        article_id = uuid.uuid4()
        revision_id = uuid.uuid4()
        payload = {
            "source_id": self.source_id,
            "source_article_identity": {
                "canonical_source_identifier": "publisher:payload-1",
                "normalization_version": "identity-v1",
                "canonical_url": "https://example.test/article/1",
            },
            "original_url": "https://example.test/original/1",
            "external_id": "external-1",
            "normalized_title": "Synthetic economic report",
            "content_availability": "metadata-only",
            "content_reference": None,
            "content_hash": None,
            "content_normalization_version": None,
            "summary": "Synthetic summary",
            "author": "Test Author",
            "language": "en",
            "published_at": "2026-11-27T12:00:00.000Z",
            "observed_at": "2026-11-27T12:01:00.000Z",
            "change_reason": "INITIAL_INGESTION",
            "rights_assessment_references": ["rights-test-1"],
            "metadata": {"publisher": "Example", "tags": ["economics", "policy"]},
        }
        async with self.connection.transaction():
            await self.connection.execute(
                """
                INSERT INTO articles
                    (article_id, source_id, external_identity,
                     canonical_source_identifier, identity_normalization_version,
                     canonical_url, original_url, title, content_availability,
                     article_metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                """,
                (
                    article_id,
                    self.source_id,
                    "publisher:payload-1",
                    "publisher:payload-1",
                    "identity-v1",
                    "https://example.test/article/1",
                    "https://example.test/original/1",
                    "Synthetic economic report",
                    "metadata-only",
                    json.dumps(payload["metadata"]),
                ),
            )
            await self.connection.execute(
                """
                INSERT INTO article_revisions
                    (revision_id, article_id, revision_number, fingerprint,
                     revision_payload, revision_fingerprint_schema_version)
                VALUES (%s, %s, 1, %s, %s::jsonb, %s)
                """,
                (
                    revision_id,
                    article_id,
                    "a" * 64,
                    json.dumps(payload),
                    "article-revision-fingerprint-v1",
                ),
            )
            await self.connection.execute(
                "UPDATE articles SET current_revision_id = %s WHERE article_id = %s",
                (revision_id, article_id),
            )

        stored = await self.connection.execute(
            """
            SELECT revision_payload, revision_fingerprint_schema_version
            FROM article_revisions WHERE revision_id = %s
            """,
            (revision_id,),
        )
        stored_payload, stored_schema = await stored.fetchone()
        self.assertEqual(stored_payload, payload)
        self.assertEqual(stored_schema, "article-revision-fingerprint-v1")

        identity_conflict = await self.connection.execute(
            """
            INSERT INTO articles
                (article_id, source_id, external_identity,
                 canonical_source_identifier, identity_normalization_version)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_id, canonical_source_identifier,
                         identity_normalization_version) DO NOTHING
            RETURNING article_id
            """,
            (
                uuid.uuid4(),
                self.source_id,
                "publisher:payload-1",
                "publisher:payload-1",
                "identity-v1",
            ),
        )
        self.assertIsNone(await identity_conflict.fetchone())

    async def test_poc_40_idempotency_result_payload_round_trips_exact_service_result(self) -> None:
        result_id = uuid.uuid4()
        result_payload = {
            "article_id": str(uuid.uuid4()),
            "revision_id": str(result_id),
            "created": True,
            "article_version": "2",
        }
        async with self.connection.transaction():
            await self.connection.execute(
                """
                INSERT INTO idempotency_records
                    (operation_scope, idempotency_key, request_fingerprint,
                     result_id, state, completed_at)
                VALUES (%s, %s, %s, NULL, 'CLAIMED', NULL)
                """,
                ("article.revision.persist", "payload-key", "f" * 64),
            )
            await self.connection.execute(
                """
                UPDATE idempotency_records
                SET result_id = %s,
                    result_payload = %s::jsonb,
                    state = 'COMPLETED',
                    completed_at = clock_timestamp()
                WHERE operation_scope = %s AND idempotency_key = %s
                  AND state = 'CLAIMED'
                """,
                (
                    result_id,
                    json.dumps(result_payload),
                    "article.revision.persist",
                    "payload-key",
                ),
            )

        stored = await self.connection.execute(
            """
            SELECT result_id, result_payload, state
            FROM idempotency_records
            WHERE operation_scope = %s AND idempotency_key = %s
            """,
            ("article.revision.persist", "payload-key"),
        )
        stored_id, stored_payload, state = await stored.fetchone()
        self.assertEqual(stored_id, result_id)
        self.assertEqual(stored_payload, result_payload)
        self.assertEqual(state, "COMPLETED")

if __name__ == "__main__":
    unittest.main()
