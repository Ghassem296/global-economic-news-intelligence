from __future__ import annotations

from typing import Any

import pytest

from global_economic_news_intelligence.application.repositories import ArticleRepository
from global_economic_news_intelligence.domain.article_revision_contracts import (
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import CommitResult, UnitOfWork


class FakeUnitOfWork:
    def commit(self) -> CommitResult:
        raise AssertionError("Repositories must not commit the caller's UnitOfWork.")

    def rollback(self) -> None:
        raise AssertionError("Rollback is owned by the application service.")


class FakeArticleRepository:
    def __init__(self) -> None:
        self.article: dict[str, Any] = {
            "id": "article-1",
            "source_id": "source-1",
            "current_revision_id": "revision-1",
        }
        self.saved_expected_version: str | None = None
        self.saved_uow: UnitOfWork | None = None

    def get_by_id(
        self, article_id: str, uow: UnitOfWork | None = None
    ) -> dict[str, Any] | None:
        return self.article if article_id == self.article["id"] else None

    def find_by_source_identity(
        self,
        source_id: str,
        external_identity: SourceArticleIdentity,
        uow: UnitOfWork | None = None,
    ) -> dict[str, Any] | None:
        if (
            source_id == self.article["source_id"]
            and external_identity.canonical_source_identifier == "publisher:123"
        ):
            return self.article
        return None

    def save_projection(
        self,
        article: dict[str, Any],
        expected_version: str | None,
        uow: UnitOfWork,
    ) -> dict[str, Any]:
        self.saved_expected_version = expected_version
        self.saved_uow = uow
        self.article = article
        return self.article


def test_article_repository_protocol_is_structurally_implementable() -> None:
    repository = FakeArticleRepository()

    assert isinstance(repository, ArticleRepository)


def test_article_repository_resolves_source_scoped_identity() -> None:
    repository = FakeArticleRepository()
    identity = SourceArticleIdentity("publisher:123", "source-id-v1")

    uow = FakeUnitOfWork()
    assert repository.find_by_source_identity("source-1", identity, uow) == {
        "id": "article-1",
        "source_id": "source-1",
        "current_revision_id": "revision-1",
    }
    assert repository.find_by_source_identity("source-2", identity, uow) is None


@pytest.mark.parametrize(
    "expected_version",
    ["article-version-1", None],
)
def test_article_repository_projection_write_preserves_version_and_caller_unit_of_work(
    expected_version: str | None,
) -> None:
    repository = FakeArticleRepository()
    article = {
        "id": "article-1",
        "source_id": "source-1",
        "current_revision_id": "revision-2",
    }
    uow = FakeUnitOfWork()

    saved = repository.save_projection(
        article,
        expected_version=expected_version,
        uow=uow,
    )

    assert saved["current_revision_id"] == "revision-2"
    assert repository.saved_expected_version == expected_version
    assert repository.saved_uow is uow
