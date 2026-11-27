"""Application orchestration for atomic ArticleRevision persistence.

This service coordinates authorization, content-rights revalidation, command
idempotency, immutable revision append/reuse, and the current Article projection.
Concrete security, rights, idempotency, identifier, and persistence adapters remain
infrastructure responsibilities and must share the supplied UnitOfWork.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Protocol


from global_economic_news_intelligence.application.article_revision_commands import (
    PersistArticleRevisionCommand,
    PersistArticleRevisionResult,
)
from global_economic_news_intelligence.application.repositories import (
    ArticleRepository,
    ArticleRevisionRepository,
)
from global_economic_news_intelligence.domain.article_revision_contracts import (
    ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
    ArticleRevisionRecord,
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import (
    CommandMetadata,
    UnitOfWork,
    UnitOfWorkFactory,
)
from global_economic_news_intelligence.exceptions import ErrorCode, GeniError


@dataclass(frozen=True, slots=True)
class ArticleProjection:
    """Typed current Article projection owned by ArticleRepository.

    This is deliberately a persistence-facing projection, not a second editable
    source of article content. ArticleRevision remains the immutable history.
    """

    article_id: str
    source_id: str
    source_article_identity: SourceArticleIdentity
    url: str
    canonical_url: str | None
    external_id: str | None
    title: str
    content_availability: ContentAvailability
    content_reference: str | None
    content_hash: str | None
    content_normalization_version: str | None
    summary: str | None
    author: str | None
    language: str | None
    published_at: datetime | None
    current_revision_id: str | None
    metadata: Mapping[str, object]
    aggregate_version: str | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        for name in ("article_id", "source_id", "url", "title"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string.")
        if not isinstance(self.source_article_identity, SourceArticleIdentity):
            raise TypeError("source_article_identity must be SourceArticleIdentity.")
        if not isinstance(self.content_availability, ContentAvailability):
            raise TypeError("content_availability must be ContentAvailability.")
        for name in ("created_at", "updated_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime) or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware.")
        if self.aggregate_version is not None and not self.aggregate_version.strip():
            raise ValueError("aggregate_version must be non-empty when supplied.")


class Clock(Protocol):
    """Provides trusted application time, independent of source observation time."""

    def now(self) -> datetime:
        ...


class ArticleIdGenerator(Protocol):
    """Creates a stable, server-owned Article identifier."""

    def new_article_id(self) -> str:
        ...


class AuthorizationVerifier(Protocol):
    """Resolves an immutable authorization reference against the exact action."""

    def is_authorized(
        self,
        metadata: CommandMetadata,
        *,
        action: str,
        resource_reference: str,
    ) -> bool:
        ...


class ContentRightsVerifier(Protocol):
    """Revalidates exact metadata/content rights; missing assessment references deny by default."""

    def permits_metadata_retention(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
    ) -> bool:
        """Verify METADATA_ACCESS plus the applicable metadata-preservation rule."""
        ...

    def permits_persistent_storage(
        self,
        revision: PersistArticleRevision,
        *,
        at: datetime,
    ) -> bool:
        ...


class IdempotencyRepository(Protocol):
    """Atomic command-idempotency port participating in the caller's UnitOfWork."""

    def claim(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        uow: UnitOfWork,
    ) -> PersistArticleRevisionResult | None:
        """Reserve a new key or return the completed result for an identical retry.

        A reused key with a different fingerprint must raise
        IDEMPOTENCY_KEY_REUSE_CONFLICT. A concurrent uncommitted claim must be
        serialized by the adapter's unique constraint/locking strategy.
        """
        ...

    def complete(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        result: PersistArticleRevisionResult,
        uow: UnitOfWork,
    ) -> None:
        """Store the result in the same transaction as Article and revision writes."""
        ...


class ArticleRevisionService:
    """Execute one authorized and rights-checked revision persistence command."""

    ACTION = "article.revision.persist"

    def __init__(
        self,
        *,
        articles: ArticleRepository[ArticleProjection],
        revisions: ArticleRevisionRepository,
        idempotency: IdempotencyRepository,
        unit_of_work_factory: UnitOfWorkFactory,
        authorization: AuthorizationVerifier,
        content_rights: ContentRightsVerifier,
        article_ids: ArticleIdGenerator,
        clock: Clock,
    ) -> None:
        self._articles = articles
        self._revisions = revisions
        self._idempotency = idempotency
        self._uow_factory = unit_of_work_factory
        self._authorization = authorization
        self._content_rights = content_rights
        self._article_ids = article_ids
        self._clock = clock

    def execute(self, command: PersistArticleRevisionCommand) -> PersistArticleRevisionResult:
        """Append/reuse one revision and atomically update its Article projection."""

        if not isinstance(command, PersistArticleRevisionCommand):
            raise TypeError("command must be a PersistArticleRevisionCommand.")

        metadata = command.metadata
        revision = command.revision
        resource_reference = self._resource_reference(command)
        self._require_authorization(metadata, resource_reference)
        self._require_content_rights(revision, metadata)

        request_fingerprint = self._request_fingerprint(command)
        uow = self._uow_factory.begin()
        try:
            replay = self._idempotency.claim(
                scope=metadata.idempotency_scope,
                key=metadata.idempotency_key,
                request_fingerprint=request_fingerprint,
                uow=uow,
            )
            if replay is not None:
                uow.rollback()
                return replay

            article, current = self._resolve_article(command)
            if (
                article is not None
                and current is not None
                and self._matches_current(current, revision)
            ):
                # Source routing attributes may change without a semantic revision.
                proposed = self._build_projection(
                    article_id=article.article_id,
                    revision=revision,
                    record=current,
                    previous=article,
                    now=self._now(),
                )
                comparable = replace(
                    proposed,
                    aggregate_version=article.aggregate_version,
                    updated_at=article.updated_at,
                )
                if comparable != article:
                    article = self._articles.save_projection(
                        proposed,
                        expected_version=article.aggregate_version,
                        uow=uow,
                    )
                    if (
                        not article.aggregate_version
                        or article.article_id != current.article_id
                        or article.current_revision_id != current.revision_id
                    ):
                        raise self._error(
                            ErrorCode.INVARIANT_VIOLATION,
                            "ArticleRepository returned an inconsistent projection refresh.",
                            metadata,
                        )
                result = self._result(article, current, created=False)
                self._idempotency.complete(
                    scope=metadata.idempotency_scope,
                    key=metadata.idempotency_key,
                    request_fingerprint=request_fingerprint,
                    result=result,
                    uow=uow,
                )
                uow.commit()
                return result

            article_id = (
                article.article_id if article is not None else self._article_ids.new_article_id()
            )
            expected_version = (
                metadata.expected_aggregate_version if article is not None else None
            )
            record = self._revisions.append_revision(
                article_id=article_id,
                revision=revision,
                expected_article_version=expected_version,
                uow=uow,
            )
            if (
                record.article_id != article_id
                or record.revision_fingerprint != revision.revision_fingerprint
                or record.revision_fingerprint_schema_version
                != ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION
            ):
                raise self._error(
                    ErrorCode.INVARIANT_VIOLATION,
                    "ArticleRevisionRepository returned a mismatched revision record.",
                    metadata,
                )
            projection = self._build_projection(
                article_id=article_id,
                revision=revision,
                record=record,
                previous=article,
                now=self._now(),
            )
            saved = self._articles.save_projection(
                projection,
                expected_version=expected_version,
                uow=uow,
            )
            if (
                not saved.aggregate_version
                or saved.article_id != article_id
                or saved.current_revision_id != record.revision_id
                or saved.content_availability is not revision.content_availability
                or saved.source_id != revision.source_id
            ):
                raise self._error(
                    ErrorCode.INVARIANT_VIOLATION,
                    "ArticleRepository returned an inconsistent Article projection.",
                    metadata,
                )
            result = PersistArticleRevisionResult(
                article_id=article_id,
                revision_id=record.revision_id,
                created=True,
                article_version=saved.aggregate_version,
            )
            self._idempotency.complete(
                scope=metadata.idempotency_scope,
                key=metadata.idempotency_key,
                request_fingerprint=request_fingerprint,
                result=result,
                uow=uow,
            )
            uow.commit()
            return result
        except BaseException:
            # BaseException: a cancellation or interrupt must not leave the transaction open.
            uow.rollback()
            raise

    def _resolve_article(
        self,
        command: PersistArticleRevisionCommand,
    ) -> tuple[ArticleProjection | None, ArticleRevisionRecord | None]:
        """Resolve the target Article and its verified current revision, if any.

        An Article addressed only by source identity may be reused when the supplied
        revision is already current; otherwise the caller must address it by ID and
        expected version so that a silent overwrite is impossible.
        """
        metadata = command.metadata
        if command.article_id is not None:
            article = self._articles.get_by_id(command.article_id)
            if article is None:
                raise self._error(ErrorCode.NOT_FOUND, "Article was not found.", metadata)
            if not self._same_identity(article, command.revision):
                raise self._error(
                    ErrorCode.CONFLICT,
                    "Article source identity does not match the command.",
                    metadata,
                )
        else:
            article = self._articles.find_by_source_identity(
                command.revision.source_id,
                command.revision.source_article_identity,
            )
            if article is None:
                return None, None
            if not self._same_identity(article, command.revision):
                raise self._error(
                    ErrorCode.CONFLICT,
                    "Source identity resolved to a conflicting Article.",
                    metadata,
                )

        if article.aggregate_version is None:
            raise self._error(
                ErrorCode.INVARIANT_VIOLATION,
                "Persisted Article is missing its aggregate version.",
                metadata,
            )
        current = self._revisions.get_current_for_article(article.article_id)
        if current is None or current.revision_id != article.current_revision_id:
            raise self._error(
                ErrorCode.INVARIANT_VIOLATION,
                "Article current revision pointer is inconsistent.",
                metadata,
            )
        if command.article_id is None and not self._matches_current(current, command.revision):
            raise self._error(
                ErrorCode.CONFLICT,
                "Source identity already exists; update requires an Article ID "
                "and expected version.",
                metadata,
            )
        return article, current

    @staticmethod
    def _matches_current(
        current: ArticleRevisionRecord,
        revision: PersistArticleRevision,
    ) -> bool:
        return (
            current.revision_fingerprint == revision.revision_fingerprint
            and current.revision_fingerprint_schema_version
            == ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION
        )

    @staticmethod
    def _same_identity(
        article: ArticleProjection,
        revision: PersistArticleRevision,
    ) -> bool:
        return (
            article.source_id == revision.source_id
            and article.source_article_identity.canonical_source_identifier
            == revision.source_article_identity.canonical_source_identifier
            and article.source_article_identity.normalization_version
            == revision.source_article_identity.normalization_version
        )

    def _build_projection(
        self,
        *,
        article_id: str,
        revision: PersistArticleRevision,
        record: ArticleRevisionRecord,
        previous: ArticleProjection | None,
        now: datetime,
    ) -> ArticleProjection:
        created_at = previous.created_at if previous is not None else revision.observed_at
        return ArticleProjection(
            article_id=article_id,
            source_id=revision.source_id,
            source_article_identity=revision.source_article_identity,
            url=revision.original_url,
            canonical_url=revision.source_article_identity.canonical_url,
            external_id=revision.external_id,
            title=revision.normalized_title,
            content_availability=revision.content_availability,
            content_reference=revision.content_reference,
            content_hash=revision.content_hash,
            content_normalization_version=revision.content_normalization_version,
            summary=revision.summary,
            author=revision.author,
            language=revision.language,
            published_at=revision.published_at,
            current_revision_id=record.revision_id,
            metadata=revision.metadata or {},
            aggregate_version=previous.aggregate_version if previous is not None else None,
            created_at=created_at,
            updated_at=now,
        )

    def _require_authorization(
        self,
        metadata: CommandMetadata,
        resource_reference: str,
    ) -> None:
        if not self._authorization.is_authorized(
            metadata,
            action=self.ACTION,
            resource_reference=resource_reference,
        ):
            raise self._error(
                ErrorCode.AUTHORIZATION_DENIED,
                "The command is not authorized.",
                metadata,
            )

    def _require_content_rights(
        self,
        revision: PersistArticleRevision,
        metadata: CommandMetadata,
    ) -> None:
        evaluation_time = self._now()
        if not revision.rights_assessment_references:
            raise self._error(
                ErrorCode.RIGHTS_NOT_ALLOWED,
                "No rights-assessment references were supplied for this revision.",
                metadata,
            )
        if not self._content_rights.permits_metadata_retention(
            revision,
            at=evaluation_time,
        ):
            raise self._error(
                ErrorCode.RIGHTS_NOT_ALLOWED,
                "Metadata access or preservation is not authorized for this source scope.",
                metadata,
            )
        if revision.content_availability not in {
            ContentAvailability.AVAILABLE,
            ContentAvailability.PARTIAL,
        }:
            return
        if not self._content_rights.permits_persistent_storage(
            revision,
            at=evaluation_time,
        ):
            raise self._error(
                ErrorCode.RIGHTS_NOT_ALLOWED,
                "Persistent storage is not authorized for this content scope.",
                metadata,
            )

    def _now(self) -> datetime:
        """Return one validated, trusted application instant."""
        value = self._clock.now()
        if not isinstance(value, datetime) or value.utcoffset() is None:
            raise ValueError("Clock.now() must return a timezone-aware datetime.")
        return value

    @staticmethod
    def _resource_reference(command: PersistArticleRevisionCommand) -> str:
        if command.article_id is not None:
            return f"article:{command.article_id}"
        identity = command.revision.source_article_identity
        return (
            f"source-article:{command.revision.source_id}:"
            f"{identity.normalization_version}:{identity.canonical_source_identifier}"
        )

    @staticmethod
    def _request_fingerprint(command: PersistArticleRevisionCommand) -> str:
        revision = command.revision
        manifest = {
            "schema_version": command.metadata.schema_version,
            "expected_aggregate_version": command.metadata.expected_aggregate_version,
            "actor_reference": command.metadata.actor_reference,
            "authorization_reference": command.metadata.authorization_reference,
            "article_id": command.article_id,
            "source_id": revision.source_id,
            "canonical_source_identifier": (
                revision.source_article_identity.canonical_source_identifier
            ),
            "source_identity_normalization_version": (
                revision.source_article_identity.normalization_version
            ),
            "canonical_url": revision.source_article_identity.canonical_url,
            "original_url": revision.original_url,
            "external_id": revision.external_id,
            "revision_fingerprint": revision.revision_fingerprint,
            "content_reference": revision.content_reference,
            "observed_at": revision.observed_at.isoformat(),
            "change_reason": revision.change_reason,
            "rights_assessment_references": list(revision.rights_assessment_references),
        }
        encoded = json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _result(
        article: ArticleProjection,
        record: ArticleRevisionRecord,
        *,
        created: bool,
    ) -> PersistArticleRevisionResult:
        if not article.aggregate_version:
            raise ValueError("Persisted Article must have an aggregate version.")
        return PersistArticleRevisionResult(
            article_id=article.article_id,
            revision_id=record.revision_id,
            created=created,
            article_version=article.aggregate_version,
        )

    @staticmethod
    def _error(
        code: ErrorCode,
        message: str,
        metadata: CommandMetadata | None,
    ) -> GeniError:
        return GeniError(
            code,
            message,
            correlation_id=metadata.correlation_id if metadata is not None else "unknown",
        )
