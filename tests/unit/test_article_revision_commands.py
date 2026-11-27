from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.application.article_revision_commands import (
    PersistArticleRevisionCommand,
    PersistArticleRevisionResult,
)
from global_economic_news_intelligence.domain.article_revision_contracts import (
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)
from global_economic_news_intelligence.domain.contracts import CommandMetadata

NOW = datetime(2026, 11, 26, 10, 0, tzinfo=UTC)


def revision() -> PersistArticleRevision:
    return PersistArticleRevision(
        source_id="source-1",
        source_article_identity=SourceArticleIdentity("publisher:123", "source-id-v1"),
        original_url="https://example.com/article/123",
        external_id="123",
        normalized_title="Central bank keeps rates unchanged",
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
        summary=None,
        author="A. Writer",
        language="en",
        published_at=None,
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=("metadata-rights-assessment-v1",),
    )


def metadata(expected_version: str | None = None) -> CommandMetadata:
    return CommandMetadata(
        command_id="command-1",
        schema_version="1",
        actor_reference="service:article-revision",
        authorization_reference="authorization-1",
        correlation_id="correlation-1",
        idempotency_scope="article-revision.persist",
        idempotency_key="request-1",
        expected_aggregate_version=expected_version,
    )


def test_new_article_command_uses_common_metadata_without_expected_version() -> None:
    command = PersistArticleRevisionCommand(metadata=metadata(), revision=revision())
    assert command.article_id is None
    assert command.metadata.expected_aggregate_version is None
    assert command.revision.revision_fingerprint


def test_existing_article_command_uses_expected_version_from_common_envelope() -> None:
    command = PersistArticleRevisionCommand(
        metadata=metadata("article-version-7"),
        revision=revision(),
        article_id="article-1",
    )
    assert command.article_id == "article-1"
    assert command.metadata.expected_aggregate_version == "article-version-7"


def test_existing_article_command_requires_expected_version() -> None:
    with pytest.raises(ValueError, match="requires expected_aggregate_version"):
        PersistArticleRevisionCommand(
            metadata=metadata(),
            revision=revision(),
            article_id="article-1",
        )


def test_new_article_command_rejects_expected_version() -> None:
    with pytest.raises(ValueError, match="must not supply an expected aggregate version"):
        PersistArticleRevisionCommand(
            metadata=metadata("article-version-7"),
            revision=revision(),
        )


def test_command_rejects_untyped_metadata_or_revision_payload() -> None:
    with pytest.raises(TypeError, match="CommandMetadata"):
        PersistArticleRevisionCommand(metadata=object(), revision=revision())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="PersistArticleRevision"):
        PersistArticleRevisionCommand(metadata=metadata(), revision=object())  # type: ignore[arg-type]


def test_command_rejects_blank_article_id() -> None:
    with pytest.raises(ValueError, match="article_id"):
        PersistArticleRevisionCommand(
            metadata=metadata("article-version-7"),
            revision=revision(),
            article_id=" ",
        )

@pytest.mark.parametrize("created", [True, False])
def test_revision_result_reports_append_or_reuse(created: bool) -> None:
    result = PersistArticleRevisionResult(
        article_id="article-1",
        revision_id="revision-4",
        created=created,
        article_version="article-version-8",
    )
    assert result.article_id == "article-1"
    assert result.revision_id == "revision-4"
    assert result.created is created
    assert result.article_version == "article-version-8"


@pytest.mark.parametrize("field_name", ["article_id", "revision_id", "article_version"])
def test_revision_result_rejects_missing_identifiers(field_name: str) -> None:
    values: dict[str, object] = {
        "article_id": "article-1",
        "revision_id": "revision-1",
        "created": True,
        "article_version": "article-version-1",
    }
    values[field_name] = " "
    with pytest.raises(ValueError, match=field_name):
        PersistArticleRevisionResult(**values)  # type: ignore[arg-type]


def test_revision_result_requires_boolean_created_flag() -> None:
    with pytest.raises(TypeError, match="created must be a bool"):
        PersistArticleRevisionResult(
            article_id="article-1",
            revision_id="revision-1",
            created=1,  # type: ignore[arg-type]
            article_version="article-version-1",
        )
