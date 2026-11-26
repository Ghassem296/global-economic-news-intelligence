"""Technology-neutral command, query, and transaction contracts.

These contracts intentionally contain no database, ORM, transport, or provider
implementation. Concrete persistence behavior belongs to infrastructure adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CommandMetadata:
    """Trusted metadata required by every state-changing application command."""

    command_id: str
    schema_version: str
    actor_reference: str
    authorization_reference: str
    correlation_id: str
    idempotency_scope: str
    idempotency_key: str
    causation_id: str | None = None
    expected_aggregate_version: str | None = None
    deadline: datetime | None = None

    def __post_init__(self) -> None:
        required = (
            "command_id",
            "schema_version",
            "actor_reference",
            "authorization_reference",
            "correlation_id",
            "idempotency_scope",
            "idempotency_key",
        )
        for field_name in required:
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")

        if self.causation_id is not None and not self.causation_id.strip():
            raise ValueError("causation_id must be non-empty when supplied.")
        if (
            self.expected_aggregate_version is not None
            and not self.expected_aggregate_version.strip()
        ):
            raise ValueError(
                "expected_aggregate_version must be non-empty when supplied."
            )
        if self.deadline is not None and self.deadline.utcoffset() is None:
            raise ValueError("deadline must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class PageRequest:
    """Bounded query request; cursor interpretation remains repository-specific."""

    limit: int
    cursor: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.limit, bool) or self.limit <= 0:
            raise ValueError("limit must be a positive integer.")
        if self.cursor is not None and not self.cursor.strip():
            raise ValueError("cursor must be non-empty when supplied.")


@dataclass(frozen=True, slots=True)
class Page[T]:
    """Stable, bounded query result with an opaque continuation cursor."""

    items: tuple[T, ...]
    next_cursor: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise TypeError("items must be an immutable tuple.")
        if self.next_cursor is not None and not self.next_cursor.strip():
            raise ValueError("next_cursor must be non-empty when supplied.")


class CommitStatus(StrEnum):
    COMMITTED = "COMMITTED"


@dataclass(frozen=True, slots=True)
class CommitResult:
    """Acknowledgement that the complete local write set committed atomically."""

    status: CommitStatus = CommitStatus.COMMITTED


class UnitOfWork(Protocol):
    """Single-use transaction boundary shared by all participating repositories."""

    def commit(self) -> CommitResult:
        """Atomically commit every participating local write."""
        ...

    def rollback(self) -> None:
        """Abort the active transaction without exposing partial local writes."""
        ...


class UnitOfWorkFactory(Protocol):
    """Creates a fresh UnitOfWork; implementations own transaction startup."""

    def begin(self) -> UnitOfWork:
        """Begin and return a new single-use transaction."""
        ...
