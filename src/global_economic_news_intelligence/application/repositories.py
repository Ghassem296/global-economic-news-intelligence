"""Application persistence ports for the GENI first-slice use cases.

These are technology-neutral Protocols. They define transaction participation
without selecting a database, ORM, driver, or migration system.
"""

from __future__ import annotations

from typing import Protocol

from global_economic_news_intelligence.domain.article_revision_contracts import (
    ArticleRevisionRecord,
    PersistArticleRevision,
)
from global_economic_news_intelligence.domain.contracts import UnitOfWork


class ArticleRevisionRepository(Protocol):
    """Append-only ArticleRevision persistence port."""

    def get_by_id(self, revision_id: str) -> ArticleRevisionRecord | None:
        """Return one immutable revision by its server-owned ID."""
        ...

    def get_current_for_article(self, article_id: str) -> ArticleRevisionRecord | None:
        """Return the exact revision referenced by the Article current pointer."""
        ...

    def find_current_by_revision_fingerprint(
        self,
        article_id: str,
        revision_fingerprint: str,
        schema_version: str,
    ) -> ArticleRevisionRecord | None:
        """Return the current revision only when its fingerprint/version match."""
        ...

    def append_revision(
        self,
        article_id: str,
        revision: PersistArticleRevision,
        expected_article_version: str | None,
        uow: UnitOfWork,
    ) -> ArticleRevisionRecord:
        """Append a new immutable revision inside the caller's UnitOfWork.

        The ArticleRevisionService coordinates this write with the Article
        projection update through ArticleRepository in the same UnitOfWork.
        Implementations must not commit the supplied UnitOfWork themselves.
        """
        ...
