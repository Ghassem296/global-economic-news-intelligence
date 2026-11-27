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

@dataclass(frozen=True, slots=True)
class PersistArticleRevisionResult:
    """Outcome of a revision append/reuse and its atomic Article projection update.

    The result reports only the identifiers and aggregate version required by the
    application contract; it does not expose persistence-specific details.
    """

    article_id: str
    revision_id: str
    created: bool
    article_version: str

    def __post_init__(self) -> None:
        for field_name in ("article_id", "revision_id", "article_version"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        if not isinstance(self.created, bool):
            raise TypeError("created must be a bool indicating append versus reuse.")
