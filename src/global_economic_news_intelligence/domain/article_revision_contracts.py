"""Typed payload contract for persisting an immutable ArticleRevision.

Revision identity is independent from the optional retained-content hash. The
fingerprint is built only from the versioned, permission-filtered revision
snapshot; storage references, observation time, and rights-decision references
do not create new content revisions.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from types import MappingProxyType
from typing import cast
from urllib.parse import urlsplit

type JsonScalar = str | int | bool | None
type FrozenJson = JsonScalar | tuple[FrozenJson, ...] | Mapping[str, FrozenJson]

ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION = "article-revision-fingerprint-v1"
_MAX_SAFE_INTEGER = (2**53) - 1


class ContentAvailability(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    METADATA_ONLY = "metadata-only"
    UNAVAILABLE = "unavailable"


def _valid_unicode(value: str, field_name: str) -> None:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{field_name} must contain valid Unicode scalar values.") from exc


def _required_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    _valid_unicode(value, field_name)


def _optional_text(value: object, field_name: str) -> None:
    if value is not None:
        _required_text(value, field_name)


def _aware_instant(value: object, field_name: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")
    if value.microsecond % 1000:
        raise ValueError(f"{field_name} must have millisecond precision.")


def _http_url(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a non-empty string.")
    _required_text(value, field_name)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{field_name} must be an absolute HTTP(S) URL.")


def _freeze_json(value: object, field_name: str) -> FrozenJson:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        _valid_unicode(value, field_name)
        return value
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise ValueError(f"{field_name} integers must be within the JCS safe range.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJson] = {}
        for key, item in value.items():
            _required_text(key, f"{field_name} key")
            frozen[key] = _freeze_json(item, field_name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item, field_name) for item in value)
    raise TypeError(
        f"{field_name} must contain JCS-safe JSON values "
        "(string, boolean, null, safe integer, array, or object)."
    )


def _freeze_metadata(value: Mapping[str, object] | None) -> Mapping[str, FrozenJson] | None:
    if value is None:
        return None
    frozen = _freeze_json(value, "metadata")
    if not isinstance(frozen, Mapping):
        raise TypeError("metadata must be a mapping.")
    return frozen


def _jcs_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _jcs(value: FrozenJson | dict[str, FrozenJson]) -> str:
    """Serialize the supported JCS subset; floating-point values are excluded."""

    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, int):
        if abs(value) > _MAX_SAFE_INTEGER:
            raise ValueError("JCS integer is outside the safe interoperable range.")
        return str(value)
    if isinstance(value, Mapping):
        keys = sorted(value, key=lambda item: item.encode("utf-16-be"))
        return "{" + ",".join(
            f"{_jcs_string(key)}:{_jcs(value[key])}" for key in keys
        ) + "}"
    if isinstance(value, tuple):
        return "[" + ",".join(_jcs(item) for item in value) + "]"
    raise TypeError("Unsupported value in ArticleRevision fingerprint manifest.")


def _timestamp_for_fingerprint(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class SourceArticleIdentity:
    """Source-scoped canonical identity; the canonicalization algorithm is external."""

    canonical_source_identifier: str
    normalization_version: str
    canonical_url: str | None = None

    def __post_init__(self) -> None:
        _required_text(self.canonical_source_identifier, "canonical_source_identifier")
        _required_text(self.normalization_version, "normalization_version")
        if self.canonical_url is not None:
            _http_url(self.canonical_url, "canonical_url")


@dataclass(frozen=True, slots=True)
class PersistArticleRevision:
    """Immutable revision payload; server-owned IDs and versions are excluded."""

    source_id: str
    source_article_identity: SourceArticleIdentity
    original_url: str
    external_id: str | None
    normalized_title: str
    content_availability: ContentAvailability
    content_reference: str | None
    content_hash: str | None
    content_normalization_version: str | None
    summary: str | None
    language: str | None
    published_at: datetime | None
    observed_at: datetime
    change_reason: str
    rights_assessment_references: tuple[str, ...] = ()
    metadata: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in ("source_id", "normalized_title", "change_reason"):
            _required_text(getattr(self, field_name), field_name)
        if not isinstance(self.source_article_identity, SourceArticleIdentity):
            raise ValueError("source_article_identity must be a SourceArticleIdentity.")
        _http_url(self.original_url, "original_url")
        for field_name in (
            "external_id",
            "content_reference",
            "content_hash",
            "content_normalization_version",
            "summary",
            "language",
        ):
            _optional_text(getattr(self, field_name), field_name)
        if not isinstance(self.content_availability, ContentAvailability):
            raise ValueError("content_availability must be a ContentAvailability.")
        _aware_instant(self.observed_at, "observed_at")
        if self.published_at is not None:
            _aware_instant(self.published_at, "published_at")

        has_reference = self.content_reference is not None
        has_hash = self.content_hash is not None
        has_normalization = self.content_normalization_version is not None
        if self.content_availability in {
            ContentAvailability.AVAILABLE,
            ContentAvailability.PARTIAL,
        }:
            if not (has_reference and has_hash and has_normalization):
                raise ValueError(
                    "available or partial content requires content_reference, "
                    "content_hash, and content_normalization_version."
                )
            if len(self.content_hash or "") != 64 or any(
                character not in "0123456789abcdef" for character in self.content_hash or ""
            ):
                raise ValueError(
                    "content_hash must be a 64-character lowercase SHA-256 hex digest."
                )
        elif has_reference or has_hash or has_normalization:
            raise ValueError(
                "metadata-only or unavailable content must not persist "
                "content_reference, content_hash, or content_normalization_version."
            )

        if not isinstance(self.rights_assessment_references, tuple):
            raise TypeError("rights_assessment_references must be an immutable tuple.")
        for reference in self.rights_assessment_references:
            _required_text(reference, "rights_assessment_references item")
        if len(set(self.rights_assessment_references)) != len(
            self.rights_assessment_references
        ):
            raise ValueError("rights_assessment_references must not contain duplicates.")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))

    @property
    def revision_fingerprint(self) -> str:
        """SHA-256 identity for the semantic revision, not for retained article text."""

        manifest: dict[str, FrozenJson] = {
            "schema_version": ARTICLE_REVISION_FINGERPRINT_SCHEMA_VERSION,
            "source_id": self.source_id,
            "canonical_source_identifier": (
                self.source_article_identity.canonical_source_identifier
            ),
            "source_identity_normalization_version": (
                self.source_article_identity.normalization_version
            ),
            "normalized_title": self.normalized_title,
            "summary": self.summary,
            "language": self.language,
            "published_at": _timestamp_for_fingerprint(self.published_at),
            "content_availability": self.content_availability.value,
            "content_hash": self.content_hash,
            "content_normalization_version": self.content_normalization_version,
            "metadata": cast(FrozenJson, self.metadata) if self.metadata is not None else MappingProxyType({}),
        }
        return hashlib.sha256(_jcs(manifest).encode("utf-8")).hexdigest()
