# Global Economic News Intelligence

GENI is an event-centric global economic news intelligence platform. It separates published articles from real-world events, preserves evidence provenance, represents uncertainty explicitly, and uses deterministic workflows with bounded LLM assistance.

## Repository status

The repository contains architecture and governance documentation plus the initial executable Python foundation. The current code establishes pure domain lifecycle policies, a minimal CLI, and automated quality checks. It is **not** a production news-ingestion or publishing system.

The following capabilities remain disabled until their architecture, rights, privacy, security, and operational gates are satisfied:

- Production source acquisition and full-text retention.
- External LLM transmission of source content.
- Automatic event creation and matching decisions.
- Market-data integrations and semantic retrieval.
- Publication execution and recipient delivery.
- Processing of personal data outside an approved test context.

The authoritative readiness assessment is [Document 16](docs/16-implementation-readiness-and-release-gates.md). The first-slice contracts are in [Document 15](docs/15-first-slice-implementation-contracts.md).

## Development setup

Requirements: Python 3.12 or 3.13.

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

## Commands

~~~powershell
geni version
geni readiness
ruff check .
mypy
pytest
~~~

Or run the CLI without installing the console script:

~~~powershell
python -m global_economic_news_intelligence version
~~~

## Architecture boundaries

- Domain lifecycle policies are pure Python and have no persistence or provider dependencies.
- Application workflows own orchestration and authorization.
- Repositories own persistence; domain policies do not import database or ORM types.
- LLM output is untrusted input and cannot directly perform material domain transitions.
- External side effects require durable intent, idempotency, and reconciliation.
- Rights and privacy authorization are separate, operation-specific controls.

## Persistence status

No database engine or migration tool is configured yet. GENI-ADR-005 remains Proposed; a relational persistence proof-of-concept and explicit decision are required before choosing the production persistence adapter. The current foundation intentionally avoids creating a misleading in-memory or SQLite production implementation.

## License and content

This repository does not grant rights to third-party news content. Source access, storage, model processing, quotation, and republication must each be authorized for the specific operation.
