"""Minimal command-line entry point for the GENI foundation."""

from __future__ import annotations

import argparse
import sys

from global_economic_news_intelligence import __version__
from global_economic_news_intelligence.config import ConfigurationError, Settings
from global_economic_news_intelligence.observability.logging import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geni",
        description="Global Economic News Intelligence",
    )
    parser.add_argument(
        "command",
        choices=("version", "readiness"),
        help="Show the application version or current capability boundary.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        settings = Settings.from_env()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    configure_logging(settings.log_level.value)

    if args.command == "version":
        print(__version__)
        return 0
    if args.command == "readiness":
        print("GENI foundation is installed.")
        print("Production acquisition, LLM egress, publication, and delivery are disabled.")
        print("See docs/16-implementation-readiness-and-release-gates.md.")
        return 0
    print("Unsupported command.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
