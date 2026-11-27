from __future__ import annotations

import os
import unittest
import uuid
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql

from postgres_poc_uow import PostgreSQLUnitOfWorkFactory

DATABASE_URL = os.environ.get("GENI_POC_DATABASE_URL", "")
POSTGRES_CONTAINER_ID = os.environ.get("GENI_POC_POSTGRES_CONTAINER_ID", "")
MIGRATIONS = Path(__file__).parent / "migrations"
MIGRATION_NAMES = (
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


@unittest.skipUnless(
    DATABASE_URL and POSTGRES_CONTAINER_ID,
    "PostgreSQL PoC database/container environment is not configured",
)
class PostgreSQLUnitOfWorkPoCTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = f"uow_{uuid.uuid4().hex}"
        self.admin: psycopg.Connection[Any] = psycopg.connect(DATABASE_URL)
        self.admin.execute(
            sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(self.schema))
        )
        self.admin.commit()

        migration_connection = psycopg.connect(DATABASE_URL)
        try:
            migration_connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self.schema))
            )
            migration_connection.commit()
            with migration_connection.transaction():
                for migration_name in MIGRATION_NAMES:
                    migration_sql = (MIGRATIONS / migration_name).read_text(
                        encoding="utf-8"
                    )
                    migration_connection.execute(migration_sql, prepare=False)
        finally:
            migration_connection.close()

        self.factory = PostgreSQLUnitOfWorkFactory(
            database_url=DATABASE_URL,
            schema=self.schema,
        )

    def tearDown(self) -> None:
        self.admin.execute(
            sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                sql.Identifier(self.schema)
            )
        )
        self.admin.commit()
        self.admin.close()

    def test_commit_persists_write_and_closes_single_use_uow(self) -> None:
        uow = self.factory.begin()
        uow.connection.execute(
            "INSERT INTO counters (counter_name, value) VALUES ('uow-commit', 1)"
        )

        result = uow.commit()

        self.assertEqual(result.status.value, "COMMITTED")
        self.assertEqual(uow.state, "COMMITTED")
        with self.assertRaises(RuntimeError):
            uow.commit()
        with self.assertRaises(RuntimeError):
            uow.rollback()

        row = self.admin.execute(
            sql.SQL("SELECT value FROM {}.counters WHERE counter_name = %s").format(
                sql.Identifier(self.schema)
            ),
            ("uow-commit",),
        ).fetchone()
        self.assertEqual(row, (1,))

    def test_rollback_discards_write_and_closes_single_use_uow(self) -> None:
        uow = self.factory.begin()
        uow.connection.execute(
            "INSERT INTO counters (counter_name, value) VALUES ('uow-rollback', 1)"
        )

        uow.rollback()

        self.assertEqual(uow.state, "ROLLED_BACK")
        with self.assertRaises(RuntimeError):
            uow.commit()
        with self.assertRaises(RuntimeError):
            uow.rollback()
        row = self.admin.execute(
            sql.SQL("SELECT value FROM {}.counters WHERE counter_name = %s").format(
                sql.Identifier(self.schema)
            ),
            ("uow-rollback",),
        ).fetchone()
        self.assertIsNone(row)

    def test_uow_rejects_cross_thread_use(self) -> None:
        from concurrent.futures import ThreadPoolExecutor

        uow = self.factory.begin()
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(uow.rollback)
                with self.assertRaises(RuntimeError):
                    future.result()
        finally:
            uow.rollback()
