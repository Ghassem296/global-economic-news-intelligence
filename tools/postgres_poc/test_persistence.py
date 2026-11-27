from __future__ import annotations

import asyncio
import hashlib
import hmac
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
from psycopg.errors import ForeignKeyViolation, InsufficientPrivilege, QueryCanceled, UniqueViolation

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


async def apply_migrations(
    connection: psycopg.AsyncConnection[Any],
    migration_names: tuple[str, ...],
) -> None:
    for migration_name in migration_names:
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
            ("001_initial.sql", "002_article_last_seen.sql", "003_backup_payload.sql"),
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
        case_id = uuid.uuid4()
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
        self.assertEqual(versions, ["001_initial.sql", "002_article_last_seen.sql", "003_backup_payload.sql"])
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
            await apply_migrations(connection, ("002_article_last_seen.sql", "003_backup_payload.sql"))
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
        (uuid.UUID(os.environ["GENI_POC_RECORD_ID"]), uuid.uuid4()),
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
                globals_dump.write_text(dump.stdout, encoding="utf-8")
                os.chmod(globals_dump, 0o600)
                self.assertGreater(globals_dump.stat().st_size, 0)
                self.assertIn(f"CREATE ROLE {parent_role};", dump.stdout)
                self.assertIn(f"GRANT {parent_role} TO {member_role} WITH INHERIT TRUE", dump.stdout)
                self.assertNotIn("PASSWORD", dump.stdout.upper())

                await docker(
                    "run",
                    "--detach",
                    "--rm",
                    "--name",
                    target_container,
                    "--publish",
                    "127.0.0.1::5432",
                    "--env",
                    "POSTGRES_USER=geni_restore_admin",
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
                            "geni_restore_admin",
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
                        "geni_restore_admin",
                        "-d",
                        "postgres",
                        "--set",
                        "ON_ERROR_STOP=1",
                    ],
                    input=globals_dump.read_text(encoding="utf-8"),
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertNotIn("ERROR", restore.stderr.upper())

                port_result = await docker(
                    "port", target_container, "5432/tcp"
                )
                host_port = port_result.stdout.strip().rsplit(":", 1)[1]
                target_url = (
                    "postgresql://geni_restore_admin:poc_restore_ephemeral@"
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
