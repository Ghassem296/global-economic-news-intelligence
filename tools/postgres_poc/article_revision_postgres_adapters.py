"""PoC-only PostgreSQL adapters for the ArticleRevision application ports.

These adapters are deliberately isolated from the production package. Security
and content-rights verifiers are injected separately; this module does not grant
or infer authorization or content-retention permission.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Any
from uuid import UUID, uuid4

import psycopg
from psycopg import sql
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

from global_economic_news_intelligence.application.article_revision_commands import (
    PersistArticleRevisionResult,
)
from global_economic_news_intelligence.application.article_revision_service import (
    ArticleProjection,
)
from global_economic_news_intelligence.domain.article_revision_contracts import (
    ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
    ArticleRevisionRecord,
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import UnitOfWork
from global_economic_news_intelligence.exceptions import ErrorCode, GeniError

from postgres_poc_uow import PostgreSQLUnitOfWork, PostgreSQLUnitOfWorkFactory


def _require_uow(uow: UnitOfWork) -> PostgreSQLUnitOfWork:
    if not isinstance(uow, PostgreSQLUnitOfWork):
        raise TypeError("PoC PostgreSQL repositories require PostgreSQLUnitOfWork.")
    return uow


def _aggregate_version(value: str) -> int:
    prefix = "article-version-"
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ValueError("Unsupported Article aggregate version token.")
    number = value[len(prefix) :]
    if not number.isascii() or not number.isdecimal() or int(number) < 1:
        raise ValueError("Invalid Article aggregate version token.")
    return int(number)


def _version_token(value: int) -> str:
    return f"article-version-{value}"


def _timestamp(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _plain_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _plain_json(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain_json(item) for item in value]
    return value


def _revision_payload_to_json(revision: PersistArticleRevision) -> dict[str, object]:
    return {
        "source_id": revision.source_id,
        "source_article_identity": {
            "canonical_source_identifier": (
                revision.source_article_identity.canonical_source_identifier
            ),
            "normalization_version": revision.source_article_identity.normalization_version,
            "canonical_url": revision.source_article_identity.canonical_url,
        },
        "original_url": revision.original_url,
        "external_id": revision.external_id,
        "normalized_title": revision.normalized_title,
        "content_availability": revision.content_availability.value,
        "content_reference": revision.content_reference,
        "content_hash": revision.content_hash,
        "content_normalization_version": revision.content_normalization_version,
        "summary": revision.summary,
        "author": revision.author,
        "language": revision.language,
        "published_at": _timestamp(revision.published_at),
        "observed_at": _timestamp(revision.observed_at),
        "change_reason": revision.change_reason,
        "rights_assessment_references": list(revision.rights_assessment_references),
        "metadata": _plain_json(revision.metadata),
    }


def _revision_payload_from_json(payload: Mapping[str, Any]) -> PersistArticleRevision:
    identity = payload["source_article_identity"]
    if not isinstance(identity, Mapping):
        raise ValueError("Stored source_article_identity must be a JSON object.")
    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ValueError("Stored revision metadata must be a JSON object or null.")
    references = payload["rights_assessment_references"]
    if not isinstance(references, list):
        raise ValueError("Stored rights_assessment_references must be a JSON array.")
    observed_at = _parse_timestamp(payload["observed_at"])
    if observed_at is None:
        raise ValueError("Stored observed_at must not be null.")
    return PersistArticleRevision(
        source_id=payload["source_id"],
        source_article_identity=SourceArticleIdentity(
            canonical_source_identifier=identity["canonical_source_identifier"],
            normalization_version=identity["normalization_version"],
            canonical_url=identity.get("canonical_url"),
        ),
        original_url=payload["original_url"],
        external_id=payload.get("external_id"),
        normalized_title=payload["normalized_title"],
        content_availability=ContentAvailability(payload["content_availability"]),
        content_reference=payload.get("content_reference"),
        content_hash=payload.get("content_hash"),
        content_normalization_version=payload.get("content_normalization_version"),
        summary=payload.get("summary"),
        author=payload.get("author"),
        language=payload.get("language"),
        published_at=_parse_timestamp(payload.get("published_at")),
        observed_at=observed_at,
        change_reason=payload["change_reason"],
        rights_assessment_references=tuple(references),
        metadata=metadata,
    )


def _revision_record_from_row(row: tuple[Any, ...]) -> ArticleRevisionRecord:
    payload = row[4]
    if not isinstance(payload, Mapping):
        raise ValueError("Stored ArticleRevision payload is missing or invalid.")
    created_at = row[6]
    if not isinstance(created_at, datetime):
        raise ValueError("Stored ArticleRevision created_at is invalid.")
    return ArticleRevisionRecord(
        revision_id=str(row[0]),
        article_id=str(row[1]),
        revision_number=row[2],
        payload=_revision_payload_from_json(payload),
        revision_fingerprint=row[3],
        revision_fingerprint_schema_version=row[5],
        created_at=created_at,
    )


_ARTICLE_COLUMNS = """
    article_id, source_id, canonical_source_identifier,
    identity_normalization_version, original_url, canonical_url, external_id,
    title, content_availability, content_reference, content_hash,
    content_normalization_version, summary, author, language, published_at,
    current_revision_id, article_metadata, version, created_at, updated_at
"""


def _projection_from_row(row: tuple[Any, ...]) -> ArticleProjection:
    metadata = row[17] if row[17] is not None else {}
    if not isinstance(metadata, Mapping):
        raise ValueError("Stored Article metadata must be a JSON object.")
    return ArticleProjection(
        article_id=str(row[0]),
        source_id=row[1],
        source_article_identity=SourceArticleIdentity(
            canonical_source_identifier=row[2],
            normalization_version=row[3],
            canonical_url=row[5],
        ),
        url=row[4],
        canonical_url=row[5],
        external_id=row[6],
        title=row[7],
        content_availability=ContentAvailability(row[8]),
        content_reference=row[9],
        content_hash=row[10],
        content_normalization_version=row[11],
        summary=row[12],
        author=row[13],
        language=row[14],
        published_at=row[15],
        current_revision_id=str(row[16]) if row[16] is not None else None,
        metadata=MappingProxyType(dict(metadata)),
        aggregate_version=_version_token(row[18]),
        created_at=row[19],
        updated_at=row[20],
    )


def _raise_duplicate_identity() -> GeniError:
    return GeniError(
        ErrorCode.DUPLICATE_IDENTITY,
        "The source Article identity already exists.",
        correlation_id="postgres-poc",
    )


class PostgreSQLArticleRepository:
    """Article projection repository; all writes join the supplied UnitOfWork."""

    def get_by_id(
        self,
        article_id: str,
        uow: UnitOfWork,
    ) -> ArticleProjection | None:
        connection = _require_uow(uow).connection
        row = connection.execute(
            f"SELECT {_ARTICLE_COLUMNS} FROM articles WHERE article_id = %s",
            (UUID(article_id),),
        ).fetchone()
        return _projection_from_row(row) if row is not None else None

    def find_by_source_identity(
        self,
        source_id: str,
        external_identity: SourceArticleIdentity,
        uow: UnitOfWork,
    ) -> ArticleProjection | None:
        connection = _require_uow(uow).connection
        row = connection.execute(
            f"""
            SELECT {_ARTICLE_COLUMNS}
            FROM articles
            WHERE source_id = %s
              AND canonical_source_identifier = %s
              AND identity_normalization_version = %s
            FOR UPDATE
            """,
            (
                source_id,
                external_identity.canonical_source_identifier,
                external_identity.normalization_version,
            ),
        ).fetchone()
        if row is None and external_identity.canonical_url is not None:
            collision = connection.execute(
                """
                SELECT 1 FROM articles
                WHERE source_id = %s AND canonical_url = %s
                LIMIT 1
                """,
                (source_id, external_identity.canonical_url),
            ).fetchone()
            if collision is not None:
                raise GeniError(
                    ErrorCode.CONFLICT,
                    "Canonical URL is already associated with another Article identity.",
                    correlation_id="postgres-poc",
                )
        return _projection_from_row(row) if row is not None else None

    def save_projection(
        self,
        article: ArticleProjection,
        expected_version: str | None,
        uow: UnitOfWork,
    ) -> ArticleProjection:
        connection = _require_uow(uow).connection
        identity = article.source_article_identity
        if identity.canonical_url is not None:
            collision = connection.execute(
                """
                SELECT article_id FROM articles
                WHERE source_id = %s AND canonical_url = %s AND article_id <> %s
                LIMIT 1
                """,
                (article.source_id, identity.canonical_url, UUID(article.article_id)),
            ).fetchone()
            if collision is not None:
                raise GeniError(
                    ErrorCode.CONFLICT,
                    "Canonical URL is already associated with another Article identity.",
                    correlation_id="postgres-poc",
                )

        values = (
            article.source_id,
            identity.canonical_source_identifier,
            identity.normalization_version,
            article.url,
            article.canonical_url,
            article.external_id,
            article.title,
            article.content_availability.value,
            article.content_reference,
            article.content_hash,
            article.content_normalization_version,
            article.summary,
            article.author,
            article.language,
            article.published_at,
            UUID(article.current_revision_id) if article.current_revision_id else None,
            Jsonb(_plain_json(article.metadata)),
            article.updated_at,
        )
        if expected_version is None:
            try:
                row = connection.execute(
                    """
                    INSERT INTO articles (
                        article_id, source_id, external_identity,
                        canonical_source_identifier, identity_normalization_version,
                        original_url, canonical_url, external_id, title,
                        content_availability, content_reference, content_hash,
                        content_normalization_version, summary, author, language,
                        published_at, current_revision_id, article_metadata,
                        version, created_at, updated_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s
                    )
                    RETURNING version, created_at, updated_at
                    """,
                    (
                        UUID(article.article_id),
                        article.source_id,
                        identity.canonical_source_identifier,
                        identity.canonical_source_identifier,
                        identity.normalization_version,
                        *values[3:],
                        article.created_at,
                        article.updated_at,
                    ),
                ).fetchone()
            except UniqueViolation as exc:
                raise _raise_duplicate_identity() from exc
            if row is None:
                raise RuntimeError("Article insert returned no row.")
            return ArticleProjection(
                **{
                    **article.__dict__,
                    "aggregate_version": _version_token(row[0]),
                    "created_at": row[1],
                    "updated_at": row[2],
                }
            )

        expected_number = _aggregate_version(expected_version)
        try:
            row = connection.execute(
                """
                UPDATE articles
                SET canonical_source_identifier = %s,
                    identity_normalization_version = %s,
                    external_identity = %s,
                    original_url = %s,
                    canonical_url = %s,
                    external_id = %s,
                    title = %s,
                    content_availability = %s,
                    content_reference = %s,
                    content_hash = %s,
                    content_normalization_version = %s,
                    summary = %s,
                    author = %s,
                    language = %s,
                    published_at = %s,
                    current_revision_id = %s,
                    article_metadata = %s,
                    version = version + 1,
                    updated_at = %s
                WHERE article_id = %s AND version = %s
                RETURNING version, created_at, updated_at
                """,
                (
                    identity.canonical_source_identifier,
                    identity.normalization_version,
                    identity.canonical_source_identifier,
                    article.url,
                    article.canonical_url,
                    article.external_id,
                    article.title,
                    article.content_availability.value,
                    article.content_reference,
                    article.content_hash,
                    article.content_normalization_version,
                    article.summary,
                    article.author,
                    article.language,
                    article.published_at,
                    UUID(article.current_revision_id) if article.current_revision_id else None,
                    Jsonb(_plain_json(article.metadata)),
                    article.updated_at,
                    UUID(article.article_id),
                    expected_number,
                ),
            ).fetchone()
        except UniqueViolation as exc:
            raise _raise_duplicate_identity() from exc
        if row is None:
            raise GeniError(
                ErrorCode.STALE_VERSION,
                "Article aggregate version is stale.",
                correlation_id="postgres-poc",
            )
        return ArticleProjection(
            article_id=article.article_id,
            source_id=article.source_id,
            source_article_identity=article.source_article_identity,
            url=article.url,
            canonical_url=article.canonical_url,
            external_id=article.external_id,
            title=article.title,
            content_availability=article.content_availability,
            content_reference=article.content_reference,
            content_hash=article.content_hash,
            content_normalization_version=article.content_normalization_version,
            summary=article.summary,
            author=article.author,
            language=article.language,
            published_at=article.published_at,
            current_revision_id=article.current_revision_id,
            metadata=article.metadata,
            aggregate_version=_version_token(row[0]),
            created_at=row[1],
            updated_at=row[2],
        )


class PostgreSQLArticleRevisionRepository:
    """Append-only ArticleRevision history with optimistic aggregate locking."""

    def __init__(self, uow_factory: PostgreSQLUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    @staticmethod
    def _get_by_id(
        revision_id: str,
        uow: PostgreSQLUnitOfWork,
    ) -> ArticleRevisionRecord | None:
        row = uow.connection.execute(
            """
            SELECT revision_id, article_id, revision_number, fingerprint,
                   revision_payload, revision_fingerprint_schema_version, created_at
            FROM article_revisions
            WHERE revision_id = %s
            """,
            (UUID(revision_id),),
        ).fetchone()
        return _revision_record_from_row(row) if row is not None else None

    def get_by_id(self, revision_id: str) -> ArticleRevisionRecord | None:
        uow = self._uow_factory.begin()
        try:
            record = self._get_by_id(revision_id, uow)
        except BaseException:
            uow.rollback()
            raise
        uow.rollback()
        return record

    def get_current_for_article(
        self,
        article_id: str,
        uow: UnitOfWork,
    ) -> ArticleRevisionRecord | None:
        connection = _require_uow(uow).connection
        row = connection.execute(
            """
            SELECT revision.revision_id, revision.article_id,
                   revision.revision_number, revision.fingerprint,
                   revision.revision_payload,
                   revision.revision_fingerprint_schema_version,
                   revision.created_at
            FROM articles AS article
            JOIN article_revisions AS revision
              ON revision.revision_id = article.current_revision_id
             AND revision.article_id = article.article_id
            WHERE article.article_id = %s
            """,
            (UUID(article_id),),
        ).fetchone()
        return _revision_record_from_row(row) if row is not None else None

    def find_current_by_revision_fingerprint(
        self,
        article_id: str,
        revision_fingerprint: str,
        schema_version: str,
        uow: UnitOfWork,
    ) -> ArticleRevisionRecord | None:
        connection = _require_uow(uow).connection
        row = connection.execute(
            """
            SELECT revision.revision_id, revision.article_id,
                   revision.revision_number, revision.fingerprint,
                   revision.revision_payload,
                   revision.revision_fingerprint_schema_version,
                   revision.created_at
            FROM articles AS article
            JOIN article_revisions AS revision
              ON revision.revision_id = article.current_revision_id
             AND revision.article_id = article.article_id
            WHERE article.article_id = %s
              AND revision.fingerprint = %s
              AND revision.revision_fingerprint_schema_version = %s
            """,
            (UUID(article_id), revision_fingerprint, schema_version),
        ).fetchone()
        return _revision_record_from_row(row) if row is not None else None

    def append_revision(
        self,
        article_id: str,
        revision: PersistArticleRevision,
        expected_article_version: str | None,
        uow: UnitOfWork,
    ) -> ArticleRevisionRecord:
        connection = _require_uow(uow).connection
        article_uuid = UUID(article_id)
        current = connection.execute(
            "SELECT version FROM articles WHERE article_id = %s FOR UPDATE",
            (article_uuid,),
        ).fetchone()
        if current is None:
            if expected_article_version is not None:
                raise GeniError(
                    ErrorCode.NOT_FOUND,
                    "Article was not found for revision append.",
                    correlation_id="postgres-poc",
                )
        elif expected_article_version is None or current[0] != _aggregate_version(
            expected_article_version
        ):
            raise GeniError(
                ErrorCode.STALE_VERSION,
                "Article aggregate version is stale.",
                correlation_id="postgres-poc",
            )

        revision_number_row = connection.execute(
            """
            SELECT COALESCE(MAX(revision_number), 0) + 1
            FROM article_revisions WHERE article_id = %s
            """,
            (article_uuid,),
        ).fetchone()
        revision_number = revision_number_row[0]
        revision_id = uuid4()
        payload = _revision_payload_to_json(revision)
        row = connection.execute(
            """
            INSERT INTO article_revisions (
                revision_id, article_id, revision_number, fingerprint,
                revision_payload, revision_fingerprint_schema_version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING created_at
            """,
            (
                revision_id,
                article_uuid,
                revision_number,
                revision.revision_fingerprint,
                Jsonb(payload),
                ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
            ),
        ).fetchone()
        if row is None:
            raise RuntimeError("ArticleRevision insert returned no row.")
        return ArticleRevisionRecord(
            revision_id=str(revision_id),
            article_id=article_id,
            revision_number=revision_number,
            payload=revision,
            revision_fingerprint=revision.revision_fingerprint,
            revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
            created_at=row[0],
        )


class PostgreSQLIdempotencyRepository:
    """Transactional idempotency claim and typed-result replay adapter."""

    @staticmethod
    def _result_payload(result: PersistArticleRevisionResult) -> dict[str, object]:
        return {
            "article_id": result.article_id,
            "revision_id": result.revision_id,
            "created": result.created,
            "article_version": result.article_version,
        }

    @staticmethod
    def _result_from_payload(payload: Mapping[str, Any]) -> PersistArticleRevisionResult:
        return PersistArticleRevisionResult(
            article_id=payload["article_id"],
            revision_id=payload["revision_id"],
            created=payload["created"],
            article_version=payload["article_version"],
        )

    def claim(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        uow: UnitOfWork,
    ) -> PersistArticleRevisionResult | None:
        connection = _require_uow(uow).connection
        inserted = connection.execute(
            """
            INSERT INTO idempotency_records (
                operation_scope, idempotency_key, request_fingerprint,
                state, result_id, completed_at
            )
            VALUES (%s, %s, %s, 'CLAIMED', NULL, NULL)
            ON CONFLICT (operation_scope, idempotency_key) DO NOTHING
            RETURNING operation_scope
            """,
            (scope, key, request_fingerprint),
        ).fetchone()
        if inserted is not None:
            return None

        existing = connection.execute(
            """
            SELECT request_fingerprint, state, result_payload
            FROM idempotency_records
            WHERE operation_scope = %s AND idempotency_key = %s
            FOR UPDATE
            """,
            (scope, key),
        ).fetchone()
        if existing is None:
            raise GeniError(
                ErrorCode.INVARIANT_VIOLATION,
                "Idempotency claim disappeared during lookup.",
                correlation_id="postgres-poc",
            )
        previous_fingerprint, state, payload = existing
        if previous_fingerprint != request_fingerprint:
            raise GeniError(
                ErrorCode.IDEMPOTENCY_KEY_REUSE_CONFLICT,
                "Idempotency key was reused with a different request.",
                correlation_id="postgres-poc",
            )
        if state != "COMPLETED" or not isinstance(payload, Mapping):
            raise GeniError(
                ErrorCode.INVARIANT_VIOLATION,
                "A persisted idempotency claim has no completed typed result.",
                correlation_id="postgres-poc",
            )
        return self._result_from_payload(payload)

    def complete(
        self,
        *,
        scope: str,
        key: str,
        request_fingerprint: str,
        result: PersistArticleRevisionResult,
        uow: UnitOfWork,
    ) -> None:
        connection = _require_uow(uow).connection
        updated = connection.execute(
            """
            UPDATE idempotency_records
            SET result_id = %s,
                result_payload = %s,
                state = 'COMPLETED',
                completed_at = clock_timestamp()
            WHERE operation_scope = %s
              AND idempotency_key = %s
              AND request_fingerprint = %s
              AND state = 'CLAIMED'
            RETURNING operation_scope
            """,
            (
                UUID(result.revision_id),
                Jsonb(self._result_payload(result)),
                scope,
                key,
                request_fingerprint,
            ),
        ).fetchone()
        if updated is None:
            raise GeniError(
                ErrorCode.INVARIANT_VIOLATION,
                "Idempotency completion did not match an active claim.",
                correlation_id="postgres-poc",
            )


class UUIDArticleIdGenerator:
    """Creates server-owned UUID Article identifiers for the PoC."""

    @staticmethod
    def new_article_id() -> str:
        return str(uuid4())
