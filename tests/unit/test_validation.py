from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from global_economic_news_intelligence.domain.validation import (
    require_aware_instant,
    require_optional_finite_decimal,
    require_text,
)


@pytest.mark.parametrize("value", ["", "   ", None, 1, b"x"])
def test_require_text_rejects_blank_or_non_string(value: object) -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        require_text(value, "name")


def test_require_text_accepts_non_blank_string() -> None:
    require_text("value", "name")


@pytest.mark.parametrize("value", [None, "2026-11-27", datetime(2026, 11, 27)])
def test_require_aware_instant_rejects_naive_or_non_datetime(value: object) -> None:
    with pytest.raises(ValueError, match="when must be a timezone-aware datetime"):
        require_aware_instant(value, "when")


def test_require_aware_instant_accepts_aware_datetime() -> None:
    require_aware_instant(datetime(2026, 11, 27, tzinfo=UTC), "when")


@pytest.mark.parametrize("value", [0.5, 1, "1", Decimal("NaN"), Decimal("Infinity")])
def test_require_optional_decimal_rejects_non_finite_decimal(value: object) -> None:
    with pytest.raises(ValueError, match="score must be a finite Decimal or None"):
        require_optional_finite_decimal(value, "score")


@pytest.mark.parametrize("value", [None, Decimal("0.75"), Decimal("-1")])
def test_require_optional_decimal_accepts_none_or_finite_decimal(value: object) -> None:
    require_optional_finite_decimal(value, "score")
