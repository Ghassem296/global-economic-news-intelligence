from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.domain.contracts import (
    CommandMetadata,
    CommitResult,
    CommitStatus,
    Page,
    UnitOfWork,
    UnitOfWorkFactory,
)


def valid_metadata(**overrides: object) -> CommandMetadata:
    values: dict[str, object] = {
        "command_id": "cmd-1",
        "schema_version": "1",
        "actor_reference": "actor-1",
        "authorization_reference": "auth-1",
        "correlation_id": "corr-1",
        "idempotency_key": "scope:key-1",
    }
    values.update(overrides)
    return CommandMetadata(**values)  # type: ignore[arg-type]


def test_command_metadata_accepts_complete_trusted_context() -> None:
    metadata = valid_metadata(
        causation_id="cause-1",
        expected_aggregate_version="v7",
        deadline=datetime(2026, 11, 26, 12, 0, tzinfo=UTC),
    )
    assert metadata.command_id == "cmd-1"
    assert metadata.expected_aggregate_version == "v7"


@pytest.mark.parametrize(
    "field_name",
    (
        "command_id",
        "schema_version",
        "actor_reference",
        "authorization_reference",
        "correlation_id",
        "idempotency_key",
    ),
)
def test_command_metadata_rejects_missing_required_context(field_name: str) -> None:
    with pytest.raises(ValueError, match=field_name):
        valid_metadata(**{field_name: "  "})


def test_command_metadata_rejects_empty_optional_references() -> None:
    with pytest.raises(ValueError, match="causation_id"):
        valid_metadata(causation_id=" ")
    with pytest.raises(ValueError, match="expected_aggregate_version"):
        valid_metadata(expected_aggregate_version="")


def test_command_metadata_requires_timezone_aware_deadline() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        valid_metadata(deadline=datetime(2026, 11, 26, 12, 0))


def test_page_preserves_order_and_optional_cursor() -> None:
    page = Page(items=("first", "second"), next_cursor="cursor-2")
    assert page.items == ("first", "second")
    assert page.next_cursor == "cursor-2"


def test_page_rejects_mutable_items() -> None:
    with pytest.raises(TypeError, match="immutable tuple"):
        Page(items=["mutable"])  # type: ignore[arg-type]


def test_page_rejects_empty_cursor() -> None:
    with pytest.raises(ValueError, match="next_cursor"):
        Page(items=(), next_cursor=" ")


def test_commit_result_is_explicit() -> None:
    assert CommitResult().status is CommitStatus.COMMITTED


def test_unit_of_work_contract_is_structurally_implementable() -> None:
    class FakeUnitOfWork:
        def __init__(self) -> None:
            self.committed = False
            self.rolled_back = False

        def commit(self) -> CommitResult:
            self.committed = True
            return CommitResult()

        def rollback(self) -> None:
            self.rolled_back = True

    class FakeFactory:
        def begin(self) -> UnitOfWork:
            return FakeUnitOfWork()

    factory: UnitOfWorkFactory = FakeFactory()
    transaction = factory.begin()
    assert transaction.commit().status is CommitStatus.COMMITTED
    assert isinstance(transaction, FakeUnitOfWork)
    assert transaction.committed
