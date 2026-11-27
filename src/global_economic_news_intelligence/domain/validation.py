"""Shared, dependency-free field validators for immutable domain payloads.

These helpers raise ``ValueError`` with a stable message so every payload contract
reports the same failure for the same kind of invalid field.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal


def require_text(value: object, field_name: str) -> None:
    """Require a non-empty, non-blank string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def require_aware_instant(value: object, field_name: str) -> None:
    """Require a timezone-aware ``datetime``."""
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")


def require_optional_finite_decimal(value: object, field_name: str) -> None:
    """Allow ``None`` or a finite ``Decimal``; reject floats, NaN and infinities."""
    if value is None:
        return
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field_name} must be a finite Decimal or None.")
