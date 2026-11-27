"""Shared, dependency-free field validators for immutable domain payloads.

These helpers raise ``ValueError`` with a stable message so every payload contract
reports the same failure for the same kind of invalid field.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from urllib.parse import parse_qsl, urlsplit


def require_text(value: object, field_name: str) -> None:
    """Require a non-empty, non-blank string."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def require_aware_instant(value: object, field_name: str) -> None:
    """Require a timezone-aware ``datetime``."""
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be a timezone-aware datetime.")



_URL_SENSITIVE_KEY_PARTS = (
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


def require_http_url(value: object, field_name: str) -> None:
    """Require a structurally safe absolute HTTP(S) URL without embedded secrets.

    This validates URL syntax and credential hygiene only. DNS resolution,
    redirect revalidation, private-address blocking, and egress policy remain
    use-time responsibilities of the network boundary.
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a non-empty string.")
    require_text(value, field_name)
    if any(
        ord(character) <= 0x20
        or ord(character) == 0x7F
        or character == "\\"
        for character in value
    ):
        raise ValueError(
            f"{field_name} must not contain whitespace, control characters, or backslashes."
        )
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid absolute HTTP(S) URL.") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError(f"{field_name} must be an absolute HTTP(S) URL.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError(f"{field_name} must not embed credentials.")
    if parsed.fragment:
        raise ValueError(f"{field_name} must not contain a fragment.")
    try:
        _port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{field_name} contains an invalid port.") from exc
    for key, _ in parse_qsl(parsed.query, keep_blank_values=True):
        normalized_key = "".join(
            character for character in key.casefold() if character.isalnum()
        )
        if any(part in normalized_key for part in _URL_SENSITIVE_KEY_PARTS):
            raise ValueError(
                f"{field_name} query must not contain credential-like parameters."
            )

def require_optional_finite_decimal(value: object, field_name: str) -> None:
    """Allow ``None`` or a finite ``Decimal``; reject floats, NaN and infinities."""
    if value is None:
        return
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{field_name} must be a finite Decimal or None.")
