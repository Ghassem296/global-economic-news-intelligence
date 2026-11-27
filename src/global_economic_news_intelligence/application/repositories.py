"""Application persistence ports for the GENI first-slice use cases.

These are technology-neutral Protocols. They define transaction participation
without selecting a database, ORM, driver, or migration system.
"""

from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from global_economic_news_intelligence.domain.article_revision_contracts import (
    ArticleRevisionRecord,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import UnitOfWork
from global_economic_news_intelligence.domain.source_contracts import SourceRecord

ArticleT = TypeVar("ArticleT")


@runtime_checkable
class SourceRepository(Protocol):
    """Read-only Source configuration port for authorized registry queries.

    Collection eligibility is configuration state, not content-access rights.
    Mutation and collection-query DTOs remain gated until their field-level
    contracts and authorization/SSRF policies are approved.
    """

    def get_by_id(self, source_id: str) -> SourceRecord | None:
        """Return one configured Source snapshot without exposing secrets."""
        ...



@runtime_checkable
class ArticleRepository(Protocol[ArticleT]):
    """Current Article projection port used by ArticleRevisionService.

    The Article domain record remains defined by the approved domain model;
    this generic port does not invent its fields or a concrete persistence type.
    """

    def get_by_id(self, article_id: str, uow: UnitOfWork) -> ArticleT | None:
        """Read the current projection using the caller's active transaction."""
        ...

    def find_by_source_identity(
        self,
        source_id: str,
        external_identity: SourceArticleIdentity,
        uow: UnitOfWork,
    ) -> ArticleT | None:
        """Resolve the stable source identity tuple, never the mutable canonical URL.

        Implementations key on source_id, canonical_source_identifier, and
        normalization_version. canonical_url is a mutable secondary routing hint,
        not part of identity equality; collisions must return CONFLICT, never merge.
        """
        ...

    def save_projection(
        self,
        article: ArticleT,
        expected_version: str | None,
        uow: UnitOfWork,
    ) -> ArticleT:
        """Save the projection in the caller's revision transaction; never commit."""
        ...


class ArticleRevisionRepository(Protocol):
    """Append-only ArticleRevision persistence port."""

    def get_by_id(self, revision_id: str) -> ArticleRevisionRecord | None:
        """Return one immutable revision by its server-owned ID."""
        ...

    def get_current_for_article(
        self, article_id: str, uow: UnitOfWork
    ) -> ArticleRevisionRecord | None:
        """Read the current revision through the caller's active transaction."""
        ...

    def find_current_by_revision_fingerprint(
        self,
        article_id: str,
        revision_fingerprint: str,
        schema_version: str,
        uow: UnitOfWork,
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
