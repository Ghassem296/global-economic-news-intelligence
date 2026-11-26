from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.domain.article_revision_contracts import (
    ContentAvailability,
    PersistArticleRevision,
    SourceArticleIdentity,
)


NOW = datetime(2026, 11, 26, 10, 0, tzinfo=UTC)


def revision(**overrides: object) -> PersistArticleRevision:
    values: dict[str, object] = {
        "source_id": "source-1",
        "source_article_identity": SourceArticleIdentity("publisher:item:123", "source-identity-v1"),
        "original_url": "https://example.com/news/123",
        "external_id": "123",
        "normalized_title": "Central bank keeps rates unchanged",
        "content_availability": ContentAvailability.AVAILABLE,
        "content_reference": "content://article/revision-1",
        "content_hash": "sha256:fingerprint",
        "content_normalization_version": "normalization-v1",
        "summary": None,
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
def test_content_backed_revision_requires_reference_and_fingerprint(
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
def test_metadata_only_and_unavailable_revisions_have_no_content_reference(
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


def test_metadata_only_revision_may_keep_a_permitted_transient_content_fingerprint() -> None:
    result = revision(
        content_availability=ContentAvailability.METADATA_ONLY,
        content_reference=None,
    )
    assert result.content_hash == "sha256:fingerprint"


def test_available_or_partial_revision_requires_all_content_fields() -> None:
    with pytest.raises(ValueError, match="requires content_reference"):
        revision(content_reference=None)
    with pytest.raises(ValueError, match="requires content_reference"):
        revision(content_hash=None)


def test_metadata_only_or_unavailable_rejects_persistent_content_reference() -> None:
    with pytest.raises(ValueError, match="must not have content_reference"):
        revision(
            content_availability=ContentAvailability.METADATA_ONLY,
            content_reference="content://not-permitted",
        )


def test_hash_and_normalization_version_must_be_supplied_together() -> None:
    with pytest.raises(ValueError, match="must be supplied together"):
        revision(
            content_availability=ContentAvailability.METADATA_ONLY,
            content_reference=None,
            content_normalization_version=None,
        )


def test_source_identity_is_source_scoped_and_does_not_guess_canonicalization() -> None:
    identity = SourceArticleIdentity("provider:opaque-id:ABC", "source-id-v2")
    assert identity.canonical_source_identifier == "provider:opaque-id:ABC"\n    assert identity.normalization_version == "source-id-v2"
    with pytest.raises(ValueError, match="canonical_source_identifier"):
        SourceArticleIdentity(" ", "source-id-v1")


@pytest.mark.parametrize("url", ["example.com/article", "ftp://example.com/file", "https:///missing-host"])
def test_original_url_requires_absolute_http_url(url: str) -> None:
    with pytest.raises(ValueError, match="absolute HTTP"):
        revision(original_url=url)


def test_observation_and_publication_times_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="observed_at"):
        revision(observed_at=datetime(2026, 11, 26, 10, 0))
    with pytest.raises(ValueError, match="published_at"):
        revision(published_at=datetime(2026, 11, 26, 10, 0))


def test_rights_assessment_references_are_immutable_and_unique() -> None:
    with pytest.raises(TypeError, match="immutable tuple"):
        revision(rights_assessment_references=["rights-1"])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="duplicates"):
        revision(rights_assessment_references=("rights-1", "rights-1"))


def test_revision_metadata_is_deeply_immutable() -> None:
    source = {"collection": {"labels": ["fixture", "authorized"]}}
    item = revision(metadata=source)
    source["collection"]["labels"].append("changed")  # type: ignore[index, union-attr]
    assert item.metadata is not None
    assert item.metadata["collection"]["labels"] == ("fixture", "authorized")  # type: ignore[index]
    with pytest.raises(TypeError):
        item.metadata["new"] = "value"  # type: ignore[index]


def test_revision_rejects_non_json_metadata() -> None:
    with pytest.raises(TypeError, match="JSON-compatible"):
        revision(metadata={"bad": object()})
