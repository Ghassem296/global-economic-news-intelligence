from __future__ import annotations

import asyncio
import json
import os
import platform
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg

ROOT = Path(__file__).parent
RESULTS = ROOT / "results" / "poc-results.json"
DATABASE_URL = os.environ.get("GENI_POC_DATABASE_URL", "")


async def postgres_metadata() -> dict[str, str]:
    if not DATABASE_URL:
        return {}
    connection = await psycopg.AsyncConnection.connect(DATABASE_URL)
    try:
        cursor = await connection.execute(
            "SELECT version(), current_setting('server_version_num')"
        )
        version, version_num = await cursor.fetchone()
        return {"server_version": version, "server_version_num": version_num}
    finally:
        await connection.close()


def main() -> int:
    suite = unittest.defaultTestLoader.discover(
        str(ROOT),
        pattern="test_*.py",
        top_level_dir=str(ROOT.parent.parent),
    )
    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    result = runner.run(suite)

    summary: dict[str, Any] = {
        "run_at_utc": datetime.now(UTC).isoformat(),
        "commit_sha": os.environ.get("GITHUB_SHA", "local-uncommitted"),
        "python_version": platform.python_version(),
        "psycopg_version": psycopg.__version__,
        "postgres_image_digest": os.environ.get(
            "GENI_POC_POSTGRES_IMAGE_DIGEST", "not-captured"
        ),
        "database": asyncio.run(postgres_metadata()),
        "tests_run": result.testsRun,
        "failures": [
            {"test": str(test), "traceback": traceback}
            for test, traceback in result.failures
        ],
        "errors": [
            {"test": str(test), "traceback": traceback}
            for test, traceback in result.errors
        ],
        "skipped": [
            {"test": str(test), "reason": reason}
            for test, reason in result.skipped
        ],
        "successful": result.wasSuccessful(),
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"PoC evidence written to {RESULTS}")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
