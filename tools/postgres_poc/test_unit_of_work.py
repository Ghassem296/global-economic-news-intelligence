from __future__ import annotations

import os
import unittest
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import psycopg

from postgres_poc_uow import PostgreSQLUnitOfWork, PostgreSQLUnitOfWorkFactory
from psycopg import sql

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
    "010_article_revision_service_payload.sql",
    "011_idempotency_result_payload.sql",
)


@unittest.skipUnless(
    DATABASE_URL and POSTGRES_CONTAINER_ID,
    "PostgreSQL PoC database/container environment is not configured",
)
class PostgreSQLUnitOfWorkPoCTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = f"uow_{uuid.uuid4().hex}"
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

            self.factory = PostgreSQLUnitOfWorkFactory(
                database_url=DATABASE_URL,
                schema=self.schema,
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


class PostgreSQLUnitOfWorkFailureTests(unittest.TestCase):
    def test_rollback_error_is_not_masked_by_connection_close_error(self) -> None:
        connection = Mock()
        connection.rollback.side_effect = RuntimeError("rollback failed")
        connection.close.side_effect = OSError("close failed")
        uow = PostgreSQLUnitOfWork(connection)

        with self.assertRaisesRegex(RuntimeError, "rollback failed"):
            uow.rollback()

        self.assertEqual(uow.state, "ROLLED_BACK")
        connection.rollback.assert_called_once_with()
        connection.close.assert_called_once_with()

    def test_successful_rollback_reports_connection_close_error(self) -> None:
        connection = Mock()
        connection.close.side_effect = OSError("close failed")
        uow = PostgreSQLUnitOfWork(connection)

        with self.assertRaisesRegex(OSError, "close failed"):
            uow.rollback()

        self.assertEqual(uow.state, "ROLLED_BACK")
        connection.rollback.assert_called_once_with()
        connection.close.assert_called_once_with()

    def test_commit_close_error_keeps_committed_state(self) -> None:
        connection = Mock()
        connection.close.side_effect = OSError("close failed after commit")
        uow = PostgreSQLUnitOfWork(connection)

        with self.assertRaisesRegex(OSError, "close failed after commit"):
            uow.commit()

        self.assertEqual(uow.state, "COMMITTED")
        connection.commit.assert_called_once_with()
        connection.close.assert_called_once_with()

