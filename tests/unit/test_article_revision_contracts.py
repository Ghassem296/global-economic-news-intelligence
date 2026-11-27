from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.domain.article_revision_contracts import (
    ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
    ArticleRevisionRecord,
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)

NOW = datetime(2026, 11, 26, 10, 0, tzinfo=UTC)
CONTENT_HASH = "a" * 64


def revision(**overrides: object) -> PersistArticleRevision:
    values: dict[str, object] = {
        "source_id": "source-1",
        "source_article_identity": SourceArticleIdentity(
            "publisher:item:123", "source-identity-v1"
        ),
        "original_url": "https://example.com/news/123",
        "external_id": "123",
        "normalized_title": "Central bank keeps rates unchanged",
        "content_availability": ContentAvailability.AVAILABLE,
        "content_reference": "content://article/revision-1",
        "content_hash": CONTENT_HASH,
        "content_normalization_version": "normalization-v1",
        "summary": None,
        "author": "A. Writer",
        "language": "en",
        "published_at": None,
        "observed_at": NOW,
        "change_reason": "INITIAL_COLLECTION",
        "rights_assessment_references": ("rights-assessment-1",),
    }
    values.update(overrides)
    return PersistArticleRevision(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("availability", "reference"),
    [
        (ContentAvailability.AVAILABLE, "content://revision"),
        (ContentAvailability.PARTIAL, "content://permitted-extract"),
    ],
)
def test_content_backed_revision_requires_reference_and_sha256(
    availability: ContentAvailability, reference: str
) -> None:
    result = revision(
        content_availability=availability,
        content_reference=reference,
    )
    assert result.content_reference == reference


@pytest.mark.parametrize(
    "availability",
    [ContentAvailability.METADATA_ONLY, ContentAvailability.UNAVAILABLE],
)
def test_non_content_revision_has_no_content_reference_or_content_hash(
    availability: ContentAvailability,
) -> None:
    result = revision(
        content_availability=availability,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
    )
    assert result.content_reference is None
    assert result.content_hash is None
    assert result.content_normalization_version is None


def test_metadata_only_revision_rejects_persisted_content_fingerprint() -> None:
    with pytest.raises(ValueError, match="must not persist"):
        revision(
            content_availability=ContentAvailability.METADATA_ONLY,
            content_reference=None,
        )


def test_unavailable_revision_rejects_persisted_content_fingerprint() -> None:
    with pytest.raises(ValueError, match="must not persist"):
        revision(
            content_availability=ContentAvailability.UNAVAILABLE,
            content_reference=None,
        )


def test_available_or_partial_revision_requires_all_content_fields() -> None:
    with pytest.raises(ValueError, match="requires content_reference"):
        revision(content_reference=None)
    with pytest.raises(ValueError, match="requires content_reference"):
        revision(content_hash=None)


def test_metadata_only_or_unavailable_rejects_persistent_content_reference() -> None:
    with pytest.raises(ValueError, match="must not persist"):
        revision(
            content_availability=ContentAvailability.METADATA_ONLY,
            content_reference="content://not-permitted",
        )


def test_persisted_content_requires_rights_assessment_provenance() -> None:
    with pytest.raises(ValueError, match="requires at least one rights_assessment_reference"):
        revision(rights_assessment_references=())


def test_content_hash_must_be_lowercase_sha256_hex() -> None:
    with pytest.raises(ValueError, match="64-character lowercase SHA-256"):
        revision(content_hash="sha256:fingerprint")
    with pytest.raises(ValueError, match="64-character lowercase SHA-256"):
        revision(content_hash="A" * 64)


def test_hash_and_normalization_version_must_be_supplied_together() -> None:
    with pytest.raises(ValueError, match="requires content_reference"):
        revision(content_normalization_version=None)


def test_source_identity_is_source_scoped_and_versioned() -> None:
    identity = SourceArticleIdentity("provider:opaque-id:ABC", "source-id-v2")
    assert identity.canonical_source_identifier == "provider:opaque-id:ABC"
    assert identity.normalization_version == "source-id-v2"
    with pytest.raises(ValueError, match="canonical_source_identifier"):
        SourceArticleIdentity(" ", "source-id-v1")
    with pytest.raises(ValueError, match="normalization_version"):
        SourceArticleIdentity("provider:id", " ")


@pytest.mark.parametrize(
    "url",
    ["example.com/article", "ftp://example.com/file", "https:///missing-host"],
)
def test_original_url_requires_absolute_http_url(url: str) -> None:
    with pytest.raises(ValueError, match="absolute HTTP"):
        revision(original_url=url)


def test_observation_and_publication_times_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="observed_at"):
        revision(observed_at=datetime(2026, 11, 26, 10, 0))
    with pytest.raises(ValueError, match="published_at"):
        revision(published_at=datetime(2026, 11, 26, 10, 0))


def test_article_revision_record_validates_persisted_fingerprint_and_identity() -> None:
    payload = revision()
    record = ArticleRevisionRecord(
        revision_id="revision-1",
        article_id="article-1",
        revision_number=1,
        payload=payload,
        revision_fingerprint=payload.revision_fingerprint,
        revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        created_at=NOW,
    )
    assert record.revision_fingerprint == payload.revision_fingerprint


def test_article_revision_record_rejects_fingerprint_mismatch() -> None:
    payload = revision()
    with pytest.raises(ValueError, match="does not match the payload"):
        ArticleRevisionRecord(
            revision_id="revision-1",
            article_id="article-1",
            revision_number=1,
            payload=payload,
            revision_fingerprint="0" * 64,
            revision_fingerprint_schema_version=ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
            created_at=NOW,
        )


def test_article_revision_record_rejects_invalid_server_owned_fields() -> None:
    payload = revision()
    values = {
        "revision_id": "revision-1",
        "article_id": "article-1",
        "revision_number": 1,
        "payload": payload,
        "revision_fingerprint": payload.revision_fingerprint,
        "revision_fingerprint_schema_version": ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
        "created_at": NOW,
    }
    with pytest.raises(ValueError, match="positive integer"):
        ArticleRevisionRecord(**(values | {"revision_number": True}))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unsupported revision_fingerprint_schema_version"):
        ArticleRevisionRecord(
            **(values | {"revision_fingerprint_schema_version": "unknown-v2"})
        )  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="created_at"):
        ArticleRevisionRecord(
            **(values | {"created_at": datetime(2026, 11, 26, 10, 0)})
        )  # type: ignore[arg-type]


def test_revision_fingerprint_v1_matches_golden_sha256_vector() -> None:
    result = revision()
    assert result.revision_fingerprint == (
        "7c90a88070e9643d26b70690ab270cb7c8c66b4cb3030d1c40e541d7b7d9caab"
    )


def test_fingerprint_is_stable_across_observation_storage_and_rights_metadata() -> None:
    first = revision(
        content_reference="content://first-location",
        observed_at=NOW,
        change_reason="INITIAL_COLLECTION",
        rights_assessment_references=("rights-v1",),
    )
    second = revision(
        content_reference="content://moved-location",
        observed_at=datetime(2026, 11, 26, 11, 0, tzinfo=UTC),
        change_reason="RECOLLECTION",
        rights_assessment_references=("rights-v2",),
    )
    assert first.revision_fingerprint == second.revision_fingerprint


def test_author_snapshot_participates_in_revision_fingerprint() -> None:
    first = revision(author="A. Writer")
    changed = revision(author="B. Writer")
    assert first.revision_fingerprint != changed.revision_fingerprint


def test_metadata_only_revision_fingerprint_tracks_permitted_metadata() -> None:
    first = revision(
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
        metadata={"publisher_section": "economy", "author": "A. Writer"},
    )
    changed = revision(
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
        content_hash=None,
        content_normalization_version=None,
        metadata={"publisher_section": "economy", "author": "B. Writer"},
    )
    assert first.revision_fingerprint != changed.revision_fingerprint
    assert len(first.revision_fingerprint) == 64


def test_revision_fingerprint_ignores_metadata_key_order_and_uses_versioned_schema() -> None:
    first = revision(metadata={"b": "two", "a": "one"})
    second = revision(metadata={"a": "one", "b": "two"})
    assert first.revision_fingerprint == second.revision_fingerprint
    assert ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION == "article-revision-fingerprint-v1"


def test_fingerprint_uses_utc_millisecond_timestamp_precision() -> None:
    utc_revision = revision(published_at=datetime(2026, 11, 26, 10, 0, tzinfo=UTC))
    equivalent_offset = revision(
        published_at=datetime.fromisoformat("2026-11-26T13:30:00+03:30")
    )
    assert utc_revision.revision_fingerprint == equivalent_offset.revision_fingerprint
    with pytest.raises(ValueError, match="millisecond precision"):
        revision(published_at=datetime(2026, 11, 26, 10, 0, 0, 1, tzinfo=UTC))


def test_revision_metadata_is_deeply_immutable() -> None:
    source = {"collection": {"labels": ["fixture", "authorized"]}}
    item = revision(metadata=source)
    source["collection"]["labels"].append("changed")  # type: ignore[index, union-attr]
    assert item.metadata is not None
    assert item.metadata["collection"]["labels"] == ("fixture", "authorized")  # type: ignore[index]
    with pytest.raises(TypeError):
        item.metadata["new"] = "value"  # type: ignore[index]


def test_revision_rejects_non_jcs_metadata_values() -> None:
    with pytest.raises(TypeError, match="JCS-safe JSON"):
        revision(metadata={"bad": object()})
    with pytest.raises(TypeError, match="JCS-safe JSON"):
        revision(metadata={"floating": 1.25})
    with pytest.raises(ValueError, match="safe range"):
        revision(metadata={"large_integer": 2**54})

def test_canonical_url_is_optional_secondary_source_identity_signal() -> None:
    identity = SourceArticleIdentity(
        "publisher:item:123",
        "source-identity-v1",
        canonical_url="https://example.com/canonical/123",
    )
    assert identity.canonical_url == "https://example.com/canonical/123"


def test_canonical_url_does_not_change_semantic_revision_fingerprint() -> None:
    without_canonical_url = revision()
    with_canonical_url = revision(
        source_article_identity=SourceArticleIdentity(
            "publisher:item:123",
            "source-identity-v1",
            canonical_url="https://example.com/canonical/123",
        )
    )
    assert (
        with_canonical_url.revision_fingerprint
        == without_canonical_url.revision_fingerprint
    )


@pytest.mark.parametrize(
    "canonical_url",
    ["example.com/article", "ftp://example.com/file", "https:///missing-host"],
)
def test_canonical_url_requires_absolute_http_url(canonical_url: str) -> None:
    with pytest.raises(ValueError, match="absolute HTTP"):
        SourceArticleIdentity(
            "publisher:item:123",
            "source-identity-v1",
            canonical_url=canonical_url,
        )


@pytest.mark.parametrize(
    "url",
    [
        "https://user:password@example.com/article",
        "https://example.com/article#fragment",
        "https://example.com:invalid/article",
        "https://example.com/article?api_key=secret",
        "https://example.com/article?access_token=secret",
        "https://example.com/article path",
        "https://example.com/article\u00a0path",
        "https://example.com/article\u200bpath",
        "https://example.com/article\\\\path",
        "https://example.com/article\npath",
    ],
)
def test_original_url_rejects_credentials_and_ambiguous_url_forms(url: str) -> None:
    with pytest.raises(ValueError):
        revision(original_url=url)


@pytest.mark.parametrize(
    "url",
    [
        "https://user:password@example.com/canonical",
        "https://example.com/canonical#fragment",
        "https://example.com:invalid/canonical",
        "https://example.com/canonical?api_key=secret",
        "https://example.com/canonical path",
        "https://example.com/canonical\u00a0path",
        "https://example.com/canonical\u200bpath",
        "https://example.com/canonical\\\\path",
        "https://example.com/canonical\npath",
    ],
)
def test_canonical_url_rejects_credentials_and_ambiguous_url_forms(url: str) -> None:
    with pytest.raises(ValueError):
        SourceArticleIdentity(
            "publisher:opaque-id",
            "source-identity-v1",
            canonical_url=url,
        )


def test_article_urls_allow_non_sensitive_query_parameters() -> None:
    item = revision(original_url="https://example.com/article?id=123&lang=en")
    identity = SourceArticleIdentity(
        "publisher:opaque-id",
        "source-identity-v1",
        canonical_url="https://example.com/canonical?id=123",
    )
    assert item.original_url.endswith("?id=123&lang=en")
    assert identity.canonical_url == "https://example.com/canonical?id=123"
