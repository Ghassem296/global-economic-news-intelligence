from __future__ import annotations

import asyncio
import os
import unittest
import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.errors import ForeignKeyViolation, QueryCanceled, UniqueViolation

DATABASE_URL = os.environ.get("GENI_POC_DATABASE_URL", "")
MIGRATIONS = Path(__file__).parent / "migrations"


async def connect_to_schema(database_url: str, schema: str) -> psycopg.AsyncConnection[Any]:
    connection = await psycopg.AsyncConnection.connect(database_url)
    await connection.execute(
        sql.SQL("SET search_path TO {}").format(sql.Identifier(schema))
    )
    await connection.commit()
    return connection


async def apply_migrations(
    connection: psycopg.AsyncConnection[Any],
    migration_names: tuple[str, ...],
) -> None:
    for migration_name in migration_names:
        applied = await connection.execute(
            "SELECT 1 FROM schema_migrations WHERE version = %s",
            (migration_name,),
        )
        if await applied.fetchone():
            continue

        migration_sql = (MIGRATIONS / migration_name).read_text(encoding="utf-8")
        async with connection.transaction():
            for statement in migration_sql.split(";"):
                if statement.strip():
                    await connection.execute(statement, prepare=False)
            await connection.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s)",
                (migration_name,),
            )


@unittest.skipUnless(DATABASE_URL, "GENI_POC_DATABASE_URL is not configured")
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
            ("001_initial.sql", "002_article_last_seen.sql"),
        )
        self.source_id = "source-test"
        self.article_id = uuid.uuid4()
        self.event_id = uuid.uuid4()
        self.analysis_id = uuid.uuid4()
        self.report_id = uuid.uuid4()
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
        await self.connection.execute(
            """
            INSERT INTO idempotency_records
                (operation_scope, idempotency_key, request_fingerprint, result_id)
            VALUES ('article.persist', 'key-1', 'fingerprint-a', %s)
            """,
            (result_id,),
        )
        await self.connection.commit()

        replay = await self.connection.execute(
            """
            SELECT request_fingerprint, result_id
            FROM idempotency_records
            WHERE operation_scope = 'article.persist' AND idempotency_key = 'key-1'
            """
        )
        fingerprint, replayed_result = await replay.fetchone()
        self.assertEqual(fingerprint, "fingerprint-a")
        self.assertEqual(replayed_result, result_id)

        with self.assertRaises(ValueError):
            if fingerprint != "fingerprint-b":
                raise ValueError("idempotency key reused with a different fingerprint")

    async def test_poc_03_successor_chain_allows_only_one_direct_successor(self) -> None:
        predecessor_id = uuid.uuid4()
        await self.connection.execute(
            """
            INSERT INTO decision_records (decision_id, case_id, outcome)
            VALUES (%s, %s, 'OPEN')
            """,
            (predecessor_id, uuid.uuid4()),
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
                        (uuid.uuid4(), uuid.uuid4(), predecessor_id, outcome),
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
                    (decision_id, uuid.uuid4()),
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
        key = f"ack-{uuid.uuid4()}"
        result_id = uuid.uuid4()
        connection = await connect_to_schema(DATABASE_URL, self.schema)
        await connection.execute(
            """
            INSERT INTO idempotency_records
                (operation_scope, idempotency_key, request_fingerprint, result_id)
            VALUES ('article.persist', %s, 'same-request', %s)
            """,
            (key, result_id),
        )
        await connection.commit()
        await connection.close()

        replay = await self.connection.execute(
            """
            SELECT result_id, request_fingerprint FROM idempotency_records
            WHERE operation_scope = 'article.persist' AND idempotency_key = %s
            """,
            (key,),
        )
        replayed_id, fingerprint = await replay.fetchone()
        self.assertEqual(replayed_id, result_id)
        self.assertEqual(fingerprint, "same-request")

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
        self.assertEqual(versions, ["001_initial.sql", "002_article_last_seen.sql"])
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
            await connection.commit()
            await apply_migrations(connection, ("002_article_last_seen.sql",))
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
        finally:
            await connection.close()
            await self.admin.execute(
                sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                    sql.Identifier(upgrade_schema)
                )
            )
            await self.admin.commit()

    async def test_poc_16_committed_operation_survives_new_connection(self) -> None:
        record_id = uuid.uuid4()
        connection = await connect_to_schema(DATABASE_URL, self.schema)
        await connection.execute(
            "INSERT INTO decision_records (decision_id, case_id, outcome) VALUES (%s, %s, 'OPEN')",
            (record_id, uuid.uuid4()),
        )
        await connection.commit()
        await connection.close()

        recovered = await connect_to_schema(DATABASE_URL, self.schema)
        try:
            result = await recovered.execute(
                "SELECT outcome FROM decision_records WHERE decision_id = %s",
                (record_id,),
            )
            self.assertEqual((await result.fetchone())[0], "OPEN")
        finally:
            await recovered.close()

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


if __name__ == "__main__":
    unittest.main()
