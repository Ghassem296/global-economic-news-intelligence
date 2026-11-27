"""Immutable Source registry record contract.

This module models configured source metadata only. It does not authorize
network access, collection, content retention, provider egress, or publication.
Adapter-specific configuration validation and use-time SSRF controls remain
owned by their respective boundaries.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from urllib.parse import parse_qsl, urlsplit

from global_economic_news_intelligence.domain.validation import (
    require_aware_instant,
    require_text,
)

type JsonScalar = str | int | float | bool | None
type FrozenJson = JsonScalar | tuple[FrozenJson, ...] | Mapping[str, FrozenJson]

_SENSITIVE_KEY_PARTS = (
    "secret",
    "password",
    "passwd",
    "token",
    "credential",
    "apikey",
    "authorization",
    "cookie",
    "privatekey",
)


def _freeze_config(value: object, field_name: str = "collection_config") -> FrozenJson:
    """Deep-freeze JSON-compatible configuration and reject secret-like keys."""

    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{field_name} cannot contain a non-finite number.")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJson] = {}
        for key, item in value.items():
            require_text(key, f"{field_name} key")
            normalized_key = "".join(
                character for character in key.casefold() if character.isalnum()
            )
            if any(part in normalized_key for part in _SENSITIVE_KEY_PARTS):
                raise ValueError(
                    f"{field_name} must not contain credentials or secret-like fields."
                )
            frozen[key] = _freeze_config(item, field_name)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_config(item, field_name) for item in value)
    raise TypeError(f"{field_name} must contain JSON-compatible values.")


def _validate_source_url(value: object) -> None:
    if not isinstance(value, str):
        raise ValueError("base_url must be a non-empty string.")
    require_text(value, "base_url")
    has_ambiguous_characters = any(
        ord(character) <= 0x20
        or ord(character) == 0x7F
        or character == "\\"
        for character in value
    )
    if has_ambiguous_characters:
        raise ValueError(
            "base_url must not contain whitespace, control characters, or backslashes."
        )
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("base_url must be an absolute HTTP(S) URL.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("base_url must not embed credentials.")
    if parsed.fragment:
        raise ValueError("base_url must not contain a fragment.")
    try:
        _port = parsed.port
    except ValueError as exc:
        raise ValueError("base_url contains an invalid port.") from exc
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = "".join(character for character in key.casefold() if character.isalnum())
        if any(part in normalized_key for part in _SENSITIVE_KEY_PARTS):
            raise ValueError("base_url query must not contain credential-like parameters.")


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """Versioned Source configuration snapshot; not a collection permission."""

    source_id: str
    name: str
    source_type: str
    base_url: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    language: str | None = None
    country_code: str | None = None
    ownership_group: str | None = None
    syndication_group: str | None = None
    collection_config: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for field_name in ("source_id", "name", "source_type", "version"):
            require_text(getattr(self, field_name), field_name)
        _validate_source_url(self.base_url)
        if not isinstance(self.is_active, bool):
            raise ValueError("is_active must be a boolean.")
        for field_name in (
            "language",
            "country_code",
            "ownership_group",
            "syndication_group",
        ):
            value = getattr(self, field_name)
            if value is not None:
                require_text(value, field_name)
        require_aware_instant(self.created_at, "created_at")
        require_aware_instant(self.updated_at, "updated_at")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not precede created_at.")

        config = self.collection_config
        if config is None:
            config = {}
        if not isinstance(config, Mapping):
            raise TypeError("collection_config must be a mapping.")
        frozen = _freeze_config(config)
        if not isinstance(frozen, Mapping):
            raise TypeError("collection_config must be a mapping.")
        object.__setattr__(self, "collection_config", frozen)
