import json
import logging

from global_economic_news_intelligence.observability.logging import (
    SafeJsonFormatter,
    configure_logging,
)


def test_json_formatter_uses_allowlisted_fields_only() -> None:
    record = logging.LogRecord(
        name="geni.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="This free-form message must not be logged",
        args=(),
        exc_info=None,
    )
    record.event_name = "workflow_step_completed"
    record.correlation_id = "corr-1"
    record.secret = "must-not-appear"
    record.component = {"payload": "must-not-be-serialized"}
    rendered = SafeJsonFormatter().format(record)
    payload = json.loads(rendered)
    assert payload["event_name"] == "workflow_step_completed"
    assert payload["correlation_id"] == "corr-1"
    assert "secret" not in rendered
    assert "free-form message" not in rendered
    assert "must-not-be-serialized" not in rendered


def test_configure_logging_rejects_unknown_level() -> None:
    try:
        configure_logging("NOT_A_LEVEL")
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid log level should fail.")


def test_json_formatter_omits_non_finite_float_metadata() -> None:
    for value in (float("nan"), float("inf"), float("-inf")):
        record = logging.LogRecord(
            name="geni.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="ignored",
            args=(),
            exc_info=None,
        )
        record.duration_ms = value

        rendered = SafeJsonFormatter().format(record)
        payload = json.loads(rendered)

        assert "duration_ms" not in payload
        assert "NaN" not in rendered
        assert "Infinity" not in rendered
