import pytest

from global_economic_news_intelligence.config import (
    ConfigurationError,
    Environment,
    LogLevel,
    Settings,
)


def test_settings_use_safe_development_defaults() -> None:
    settings = Settings.from_env({})
    assert settings.environment is Environment.DEVELOPMENT
    assert settings.log_level is LogLevel.INFO


def test_settings_parse_environment_and_log_level() -> None:
    settings = Settings.from_env(
        {"GENI_ENV": "TEST", "GENI_LOG_LEVEL": "warning"}
    )
    assert settings.environment is Environment.TEST
    assert settings.log_level is LogLevel.WARNING


@pytest.mark.parametrize("value", ["", "staging", "prod", "productionx"])
def test_invalid_environment_is_rejected(value: str) -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_env({"GENI_ENV": value})


@pytest.mark.parametrize("value", ["TRACE", "FATAL", "verbose"])
def test_invalid_log_level_is_rejected(value: str) -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_env({"GENI_LOG_LEVEL": value})
