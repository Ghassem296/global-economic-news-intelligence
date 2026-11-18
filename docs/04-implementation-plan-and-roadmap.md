# Global Economic News Intelligence
## Implementation Plan & Development Roadmap

**Document ID:** GENI-PLAN-004

**Version:** 1.26
**Status:** Draft — Under Architecture Review
**Last Updated:** 2026-11-18
**Project:** Global Economic News Intelligence  
**Owner:** Project Owner

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
| Database | Relational database; SQLite and PostgreSQL are candidates pending the GENI-ADR-005 workload proof-of-concept |
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

PostgreSQL may be selected for the initial deployment if the GENI-ADR-005 proof-of-concept demonstrates that SQLite does not meet the workload or operational constraints; it may also be considered for a later deployment. Migration must not be assumed to be automatic merely because repositories are used.

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
│   ├── README.md
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
│   │
│   ├── adr/
│   │   ├── README.md
│   │   ├── adr-template.md
│   │   └── decisions/
│   │       ├── GENI-ADR-001-event-centric-intelligence-architecture.md
│   │       ├── GENI-ADR-002-article-deduplication-and-event-matching.md
│   │       ├── GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md
│   │       ├── GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md
│   │       ├── GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md
│   │       ├── GENI-ADR-006-provider-independent-llm-execution-architecture.md
│   │       ├── GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md
│   │       ├── GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md
│   │       ├── GENI-ADR-009-near-real-time-news-acquisition-strategy.md
│   │       ├── GENI-ADR-010-phased-text-audio-and-video-delivery.md
│   │       ├── GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md
│   │       ├── GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md
│   │       ├── GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md
│   │       ├── GENI-ADR-014-human-review-corrections-and-withdrawals.md
│   │       ├── GENI-ADR-015-market-data-integration-and-economic-impact-classification.md
│   │       ├── GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md
│   │       ├── GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md
│   │       ├── GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md
│   │       ├── GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md
│       └── GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md
│   │
│   └── references/
│       └── agent-template/
│           ├── README.md
│           ├── agent-template-architecture.md
│           └── agent-template-implementation-specification.md

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
12. Define the initial source and content-rights policy, including operation-specific permissions and a fail-closed rule for unknown rights.
13. Define initial event identity and correlation rules.
14. Define reviewer roles, authorization, and the review process for held reports.
15. Define the first evaluation cases.
16. Define the typed method-level contracts and transaction boundaries required by the first vertical slice.

### Required Architectural Topics

The following topics must be resolved or explicitly bounded before dependent implementation:

- Workflow-first architecture and shared LLM execution.
- Article deduplication versus event matching.
- Event identity, matching, merging, and splitting.
- EventCreationPolicy authorization, stable proposed Event identifiers, and idempotent recovery after partial creation.
- Semantic similarity and embedding strategy.
- Initial persistence and async execution strategy.
- News acquisition and full-text access rights, including the rights-profile owner and mandatory permission checks before retrieval, persistent storage, external processing, and distribution.
- Publication, review, correction, and withdrawal policy, including reviewer authorization and the separation of publication eligibility from recipient-distribution authorization.
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
- EventCreationPolicy has an approved, versioned decision rule and authorization owner; until then, automatic Event creation from NEW_EVENT_CANDIDATE is disabled and requires explicit authorized handling.
- Initial source rights profiles and operation-specific permission rules are approved or bounded for the selected test sources; unknown rights block restricted operations.
- Reviewer identity, role, and authority are defined for each review type before a review can authorize a material decision.
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
- Article.
- ArticleRevision as an immutable content version.
- DuplicateCandidate evaluations and immutable DuplicateDecision history.
- Topic classification.
- Entity and entity mention.
- Event.
- EventMatchCase, EventMatchCandidate, and EventMatchDecision as separate matching records.
- ArticleEventLink as a decision-authorized association.
- ProcessingRun and ProcessingStep.
- Evidence and evidence references.
- ClaimAssessment, ClaimAssessmentEvidenceLink, and append-only AssessmentHistory.
- Separate Analysis records for each assessment type.
- Report with immutable version lineage.
- PublicationDecision, typed ReviewRecord, immutable ReviewContextLink, and append-only ReviewAction.
- DeliveryRecord and DeliveryAttempt, with recipient-specific distribution authorization implemented in the delivery stage.
- LLMUsageRecord for model execution and usage records.
- Versioned, human-reviewed evaluation datasets and EvaluationRun/EvaluationResult artifacts.

Additional concepts from the approved data model should be introduced when required by a concrete workflow.

The project should not implement every planned table or entity simply because it appears in the complete conceptual model.

### Domain Rules

Implement and test:

- Article identity and revision behavior.
- Article deduplication boundaries.
- Immutable DuplicateCandidate evaluation and separate DuplicateDecision/supersession.
- Per-ArticleRevision EventMatchCase creation and uniqueness.
- Candidate evaluation separate from case-level EventMatchDecision.
- MATCH-only ArticleEventLink creation with exact case and decision references.
- Event association correction through immutable successor decisions.
- Event lifecycle transitions.
- Event history append-only behavior.
- Claim and evidence relationships.
- Immutable ClaimAssessment versions, exact assessment evidence links, and append-only AssessmentHistory.
- Analysis versioning.
- Report versioning.
- Publication decision rules.
- Review task transitions, exact ReviewContextLink references, and append-only ReviewAction history for exactly `ARTICLE_DEDUPLICATION`, `EVENT_MATCHING`, and `REPORT_VERSION`. Keep `CLAIM_ASSESSMENT`, `PUBLICATION_OPERATION`, and `CONTENT_RIGHTS` disabled until their specified successor workflows, authorization rules, and integration tests are implemented.
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
- Auditability of publication, duplicate, claim-assessment, and review decisions.
- DuplicateDecision supersession and at most one effective decision per DuplicateCandidate.
- ClaimAssessment sequence, supersession, and current-assessment referential integrity.
- Append-only ReviewAction identity and idempotency.
- Unique EventMatchCase identity per ArticleRevision and development key.
- Versioned, immutable candidate evaluations with deterministic input fingerprints.
- Atomic EventMatchDecision creation and EventMatchCase.effective_decision_id updates.
- Case-scoped candidate and decision references that prevent cross-case selection.
- Atomic ArticleEventLink activation/deactivation with its authorizing decision.
- At most one effective decision and one active ArticleEventLink per case.

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
11. Check the applicable rights assessment before submitting source content to an external LLM provider; an internal processing permission does not imply external-processing permission.
12. Prevent analysis stages from receiving unrestricted tool access.

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
       +---- AMBIGUOUS / REVIEW_REQUIRED ---> Authorized Review
       |
       +---- NEW_EVENT_CANDIDATE ----------> Authorized Event Creation
       |                                      |
       |                                      v
       |                               Persist New Candidate
       |                                      |
       |                                      v
       |                               Record MATCH Decision
       |
       v
Apply ArticleEventLink only for effective MATCH
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
- External LLM calls use only content whose operation-specific rights assessment permits that provider and processing purpose.
- The vertical slice uses explicit source fixtures or approved test sources; it must not assume a production source license or content-retention permission.

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
15. Implement the initial source rights profile and ContentRightsService integration; check permission separately for discovery, metadata retrieval, and full-text retrieval.
16. Persist ContentAccessRecord and RightsAssessment provenance for each applicable acquisition operation; support a permitted metadata-only route when full-text rights are unavailable.

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
- Versioned source-rights profiles and operation-specific acquisition checks.
- Content-access provenance and explicit metadata-only/restricted-source outcomes.

### Exit Criteria

- Configured sources can be collected.
- Repeated collection does not create uncontrolled duplicates.
- Failed collection does not advance an unsafe checkpoint.
- Source failures are observable.
- Collection can resume after interruption.
- Unsafe URLs and redirects are rejected.
- Content is retained only according to the configured rights policy.
- Unknown, denied, expired, revoked, or review-required permissions block the restricted acquisition/storage operation.
- Metadata retrieval does not silently authorize full-text retrieval or persistent storage.
- Source terms, rights-profile version, and access outcome are traceable for each collected content artifact.

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
12. Implement ArticleRevisionService and ArticleRevisionRepository; create immutable revisions only for material content changes and atomically update the Article current projection.
13. Implement processing status management.
14. Implement translation support only where required by the approved language policy; retain the original ArticleRevision as authoritative and create a separately versioned translation artifact with provenance and quality state.
15. Apply rights checks before temporary processing, persistent storage, derived-artifact creation, and external processing of article content.
16. Add processing evaluation cases.

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
- Article revision support, including ArticleRevisionService and repository contract tests.
- Immutable duplicate candidate evaluations and DuplicateDecision history.
- Topic classifications.
- Extracted entities and mentions.
- Processing metadata.

### Exit Criteria

- Articles are normalized consistently.
- Exact duplicates are handled deterministically.
- Near-duplicate candidates retain their similarity and policy provenance.
- DuplicateDecision outcomes are immutable, versioned, and corrected only through successor decisions.
- Duplicate confirmation never deletes or merges the underlying Article or ArticleRevision records.
- Related but distinct publications are preserved.
- Topic classifications include method and confidence metadata.
- Entity mentions retain enough provenance to be reviewed.
- Processing can be repeated safely.
- Repeated collection of unchanged content does not create a new ArticleRevision.
- A material content change creates a new immutable ArticleRevision and atomically updates the Article current projection.
- Rights checks are performed before persistent content storage and derived-artifact creation; temporary processing does not leave unauthorized copies.
- Translation is not enabled for an input unless its artifact lineage, supported language, quality state, and applicable external-processing/storage permissions are defined.

---

## 13. Development Stage 7 — Event Intelligence

### Objectives

Implement the event-centric intelligence layer.

This is the core product capability.

### Tasks

1. Implement EventDetector.
2. Identify distinct development scopes within each immutable ArticleRevision.
3. Create or retrieve one EventMatchCase per ArticleRevision/development scope.
4. Retrieve plausible existing Events for each case.
5. Implement EventMatcher and lexical, entity, temporal, and geographic evaluation signals; semantic candidate retrieval, when enabled, must be provided through the optional SemanticRetrievalAdapter and compared with a lexical baseline under GENI-ADR-012. Do not assume a dedicated vector database or an uncalibrated numeric threshold.
6. Persist immutable EventMatchCandidate evaluations with matching-policy versions and input fingerprints.
7. Implement case-level EventMatchDecision creation and supersession.
8. Implement the versioned EventCreationPolicy and authorized, idempotent creation for NEW_EVENT_CANDIDATE outcomes using the preassigned proposed_event_reference; after creation, record the new Event as a candidate and create a subsequent MATCH decision before creating an ArticleEventLink.
9. Implement EventService application of MATCH decisions and case-scoped ArticleEventLink creation/deactivation.
10. Implement ReviewService routing and successor-decision handling for ambiguous or corrected cases.
11. Implement the canonical EventLifecyclePolicy transition matrix, guard validation, and append-only EventHistory linkage.
12. Implement EventRelationship using the canonical eight-type vocabulary and its direction/cycle rules.
13. Implement EventIdentityOperation and EventIdentityOperationHistory persistence with actor/authorization, explicit core-effect state, status transitions, idempotency, expected input versions, ordered input/output links, and exact EventHistory operation references.
14. Implement deterministic historical identity resolution returning CANONICAL, MULTIPLE_SUCCESSORS, or UNRESOLVED; never choose an arbitrary split successor.
15. Keep automated merge/split execution disabled while GENI-ADR-011 is Proposed. After acceptance, enable it only when operation-state/history transitions, expected-version concurrency checks, idempotent recovery, UNKNOWN-effect reconciliation, and successor ArticleEventLink reconciliation have passing tests.
16. Implement event matching evaluation datasets.

### Event Identity Policy

Event identity must represent the same underlying real-world occurrence or continuing development.

Sharing a topic, country, organization, or entity is not sufficient to establish event identity.

For example:

- A central bank rate decision is an event.
- A subsequent currency movement may be a separate event.
- The two events may be related through a causal, consequential, or contextual relationship.
- They must not be merged merely because they concern the same central bank.

### Event Resolution Outcomes

The unit of final resolution is EventMatchCase, not an individual EventMatchCandidate. A case represents one development within one immutable ArticleRevision and may contain multiple candidate Events.

A resolved case must have one effective EventMatchDecision with one of these outcomes:

- `MATCH`: exactly one eligible candidate in the same case is selected. Only this outcome may authorize an active ArticleEventLink.
- `NEW_EVENT_CANDIDATE`: a proposal to create a new Event; it does not create the Event or an ArticleEventLink. After separate event-creation authorization and idempotent creation, the new Event must be recorded as a candidate and a subsequent MATCH decision must authorize the association.
- `NO_MATCH`: none of the evaluated candidate Events matches the development represented by this case. Other cases from the same ArticleRevision may still resolve to other Events.
- `AMBIGUOUS`: multiple plausible candidates or insufficient evidence prevent a reliable decision.
- `REVIEW_REQUIRED`: policy requires an authorized human review before resolution.

Candidate-level processing statuses such as INELIGIBLE or SUPERSEDED are not case-level decision outcomes. An unresolved case must remain explicit and must not create an active association.

The system must preserve:

- Candidate signals, scores, policy versions, and candidate-input fingerprints.
- Immutable candidate evaluations and their relationship to the case.
- Final case-level decision and any superseded decision.
- Decision actor, rationale, and provenance.
- Review task and reviewer outcome where applicable.
- Exact case and decision references on every applied ArticleEventLink.

Semantic similarity is a supported matching signal, not a mandatory dependency of the initial implementation. The initial EventMatcher must operate against a documented lexical/entity/temporal/geographic baseline. Semantic retrieval may be added only after GENI-ADR-012 is accepted and a labeled evaluation demonstrates incremental value; a dedicated vector database is not automatically required.

Until GENI-ADR-012 is accepted, semantic retrieval and embedding generation remain deferred/optional. Implement and evaluate the lexical baseline and case-level decision invariants first. A later semantic adapter must be compared against that same baseline using a versioned labeled dataset before it is enabled.

No universal similarity threshold should be assumed without evaluation and calibration. The candidate-retrieval adapter must not own final decisions or article-event associations.

### Event Identity Integrity

Event IDs must remain stable. Merge/split disposition is identity state, not Event lifecycle state.

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
- Controlled event merge and split operations, enabled only after GENI-ADR-011 acceptance and the operation-recovery/reconciliation gates.

### Exit Criteria

- Multiple articles can be associated with one event.
- Unrelated developments are not automatically merged.
- Ambiguous matches are explicitly represented.
- Event identity operations are traceable.
- Event lifecycle transitions are validated.
- Every resolved development has one effective case-level decision; unresolved cases remain explicit.
- Every active ArticleEventLink references its EventMatchCase and effective MATCH decision.
- Human corrections create successor decisions and preserve prior link history.
- Merge inputs include the selected survivor and the single output is that same survivor; split operations create at least two distinct successor outputs.
- Operation status/effect history is append-only. `RECONCILIATION_REQUIRED` is the explicit operation status while the core identity effect is unknown or downstream reconciliation remains incomplete; an applied identity change remains in this state until all required downstream work completes.
- No identity operation directly repoints/deletes ArticleEventLink; every replacement link is authorized by a successor EventMatchDecision.
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
5. Implement immutable ClaimAssessment records and ClaimAssessmentEvidenceLink records.
6. Implement source attribution and append-only AssessmentHistory.
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

Market-data acquisition is optional and is not a prerequisite for the initial economic-analysis workflow. Do not select or integrate a provider, instrument universe, collection frequency, or retention scheme until coverage and rights have been reviewed under GENI-ADR-015. If no authorized, suitable observations exist, market reaction remains unknown/unavailable and the analysis must not imply that a market-data feed was observed. When integration is approved, a MarketDataCollector/normalizer contract and its ownership must be added to Documents 02 and 03 before implementation.

### Provenance Requirements

Material analytical assertions must retain references to their supporting or contradicting evidence.

Where possible, evidence references should identify the exact article revision and text span, not only the source publication.

Source independence must account for syndication and shared origin. Multiple copies of the same wire report must not be treated as independent corroboration.

### Deliverables

- Claims.
- Evidence records and precise source references.
- Immutable, versioned ClaimAssessment records with exact evidence-set references.
- Append-only AssessmentHistory and current-assessment projection integrity.
- Contradiction and uncertainty records.
- Separate versioned Event Importance, Economic Relevance, and Economic Impact Analysis outputs.
- Optional market-reaction assessments backed by actual market observations.
- Separate evaluation datasets and reports for all three assessment types.

### Exit Criteria

- Claims are linked to supporting or contradicting evidence.
- Each effective ClaimAssessment identifies its exact evidence set, method/policy version, rationale, and superseded assessment where applicable.
- Claim current-assessment projections are updated atomically and prior assessments remain immutable.
- Material assertions have traceable provenance.
- Source attribution is retained.
- Conflicting information is represented.
- Facts, source claims, analysis, and forecasts are distinguishable.
- Event Importance is evaluated independently of Economic Relevance and Economic Impact.
- Economic Relevance is evaluated independently of Event Importance and demonstrated impact.
- Economic Impact supports channel, direction, magnitude/range, horizon, evidence status, and uncertainty where supported.
- Missing information remains unknown rather than being encoded as zero.
- Observed market reactions are not described as proof of event causality.
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
15. Apply rights checks for source attribution, quotations, derived-output use, publication, and recipient distribution; preserve permitted source references independently of full-text retention.
16. Implement the canonical six-family ReviewService successor routing. The first implementation slice enables exactly ARTICLE_DEDUPLICATION, EVENT_MATCHING, and REPORT_VERSION. Keep CLAIM_ASSESSMENT, PUBLICATION_OPERATION, and CONTENT_RIGHTS disabled until their successor workflows, authorization rules, and integration tests pass.

### Initial Report Structure

The initial event dossier should support:

1. Headline.
2. Executive Summary.
3. What Happened?
4. Latest Developments.
5. Timeline.
6. Key Entities.
7. Event Importance — why the development deserves attention or follow-up.
8. Economic Relevance — direct, indirect, or contextual transmission pathways.
9. Observed Market Reaction, only when supported by actual market observations.
10. Economic Impact — realized or potential consequences by channel, direction, magnitude, and horizon where supported.
11. Supporting Evidence.
12. Conflicting or Unconfirmed Information.
13. Risks and Uncertainties.
14. Analytical Assessment.
15. Sources.

Reports should be concise enough to be useful while preserving important evidence and context.

The data model should also support reports covering multiple events, such as periodic economic briefings, without forcing them into a single-event structure.

### Publication Policy

A report must receive a publication decision before external publication. Recipient delivery is separate and must also satisfy the applicable distribution policy. A PublicationDecision records eligibility; it does not prove target-side publication success. PublicationService executes PUBLISH, REPLACE, and WITHDRAW, while ReportDelivery handles recipient/destination delivery independently.

Initial outcomes:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

Publication decisions must be recorded independently from report content and delivery state.

### Human Review

`HOLD_FOR_REVIEW` must create a persistent review task or equivalent queue record.

The review workflow must support ARTICLE_DEDUPLICATION, EVENT_MATCHING, and REPORT_VERSION as the three first-slice typed subjects. REPORT_VERSION is the pre-publication review of an exact immutable Report version and its exact effective PublicationDecision; it is not a review of an already-executed PublicationRecord. PUBLICATION_OPERATION is a separate external-operation/reconciliation review family and remains disabled in the first slice. A material review result must create the applicable successor DuplicateDecision, EventMatchDecision, corrected Report version, or PublicationDecision; a ReviewRecord alone never authorizes a domain change.

The review workflow must support:

- Queue and priority.
- Assignment or ownership.
- Review status.
- Review timestamps.
- Reviewer action.
- Review rationale.
- Resulting publication decision.

A held report must not be treated as publishable until the required REPORT_VERSION review, where applicable, and the current publication-policy conditions are satisfied. Review of an already-created PublicationRecord or an unknown external outcome belongs to the deferred PUBLICATION_OPERATION family, not this first-slice review path.

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

- Reports retain event, exact ArticleRevision, analysis-version, and evidence references; later Article revisions do not change the provenance of an existing report.
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
- External publication requires an effective publication decision for the exact report version and all applicable rights/target authorizations.
- A report or notification must not be delivered merely because a publication decision exists or because public publication succeeded; each recipient-delivery operation requires its separate distribution authorization.
- `PUBLICATION_LINK` delivery requires a confirmed successful and currently effective PublicationRecord.
- `REPORT_CONTENT` delivery may occur without public publication only when a separate distribution policy and applicable content rights explicitly authorize it; delivery does not imply publication.
- Invalid or unapproved reports cannot be externally published; report-content delivery is separately governed by distribution policy and content rights.

---

## 16. Development Stage 10 — Delivery, Scheduling, and Automation

### Objectives

Enable controlled automated processing and text report delivery.

### Tasks

1. Implement ReportDelivery as a recipient/destination delivery capability, separate from public publication execution.
2. Define delivery destination interfaces and the versioned DistributionAuthorizationPolicy.
3. Implement DistributionAuthorizationRepository and persist an immutable DistributionAuthorizationDecision plus its complete DistributionAuthorizationRightsLink set and rights-assessment-set fingerprint in one transaction.
4. Define the versioned ContentScopeManifest and deterministic fingerprint contract using RFC 8785 JCS, UTF-8, and SHA-256; keep the manifest fingerprint distinct from the serialized outbound-payload digest.
5. Implement complete source-lineage and upstream-rights revalidation at dispatch. Expired, revoked, or materially changed upstream permissions must fail closed until ContentRightsService re-evaluates the dependency chain and a successor authorization decision is issued.
6. Bind each decision to the exact report version, recipient, destination, delivery mode, channel, authorized content scope, and content-scope fingerprint. For every source-derived content item, require an exact allowed CUSTOMER_DISTRIBUTION RightsAssessment; composite reports may require multiple assessments.
7. Persist each DeliveryRecord with the exact authorization-decision reference and matching content-scope fingerprint before dispatch.
8. Implement delivery intent records.
9. Implement delivery attempt history.
10. Implement idempotent delivery operations.
11. Re-check decision expiry/revocation, every linked RightsAssessment, and the exact canonical manifest item set and content digests before dispatch; record the serialized outbound-payload digest separately and preserve completed delivery history.
12. Implement scheduled collection.
13. Implement scheduled processing.
14. Implement event monitoring.
15. Implement update detection.
16. Implement operational status reporting.
17. Implement retry and reconciliation behavior.
18. Add delivery and scheduling integration tests.

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
- Every recipient-delivery operation is authorized by its exact effective DistributionAuthorizationDecision and all applicable content-rights constraints.
- Every source-derived content scope in an authorized report payload is covered by an exact allowed CUSTOMER_DISTRIBUTION RightsAssessment linked to that decision.
- The rights-assessment-set fingerprint is reproducible from the complete immutable link set; no source or artifact permission is reused for a different content scope.
- The DeliveryRecord content-scope fingerprint matches the canonical manifest fingerprint authorized by the referenced decision; dispatch verifies each exact manifest item and records the serialized outbound payload digest separately.
- `PUBLICATION_LINK` delivery requires a confirmed successful and currently effective PublicationRecord.
- `REPORT_CONTENT` delivery may occur without public publication only when separately authorized; it must not change or imply publication state.
- A multi-source report cannot be distributed under a single representative source assessment; all included source-derived scopes must be covered or explicitly excluded from the authorized payload.
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
- Candidate retrieval recall at the configured candidate depth.
- Case-level EventMatchDecision precision, recall, and unresolved/ambiguous rate.
- False active-association rate.
- False event-creation rate.
- False event merge rate.
- Event fragmentation rate.
- Event update correctness.
- Merge and split correctness.
- Human-review escalation and correction rates.

**Evidence**

- Claim extraction quality.
- Evidence relevance.
- Provenance completeness.
- Contradiction detection quality.
- Source independence accuracy.

**Analysis**

- Event Importance ranking quality and calibration.
- Economic Relevance classification and transmission-pathway validity.
- Economic Impact channel-level direction, magnitude/range, horizon, and evidence-status quality.
- Unknown and insufficient-evidence classification quality.
- Separation of assessment confidence, forecast probability, and effect magnitude.
- Consistency and divergence checks across the three independent assessments.
- Forecast and uncertainty quality.
- Unsupported material assertion rate.
- False causal-attribution rate for observed market reactions.

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
- Publication operation success and reconciliation outcomes.
- Failed replacement safety and confirmed withdrawal correctness.
- Delivery reconciliation success and duplicate-delivery rate.
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

- False event merge rate and false active-association rate.
- Case-level matching precision/recall and false event-creation rate.
- Unsupported material assertion rate.
- Evidence provenance completeness.
- Independent quality thresholds for Event Importance, Economic Relevance, and Economic Impact.
- Publication policy enforcement and failed-replacement safety.
- Confirmed withdrawal and publication reconciliation correctness.
- Duplicate delivery rate within the documented delivery guarantees.
- Recovery correctness.

Thresholds must not be invented without a baseline or reference dataset.

### Specification Readiness Dependencies

Before first-slice or production-bound implementation, reconcile the applicable controls in Documents 08–13: security threats and authorization ownership; method-level repository/workflow contracts; source-independence semantics; versioned topic identifiers; reviewed datasets and metric definitions; and deployment, observability, backup/restore, runbooks, and measured operational objectives.

These documents are proposed specifications. Publication does not constitute approval, and specification presence does not mean implementation or verification is complete.

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
15. Review content rights and retention controls, including rights-profile expiry/revocation and derived-artifact restrictions.
16. Test content deletion/restriction requests across storage, caches, indexes, queues, backups, and supported external processors, and verify completion evidence.
17. Prepare release and rollback procedures.
18. Verify the production-readiness evidence defined in GENI-OPS-013.
19. Verify threat-linked controls and release-blocking tests defined in GENI-SEC-008.
20. Confirm runbooks, alert ownership, backup/restore evidence, and recovery exercises; document presence is not tested operational evidence.

### Deliverables

- Operational documentation.
- Deployment instructions.
- Backup and restore procedure.
- Health and failure monitoring.
- Recovery procedures.
- Release checklist.

### Exit Criteria

The application can operate within its documented deployment model and recover from expected failures without corrupting core data, losing audit history, bypassing publication controls, or continuing restricted content operations after rights expiry/revocation. Required content deletion/restriction operations must have verifiable outcomes.

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

## Privacy Architecture Implementation Gate

Privacy execution is a cross-cutting implementation dependency. Before production processing of personal data: (1) approve data inventory, categories, purposes, policy ownership and legal-review inputs; (2) implement logical privacy records, restricted subject references and PersonalDataLineage; (3) enforce independent PrivacyProcessingAuthorization and ContentRightsService checks; (4) enforce ProcessorRegister and InternationalTransferAssessment, failing closed on unknown posture; (5) implement PrivacyManagementService and idempotent internal request workflows; (6) propagate actions to derived artifacts, caches, evaluation stores, providers and backup-restore reconciliation; (7) implement minimized telemetry, audit evidence, runbooks and tested production gates.

Exit criteria require executable tests and operational evidence, not document presence. Publication does not establish legal compliance. See GENI-ADR-020 and Document 14.


**End of Document**

**Document ID:** GENI-PLAN-004
**Version:** 1.26
**Status:** Draft — Under Architecture Review
