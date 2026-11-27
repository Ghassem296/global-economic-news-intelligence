from __future__ import annotations

from datetime import UTC, datetime

import pytest

from global_economic_news_intelligence.domain.source_contracts import SourceRecord

NOW = datetime(2026, 11, 27, 8, 0, tzinfo=UTC)


def source(**overrides: object) -> SourceRecord:
    values: dict[str, object] = {
        "source_id": "source-1",
        "name": "Central Bank News",
        "source_type": "official-dataset",
        "base_url": "https://example.com/economic-data",
        "version": "source-version-1",
        "is_active": True,
        "created_at": NOW,
        "updated_at": NOW,
        "language": "en",
        "country_code": "GB",
        "ownership_group": None,
        "syndication_group": None,
        "collection_config": {"feed_path": "/rss", "poll_interval": 300},
    }
    values.update(overrides)
    return SourceRecord(**values)  # type: ignore[arg-type]


def test_source_record_preserves_configured_source_metadata() -> None:
    result = source()
    assert result.source_id == "source-1"
    assert result.source_type == "official-dataset"
    assert result.is_active is True
    assert result.collection_config == {"feed_path": "/rss", "poll_interval": 300}


def test_source_record_deeply_freezes_collection_configuration() -> None:
    config = {"parser": {"labels": ["economy", "rates"]}}
    result = source(collection_config=config)
    config["parser"]["labels"].append("changed")  # type: ignore[index, union-attr]
    assert result.collection_config is not None
    assert result.collection_config["parser"]["labels"] == ("economy", "rates")  # type: ignore[index]
    with pytest.raises(TypeError):
        result.collection_config["new"] = "value"  # type: ignore[index]


def test_source_record_defaults_to_empty_immutable_configuration() -> None:
    result = source(collection_config=None)
    assert result.collection_config == {}
    assert result.collection_config is not None
    with pytest.raises(TypeError):
        result.collection_config["new"] = "value"  # type: ignore[index]


@pytest.mark.parametrize(
    "base_url",
    [
        "example.com/feed",
        "ftp://example.com/feed",
        "https:///missing-host",
        "https://user:password@example.com/feed",
        "https://example.com/feed#fragment",
        "https://example.com:invalid/feed",
        "https://example.com/feed?api_key=secret",
        "https://example.com/feed path",
        "https://example.com/feed\\path",
        "https://example.com/feed\npath",
    ],
)
def test_source_record_rejects_invalid_or_credential_bearing_urls(base_url: str) -> None:
    with pytest.raises(ValueError):
        source(base_url=base_url)


@pytest.mark.parametrize(
    "config",
    [
        {"api_key": "secret"},
        {"nested": {"access_token": "secret"}},
        {"password": "secret"},
        {"authorizationHeader": "Bearer secret"},
    ],
)
def test_source_record_rejects_secret_like_configuration_fields(
    config: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match="credentials or secret-like"):
        source(collection_config=config)


def test_source_record_rejects_non_json_configuration_values() -> None:
    with pytest.raises(TypeError, match="JSON-compatible"):
        source(collection_config={"invalid": object()})
    with pytest.raises(ValueError, match="non-finite"):
        source(collection_config={"invalid": float("nan")})


@pytest.mark.parametrize("field", ["source_id", "name", "source_type", "version"])
def test_source_record_requires_identity_and_version_fields(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        source(**{field: " "})


def test_source_record_requires_boolean_activation_state() -> None:
    with pytest.raises(ValueError, match="is_active"):
        source(is_active="yes")


def test_source_record_requires_timezone_aware_server_timestamps() -> None:
    with pytest.raises(ValueError, match="created_at"):
        source(created_at=datetime(2026, 11, 27, 8, 0))
    with pytest.raises(ValueError, match="updated_at"):
        source(updated_at=datetime(2026, 11, 27, 8, 0))


def test_source_record_rejects_updated_time_before_creation_time() -> None:
    with pytest.raises(ValueError, match="must not precede"):
        source(updated_at=datetime(2026, 11, 27, 7, 59, tzinfo=UTC))


def test_unknown_source_context_remains_null_not_inferred() -> None:
    result = source(language=None, country_code=None, ownership_group=None, syndication_group=None)
    assert result.language is None
    assert result.country_code is None
    assert result.ownership_group is None
    assert result.syndication_group is None


def test_inactive_source_is_still_only_configuration_not_rights_permission() -> None:
    result = source(is_active=False)
    assert result.is_active is False
    # No rights or collection authorization is represented by this record.
