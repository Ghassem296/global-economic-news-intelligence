"""Typed payload contract for persisting an immutable ArticleRevision.

This module validates the revision payload shape only. Source identity
canonicalization, metadata-only idempotency, rights decisions, and persistence
remain application/policy responsibilities.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from urllib.parse import urlsplit

type JsonScalar = str | int | float | bool | None
type FrozenJson = JsonScalar | tuple[FrozenJson, ...] | Mapping[str, FrozenJson]


class ContentAvailability(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    METADATA_ONLY = "metadata-only"
    UNAVAILABLE = "unavailable"


def _required_text(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def _optional_text(value: object, field_name: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"{field_name} must be a non-empty string when supplied.")


def _aware_instant(value: object, field_name: str) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")


def _http_url(value: object, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{field_name} must be an absolute HTTP(S) URL.")


def _freeze_json(value: object, field_name: str) -> FrozenJson:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_name} cannot contain a non-finite number.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJson] = {}
        for key, item in value.items():
            _required_text(key, f"{field_name} key")
            frozen[key] = _freeze_json(item, field_name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item, field_name) for item in value)
    raise TypeError(f"{field_name} must contain JSON-compatible values.")


def _freeze_metadata(value: Mapping[str, object] | None) -> Mapping[str, FrozenJson] | None:
    if value is None:
        return None
    frozen = _freeze_json(value, "metadata")
    if not isinstance(frozen, Mapping):
        raise TypeError("metadata must be a mapping.")
    return frozen


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
        for field_name in ("external_id", "content_reference", "content_hash",
                           "content_normalization_version", "summary", "language"):
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
        elif has_reference:
            raise ValueError(
                "metadata-only or unavailable content must not have content_reference."
            )
        if has_hash != has_normalization:
            raise ValueError(
                "content_hash and content_normalization_version must be supplied together."
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
