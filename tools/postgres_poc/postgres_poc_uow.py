"""Synchronous PostgreSQL UnitOfWork used only by the isolated persistence PoC.

This adapter is intentionally outside the production package and must not be
imported by the application runtime.
"""

from __future__ import annotations

from threading import get_ident
from typing import Any

import psycopg
from psycopg import sql

from global_economic_news_intelligence.domain.contracts import CommitResult


class PostgreSQLUnitOfWork:
    """Single-use, connection-owning transaction bound to its creating thread."""

    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection
        self._owner_thread = get_ident()
        self._state = "ACTIVE"

    @property
    def state(self) -> str:
        return self._state

    @property
    def connection(self) -> psycopg.Connection[Any]:
        """Expose the owned connection to PoC repositories while the UoW is active."""
        self._require_active_owner()
        return self._connection

    def _require_active_owner(self) -> None:
        if get_ident() != self._owner_thread:
            raise RuntimeError("PostgreSQL UnitOfWork cannot cross execution threads.")
        if self._state != "ACTIVE":
            raise RuntimeError(f"PostgreSQL UnitOfWork is {self._state.lower()}.")

    def commit(self) -> CommitResult:
        self._require_active_owner()
        # If commit raises, retain ACTIVE so the service's exception handler can
        # explicitly roll back and close the connection without masking the error.
        self._connection.commit()
        self._connection.close()
        self._state = "COMMITTED"
        return CommitResult()

    def rollback(self) -> None:
        self._require_active_owner()
        try:
            self._connection.rollback()
        finally:
            self._connection.close()
            self._state = "ROLLED_BACK"


class PostgreSQLUnitOfWorkFactory:
    """Creates a fresh synchronous connection scoped to one isolated PoC schema."""

    def __init__(self, *, database_url: str, schema: str) -> None:
        if not isinstance(database_url, str) or not database_url.strip():
            raise ValueError("database_url must be a non-empty string.")
        if not isinstance(schema, str) or not schema.strip():
            raise ValueError("schema must be a non-empty string.")
        self._database_url = database_url
        self._schema = schema

    def begin(self) -> PostgreSQLUnitOfWork:
        connection = psycopg.connect(self._database_url)
        try:
            connection.execute(
                sql.SQL("SET search_path TO {}").format(sql.Identifier(self._schema))
            )
            connection.commit()
            connection.execute("BEGIN")
            return PostgreSQLUnitOfWork(connection)
        except BaseException:
            connection.close()
            raise
