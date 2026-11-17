# Global Economic News Intelligence
## Component Architecture and Interface Contracts

**Document ID:** GENI-ARCH-002  
**Version:** 1.2  
**Status:** Draft — Under Architecture Review  
**Project:** Global Economic News Intelligence  
**Last Updated:** 2026-11-17

---

## 1. Purpose

This document defines the internal component architecture, responsibilities, boundaries, and interface contracts of Global Economic News Intelligence.

It translates the high-level product architecture into implementable software components.

The design follows a workflow-first architecture and separates:

- Domain logic.
- Application workflows.
- Infrastructure implementations.
- External provider integrations.

The system uses deterministic workflows wherever practical and invokes LLM capabilities selectively through a shared execution layer.

A general-purpose conversational Agent Runtime is not a mandatory architectural dependency.

Detailed entity fields, database relationships, migrations, indexes, and persistence constraints are maintained in:

`docs/03-data-model-and-storage-design.md`

The high-level product and system architecture is maintained in:

`docs/01-product-and-system-architecture.md`

## 2. Architectural Rules

The following rules govern component design and implementation:

1. Components have explicit and non-overlapping responsibilities.
2. Components communicate through defined interfaces.
3. Domain logic does not depend on infrastructure implementations.
4. LLM providers are accessed through the Shared LLM Execution Layer.
5. External news providers are accessed through source adapters.
6. Persistence operations go through repository interfaces.
7. Article deduplication and event matching remain separate operations.
8. Event identity must remain stable across updates.
9. Evidence provenance must be preserved.
10. External content is treated as untrusted input.
11. Workflow execution must be observable and recoverable.
12. Processing operations must define idempotency behavior where retries are possible.
13. Publication decisions are separate from report generation and delivery.
14. Historical reports and analytical versions must not be silently overwritten.
15. Components must be independently testable.
16. Provider-specific logic must remain outside domain and application business rules.
17. Lifecycle transitions must be validated by domain policies.
18. Processing state must remain separate from domain state.
19. All external operations must have explicit resource and execution limits.
20. Unapproved architectural decisions must not be treated as established implementation constraints.

## 3. Logical Component Architecture

The application is divided into eight logical areas.

### 3.1 Domain

Contains:

- Domain entities.
- Value objects.
- Domain policies.
- Enumerations.
- Domain-level exceptions.
- Repository interfaces.
- Domain service contracts.

This layer must not import database, web framework, LLM provider, or external news SDK implementations.

### 3.2 Application Workflows

Contains:

- Collection workflow.
- Article processing workflow.
- Event resolution workflow.
- Event intelligence workflow.
- Reporting workflow.
- Publication workflow.
- Review workflow.
- Delivery workflow.
- Reprocessing and recovery coordination.

Application workflows coordinate components but must not duplicate domain business rules.

### 3.3 Acquisition and Processing

Contains:

- Source registry.
- News source adapters.
- News collectors.
- Article normalizers.
- Article deduplication.
- Language identification.
- Topic classification.
- Entity extraction.
- Entity resolution.
- Candidate claim extraction.

### 3.4 Event Intelligence

Contains:

- Event detection.
- Event matching.
- Event resolution.
- Event creation and association.
- Event lifecycle management.
- Event relationship management.
- Event history.

### 3.5 Evidence and Analysis

Contains:

- Source assessment.
- Claim management.
- Evidence management.
- Evidence verification.
- Importance assessment.
- Economic impact analysis.
- Historical context retrieval.

### 3.6 Reporting and Publication

Contains:

- Event dossier generation.
- Report generation.
- Report version management.
- Publication policy.
- Review management.
- Correction and withdrawal handling.
- Delivery coordination.

### 3.7 Shared LLM Execution

Contains:

- Provider-independent LLM interface.
- Provider adapters.
- Structured output validation.
- Model configuration.
- Token and cost accounting.
- Budget enforcement.
- Deadline and cancellation handling.
- Prompt and model version metadata.

### 3.8 Infrastructure and Platform

Contains:

- Repository implementations.
- Database and migration management.
- Scheduling.
- Workflow execution support.
- Source adapters.
- Delivery adapters.
- Configuration.
- Logging, metrics, and tracing.
- Application lifecycle and health checks.

## 4. Component Responsibilities

### 4.1 SourceRegistry

Responsibilities:

- Register sources.
- Update source configuration.
- Enable and disable sources.
- Retrieve source metadata.
- Expose source collection capabilities.
- Store language, geographic coverage, and access restrictions.
- Maintain source reliability metadata.
- Track source health information.

It must not collect articles.

Source reliability is an assessed attribute and must not be treated as an absolute guarantee of factual accuracy.

### 4.2 NewsCollector

Responsibilities:

- Fetch articles from configured sources.
- Handle source-specific pagination.
- Track collection checkpoints.
- Normalize collection errors.
- Record collection metadata.
- Enforce source-specific request limits.
- Identify incomplete or unavailable content.

It must not perform event matching or economic analysis.

It must not bypass source access restrictions or licensing requirements.

### 4.3 ArticleNormalizer

Responsibilities:

- Normalize article fields.
- Extract canonical URLs.
- Normalize timestamps.
- Identify and preserve source language.
- Clean retrieved article content.
- Preserve original source references.
- Record content availability and retrieval limitations.
- Produce normalized article metadata.

It must not discard provenance or silently replace original content with translated content.

### 4.4 ArticleDeduplicator

Responsibilities:

- Detect identical or substantially duplicate articles.
- Use canonical URLs and content fingerprints.
- Identify near-duplicate and syndicated content where possible.
- Generate duplicate candidates with confidence.
- Preserve original article records and duplicate relationships.
- Distinguish confirmed duplicates from uncertain candidates.

It must not merge articles merely because they describe the same event.

A duplicate candidate must be distinguishable from a confirmed duplicate relationship.

### 4.5 TopicClassifier

Responsibilities:

- Assign one or more economic topic categories.
- Produce classification confidence.
- Preserve classification method and version.
- Support deterministic and LLM-assisted classification.
- Represent insufficient information or uncertain classification explicitly.

Classification results must be versioned.

### 4.6 EntityExtractor

Responsibilities:

- Extract organizations.
- Extract countries and regions.
- Extract people.
- Extract institutions.
- Extract companies.
- Extract economic sectors.
- Extract financial instruments and commodities where applicable.
- Produce candidate entity references.

Entity resolution must be separate from raw entity extraction.

### 4.7 EntityResolver

Responsibilities:

- Match extracted entity mentions to canonical entities.
- Resolve known aliases.
- Identify possible duplicate entity records.
- Preserve the original entity mention.
- Return confidence and resolution method.
- Identify ambiguous entity matches.

It must not silently merge distinct entities.

### 4.8 ClaimExtractor

Responsibilities:

- Extract candidate claims from individual articles.
- Preserve source attribution.
- Identify relevant text references or source locations where available.
- Classify claim types.
- Record extraction confidence and method.
- Distinguish source assertions from system-generated analytical statements.

It must not independently declare a claim verified.

### 4.9 EventDetector

Responsibilities:

- Identify candidate real-world developments.
- Determine whether an article may describe a new event.
- Extract candidate event characteristics.
- Provide candidate event metadata.
- Identify insufficient or ambiguous event information.

It must not independently create persistent events without the Event Resolution workflow and EventService.

### 4.10 EventMatcher

Responsibilities:

- Compare candidate developments with existing events.
- Evaluate semantic and contextual similarity.
- Consider entities, geography, dates, topic, and event type.
- Return candidate matches with confidence.
- Identify ambiguous matches.
- Provide matching method and algorithm version.
- Explain relevant matching factors where available.

The matcher must not independently modify persistent event associations.

A low-confidence match must not silently merge unrelated events.

Matching may combine:

- Deterministic rules.
- Entity comparisons.
- Temporal and geographic context.
- Textual similarity.
- Semantic similarity.
- Confidence evaluation.

The matching strategy and thresholds must be documented, versioned, and evaluated.

The detailed event identity and matching decisions are governed by the relevant ADRs and supporting architecture specifications.

### 4.11 EventService

Responsibilities:

- Create events.
- Associate articles with events.
- Validate event identity and lifecycle rules.
- Update event metadata.
- Maintain stable event identifiers.
- Coordinate event updates.
- Record event-history occurrences.
- Coordinate approved merge and split operations.
- Preserve historical relationships after corrections.

EventService owns event-level business rules.

It must not implement low-level similarity calculations or database-specific query logic.

### 4.12 EventHistoryService

Responsibilities:

- Record material event changes.
- Record lifecycle transitions.
- Record event corrections.
- Record merge and split history.
- Preserve historical event references.
- Retrieve event history for audit and analysis.

A material update is a historical occurrence, not necessarily a persistent event status.

EventHistoryService must not overwrite previous historical records.

### 4.13 SourceAssessmentService

Responsibilities:

- Evaluate source metadata.
- Use configured source reliability information.
- Identify known source ownership or syndication relationships.
- Provide source context to evidence assessment.
- Identify missing or uncertain source information.

Source assessment is contextual input to evidence evaluation, not proof that a claim is true or false.

### 4.14 EvidenceService

Responsibilities:

- Store claims and evidence records.
- Link evidence to claims.
- Record source attribution.
- Record support and contradiction relationships.
- Maintain verification status.
- Preserve evidence provenance.
- Support evidence corrections and supersession.

Evidence records must be traceable to their original source material or other explicitly identified evidence origins.

Evidence and claim relationships may be many-to-many when justified.

### 4.15 EvidenceAnalyzer

Responsibilities:

- Evaluate evidence relevance.
- Identify support and contradiction relationships.
- Assess source diversity and independence.
- Identify repeated claims originating from one source.
- Evaluate evidence completeness.
- Produce evidence quality assessments.
- Identify unresolved contradictions.

It must not treat repeated syndication as independent corroboration.

An evidence assessment must distinguish insufficient evidence from evidence of absence.

### 4.16 ImportanceRanker

Responsibilities:

- Evaluate event importance.
- Apply the approved importance methodology.
- Produce a normalized score where appropriate.
- Explain the main factors behind the score.
- Record scoring methodology and version.
- Represent unavailable inputs explicitly.

Importance is not equivalent to economic impact.

The scoring methodology and thresholds must be documented and evaluated independently.

### 4.17 ImpactAnalyzer

Responsibilities:

- Evaluate economic transmission channels.
- Identify potentially affected markets and sectors.
- Analyze direct and indirect economic implications.
- Distinguish observed effects from reported effects and inferred effects.
- Express uncertainty.
- Identify missing market or economic data.

The component must not invent precise market effects without supporting data.

It must distinguish:

- Observed Market Reaction.
- Source-Reported Reaction.
- AI-Inferred Economic Impact.

An inferred consequence must not be presented as an observed market movement.

### 4.18 HistoricalContextService

Responsibilities:

- Retrieve relevant event history.
- Retrieve previous analytical versions.
- Retrieve historical reports.
- Provide historical context for current analysis.
- Support comparisons with previous events.

It must not own event persistence or independently change event state.

Historical retrieval may initially use relational queries and indexed search.

Semantic retrieval and vector storage are separate architectural decisions.

### 4.19 ReportGenerator

Responsibilities:

- Generate structured event reports.
- Apply report templates.
- Include evidence references.
- Separate facts from source claims and analysis.
- Include uncertainty and limitations.
- Generate immutable report versions.
- Record the analysis and template versions used.

It must not make publication decisions or deliver reports.

### 4.20 PublicationPolicy

Responsibilities:

- Evaluate report quality.
- Apply evidence and confidence requirements.
- Detect duplicate publication risk.
- Evaluate provenance completeness.
- Evaluate security and content-policy requirements.
- Determine publication outcome.
- Record decision reasons and policy version.

It returns one of:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

It must not perform delivery.

### 4.21 ReviewService

Responsibilities:

- Create review records for held reports.
- Maintain review queue status.
- Record review reasons.
- Record reviewer or authorized decision-maker where applicable.
- Record review timestamps.
- Record review outcomes.
- Route approved reports back to publication processing.
- Preserve review history.

Possible review outcomes include:

- Approve publication.
- Approve with caveats.
- Request regeneration or additional evidence.
- Reject publication.

A held report must not be automatically published without an authorized review outcome.

The initial implementation must define the actual review mechanism and the authorized decision-maker.

### 4.22 ReportVersionService

Responsibilities:

- Create report versions.
- Preserve previous versions.
- Record corrections and supersession.
- Record withdrawal.
- Maintain publication history.
- Ensure historical report content remains auditable.

Published report versions must be immutable.

A correction or withdrawal must create a traceable status or version transition rather than silently replacing previous content.

### 4.23 ReportDelivery

Responsibilities:

- Deliver approved reports.
- Track delivery attempts.
- Prevent duplicate delivery.
- Record destination and delivery references.
- Record delivery outcomes.
- Support future delivery channels.
- Handle retryable delivery failures.

It must not generate report content or determine publication eligibility.

Delivery operations must use stable idempotency keys.

### 4.24 WorkflowOrchestrator

Responsibilities:

- Coordinate application workflows.
- Schedule workflow execution.
- Track workflow and job state.
- Manage checkpoints.
- Enforce concurrency limits.
- Coordinate retries and deadlines.
- Propagate cancellation.
- Support recovery after interruption.
- Trigger controlled reprocessing.
- Record execution outcomes.

It must not contain domain-specific event matching or analytical algorithms.

Workflow state must be distinct from article, event, analysis, and publication state.

### 4.25 SharedLLMExecutionLayer

Responsibilities:

- Provide provider-independent LLM invocation.
- Normalize provider requests and responses.
- Validate structured output.
- Enforce token and cost budgets.
- Enforce deadlines.
- Support cancellation.
- Apply bounded retries for appropriate transient provider failures.
- Track model and prompt versions.
- Record token usage and cost when available.
- Normalize provider errors.

It must not own product-specific news intelligence logic.

General conversational memory, autonomous agent loops, and unrestricted tool execution are not initial-release requirements.

### 4.26 ObservabilityService

Responsibilities:

- Emit structured logs.
- Record metrics.
- Support distributed or local trace correlation as appropriate.
- Track workflow outcomes.
- Track provider usage and errors.
- Redact sensitive information.
- Provide operational health information.

Sensitive article content, secrets, and credentials must not be logged by default.

## 5. Domain Model Contracts

The following entities represent the initial domain model.

Exact fields, types, constraints, indexes, relationships, and database mappings are defined in:

`docs/03-data-model-and-storage-design.md`

This section establishes component-level expectations rather than a second authoritative database schema.

### 5.1 Source

Represents a configured information source.

The domain model must support:

- Source identity.
- Source type.
- Collection configuration.
- Language and geographic coverage.
- Access restrictions.
- Reliability metadata.
- Activation status.
- Source health information.

### 5.2 Article

Represents one collected publication.

The domain model must support:

- Source identity.
- External and canonical identifiers.
- Original URL.
- Title and available content references.
- Original source language.
- Author and publication metadata when available.
- Collection timestamp.
- Content fingerprint.
- Content availability.
- Processing history.

Full-text storage must comply with applicable source terms and content rights.

Content availability must be represented explicitly.

### 5.3 ArticleProcessingRecord

Represents a processing attempt or version for an article.

It must preserve:

- Processing stage.
- Processing status.
- Method and version.
- Execution timestamps.
- Error classification.
- Relevant processing metadata.

Processing history must not be confused with current article content.

### 5.4 Event

Represents a real-world development.

The domain model must support:

- Stable event identity.
- Event classification.
- Geographic scope.
- Lifecycle status.
- First observation.
- Last material update.
- Resolution information.
- Event history.

Importance and economic impact assessments should be stored with their methodology and version metadata rather than treated as unqualified permanent properties.

### 5.5 ArticleEventLink

Represents an article-event relationship.

The relationship must support:

- Article identity.
- Event identity.
- Relationship type.
- Association confidence.
- Matching method and version.
- Association timestamp.
- Relationship status.
- Correction and supersession history.

The system must preserve the history of corrected or superseded associations.

### 5.6 Entity

Represents a real-world entity.

The domain model must support canonical identity, entity type, geographic information, external identifiers, and metadata.

### 5.7 EntityAlias

Represents an alternative name or identifier associated with a canonical entity.

Aliases must preserve language and alias type where relevant.

### 5.8 Claim

Represents a source-attributed assertion or analytical assertion.

Claim provenance must be represented through explicit relationships to articles, sources, and evidence.

A claim must not be considered verified solely because it has been extracted from an article.

### 5.9 Evidence

Represents information supporting, qualifying, or contradicting a claim.

The domain model must support evidence origin, source attribution, evidence type, relevance, verification status, and claim relationships.

Claim-to-evidence relationships must support appropriate relationship types, including support and contradiction.

### 5.10 Analysis

Represents a versioned analytical result.

Analysis records must preserve references to relevant claims, evidence, processing inputs, model configuration, prompt version, and methodology version where applicable.

### 5.11 Report

Represents one generated report version.

Reports must be versioned and preserve their relationship to the event, analysis, evidence references, and generation metadata.

Publication decisions and delivery outcomes must be stored separately from report content.

### 5.12 PublicationDecision

Represents a publication policy evaluation.

It must preserve:

- Report reference.
- Decision.
- Decision reason.
- Policy version.
- Evaluation timestamp.

### 5.13 ReviewRecord

Represents a review request and its outcome.

It must preserve:

- Report reference.
- Review status.
- Review reason.
- Reviewer reference where applicable.
- Creation and completion timestamps.
- Review outcome.

### 5.14 DeliveryRecord

Represents a delivery attempt.

It must preserve:

- Report reference.
- Destination reference.
- Idempotency key.
- Delivery status.
- Attempt information.
- External delivery reference where available.
- Execution timestamps.

### 5.15 ProcessingRun

Represents one workflow or processing execution.

It must preserve execution identity, target, run type, status, timestamps, error category, and metadata.

ProcessingRun represents execution state, not domain state.

### 5.16 EventHistory

Represents a historical occurrence or material change associated with an event.

Event history must be append-oriented and auditable.

It must preserve relevant lifecycle transitions, material updates, corrections, merges, and splits.

## 6. Repository Interfaces

All persistence access must use repository interfaces.

Initial interfaces include:

- `SourceRepository`
- `ArticleRepository`
- `ArticleProcessingRepository`
- `EventRepository`
- `ArticleEventLinkRepository`
- `EntityRepository`
- `EntityAliasRepository`
- `ClaimRepository`
- `EvidenceRepository`
- `AnalysisRepository`
- `ReportRepository`
- `PublicationDecisionRepository`
- `ReviewRepository`
- `DeliveryRepository`
- `ProcessingRunRepository`
- `EventHistoryRepository`

Repositories provide persistence operations and query methods.

They must not implement domain-level analytical decisions.

Database-specific query logic belongs in infrastructure implementations.

Repository contracts must support the transaction boundaries required by their corresponding application workflows.

Repositories must not expose database-specific types to domain or application layers.

## 7. Workflow Contracts

### 7.1 Collection Workflow

**Input:**

- Source identifier.
- Source configuration.
- Collection checkpoint.
- Execution context and deadline.

**Output:**

- Acquired article metadata and permitted content references.
- Collection result.
- Updated checkpoint.
- Collection health information.

**Failure conditions:**

- Network errors.
- Source access failures.
- Invalid responses.
- Rate limiting.
- Source configuration errors.
- Content access restrictions.

The workflow must preserve enough information to resume collection safely.

### 7.2 Article Processing Workflow

**Input:**

- Raw article record.
- Processing configuration.
- Execution context.

**Output:**

- Normalized article.
- Language identification.
- Duplicate candidates and outcome.
- Topic classifications.
- Extracted entity mentions.
- Candidate claims.
- Processing metadata.

Processing must be idempotent for the same input and processing version where possible.

New processing versions must not silently overwrite historical results.

### 7.3 Event Resolution Workflow

**Input:**

- Processed article.
- Candidate event information.
- Existing event candidates.
- Matching configuration.

**Output:**

- Matched event, new event candidate, or unresolved candidate.
- Association confidence.
- Matching method and version.
- Decision factors.
- Ambiguity information.

Ambiguous matching must be represented explicitly.

New event creation and association must be coordinated through EventService.

### 7.4 Event Intelligence Workflow

**Input:**

- Event identifier.
- Related articles.
- Available claims and evidence.
- Historical event context.
- Analysis configuration.

**Output:**

- Evidence assessment.
- Importance assessment.
- Economic impact analysis.
- Updated event dossier.
- New analytical version.
- Processing metadata.

Observed, source-reported, and inferred economic impacts must remain distinguishable.

### 7.5 Reporting Workflow

**Input:**

- Event dossier.
- Analysis version.
- Evidence references.
- Report template and version.

**Output:**

- Immutable report version.
- Report generation metadata.
- Publication evaluation request or result.

Report generation must not itself publish or deliver the report.

### 7.6 Publication and Review Workflow

**Input:**

- Generated report.
- Publication policy configuration.
- Relevant evidence and provenance information.

**Output:**

- Publication decision.
- Decision reasons.
- Review record when required.
- Next permitted workflow action.

A held report must be routed to a defined review mechanism.

The workflow must not bypass review requirements.

### 7.7 Delivery Workflow

**Input:**

- Approved report version.
- Delivery destination.
- Stable idempotency key.

**Output:**

- Delivery status.
- Delivery reference.
- Attempt metadata.

The workflow must prevent unintended duplicate publication or delivery when retried.

### 7.8 Reprocessing Workflow

**Input:**

- Target article, event, or report-related processing scope.
- Requested processing stage.
- Processing or methodology version.

**Output:**

- New processing records.
- New analytical versions where applicable.
- Reprocessing outcome.
- Links to superseded or previous outputs.

Reprocessing must not silently overwrite published or historical records.

## 8. Execution and Error Contracts

All external operations must have explicit timeout and resource-limit behavior.

Errors should be categorized.

Suggested categories:

- `NETWORK_ERROR`
- `RATE_LIMITED`
- `SOURCE_UNAVAILABLE`
- `SOURCE_ACCESS_RESTRICTED`
- `INVALID_SOURCE_RESPONSE`
- `NORMALIZATION_ERROR`
- `DEDUPLICATION_ERROR`
- `CLASSIFICATION_ERROR`
- `ENTITY_EXTRACTION_ERROR`
- `ENTITY_RESOLUTION_ERROR`
- `CLAIM_EXTRACTION_ERROR`
- `EVENT_DETECTION_ERROR`
- `EVENT_MATCHING_ERROR`
- `EVIDENCE_ANALYSIS_ERROR`
- `IMPACT_ANALYSIS_ERROR`
- `REPORT_GENERATION_ERROR`
- `PUBLICATION_REJECTED`
- `REVIEW_REQUIRED`
- `PERSISTENCE_ERROR`
- `DELIVERY_ERROR`
- `BUDGET_EXHAUSTED`
- `DEADLINE_EXCEEDED`
- `CANCELLED`

The execution layer must distinguish:

- Recoverable failures.
- Terminal failures.
- Cancellation.
- Deadline expiration.
- Budget exhaustion.
- Validation failures.

Retries must be limited to operations that are safe to retry.

Acquisition retries may be appropriate for transient network failures. Publication and delivery retries must use idempotency controls.

A failed operation must not be reported as successful.

A workflow interrupted after a partial operation must be able to determine which steps completed and which steps require recovery.

## 9. Shared LLM Execution Contract

News intelligence components may use LLMs through the Shared LLM Execution Layer.

The interface must support:

- Normalized request and response schemas.
- Structured output requirements.
- Schema validation.
- Model selection through configuration.
- Model and provider metadata.
- Prompt and task version tracking.
- Input and output token budgets.
- Reserved output-token capacity.
- Per-operation deadlines.
- Cancellation propagation.
- Bounded retries for safe transient provider failures.
- Usage and cost recording when available.
- Provider error normalization.

LLM requests must distinguish trusted system instructions from untrusted source content.

Retrieved article content must never be treated as trusted instructions.

LLM outputs must be validated before being used to modify domain records.

The LLM is an analytical execution dependency, not the authoritative storage layer.

Persisted domain records remain the source of truth for application state.

The Shared LLM Execution Layer must not require conversation memory, general-purpose autonomous agents, or unrestricted tool execution.

## 10. Security and Trust Boundaries

External news content is untrusted.

The system must defend against:

- Prompt injection.
- Malicious URLs.
- SSRF and private network access.
- Unsafe redirects.
- Unexpected content formats.
- Oversized articles and responses.
- Malformed metadata.
- Untrusted tool output.
- Unauthorized tool execution.
- Secret leakage through logs.

Source adapters must not receive unrestricted filesystem or shell access.

LLM analysis stages must not receive unrestricted operational tools.

External URL acquisition must use explicit protocol allowlists, network restrictions, redirect limits, response size limits, and timeouts.

All external operations must have controlled resource limits.

Secrets must be redacted before logging.

Content rights and source access restrictions must be enforced independently of technical availability.

## 11. Dependency Rules

The following dependency rules apply:

- Domain depends on no infrastructure implementation.
- Application workflows depend on domain contracts and application-level component interfaces.
- Repositories are interfaces in the core and implementations in infrastructure.
- LLM adapters implement the Shared LLM Execution Layer contract.
- News source adapters implement source collection contracts.
- Delivery adapters implement delivery contracts.
- Report generation does not depend on delivery implementations.
- Publication policy does not depend on a specific delivery channel.
- Event matching does not directly manipulate database tables.
- EventService owns event-level business rules.
- EvidenceAnalyzer evaluates evidence but does not own persistence.
- HistoricalContextService retrieves context but does not own event lifecycle.
- Observability is accessed through interfaces.
- Factory or composition root wires concrete implementations.

Application workflows coordinate components but must not become containers for duplicated business logic.

The composition root is responsible for assembling concrete infrastructure implementations and injecting them into application workflows.

## 12. Observability Contracts

Each major operation should emit structured information.

Examples:

- `source.collection.started`
- `source.collection.completed`
- `source.collection.failed`
- `article.ingested`
- `article.normalized`
- `article.duplicate_candidate_detected`
- `article.duplicate_confirmed`
- `article.classified`
- `entity.extracted`
- `entity.resolved`
- `claim.extracted`
- `event.candidate_detected`
- `event.matching.completed`
- `event.matched`
- `event.created`
- `event.association.corrected`
- `event.updated`
- `event.merged`
- `event.split`
- `evidence.assessed`
- `analysis.completed`
- `report.generated`
- `report.publication_decided`
- `report.review.created`
- `report.review.completed`
- `report.corrected`
- `report.withdrawn`
- `report.delivered`
- `workflow.recovered`

Events should include correlation identifiers and relevant entity references where appropriate.

Observability must track:

- Processing duration.
- Retry counts.
- Error categories.
- Workflow status.
- LLM usage when available.
- Publication outcomes.
- Review queue age.
- Delivery outcomes.

Sensitive content and secrets must not be logged by default.

## 13. Testing Contracts

Each component must have:

- Unit tests.
- Interface contract tests where appropriate.
- Failure behavior tests.
- Boundary-condition tests.
- Idempotency tests where operations may be retried.

Integration tests should verify complete workflows using fake source providers, fake LLM providers, and test persistence implementations.

Tests must not require paid APIs.

Critical tests include:

- Article deduplication without accidental event merging.
- Near-duplicate and syndicated article detection.
- Event matching with ambiguous candidates.
- Event identity preservation.
- Event merge and split history.
- Claim and evidence traceability.
- Multiple claims linked to relevant evidence.
- Conflicting evidence handling.
- Source independence assessment.
- Publication policy enforcement.
- Review queue behavior.
- Report version consistency.
- Report correction and withdrawal.
- Duplicate delivery prevention.
- Workflow recovery after interruption.
- Idempotent reprocessing.
- Cancellation and timeout propagation.
- LLM structured output validation.
- Prompt injection resistance tests.
- Budget and deadline enforcement.

Evaluation datasets must be used to measure classification, extraction, event matching, evidence assessment, and report quality.

## 14. Versioning and Compatibility

Domain schemas and external contracts should be versioned deliberately.

Changes that alter persisted meaning require migrations or explicit compatibility handling.

LLM prompt versions, model metadata, and processing methodology versions should be retained for analytical traceability.

Report versions must be immutable after publication.

Reprocessing should create new processing or analytical versions rather than silently overwriting historical outputs.

Changes to event identity or association logic must preserve historical associations and correction records.

Breaking changes to component interfaces must be reviewed for their impact on dependent workflows.

## 15. Initial Release Implementation Boundaries

The initial product release includes the following capabilities:

- Source management.
- News acquisition.
- Article normalization.
- Language identification.
- Article deduplication.
- Topic classification.
- Entity extraction and basic entity resolution.
- Candidate claim extraction.
- Event detection and matching.
- Event management and history.
- Evidence management and assessment.
- Importance ranking.
- Economic impact analysis.
- Event dossier generation.
- Report generation and versioning.
- Publication policy.
- A defined review mechanism for held reports.
- Text delivery.
- Basic scheduling and workflow recovery.
- Shared LLM Execution Layer.
- Evaluation and observability.

The initial persistence technology must be selected and approved through the relevant architectural decision process. SQLite is a proposed initial option, not an approved implementation constraint in this document.

Deferred unless separately justified:

- Audio generation.
- Video generation.
- Advanced forecasting.
- Dedicated vector database infrastructure.
- Full-scale RAG infrastructure.
- Multi-agent orchestration.
- Distributed event processing.
- Enterprise multi-tenancy.
- Advanced personalization.

Semantic event matching is not deferred merely because a dedicated vector database is deferred. The initial matching implementation must use an explicitly selected approach that can be evaluated and upgraded.

## 16. Definition of Done

A component is complete when:

1. Its responsibility is clearly defined.
2. Its public interface is documented.
3. It follows dependency rules.
4. Its inputs are validated.
5. Its outputs are normalized.
6. Failure behavior is explicit.
7. Timeouts and cancellation are handled where applicable.
8. Retry and idempotency behavior is defined where applicable.
9. Observability is implemented.
10. Unit tests pass.
11. Relevant contract and integration tests pass.
12. Security boundaries are respected.
13. Historical records are preserved where required.
14. Documentation is updated.
15. Its dependencies and configuration are documented.
16. Its behavior is covered by relevant evaluation criteria where applicable.

## 17. Architecture Decisions and Open Items

The following items require formal review and corresponding ADRs or supporting specifications:

1. Workflow-first architecture and Shared LLM Execution Layer scope.
2. Event identity, matching, creation, merging, and splitting.
3. Article deduplication and near-duplicate detection.
4. Semantic similarity and embedding generation.
5. Embedding storage and retrieval strategy.
6. Claim and evidence relationship design.
7. Source reliability and source independence assessment.
8. Publication decisions and review operations.
9. Report correction and withdrawal.
10. Market data integration and impact classification.
11. SQLite concurrency and asynchronous persistence strategy.
12. Workflow recovery, idempotency, and retry guarantees.
13. LLM budget, cost tracking, and evaluation.
14. Source acquisition security and content retention.

The current individual ADR documents are listed in:

`docs/adr/README.md`

The project currently has six published individual ADR documents, all with Proposed status.

The remaining identified decision topics are tracked in the ADR Registry and must not be treated as accepted architectural decisions.

Until the relevant ADRs are accepted, these decisions remain proposed and must not be treated as approved implementation constraints.

## 18. Final Design Statement

The component architecture separates acquisition, article processing, event intelligence, evidence verification, economic analysis, report generation, publication, and delivery.

The system uses explicit interfaces and dependency inversion to keep the product modular, testable, and independent of specific providers.

Application workflows coordinate deterministic processing stages, while the Shared LLM Execution Layer provides controlled language-model capabilities.

The design preserves event identity, evidence provenance, historical traceability, controlled publication, and recoverable execution.

Future expansion must not compromise the simplicity, reliability, and explicit boundaries of the initial product release.