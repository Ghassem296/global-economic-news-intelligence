"""Application command envelope for ArticleRevision persistence."""

from __future__ import annotations

from dataclasses import dataclass

from global_economic_news_intelligence.domain.article_revision_contracts import (
    PersistArticleRevision,
)
from global_economic_news_intelligence.domain.contracts import CommandMetadata


@dataclass(frozen=True, slots=True)
class PersistArticleRevisionCommand:
    """One authorized, idempotent request to append/reuse an ArticleRevision.

    The common CommandMetadata envelope is kept separate from the domain payload.
    The expected aggregate version is carried only by CommandMetadata and is not
    duplicated as a second command field.
    """

    metadata: CommandMetadata
    revision: PersistArticleRevision
    article_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.metadata, CommandMetadata):
            raise TypeError("metadata must be a CommandMetadata instance.")
        if not isinstance(self.revision, PersistArticleRevision):
            raise TypeError("revision must be a PersistArticleRevision instance.")
        if self.article_id is not None and (
            not isinstance(self.article_id, str) or not self.article_id.strip()
        ):
            raise ValueError("article_id must be a non-empty string when supplied.")

        expected_version = self.metadata.expected_aggregate_version
        if self.article_id is None and expected_version is not None:
            raise ValueError(
                "A new Article command must not supply an expected aggregate version."
            )
        if self.article_id is not None and expected_version is None:
            raise ValueError(
                "An existing Article command requires expected_aggregate_version "
                "in CommandMetadata."
            )
