# Global Economic News Intelligence
## Implementation Plan & Development Roadmap

**Document ID:** GENI-PLAN-004

**Version:** 1.2
**Status:** Draft — Under Architecture Review
**Last Updated:** 2026-11-16
**Project:** Global Economic News Intelligence

---

## 1. Purpose

This document defines the implementation sequence, development stages, dependencies, milestones, testing strategy, and acceptance criteria for Global Economic News Intelligence.

The objective is to build a reliable, event-centric economic news intelligence platform through incremental, testable implementation.

The roadmap is governed by the following product-specific documents:

1. Product & System Architecture.
2. Component Architecture & Interface Contracts.
3. Data Model & Storage Design.
4. Architecture Decision Records.

The generic Agent Template Architecture and Generic Agent Template Implementation Specification are foundational reference documents. They are not, by themselves, requirements to implement a complete conversational Agent Runtime in this product.

The initial product release focuses on text-based economic news intelligence. Audio and video capabilities are outside the initial release scope.

This roadmap is a development plan, not an approval of unresolved architectural decisions. Technology and policy choices that require ADR approval remain provisional until formally accepted.

---

## 2. Development Strategy

The project follows an incremental, workflow-first development strategy.

Each development stage should produce a working, testable result and reduce a meaningful product or technical risk.

The implementation should avoid building infrastructure before a concrete requirement has been demonstrated.

### 2.1 Core Principles

1. Architecture and critical decisions before dependent implementation.
2. Small, independently testable components.
3. Domain logic separated from infrastructure.
4. Deterministic workflows as the default execution model.
5. LLM reasoning only where it adds measurable value.
6. Evidence provenance designed into the initial data model.
7. Evaluation and quality measurement from the beginning.
8. Explicit event identity and correlation policies.
9. Idempotent processing and recoverable workflows.
10. Controlled external dependencies and operating costs.
11. Security and content rights considered at acquisition time.
12. No premature distributed architecture.
13. No mandatory vector database without an approved requirement.
14. No premature audio or video implementation.

### 2.2 Workflow-First Architecture

The product is primarily a collection of deterministic application workflows supported by shared LLM execution capabilities.

The following operations should normally remain deterministic:

- Source configuration and collection scheduling.
- Article normalization and persistence.
- Exact and near-duplicate candidate generation.
- Database operations and state transitions.
- Event history recording.
- Publication policy enforcement.
- Review queue management.
- Report versioning and delivery.
- Retry, recovery, and idempotency handling.

LLMs may support tasks such as:

- Topic classification.
- Entity and claim extraction.
- Entity resolution.
- Event matching assistance.
- Evidence interpretation.
- Economic analysis.
- Report generation.

LLM output must be validated and must not directly bypass domain policies or publication controls.

A shared LLM Execution Layer should provide provider abstraction, structured output validation, execution budgets, deadlines, retry policies, cancellation, and usage tracking.

A generic conversational loop, conversation memory, generic MCP integration, or autonomous tool execution is not an initial product requirement.

---

## 3. Scope and Release Terminology

The roadmap distinguishes development stages from product capability phases.

This distinction avoids using the term "Phase 1" for both project setup and product functionality.

### 3.1 Initial Product Release

The initial release is the text-based economic intelligence platform.

It should support:

- International economic news acquisition.
- Article normalization and deduplication.
- Economic topic classification.
- Entity and claim extraction.
- Event detection and correlation.
- Evidence and uncertainty management.
- Economic analysis.
- Event dossiers and versioned reports.
- Publication decisions and human review where required.
- Text delivery.
- Scheduling, observability, and recovery.

### 3.2 Future Product Capability Phases

| Product Phase | Scope |
|---|---|
| Product Phase 1 | Text-based economic news intelligence |
| Product Phase 2 | Audio intelligence and briefings |
| Product Phase 3 | Video intelligence and publishing |
| Product Phase 4 | Advanced intelligence, personalization, and automation |

These product phases do not prescribe the order of engineering tasks. The development stages below define that order.

---

## 4. Development Environment and Technology Strategy

### 4.1 Initial Technology Candidates

The following technologies are candidates for the initial implementation. Choices requiring architectural commitment must be approved through the ADR process.

| Area | Candidate |
|---|---|
| Language | Python |
| Python version | A supported stable Python release, explicitly pinned for the project |
| Package management | uv |
| Data validation | Pydantic |
| LLM integration | Provider-independent adapter, with LiteLLM as a candidate |
| Database | Relational database; SQLite is a candidate for the initial deployment |
| Database access | SQLAlchemy or an equivalent repository-backed approach |
| Migrations | Alembic or an equivalent migration mechanism |
| Testing | pytest |
| Async testing | pytest-asyncio |
| Linting and formatting | Ruff |
| Type checking | mypy or pyright |
| Configuration | Validated settings and environment variables |
| Logging | Structured logging |
| CI | GitHub Actions |
| Version control | Git |

The selected Python version, database access library, migration mechanism, async database strategy, and LLM adapter must be recorded in the appropriate architecture decisions before they become implementation constraints.

### 4.2 Database Considerations

If SQLite is selected for the initial deployment, its implementation must explicitly address:

- Foreign key enforcement.
- Transaction boundaries.
- Write concurrency.
- Busy timeout behavior.
- WAL suitability and configuration.
- Async access strategy.
- Backup consistency.
- Migration testing.

The system must not assume that SQLite provides the same concurrency characteristics as a client-server database.

PostgreSQL may be considered as a future deployment option, but migration must not be assumed to be automatic merely because repositories are used.

### 4.3 Development Tools

Recommended development environment:

- Visual Studio Code.
- Python extension.
- Ruff extension.
- Git integration.
- Python debugger.
- Terminal with uv available.

### 4.4 Environment Configuration

Separate configuration must be supported for:

- Local development.
- Automated testing.
- Evaluation.
- Production deployment.

Secrets must be supplied through environment variables or an appropriate secret provider.

A `.env.example` file should document required configuration without containing real credentials.

Production credentials must never be committed to version control or written into ordinary application logs.

---

## 5. Project Structure

The following is a proposed target structure. It is not a requirement to create every directory during project initialization.

```text
global-economic-news-intelligence/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       └── eval.yml
│
├── docs/
│   ├── 01-product-and-system-architecture.md
│   ├── 02-component-architecture-and-interfaces.md
│   ├── 03-data-model-and-storage-design.md
│   ├── 04-implementation-plan-and-roadmap.md
│   ├── 05-agent-template-architecture.md
│   ├── 06-agent-template-implementation-specification.md
│   ├── 07-architecture-decision-records.md
│   └── adr/
│       ├── README.md
│       └── adr-template.md
│
├── evals/
│   ├── datasets/
│   ├── runners/
│   ├── rubrics/
│   ├── metrics/
│   └── failure-analysis/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── security/
│   ├── e2e/
│   └── fixtures/
│
├── src/
│   └── global_economic_news_intelligence/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── exceptions.py
│       │
│       ├── domain/
│       │   ├── entities/
│       │   ├── value_objects/
│       │   ├── enums/
│       │   ├── policies/
│       │   └── repositories/
│       │
│       ├── application/
│       │   ├── workflows/
│       │   ├── services/
│       │   ├── commands/
│       │   └── queries/
│       │
│       ├── acquisition/
│       │   ├── collectors/
│       │   ├── adapters/
│       │   └── source_registry.py
│       │
│       ├── processing/
│       │   ├── normalization/
│       │   ├── deduplication/
│       │   ├── classification/
│       │   ├── entity_extraction/
│       │   └── translation/
│       │
│       ├── intelligence/
│       │   ├── event_detection/
│       │   ├── event_matching/
│       │   ├── event_management/
│       │   ├── evidence/
│       │   ├── analysis/
│       │   └── importance/
│       │
│       ├── reporting/
│       │   ├── generators/
│       │   ├── templates/
│       │   ├── publication/
│       │   ├── review/
│       │   └── delivery/
│       │
│       ├── llm/
│       │   ├── interfaces/
│       │   ├── providers/
│       │   ├── schemas/
│       │   └── execution/
│       │
│       ├── infrastructure/
│       │   ├── persistence/
│       │   │   ├── models/
│       │   │   ├── repositories/
│       │   │   ├── migrations/
│       │   │   └── database.py
│       │   ├── external_services/
│       │   └── delivery/
│       │
│       ├── scheduling/
│       └── observability/
│
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
├── README.md
├── CHANGELOG.md
├── SECURITY.md
└── Makefile
```

The actual directory structure should evolve with implementation.

The generic Agent Template documents remain reference material. Product-specific news workflows must not be placed inside a generic conversational runtime merely to reproduce the template structure.

A separate generic runtime package should be introduced only if a concrete reusable requirement justifies it.

---

## 6. Development Stage 0 — Documentation and Architecture Approval

### Objectives

Establish a consistent architecture baseline and resolve decisions that block safe implementation.

### Tasks

1. Review the product architecture.
2. Review component responsibilities and interfaces.
3. Review the data model and storage design.
4. Review the implementation roadmap.
5. Verify documentation links and file names.
6. Identify conflicting or duplicated requirements.
7. Establish the ADR register.
8. Identify decisions that require formal ADRs.
9. Define initial product scope.
10. Define the initial economic topic taxonomy.
11. Define initial report and publication requirements.
12. Define the initial source and content-rights policy.
13. Define initial event identity and correlation rules.
14. Define the review process for held reports.
15. Define the first evaluation cases.

### Required Architectural Topics

The following topics must be resolved or explicitly bounded before dependent implementation:

- Workflow-first architecture and shared LLM execution.
- Article deduplication versus event matching.
- Event identity, matching, merging, and splitting.
- Semantic similarity and embedding strategy.
- Initial persistence and async execution strategy.
- News acquisition and full-text access rights.
- Publication, review, correction, and withdrawal policy.
- Market data availability and impact classification.
- Separate Event Importance, Economic Relevance, and Economic Impact assessment methodology (GENI-ADR-019).
- Processing recovery and idempotency.

Not every future capability must be fully designed before the first implementation. However, unresolved decisions must not be disguised as accepted architecture.

### Deliverables

- Consistent architecture documents.
- Maintained ADR register.
- Initial scope and constraints.
- Defined first implementation slice.
- Initial evaluation plan.

### Exit Criteria

- Critical architecture conflicts are resolved.
- Decisions blocking the first implementation slice are accepted or explicitly bounded.
- The initial product scope is clear.
- The documents identify which choices remain provisional.
- No dependent implementation begins on the assumption that a Proposed ADR is already Accepted.

---

## 7. Development Stage 1 — Project Foundation

### Objectives

Create a maintainable Python application foundation.

### Tasks

1. Initialize the Python project with uv.
2. Configure package metadata.
3. Pin the supported Python version.
4. Configure Ruff.
5. Configure type checking.
6. Configure pytest and pytest-asyncio.
7. Implement validated application configuration.
8. Implement shared exceptions.
9. Configure structured logging.
10. Establish import architecture rules.
11. Configure initial CI workflows.
12. Add dependency and secret scanning.
13. Establish test conventions.
14. Add a minimal CLI entry point.

### Deliverables

- Installable Python package.
- Validated configuration.
- Basic CLI.
- Test infrastructure.
- Initial CI pipeline.
- Development instructions.

### Exit Criteria

- The project installs successfully.
- Tests run without paid external services.
- Linting and type checking work.
- CI runs automatically.
- Secrets are excluded from version control.
- The package structure follows the approved dependency boundaries.

---

## 8. Development Stage 2 — Domain Foundations and Initial Evaluation

### Objectives

Implement only the domain concepts needed for the first end-to-end workflow, while establishing evaluation practices early.

### Initial Domain Concepts

The first implementation slice should introduce the minimum required concepts, including:

- Source.
- Article and ArticleRevision.
- Topic classification.
- Entity and entity mention.
- Event.
- ArticleRevision as an immutable content version.
- EventMatchCase, EventMatchCandidate, and EventMatchDecision as separate matching records.
- ArticleEventLink as a decision-authorized association.
- ProcessingRun and ProcessingStep.
- Evidence and evidence references.
- Separate Analysis records for each assessment type.
- Report and immutable ReportVersion.
- PublicationDecision and typed ReviewRecord.
- DeliveryRecord and DeliveryAttempt.

Additional concepts from the approved data model should be introduced when required by a concrete workflow.

The project should not implement every planned table or entity simply because it appears in the complete conceptual model.

### Domain Rules

Implement and test:

- Article identity and revision behavior.
- Article deduplication boundaries.
- Per-ArticleRevision EventMatchCase creation and uniqueness.
- Candidate evaluation separate from case-level EventMatchDecision.
- MATCH-only ArticleEventLink creation with exact case and decision references.
- Event association correction through immutable successor decisions.
- Event lifecycle transitions.
- Event history append-only behavior.
- Claim and evidence relationships.
- Analysis versioning.
- Report versioning.
- Publication decision rules.
- Review task transitions.
- Delivery idempotency boundaries.

### Initial Evaluation Work

Create a small, human-reviewed reference dataset covering:

- Exact duplicate articles.
- Near-duplicate articles.
- Different articles about the same event.
- Similar topics describing different events.
- Ambiguous event matches.
- Conflicting source claims.
- Unsupported analytical statements.

The dataset should evolve as the system develops.

### Deliverables

- Initial domain entities and policies.
- Domain-level tests.
- Initial reference dataset.
- Initial evaluation rubrics.

### Exit Criteria

- Core domain rules are tested.
- Domain code does not depend on database or LLM SDKs.
- Event identity is not based solely on topic similarity.
- Article revisions are immutable and material changes create a new revision.
- Candidate scores and statuses cannot substitute for case-level decisions.
- Every active article-event association is authorized by the effective MATCH decision for its case.
- Evaluation cases are version-controlled and reproducible.
- The first workflow can be implemented without inventing domain semantics.

---

## 9. Development Stage 3 — Persistence and Recovery Foundations

### Objectives

Implement the minimum reliable persistence layer for the first end-to-end workflow.

### Tasks

1. Confirm the approved database and access strategy.
2. Configure database lifecycle management.
3. Implement migrations.
4. Create the initial schema.
5. Implement repository interfaces and adapters.
6. Implement transaction boundaries.
7. Enforce foreign keys and required unique constraints.
8. Implement processing run and step persistence.
9. Implement collection checkpoint persistence.
10. Implement idempotency keys for supported operations.
11. Implement recovery of expired or interrupted work.
12. Add repository contract tests.
13. Document backup and restore procedures.

### Important Requirements

The persistence layer must support:

- Stable identifiers.
- Append-only history where required.
- Explicit versioning.
- Transactional state changes.
- Idempotent reruns.
- Processing status and error records.
- Recovery after interruption.
- Auditability of publication and review decisions.

A polymorphic reference without enforceable integrity must not silently replace required foreign-key relationships.

The exact persistence design must follow the accepted data model and ADRs.

### Deliverables

- Initial relational schema.
- Versioned migrations.
- Repository implementations.
- Transaction and recovery tests.
- Backup and restore instructions.

### Exit Criteria

- Required initial workflow entities can be stored and retrieved.
- Foreign keys and unique constraints are verified.
- Critical state changes are transactional.
- Repeated execution does not create uncontrolled duplicates.
- Interrupted processing can be detected and recovered safely.
- Migration tests pass.

---

## 10. Development Stage 4 — Shared LLM Execution and Vertical Slice

### Objectives

Build the shared LLM capability and prove that the system can execute one complete economic news workflow.

This stage intentionally occurs before the full implementation of all intelligence components.

### Shared LLM Execution Tasks

1. Define provider-independent request and response contracts.
2. Implement the selected provider adapter.
3. Implement structured output validation.
4. Implement model and prompt version tracking.
5. Apply token and execution budgets.
6. Apply deadlines and cancellation.
7. Implement bounded retry behavior.
8. Track token usage and cost when available.
9. Record model execution provenance.
10. Treat source content as untrusted input.
11. Prevent analysis stages from receiving unrestricted tool access.

The LLM layer should remain an execution capability. It must not own product workflows or domain state transitions.

### Vertical Slice

Implement one limited workflow:

```text
Configured Source
       |
       v
Collect One Article
       |
       v
Normalize and Persist
       |
       v
Classify the Article
       |
       v
Resolve an EventMatchCase
       |
       v
Evaluate EventMatchCandidate records
       |
       v
Record EventMatchDecision
       |
       v
Apply ArticleEventLink only for MATCH
       |
       v
Attach Initial Evidence
       |
       v
Generate a Structured Analysis
       |
       v
Generate a Draft Report
       |
       v
Apply Publication Policy
       |
       v
Store the Result
```

The first slice may use a deliberately small set of sources and a limited taxonomy.

It does not need to support every event type or delivery channel.

### Deliverables

- Shared LLM Execution Layer.
- Initial provider integration.
- Structured output contracts.
- LLM usage records.
- A working vertical slice.
- End-to-end test and trace.

### Exit Criteria

- The workflow completes using controlled dependencies.
- LLM outputs are schema-validated.
- LLM calls respect budgets and deadlines.
- Usage is recorded where provider data is available.
- The workflow can be rerun without uncontrolled duplication.
- The generated report retains source and evidence references.
- Event association is applied only through a case-level MATCH decision; a test stub may simulate candidate retrieval but must not bypass the decision and link invariants.
- Publication decisions cannot be bypassed.

---

## 11. Development Stage 5 — News Source Management and Acquisition

### Objectives

Collect international economic news from configured and approved sources.

### Tasks

1. Define the source adapter contract.
2. Implement SourceRegistry.
3. Implement an initial RSS collector.
4. Add approved API or other source adapters when justified.
5. Implement incremental collection.
6. Implement pagination where required.
7. Implement checkpoint handling.
8. Normalize collection errors.
9. Apply timeout and safe retry policies.
10. Implement source health records.
11. Implement source assessment records where required.
12. Record collection provenance.
13. Add collection observability.
14. Implement source URL and redirect safety checks.

### Initial Source Strategy

Start with a limited set of reputable international sources.

Source selection should prioritize:

- Reliable publication history.
- Relevant economic coverage.
- Accessible structured feeds or APIs.
- Clear publication timestamps.
- Stable source identifiers.
- Transparent attribution.
- Documented access and reuse conditions.

### Content Access and Rights

RSS availability does not imply permission to store or republish the complete article.

The acquisition design must distinguish:

- Feed metadata.
- Article title and excerpt.
- Licensed article content.
- Publicly accessible article content.
- Content requiring restricted or temporary access.
- Content that must not be retained.

Full-text acquisition and retention must follow the approved rights policy.

### Security

Source ingestion must defend against:

- Server-side request forgery.
- Unsafe redirects.
- Private or restricted network destinations.
- Unexpected content types.
- Oversized responses.
- Malformed feeds.
- Malicious or misleading metadata.

### Deliverables

- Source registry.
- Initial collectors.
- Collection checkpoints.
- Collection execution records.
- Source health visibility.
- Content-access policy enforcement.

### Exit Criteria

- Configured sources can be collected.
- Repeated collection does not create uncontrolled duplicates.
- Failed collection does not advance an unsafe checkpoint.
- Source failures are observable.
- Collection can resume after interruption.
- Unsafe URLs and redirects are rejected.
- Content is retained only according to the configured rights policy.

---

## 12. Development Stage 6 — Article Processing

### Objectives

Transform collected publications into normalized article records.

### Tasks

1. Implement ArticleNormalizer.
2. Implement canonical URL handling.
3. Normalize timestamps and time zones.
4. Detect source language.
5. Define original and normalized language fields.
6. Implement content fingerprinting.
7. Implement exact duplicate detection.
8. Implement near-duplicate candidate generation.
9. Implement TopicClassifier.
10. Implement EntityExtractor.
11. Implement entity resolution foundations.
12. Implement article revision handling.
13. Implement processing status management.
14. Implement translation support only where required by the approved language policy.
15. Add processing evaluation cases.

### Article Deduplication

Article deduplication must remain independent of event matching.

Different publications may describe the same event and must remain separate article records.

The system should distinguish:

- Exact duplicates.
- Near-duplicate versions.
- Syndicated or wire-copy content.
- Updated versions of an article.
- Independent reporting about the same event.

A similarity score alone must not cause irreversible deletion or merging.

### Deliverables

- Normalized article records.
- Article revision support.
- Duplicate candidate records.
- Topic classifications.
- Extracted entities and mentions.
- Processing metadata.

### Exit Criteria

- Articles are normalized consistently.
- Exact duplicates are handled deterministically.
- Near-duplicate candidates retain their similarity and decision provenance.
- Related but distinct publications are preserved.
- Topic classifications include method and confidence metadata.
- Entity mentions retain enough provenance to be reviewed.
- Processing can be repeated safely.

---

## 13. Development Stage 7 — Event Intelligence

### Objectives

Implement the event-centric intelligence layer.

This is the core product capability.

### Tasks

1. Implement EventDetector.
2. Implement candidate event generation.
3. Implement EventMatcher.
4. Implement semantic and lexical matching signals.
5. Implement entity and temporal matching signals.
6. Implement EventService.
7. Implement article-event association.
8. Implement event lifecycle transitions.
9. Implement EventHistory.
10. Implement event relationship handling.
11. Implement event merge and split operations.
12. Implement EventMatchCase, EventMatchCandidate, and EventMatchDecision lifecycle.
13. Implement authorized review routing and successor-decision handling for ambiguous or corrected cases.
14. Implement ArticleEventLink creation and deactivation through EventService with exact case and decision provenance.
15. Implement event matching evaluation datasets.

### Event Identity Policy

Event identity must represent the same underlying real-world occurrence or continuing development.

Sharing a topic, country, organization, or entity is not sufficient to establish event identity.

For example:

- A central bank rate decision is an event.
- A subsequent currency movement may be a separate event.
- The two events may be related through a causal, consequential, or contextual relationship.
- They must not be merged merely because they concern the same central bank.

### Event Resolution Outcomes

Each candidate must result in an explicit resolution:

- Associate with an existing event.
- Create a new event.
- Mark as ambiguous or requiring review.
- Reject the candidate association.

The system must preserve:

- Candidate signals and scores.
- Matching method and policy version.
- Final decision.
- Decision provenance.
- Relevant event history.

Semantic similarity is a required matching capability, but a dedicated vector database is not automatically required.

The initial implementation may use an approved embedding service and a simple storage or retrieval strategy. The exact approach must follow the relevant ADR.

No universal similarity threshold should be assumed without evaluation and calibration.

### Event Identity Integrity

Event IDs must remain stable.

Merge and split operations must preserve historical references and record:

- Source and resulting event IDs.
- Reason.
- Method.
- Confidence or assessment.
- Affected article associations.
- Decision time.
- Policy version.

Historical event records must not be silently deleted or rewritten.

### Deliverables

- Event detection.
- Event matching cases, candidate evaluation, and immutable decisions.
- Authorized event creation and decision-based article-event association.
- Human review and association correction workflow.
- Event creation and updates.
- Event history and relationships.
- Event merge and split operations.

### Exit Criteria

- Multiple articles can be associated with one event.
- Unrelated developments are not automatically merged.
- Ambiguous matches are explicitly represented.
- Event identity operations are traceable.
- Event lifecycle transitions are validated.
- Every resolved development has one effective case-level decision; unresolved cases remain explicit.
- Every active ArticleEventLink references its EventMatchCase and effective MATCH decision.
- Human corrections create successor decisions and preserve prior link history.
- Event identity operations are traceable.
- False merges and event fragmentation are measured.

---

## 14. Development Stage 8 — Evidence and Economic Analysis

### Objectives

Produce evidence-based economic intelligence.

### Tasks

1. Implement Claim extraction.
2. Implement EvidenceService.
3. Implement evidence spans or equivalent precise source locators.
4. Implement ClaimEvidenceLink.
5. Implement claim assessment.
6. Implement source attribution.
7. Implement contradictory claim detection.
8. Implement source independence assessment.
9. Implement uncertainty representation.
10. Implement Event Importance assessment as an independent versioned Analysis type.
11. Implement Economic Relevance assessment as an independent versioned Analysis type.
12. Implement channel-based Economic Impact assessment as an independent versioned Analysis type.
13. Implement optional market-reaction assessment only when suitable market observations are available.
14. Implement analysis versioning and input fingerprints.
15. Add separate assessment evaluation datasets.

### Economic Analysis Dimensions

The initial analysis may consider:

- Inflation.
- Interest rates.
- Currency movements.
- Financial markets.
- International trade.
- Energy markets.
- Supply chains.
- Employment.
- Public debt.
- Fiscal policy.
- Economic growth.
- Financial stability.

### Required Distinctions

The system must distinguish:

- Verified or corroborated facts.
- Claims attributed to a source.
- AI-generated interpretations.
- Forecasts and scenarios.
- Observed market reactions.
- Reactions reported by sources.
- AI-inferred potential impacts.
- Unknown or unavailable impact information.

### Market Impact Integrity

The system must not describe market movement as observed unless it has actual market data or an appropriately documented observation.

If market data is unavailable, the system may describe potential implications or clearly attributed source-reported reactions.

Temporal proximity alone does not establish causation.

### Provenance Requirements

Material analytical assertions must retain references to their supporting or contradicting evidence.

Where possible, evidence references should identify the exact article revision and text span, not only the source publication.

Source independence must account for syndication and shared origin. Multiple copies of the same wire report must not be treated as independent corroboration.

### Deliverables

- Claims.
- Evidence records and precise source references.
- Claim assessments.
- Contradiction and uncertainty records.
- Versioned economic analysis.
- Analysis evaluation results.

### Exit Criteria

- Claims are linked to supporting or contradicting evidence.
- Material assertions have traceable provenance.
- Source attribution is retained.
- Conflicting information is represented.
- Facts, source claims, analysis, and forecasts are distinguishable.
- Market impact categories are supported by the available data.
- Completed analyses are versioned and reproducible.

---

## 15. Development Stage 9 — Event Dossiers and Reporting

### Objectives

Convert event intelligence into structured, versioned reports.

### Tasks

1. Define report scope and templates.
2. Implement event dossier queries.
3. Implement ReportGenerator.
4. Implement report versioning.
5. Implement report-to-event relationships.
6. Implement evidence references.
7. Implement source references.
8. Implement report validation.
9. Implement PublicationPolicy and immutable PublicationDecision records.
10. Implement PublicationService and target-specific publication adapter contracts.
11. Implement durable PublicationRecord and PublicationAttempt history for PUBLISH, REPLACE, and WITHDRAW.
12. Implement report correction and replacement lineage without overwriting prior versions.
13. Implement confirmed withdrawal and uncertain-outcome reconciliation.
14. Implement report storage and add report evaluation datasets.

### Initial Report Structure

The initial event dossier should support:

1. Headline.
2. Executive Summary.
3. What Happened?
4. Latest Developments.
5. Timeline.
6. Key Entities.
7. Economic Significance.
8. Observed Market Reaction, if supported by data.
9. Potential Market and Sector Impact.
10. Supporting Evidence.
11. Conflicting or Unconfirmed Information.
12. Risks and Uncertainties.
13. Analytical Assessment.
14. Sources.

Reports should be concise enough to be useful while preserving important evidence and context.

The data model should also support reports covering multiple events, such as periodic economic briefings, without forcing them into a single-event structure.

### Publication Policy

A report must receive a publication decision before delivery.

Initial outcomes:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

Publication decisions must be recorded independently from report content and delivery state.

### Human Review

`HOLD_FOR_REVIEW` must create a persistent review task or equivalent queue record.

The review workflow must support:

- Queue and priority.
- Assignment or ownership.
- Review status.
- Review timestamps.
- Reviewer action.
- Review rationale.
- Resulting publication decision.

A held report must not be treated as publishable until the required review and publication policy conditions are satisfied.

### Corrections and Withdrawals

Published reports must not be silently overwritten.

The system must preserve a correction or withdrawal history and maintain links between superseded and replacement report versions.

### Deliverables

- Structured event dossiers.
- Versioned reports.
- Immutable publication decisions and persistent review workflow.
- PublicationService with durable PUBLISH, REPLACE, and WITHDRAW operations and attempts.
- Report validation and immutable report-version lineage.
- Confirmed correction, replacement, and withdrawal traceability.

### Exit Criteria

- Reports retain event, article, analysis, and evidence references.
- Multi-event report scope is supported where required.
- Reports distinguish facts from analysis.
- Uncertainty is disclosed.
- Report versions are preserved.
- Publication policy is enforced.
- Held reports enter a real review workflow.
- Corrections create a new immutable report version; they do not overwrite an earlier version.
- External publication operations are persisted before execution and have attempt history.
- A failed replacement leaves the previous confirmed publication effective.
- A withdrawal is complete only after target confirmation; unknown outcomes require reconciliation.
- Invalid or unapproved reports cannot be published or delivered.

---

## 16. Development Stage 10 — Delivery, Scheduling, and Automation

### Objectives

Enable controlled automated processing and text report delivery.

### Tasks

1. Implement ReportDelivery as a recipient/destination delivery capability, separate from public publication execution.
2. Define delivery destination interfaces.
3. Implement delivery intent records.
4. Implement delivery attempt history.
5. Implement idempotent delivery operations.
6. Implement scheduled collection.
7. Implement scheduled processing.
8. Implement event monitoring.
9. Implement update detection.
10. Implement operational status reporting.
11. Implement retry and reconciliation behavior.
12. Add delivery and scheduling integration tests.

### Scheduling Strategy

The initial release should use a simple scheduling mechanism.

A distributed task queue is not required unless demonstrated workload or reliability requirements justify it.

The scheduling design must define whether schedule definitions and execution history are persisted internally or managed by an external scheduler.

If the application owns scheduling state, it must persist enough information to recover missed or interrupted executions.

Scheduling configuration should support:

- Collection frequency.
- Processing frequency.
- Source-specific schedules.
- Retry intervals.
- Maximum concurrent jobs.
- Job deadlines.
- Execution history.
- Missed-run handling.

### Delivery Integrity

The system must distinguish a logical delivery request from individual delivery attempts.

An idempotency key should be scoped to the delivery operation, destination, report version, and relevant operation type.

Exactly-once external delivery must not be claimed unless the destination provider offers the required guarantees. Ambiguous external outcomes must be reconciled before blindly repeating non-idempotent actions.

Publication-link delivery requires a confirmed successful and currently effective PublicationRecord. Direct report-content delivery may occur only when the applicable distribution policy authorizes it. Delivery status and attempts must not alter publication state.

### Deliverables

- Text delivery.
- Scheduling.
- Delivery status and attempt tracking.
- Automated processing cycle.
- Recovery and reconciliation behavior.

### Exit Criteria

- Collection and processing can run automatically.
- New information can update existing events.
- Reports are delivered only under the publication policy.
- Duplicate delivery is controlled within documented guarantees.
- Failed operations are visible and recoverable.
- Scheduled execution can resume after interruption.

---

## 17. Development Stage 11 — Evaluation, Quality Assurance, and Hardening

### Objectives

Measure system quality using representative economic news cases and validate operational behavior.

Evaluation is continuous throughout development. This stage consolidates the evaluation system and applies release-level quality gates.

### Evaluation Datasets

Create datasets covering:

- Monetary policy announcements.
- Inflation reports.
- Central bank decisions.
- Financial market developments.
- Trade restrictions.
- Energy market developments.
- Government debt developments.
- Geopolitical economic risks.
- Conflicting reports.
- Exact duplicate articles.
- Near-duplicate articles.
- Syndicated publications.
- Multiple events in one article.
- Multiple articles about one event.
- Related but distinct developments.
- Ambiguous event matches.
- Multilingual publications where supported.

### Evaluation Areas

**Acquisition**

- Collection success rate.
- Missing article rate where measurable.
- Collection latency.
- Unsafe URL rejection.
- Checkpoint correctness.

**Processing**

- Normalization accuracy.
- Duplicate detection precision and recall.
- Topic classification quality.
- Entity extraction quality.
- Translation quality where enabled.

**Event Intelligence**

- Event detection precision and recall.
- Event matching accuracy.
- False event merge rate.
- Event fragmentation rate.
- Event update correctness.
- Merge and split correctness.

**Evidence**

- Claim extraction quality.
- Evidence relevance.
- Provenance completeness.
- Contradiction detection quality.
- Source independence accuracy.

**Analysis**

- Event Importance quality and calibration.
- Economic Relevance classification quality.
- Economic Impact channel/direction/horizon quality.
- Analytical consistency.
- Unsupported assertion rate.
- Forecast and uncertainty quality.
- Event Importance assessment quality.
- Economic Relevance classification correctness.
- Economic Impact classification and channel-level assessment correctness.
- Separation of market reaction from causal attribution.

**Reporting**

- Factual accuracy.
- Source attribution completeness.
- Summary usefulness.
- Duplicate report rate.
- Publication decision quality.
- Correction and withdrawal correctness.

**Operations**

- Processing success rate.
- Median and P95 latency.
- LLM cost per successful report when measurable.
- Failure recovery rate.
- Delivery reconciliation success.
- Resource utilization.

### Evaluation Method

Use a combination of:

- Deterministic unit and integration tests.
- Human-reviewed reference datasets.
- Component-level evaluation.
- End-to-end evaluation.
- LLM-assisted judging with explicit rubrics.
- Trace and failure analysis.
- Regression testing.

LLM-based judging must not be treated as an independent guarantee of factual correctness.

### Acceptance Thresholds

Quality thresholds must be established using representative datasets and documented in the evaluation rubrics.

Critical metrics should include:

- False event merge rate.
- Unsupported material assertion rate.
- Evidence provenance completeness.
- Publication policy enforcement.
- Duplicate delivery rate within the documented delivery guarantees.
- Recovery correctness.

Thresholds must not be invented without a baseline or reference dataset.

### Deliverables

- Versioned evaluation datasets.
- Evaluation runners.
- Evaluation rubrics.
- Failure taxonomy.
- Regression reports.
- Release quality report.

### Exit Criteria

- Core components have representative evaluation cases.
- Critical failure categories are measured.
- Regressions can be detected.
- Evaluation results are reproducible.
- Release thresholds are documented.
- Critical quality and safety failures block release.

---

## 18. Development Stage 12 — Operational Readiness

### Objectives

Prepare the initial product for controlled operation.

### Tasks

1. Review configuration security.
2. Verify secret redaction.
3. Test backup and restore.
4. Test restart recovery.
5. Review database integrity.
6. Test source failures.
7. Test LLM provider failures.
8. Test cancellation and deadlines.
9. Test review queue operation.
10. Test report delivery failures.
11. Test ambiguous delivery reconciliation.
12. Review observability and alerting.
13. Document deployment.
14. Document operational procedures.
15. Review content rights and retention controls.
16. Prepare release and rollback procedures.

### Deliverables

- Operational documentation.
- Deployment instructions.
- Backup and restore procedure.
- Health and failure monitoring.
- Recovery procedures.
- Release checklist.

### Exit Criteria

The application can operate within its documented deployment model and recover from expected failures without corrupting core data, losing audit history, or bypassing publication controls.

---

## 19. Stage Dependencies

The recommended development order is:

```text
Documentation and Architecture Approval
                  |
                  v
          Project Foundation
                  |
                  v
    Domain Foundations and Evaluation
                  |
                  v
       Persistence and Recovery
                  |
                  v
     Shared LLM Execution and Slice
                  |
                  v
          News Acquisition
                  |
                  v
          Article Processing
                  |
                  v
          Event Intelligence
                  |
                  v
     Evidence and Economic Analysis
                  |
                  v
       Event Dossiers and Reporting
                  |
                  v
   Delivery, Scheduling, and Automation
                  |
                  v
       Evaluation and Hardening
                  |
                  v
        Operational Readiness
```

Evaluation, security, observability, and documentation are cross-cutting activities. They must not be postponed until the final stage.

Some work may overlap after the relevant interfaces and decisions are stable.

A dependent implementation must not proceed on the basis of an unresolved assumption.

---

## 20. Milestone Summary

| Milestone | Expected Result |
|---|---|
| M0 | Architecture baseline and critical ADRs reviewed |
| M1 | Python project foundation operational |
| M2 | Initial domain rules and evaluation dataset available |
| M3 | Persistence and recovery foundations operational |
| M4 | Shared LLM execution and first vertical slice working |
| M5 | News acquisition operational |
| M6 | Article processing operational |
| M7 | Event intelligence operational |
| M8 | Evidence and economic analysis operational |
| M9 | Event dossiers and publication workflow operational |
| M10 | Automated delivery and scheduling operational |
| M11 | Evaluation and release quality gates operational |
| M12 | Initial product release operationally ready |

Milestones represent completion criteria, not fixed calendar deadlines.

No calendar estimate or staffing commitment is implied by this document.

---

## 21. Initial Product Release Definition of Done

The initial text-based product release is complete when:

1. International economic sources can be configured.
2. News collection runs automatically.
3. Article records and revisions are managed consistently.
4. Duplicate articles are controlled.
5. Articles are classified using the approved economic taxonomy.
6. Relevant entities and mentions are extracted.
7. Related articles can be associated with events.
8. Event identity is maintained across updates.
9. Event merge and split operations are traceable.
10. Ambiguous event matches are not silently merged.
11. Claims and evidence are traceable to source material.
12. Conflicting information is represented.
13. Economic analysis distinguishes evidence from interpretation.
14. Market impact claims reflect the data actually available.
15. Importance ranking is available and explainable.
16. Event dossiers can be generated.
17. Reports are versioned.
18. Publication policy is enforced.
19. Held reports enter a functioning review workflow.
20. Text reports can be delivered automatically.
21. Delivery attempts and outcomes are observable.
22. Processing runs can be recovered safely.
23. LLM usage and costs are tracked where available.
24. Data can be recovered from verified backups.
25. Core tests run without paid external services.
26. CI enforces required quality gates.
27. Content retention and publication comply with the approved rights policy.
28. Operational limitations are documented.

---

## 22. Development Risks and Mitigations

### 22.1 Source Availability and Content Rights

**Risk:** Sources may change feed formats, restrict access, or prohibit certain storage and redistribution practices.

**Mitigation:**

- Use source adapters.
- Track source health.
- Maintain source access and rights metadata.
- Respect licensing and terms.
- Avoid assuming that accessible content is reusable.
- Preserve attribution.
- Provide alternative sources where appropriate.

### 22.2 Duplicate and Event Matching Errors

**Risk:** Incorrect matching may merge unrelated developments or split one event into multiple records.

**Mitigation:**

- Separate article deduplication from event matching.
- Use multiple matching signals.
- Preserve candidate scores and policy versions.
- Record decisions and identity operations.
- Keep ambiguous cases explicit.
- Evaluate false merges and fragmentation.

### 22.3 Unsupported LLM Conclusions

**Risk:** Models may generate plausible but unsupported statements.

**Mitigation:**

- Require evidence references for material assertions.
- Separate source claims from AI analysis.
- Validate structured outputs.
- Treat source content as untrusted input.
- Apply publication quality gates.
- Preserve uncertainty.
- Use review workflows for cases that exceed automatic publication policy.

### 22.4 Excessive LLM Costs

**Risk:** Repeated analysis may increase cost and latency.

**Mitigation:**

- Fingerprint analysis inputs.
- Avoid unnecessary reprocessing.
- Use deterministic processing where possible.
- Apply execution budgets and deadlines.
- Track model usage and cost.
- Reanalyze only after meaningful changes.
- Evaluate model choice against quality and cost.

### 22.5 Inadequate Event Identity Policy

**Risk:** Similarity-based matching may confuse related developments with the same event.

**Mitigation:**

- Define event identity separately from topical similarity.
- Preserve related-but-distinct event relationships.
- Record matching decisions.
- Support explicit merge and split operations.
- Calibrate matching policies using reviewed examples.

### 22.6 Missing Market Data

**Risk:** Economic analysis may imply observed market reactions without actual market observations.

**Mitigation:**

- Distinguish observed, source-reported, and AI-inferred impact.
- Integrate market data only through an approved source and licensing strategy.
- Do not infer causality from timing alone.
- Represent unavailable information as unknown.

### 22.7 Operational Recovery Failures

**Risk:** Interrupted workflows may create duplicate work, inconsistent states, or repeated external side effects.

**Mitigation:**

- Persist processing runs and steps.
- Use idempotency keys.
- Apply leases or equivalent recovery mechanisms.
- Reconcile uncertain external delivery outcomes.
- Test restart and retry scenarios.

### 22.8 Premature Infrastructure

**Risk:** Excessive infrastructure may delay product delivery.

**Mitigation:**

- Start with the simplest approved deployment model.
- Avoid mandatory vector databases without evidence.
- Avoid distributed task queues until justified.
- Keep generic Agent Runtime capabilities out of the initial scope unless required.
- Introduce additional infrastructure only through explicit requirements and decisions.

---

## 23. Future Product Roadmap

### Product Phase 2 — Audio Intelligence

Potential capabilities:

- Audio script generation.
- Text-to-speech.
- Daily economic audio briefings.
- Multiple briefing lengths.
- Audio version management.
- Audio delivery integrations.

### Product Phase 3 — Video Intelligence

Potential capabilities:

- Video script generation.
- Charts and visual assets.
- Automated narration.
- Video composition.
- Publishing integrations.
- Video version management.

### Product Phase 4 — Advanced Intelligence

Potential capabilities:

- Historical event comparisons.
- Economic indicator integration.
- Advanced scenario analysis.
- User personalization.
- Custom alerts.
- Advanced retrieval.
- Expanded multilingual reporting.
- Additional analytical tools.

Future phases must reuse the established event, evidence, analysis, and report foundations.

They must not require rewriting core event identity or provenance mechanisms.

---

## 24. Change Management

Changes to the roadmap or architecture must be documented.

A material change should identify:

- Reason for change.
- Affected requirements.
- Affected components.
- Data migration implications.
- Security and content-rights implications.
- Operational and cost implications.
- Compatibility implications.
- Testing and evaluation requirements.
- Relevant ADRs.

Changes to domain concepts, data relationships, event identity, publication policy, or workflow guarantees require corresponding updates to the architecture and data model documents before dependent implementation.

An implementation shortcut must not silently become a permanent architectural decision.

---

## 25. Final Development Statement

The project should be implemented as a sequence of controlled, testable development stages.

The first objective is a reliable economic news intelligence pipeline that transforms international publications into evidence-based event dossiers and controlled, automatically delivered text reports.

The initial implementation must prioritize:

- Correct event identity.
- Evidence traceability.
- Transparent uncertainty.
- Reliable workflow execution.
- Publication governance.
- Recovery and idempotency.
- Measurable quality.
- Operational simplicity.

The system should use deterministic workflows supported by a shared, provider-independent LLM execution layer.

It should not implement a general conversational Agent architecture unless a concrete product requirement justifies that complexity.

Audio, video, and advanced intelligence capabilities should build on the completed text intelligence foundation rather than complicate the initial release.

---

**End of Document**

**Document ID:** GENI-PLAN-004
**Version:** 1.1
**Status:** Draft — Under Architecture Review