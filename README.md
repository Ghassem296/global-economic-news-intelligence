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

The authoritative readiness assessment is [Document 16](docs/16-implementation-readiness-and-release-gates.md). The first-slice contracts are in [Document 15](docs/15-first-slice-implementation-contracts.md), and the executable lifecycle baseline is in [Document 17](docs/17-executable-foundation-and-domain-lifecycle-contracts.md). The [ADR registry](docs/adr/README.md) is the authoritative inventory of architectural decisions.

## Development setup

Requirement: Python 3.15 only.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://releases.astral.sh/github/uv/releases/download/0.13.9/uv-installer.ps1 | iex"
uv --version
uv sync --locked --extra dev
```

The repository pins uv 0.13.9 in `pyproject.toml` and commits `uv.lock`. Use `uv sync --locked` so local environments do not silently resolve a different dependency set.

## Commands

```powershell
uv run --locked geni version
uv run --locked geni readiness
uv run --locked --no-sync ruff check .
uv run --locked --no-sync mypy
uv run --locked --no-sync pytest
```

Or run the CLI without installing the console script:

```powershell
uv run --locked python -m global_economic_news_intelligence version
```

## Architecture boundaries

- Domain lifecycle policies are pure Python and have no persistence or provider dependencies.
- Application workflows own orchestration and authorization.
- Repositories own persistence; domain policies do not import database or ORM types.
- LLM output is untrusted input and cannot directly perform material domain transitions.
- External side effects require durable intent, idempotency, and reconciliation.
- Rights and privacy authorization are separate, operation-specific controls.

## Persistence status

PostgreSQL is the Project Owner-selected target relational database. No production database adapter, driver, ORM/query layer, or migration tool is configured yet. GENI-ADR-005 remains Proposed; the PostgreSQL proof-of-concept, workload/correctness/recovery qualification, and formal ADR acceptance are required before production persistence activation. The current foundation intentionally avoids creating a misleading in-memory or SQLite production implementation.

## License and content

No open-source software license has been selected or granted for this repository. Public visibility does not grant permission to reuse, modify, or redistribute the software; do not assume that a license exists until an explicit license is approved and added.

This repository also does not grant rights to third-party news content. Source access, storage, model processing, quotation, and republication must each be authorized for the specific operation.


## Documentation repository tree

```text
global-economic-news-intelligence/
├── docs/
│   ├── 01-product-and-system-architecture.md
│   ├── 02-component-architecture-and-interfaces.md
│   ├── 03-data-model-and-storage-design.md
│   ├── 04-implementation-plan-and-roadmap.md
│   ├── 05-architecture-decision-records.md
│   ├── 06-documentation-governance-and-change-management.md
│   ├── 07-documentation-registry.md
│   ├── 08-security-architecture-and-threat-model.md
│   ├── 09-api-and-integration-contracts.md
│   ├── 10-source-credibility-and-independence.md
│   ├── 11-economic-taxonomy-specification.md
│   ├── 12-testing-and-evaluation-strategy.md
│   ├── 13-deployment-operations-and-observability.md
│   ├── 14-data-protection-and-privacy-specification.md
│   ├── 15-first-slice-implementation-contracts.md
│   ├── 16-implementation-readiness-and-release-gates.md
│   ├── 17-executable-foundation-and-domain-lifecycle-contracts.md
│   ├── adr/
│   │   ├── adr-template.md
│   │   ├── evidence/
│   │   │   └── GENI-ADR-005-persistence-proof-of-concept-protocol.md
│   │   ├── decisions/
│   │   │   ├── GENI-ADR-001-event-centric-intelligence-architecture.md
│   │   │   ├── GENI-ADR-002-article-deduplication-and-event-matching.md
│   │   │   ├── GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md
│   │   │   ├── GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md
│   │   │   ├── GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md
│   │   │   ├── GENI-ADR-006-provider-independent-llm-execution-architecture.md
│   │   │   ├── GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md
│   │   │   ├── GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md
│   │   │   ├── GENI-ADR-009-near-real-time-news-acquisition-strategy.md
│   │   │   ├── GENI-ADR-010-phased-text-audio-and-video-delivery.md
│   │   │   ├── GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md
│   │   │   ├── GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md
│   │   │   ├── GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md
│   │   │   ├── GENI-ADR-014-human-review-corrections-and-withdrawals.md
│   │   │   ├── GENI-ADR-015-market-data-integration-and-economic-impact-classification.md
│   │   │   ├── GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md
│   │   │   ├── GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md
│   │   │   ├── GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md
│   │   │   ├── GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md
│   │   │   └── GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md
│   │   └── README.md
│   ├── README.md
│   └── references/
│       └── agent-template/
│           ├── agent-template-architecture.md
│           ├── agent-template-implementation-specification.md
│           └── README.md
└── README.md
```
