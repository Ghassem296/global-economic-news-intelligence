# Global Economic News Intelligence
## Component Architecture and Interface Contracts

**Document ID:** GENI-ARCH-002  
**Version:** 1.8  
**Status:** Draft — Under Architecture Review  
**Project:** Global Economic News Intelligence  
**Last Updated:** 2026-11-18

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
- Economic relevance assessment.
- Economic impact analysis.
- Historical context retrieval.

### 3.6 Reporting and Publication

Contains:

- Event dossier generation.
- Report generation.
- Report version management.
- Publication policy and review management.
- Publication execution, including publish, replace, and withdraw operations.
- Report-version correction and supersession lineage.
- Independent recipient delivery coordination.

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

- Generate and evaluate candidate events for one event-matching case.
- Use the specific ArticleRevision and development scope recorded by that case.
- Evaluate deterministic, lexical, entity, temporal, geographic, and optional semantic signals.
- Persist candidate evidence, scores, method, and matching-policy version.
- Explain why each candidate is eligible, ineligible, or inconclusive.
- Return candidate evaluations to the Event Resolution workflow.

EventMatcher is an evaluation component. It must not issue the authoritative matching decision, create an ArticleEventLink, create or merge an Event, or modify an existing association.

A candidate score or candidate status is not a final matching decision. A candidate must never be marked ACCEPTED or REJECTED as a substitute for a case-level decision.

### 4.10.1 Event Resolution Workflow

The Event Resolution workflow coordinates one EventMatchCase at a time.

Responsibilities:

- Create or retrieve a case scoped to one ArticleRevision and one independently identified development within that revision.
- Request candidate generation and evaluation.
- Ensure all candidates belong to the same case.
- Evaluate whether the case has sufficient information for an automated decision.
- Request a new immutable EventMatchDecision.
- Route ambiguous or policy-defined cases to authorized human review.
- Apply an eligible decision through EventService.
- Preserve decision, review, and association history.

A single article revision may create multiple independent EventMatchCase records. A decision for one case must not implicitly decide another development in the same article.

### 4.10.2 EventMatchDecision

EventMatchDecision is the authoritative, immutable record of the outcome for one EventMatchCase.

The decision outcome must be explicit: MATCH, NEW_EVENT_CANDIDATE, NO_MATCH, AMBIGUOUS, or REVIEW_REQUIRED. MATCH must identify exactly one selected candidate. Other outcomes must not create an active ArticleEventLink. A human correction or later reassessment creates a new decision that supersedes the previous effective decision; it does not mutate the historical decision.

The decision must identify its method, policy version, rationale, decision actor, timestamp, confidence semantics where applicable, and any superseded decision. A review task or review comment is not itself an EventMatchDecision.

### 4.11 EventService

Responsibilities:

- Create events only through the authorized event-creation workflow.
- Apply an authorized EventMatchDecision.
- Create an ArticleEventLink only for a valid MATCH decision.
- Deactivate an existing ArticleEventLink only through an authorized successor decision or identity-correction operation.
- Validate event identity and lifecycle rules.
- Update event metadata and maintain stable event identifiers.
- Coordinate event updates and record event-history occurrences.
- Coordinate approved merge and split operations.
- Preserve historical relationships after corrections.

EventService owns event-level business rules and the application of authorized event-association decisions. The Event Resolution workflow coordinates candidate evaluation, case-level decision creation, and review routing. EventService must reject attempts to create an active association from a non-MATCH decision.

EventService must not implement low-level similarity calculations or database-specific query logic.

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

- Evaluate the overall significance and attention priority of an event.
- Apply the approved importance methodology independently of the economic relevance and impact assessments.
- Produce a qualitative rank or a numeric score only when a defined scale is approved.
- Explain the main factors behind the result.
- Record methodology, policy, and result-schema versions.
- Represent unavailable, contradictory, and insufficient inputs explicitly.

Importance is not a measure of economic relevance, economic-effect magnitude, or forecast probability. It must not silently combine the other assessment outputs.

### 4.17 EconomicRelevanceAssessor

Responsibilities:

- Assess whether and how an event is connected to economic activity, policy, institutions, or markets.
- Identify direct, indirect, and contextual economic transmission pathways.
- Identify affected countries, institutions, sectors, industries, commodities, and markets.
- Distinguish a demonstrated or plausible economic connection from a connection that has not been established.
- Represent insufficient information as unknown rather than treating it as no economic relevance.
- Record the methodology, policy, and result-schema versions used.

Economic relevance measures the strength and nature of the economic connection. It does not estimate the magnitude, direction, or certainty of economic consequences. The component must not reuse the ImportanceRanker result as a substitute for its own assessment.

### 4.18 ImpactAnalyzer

Responsibilities:

- Evaluate realized and potential economic consequences across relevant transmission channels.
- Identify affected markets, sectors, institutions, countries, and groups.
- Assess direction, magnitude or defensible range, time horizon, duration, and distribution where supported.
- Distinguish observed economic effects, source-reported effects, inferred potential effects, and unknown effects.
- Link conclusions to supporting and conflicting evidence.
- Express uncertainty and identify missing market or economic data.

The component must not invent precise economic effects or aggregate distinct channel-level impacts into a misleading single value. Its output is an economic-impact assessment, not an importance or economic-relevance score.

Observed market reaction is a separate evidence category. The component must not infer causality merely because market data records a movement.

### 4.19 HistoricalContextService

Responsibilities:

- Retrieve relevant event history.
- Retrieve previous analytical versions.
- Retrieve historical reports.
- Provide historical context for current analysis.
- Support comparisons with previous events.

It must not own event persistence or independently change event state.

Historical retrieval may initially use relational queries and indexed search.

Semantic retrieval and vector storage are separate architectural decisions.

### 4.20 ReportGenerator

Responsibilities:

- Generate structured report content from an event dossier and approved analysis inputs.
- Apply report templates.
- Include evidence and source references.
- Separate observed facts, source-attributed claims, analysis, and forecasts.
- Include uncertainty and limitations.
- Produce report content and generation metadata.

It must not make publication decisions, create publication operations, or deliver reports. Immutable report-version creation and lineage are managed by ReportVersionService.

### 4.21 PublicationPolicy

Responsibilities:

- Evaluate report quality.
- Apply evidence and confidence requirements.
- Detect duplicate publication risk.
- Evaluate provenance completeness.
- Evaluate security, content-rights, and content-policy requirements.
- Determine publication eligibility.
- Record decision reasons, caveats, and policy version.

It returns one of:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

A publication decision is an authorization outcome, not an instruction that an external publication has succeeded. PublicationPolicy must not execute publication or delivery operations.

### 4.22 ReviewService

Responsibilities:

- Create typed review tasks for EventMatchCase records, held reports, and other policy-defined review subjects.
- Maintain review queue status, priority, assignment, due dates, and escalation metadata.
- Record review reasons, reviewer identity, authorized role, timestamps, and immutable review outcomes.
- Link each review to the exact subject and decision under review.
- Route event-matching review outcomes to the Event Resolution workflow.
- Route publication review outcomes back to PublicationPolicy for a new PublicationDecision.
- Preserve review actions and reassignment history.

ReviewService manages review tasks and reviewer actions; it does not own event identity or publication eligibility decisions.

For event matching, a material review outcome must create a new EventMatchDecision that supersedes the prior effective decision. For publication, a material review outcome must create a new effective PublicationDecision. ReviewService must not mutate either prior decision, bypass EventService or PublicationPolicy, or directly call an external publication target.

Reviewer identity and authorization must be enforced by the application's security layer. The initial implementation must define the authorized decision-maker and review mechanism for each review type.

### 4.23 ReportVersionService

Responsibilities:

- Create immutable report versions from generated content.
- Assign and validate version identity.
- Preserve previous report versions.
- Record report-level correction and supersession lineage.
- Maintain report-generation history.
- Ensure historical report content remains auditable.

A correction creates a new report version; it must not overwrite a previously generated or published report. ReportVersionService manages report-version lineage only. It does not execute an external replacement or withdrawal and does not own publication-target state.

### 4.24 PublicationService

Responsibilities:

- Execute authorized `PUBLISH`, `REPLACE`, and `WITHDRAW` operations.
- Validate the effective publication decision and required review authorization.
- Validate the report version, publication target, stable publication key, and any existing publication being replaced or withdrawn.
- Serialize conflicting operations for the same target and publication key without blocking unrelated keys at that target.
- Persist a durable PublicationRecord before an external side effect.
- Create and update PublicationAttempt records.
- Generate and reuse stable idempotency keys for retries of the same logical operation.
- Invoke a target-specific publication adapter through an explicit interface.
- Record confirmed external references, URLs, timestamps, and outcomes.
- Reconcile uncertain external outcomes before another side-effecting attempt.
- Preserve the history of successful, failed, superseded, and withdrawn publication operations.

It must not generate report content, decide publication eligibility, silently alter a report version, or perform subscriber delivery.

A failed replacement must leave the previous confirmed publication effective. A failed or uncertain withdrawal must not be represented as completed. A publication operation with an uncertain external outcome must enter reconciliation rather than being blindly retried.

### 4.25 ReportDelivery

Responsibilities:

- Deliver approved report content, confirmed publication links, or notifications to configured recipients and delivery destinations.
- Track logical delivery operations and individual delivery attempts.
- Prevent duplicate delivery.
- Record destination and external delivery references.
- Record delivery outcomes.
- Support future delivery channels.
- Handle retryable delivery failures.

It must not generate report content, determine publication eligibility, or execute public publication, replacement, or withdrawal operations. A delivery containing a publication link must reference a confirmed successful PublicationRecord. Delivery outcomes must not change publication state.

Delivery operations must use stable idempotency keys.

### 4.26 WorkflowOrchestrator

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

Workflow state must be distinct from article, event, analysis, publication, and delivery state.

### 4.27 SharedLLMExecutionLayer

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

### 4.28 ObservabilityService

Responsibilities:

- Emit structured logs.
- Record metrics.
- Support distributed or local trace correlation as appropriate.
- Track workflow outcomes.
- Track provider usage and errors.
- Track publication-operation and delivery outcomes separately.
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

Content availability must be represented explicitly. Article is the current searchable projection of its latest accepted ArticleRevision; it is not a second independently editable copy of revision content. Updating the current projection and creating a material new revision must be atomic.

### 5.3 ArticleRevision

Represents an immutable, meaningful observed version of an Article's published content.

Fields:

- `id`
- `article_id`
- `revision_number`
- `title`
- `content_reference` — reference to content retained or accessed under the applicable rights policy
- `content_hash`
- `summary` nullable
- `language`
- `observed_at`
- `change_reason`
- `rights_status`
- `metadata`

Constraints:

- `(article_id, revision_number)` must be unique.
- Repeated collection of unchanged content must not create a new revision.
- A material content change creates a new revision and preserves earlier revisions subject to retention policy.
- Content references and derived artifacts must comply with source rights and retention rules.
- Hashes and evidence offsets must identify the exact text representation and normalization version to which they apply.
- The Article current projection must reference the latest accepted revision and must be updated atomically with revision creation.
- EventMatchCase must reference one exact immutable ArticleRevision; a later revision does not silently mutate or reuse the prior revision's matching cases.

### 5.4 ArticleProcessingRecord

Represents a processing attempt or version for an article.

It must preserve:

- Processing stage.
- Processing status.
- Method and version.
- Execution timestamps.
- Error classification.
- Relevant processing metadata.

Processing history must not be confused with current article content.

### 5.5 Event

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

### 5.6 EventMatchCase

Represents one independent attempt to resolve the event identity of one development identified within one immutable ArticleRevision.

Fields:

- `id`
- `article_revision_id`
- `development_key` — stable within the ArticleRevision and identifying the particular development or event mention being resolved
- `scope_description`
- `case_status`
- `effective_decision_id` — nullable pointer to the current effective EventMatchDecision; a mutable projection updated transactionally when a new decision is recorded
- `created_at`
- `closed_at`
- `metadata`

The effective-decision pointer is a current-state projection; historical EventMatchDecision records remain immutable.

A separate case is required for each independently identifiable development in an article revision. The case is the unit of candidate evaluation, final decision, and human review. A case must not be silently reused for a materially different article revision or development scope.

### 5.7 EventMatchCandidate

Represents one existing Event considered as a possible match within an EventMatchCase. Candidate generation and evaluation do not establish an association.

Fields:

- `id`
- `case_id`
- `candidate_event_id`
- `lexical_similarity`
- `semantic_similarity`
- `entity_overlap_score`
- `temporal_compatibility_score`
- `geographic_compatibility_score`
- `overall_score`
- `matching_method`
- `matching_policy_version`
- `candidate_input_fingerprint`
- `candidate_status`
- `evaluation_reason`
- `created_at`
- `evaluated_at`
- `metadata`

Each candidate record represents one versioned evaluation of one candidate Event within one case. An evaluated candidate record is immutable. A changed policy or evaluation input creates a new candidate record; an identical evaluation input is idempotent through its fingerprint.

Candidate status describes processing only (for example GENERATED, EVALUATED, INELIGIBLE, or SUPERSEDED). ACCEPTED and REJECTED are prohibited candidate statuses because acceptance or rejection is a case-level decision, not a property of candidate retrieval.

A candidate score is not a decision confidence and must not be interpreted as one. Candidate evaluation identity is scoped by case, candidate Event, matching-policy version, and candidate-input fingerprint.

### 5.8 EventMatchDecision

Represents an immutable, authoritative outcome for one EventMatchCase.

Fields:

- `id`
- `case_id`
- `outcome`
- `selected_candidate_id` — required only for MATCH
- `proposed_event_reference` — optional reference for NEW_EVENT_CANDIDATE
- `decision_method`
- `decision_confidence` — optional and distinct from candidate similarity
- `decision_rationale`
- `matching_policy_version`
- `decided_by_type`
- `decided_by_reference`
- `supersedes_decision_id`
- `created_at`
- `metadata`

Allowed outcomes:

- `MATCH`
- `NEW_EVENT_CANDIDATE`
- `NO_MATCH`
- `AMBIGUOUS`
- `REVIEW_REQUIRED`

Constraints:

- MATCH must reference exactly one eligible candidate belonging to the same case.
- Non-MATCH outcomes must not authorize an active ArticleEventLink.
- NEW_EVENT_CANDIDATE proposes event creation but does not itself create an Event.
- A later reassessment or human correction creates a new decision and references the decision it supersedes.
- Historical decisions are immutable.
- A review record is not a decision; an authorized review outcome must be materialized as a new EventMatchDecision.

### 5.9 ArticleEventLink

Represents an applied, decision-authorized association between an ArticleRevision and an Event.

Fields:

- `id`
- `article_revision_id`
- `event_match_case_id` — the EventMatchCase that authorized this specific association
- `event_id`
- `relationship_type`
- `association_confidence`
- `association_method`
- `matching_policy_version`
- `event_match_decision_id`
- `associated_at`
- `is_active`
- `deactivated_at`
- `deactivated_by_decision_id`
- `metadata`

Relationship types may include INITIAL_REPORT, FOLLOW_UP, CONFIRMATION, CONTEXT, CONTRADICTION, and RELATED_DEVELOPMENT.

Constraints:

- Every association must reference the exact EventMatchCase and EventMatchDecision that authorized its creation.
- The referenced EventMatchDecision must belong to the referenced EventMatchCase, have outcome MATCH and must identify the linked event through its selected candidate.
- At most one active ArticleEventLink may exist for an EventMatchCase; historical inactive links must be retained.
- The link's article_revision_id must equal the ArticleRevision referenced by its EventMatchCase.
- The link's event_id must equal the Event selected by the referenced MATCH decision.
- A link is active only while its authorizing MATCH decision remains the effective decision for that case.
- Deactivation must preserve the original link and identify the decision or authorized correction that deactivated it.
- A correction creates a new decision and a new association where appropriate; it must not rewrite the historical decision or silently repoint an existing link.
- A single article may have multiple active links when separate EventMatchCase records justify them.

### 5.10 Entity

Represents a real-world entity.

The domain model must support canonical identity, entity type, geographic information, external identifiers, and metadata.

### 5.11 EntityAlias

Represents an alternative name or identifier associated with a canonical entity.

Aliases must preserve language and alias type where relevant.

### 5.12 Claim

Represents a source-attributed assertion or analytical assertion.

Claim provenance must be represented through explicit relationships to articles, sources, and evidence.

A claim must not be considered verified solely because it has been extracted from an article.

### 5.13 Evidence

Represents information supporting, qualifying, or contradicting a claim.

The domain model must support evidence origin, source attribution, evidence type, relevance, verification status, and claim relationships.

Claim-to-evidence relationships must support appropriate relationship types, including support and contradiction.

### 5.14 Analysis

Represents a versioned analytical result or assessment.

Analysis records must preserve references to relevant claims, evidence, processing inputs, model configuration, prompt version, result-schema version, and methodology version where applicable. The initial assessment types must keep `IMPORTANCE_ASSESSMENT`, `ECONOMIC_RELEVANCE_ASSESSMENT`, and `ECONOMIC_IMPACT_ASSESSMENT` as separate results. A shared workflow or evidence set does not permit these assessment types to be merged into one score.

### 5.15 Report

Represents one generated report version.

Reports must be versioned and preserve their relationship to the event, analysis, evidence references, and generation metadata.

Publication decisions and delivery outcomes must be stored separately from report content.

### 5.16 PublicationDecision

Represents a publication policy evaluation.

It must preserve:

- Report-version reference.
- Decision.
- Decision reasons and caveats.
- Policy version.
- Evaluation timestamp.
- Supersession reference where applicable.

A publication decision records eligibility and authorization only. It does not prove that a report has been published at an external target.

### 5.17 ReviewRecord

Represents a review request and its outcome.

It must preserve:

- Report reference.
- Review status.
- Review reason.
- Reviewer reference where applicable.
- Creation and completion timestamps.
- Review outcome.

### 5.18 DeliveryRecord

Represents a logical delivery operation.

It must preserve:

- Report-version reference.
- Delivery mode.
- Destination and recipient reference.
- Optional successful PublicationRecord reference when delivering a publication link.
- Idempotency key.
- Delivery status and attempt information.
- External delivery reference where available.
- Execution timestamps.

Delivery status is independent of publication status. A delivery operation must not create, replace, withdraw, or otherwise mutate a publication.

### 5.19 ProcessingRun

Represents one workflow or processing execution.

It must preserve execution identity, target, run type, status, timestamps, error category, and metadata.

ProcessingRun represents execution state, not domain state.

### 5.20 EventHistory

Represents a historical occurrence or material change associated with an event.

Event history must be append-oriented and auditable.

It must preserve relevant lifecycle transitions, material updates, corrections, merges, and splits.

### 5.21 PublicationRecord

Represents one logical operation against a publication target.

It must preserve:

- Report-version identity.
- Applicable publication-decision reference.
- Publication-target reference.
- Stable publication key identifying the logical publication slot within that target.
- Operation sequence within that target and publication key.
- Operation type: `PUBLISH`, `REPLACE`, or `WITHDRAW`.
- Reference to the earlier publication for replacement or withdrawal.
- Stable idempotency key.
- Operation status and timestamps.
- External publication reference and URL where available.
- Authorization and reason information for withdrawal.
- Error and reconciliation information.

A PublicationRecord represents an operation, not merely a policy decision or a delivery. Its successful operation history is the basis for determining whether a report version is currently available at a publication target.

### 5.22 PublicationAttempt

Represents one execution attempt for a PublicationRecord.

It must preserve:

- Publication-operation identity.
- Attempt number.
- Start and completion timestamps.
- Outcome.
- External reference where available.
- Error classification and summary.
- Reconciliation information and metadata.

Attempts must remain separately traceable. Retrying an operation must not create a new logical publication operation or a new idempotency key.

## 6. Repository Interfaces

All persistence access must use repository interfaces.

Initial interfaces include:

- `SourceRepository`
- `ArticleRepository`
- `ArticleProcessingRepository`
- `EventRepository`
- `EventMatchCaseRepository`
- `EventMatchCandidateRepository`
- `EventMatchDecisionRepository`
- `ArticleEventLinkRepository`
- `EntityRepository`
- `EntityAliasRepository`
- `ClaimRepository`
- `EvidenceRepository`
- `AnalysisRepository`
- `ReportRepository`
- `PublicationDecisionRepository`
- `ReviewRepository`
- `PublicationRepository`
- `PublicationAttemptRepository`
- `DeliveryRepository`
- `ProcessingRunRepository`
- `EventHistoryRepository`

Repositories provide persistence operations and query methods.

They must not implement domain-level analytical decisions.

Database-specific query logic belongs in infrastructure implementations.

Repository contracts must support the transaction boundaries required by their corresponding application workflows.

Repositories must not expose database-specific types to domain or application layers. A repository may encapsulate multiple closely related tables when doing so preserves a clear aggregate and transaction boundary.

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

- Immutable ArticleRevision.
- One independently identified development scope within that revision.
- Matching configuration and policy version.
- Existing event context and candidate retrieval signals.

**Output:**

- One EventMatchCase for the development scope.
- Zero or more EventMatchCandidate records belonging to that case.
- An immutable EventMatchDecision, or an explicit unresolved/review-required case.
- An ArticleEventLink only when an eligible MATCH decision is applied.
- Full decision, review, and association provenance.

**Workflow invariants:**

- One ArticleRevision may have multiple EventMatchCase records; each case represents one development and is resolved independently.
- Candidate generation/evaluation does not issue the final decision and does not modify persistent event associations.
- EventMatchCandidate status describes candidate processing only; ACCEPTED and REJECTED are not candidate statuses.
- Every EventMatchDecision belongs to exactly one case. MATCH selects exactly one eligible candidate from that same case.
- A non-MATCH outcome must not create an active ArticleEventLink.
- Human review references the case and the decision under review. Its outcome creates a new EventMatchDecision that supersedes the prior effective decision.
- Every ArticleEventLink references the exact MATCH decision that authorized it.
- NEW_EVENT_CANDIDATE does not create an Event automatically; event creation follows the separate policy and idempotency rules.

EventMatcher performs candidate evaluation. Event Resolution Workflow coordinates the case and decision lifecycle. EventService applies an authorized decision and maintains event and association invariants.

### 7.4 Event Matching Review Workflow

**Input:**

- EventMatchCase identifier.
- The current effective EventMatchDecision under review.
- Review reason and policy-defined priority.
- Authorized reviewer assignment and execution context.

**Output:**

- A ReviewRecord linked to the exact EventMatchCase and decision.
- An immutable reviewer action and outcome.
- A new EventMatchDecision when the outcome changes the effective matching result.
- Updated case status and effective-decision pointer.

**Workflow invariants:**

- ReviewRecord is a task and audit record, not an EventMatchDecision.
- A reviewer must be authorized for the requested action.
- A review outcome that changes the result creates a new decision with a supersedes reference.
- The previous decision and any prior ArticleEventLink remain historically traceable.
- Any association correction is applied through EventService in the same controlled transaction as the effective decision update.
- A review task cannot directly create an Event or call an external publication target.

### 7.5 Event Intelligence Workflow

**Input:**

- Event identifier.
- Related articles.
- Available claims and evidence.
- Historical event context.
- Analysis configuration.

**Output:**

- Evidence assessment.
- Importance assessment as a distinct versioned result.
- Economic relevance assessment as a distinct versioned result.
- Economic impact analysis as a channel-based versioned result.
- Market-reaction assessment where suitable market observations are available.
- Updated event dossier.
- New analytical versions.
- Processing metadata.

Observed economic effects, source-reported effects, inferred potential effects, and unknown effects must remain distinguishable. Market observations must not be treated as proof of causal attribution.

### 7.6 Reporting Workflow

**Input:**

- Event dossier.
- Analysis version.
- Evidence references.
- Report template and version.

**Output:**

- Generated report content.
- Report generation metadata.
- Report-version creation request.

Report generation must not itself create an external publication or delivery operation. ReportVersionService creates the immutable report version and preserves its lineage.

### 7.7 Publication Decision and Review Workflow

**Input:**

- Generated report version.
- Publication policy configuration.
- Relevant evidence, provenance, security, and content-rights information.

**Output:**

- Immutable publication decision.
- Decision reasons and caveats.
- Review record when required.
- Next permitted workflow action.

A held report must be routed to a defined review mechanism. An authorized review outcome must be recorded, and a material outcome must produce a new effective publication decision. This workflow does not perform an external publication.

### 7.8 Publication Execution Workflow

**Input:**

- Report version.
- Effective publication decision for `PUBLISH` or `PUBLISH_WITH_CAVEATS`, when applicable.
- Publication target reference.
- Stable publication key identifying the logical publication slot within that target.
- Operation type: `PUBLISH`, `REPLACE`, or `WITHDRAW`.
- Earlier PublicationRecord reference for replacement or withdrawal.
- Stable idempotency key and required authorization context.

**Publication adapter contract:**

The target-specific adapter must expose the capabilities supported by its target through an explicit interface:

- `publish(request)` for a new publication.
- `replace(request)` where the target supports replacement semantics.
- `withdraw(request)` where the target supports removal or formal withdrawal.
- `get_status(request)` or an equivalent reconciliation operation where the target supports status lookup.

A request must include the logical operation identifier, idempotency key, target reference, publication key, report-version identity, and the exact authorized publication representation, including required caveats. It must not expose unrelated filesystem, shell, or secret-management capabilities.

The adapter result must distinguish confirmed success, confirmed failure, and unknown outcome. It should return an external publication reference and URL when available. An unsupported target capability must be reported explicitly; the application must not simulate a successful replacement or withdrawal.

**Output:**

- PublicationRecord.
- PublicationAttempt history.
- Confirmed external publication reference and URL where available.
- Operation outcome or reconciliation requirement.

The workflow must persist the logical operation before calling the external target. A replacement must not supersede the previous publication until success is confirmed. A withdrawal must not be marked complete until the target outcome is confirmed. An uncertain external outcome must be reconciled before another side-effecting attempt.

### 7.9 Delivery Workflow

**Input:**

- Report version.
- Delivery mode: report content, publication link, or notification.
- Delivery destination and recipient reference.
- PublicationRecord reference when delivering a publication link.
- Stable idempotency key.

**Output:**

- Delivery status.
- Delivery reference.
- Attempt metadata.

A publication-link delivery must reference a confirmed successful publication. Direct report-content delivery may occur independently when its distribution policy permits it. The workflow must prevent unintended duplicate delivery and must not change publication state.

### 7.10 Reprocessing Workflow

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
- `IMPORTANCE_ASSESSMENT_ERROR`
- `ECONOMIC_RELEVANCE_ASSESSMENT_ERROR`
- `IMPACT_ANALYSIS_ERROR`
- `REPORT_GENERATION_ERROR`
- `PUBLICATION_REJECTED`
- `PUBLICATION_ERROR`
- `PUBLICATION_OUTCOME_UNKNOWN`
- `WITHDRAWAL_ERROR`
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
- Publication adapters implement explicit publication-target contracts.
- Delivery adapters implement separate delivery contracts.
- Report generation does not depend on publication or delivery implementations.
- Publication policy does not depend on a specific delivery channel.
- Event matching does not directly manipulate database tables.
- EventService owns event-level business rules.
- EvidenceAnalyzer evaluates evidence but does not own persistence.
- ImportanceRanker, EconomicRelevanceAssessor, and ImpactAnalyzer produce separate assessment outputs; application workflows persist the corresponding versioned Analysis records.
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
- `event.importance_assessed`
- `event.economic_relevance_assessed`
- `event.economic_impact_assessed`
- `event.merged`
- `event.split`
- `evidence.assessed`
- `analysis.completed`
- `report.generated`
- `report.publication_decided`
- `report.publication_operation.started`
- `report.publication_operation.succeeded`
- `report.publication_operation.failed`
- `report.publication_operation.reconciliation_required`
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
- Assessment outcomes, methodology versions, and unknown/insufficient-data rates by assessment type.
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
- Multiple independent matching cases within one article revision.
- Candidate scores that must not be mistaken for final decisions.
- Human review producing a new immutable EventMatchDecision.
- Correcting and deactivating an ArticleEventLink without losing its history.
- Event identity preservation.
- Event merge and split history.
- Importance assessment behavior independently of economic relevance and impact.
- Economic relevance classification for direct, indirect, contextual, not-established, and unknown cases.
- Economic impact direction and magnitude assessment by channel with explicit evidence status.
- Separation of observed market reactions from event-causality conclusions.
- Claim and evidence traceability.
- Multiple claims linked to relevant evidence.
- Conflicting evidence handling.
- Source independence assessment.
- Publication policy enforcement.
- Review queue behavior.
- Publication execution only after an effective authorization decision.
- Publication idempotency and duplicate prevention.
- Publication replacement success and failure behavior.
- Publication withdrawal authorization and history.
- Reconciliation of uncertain external publication outcomes.
- Independent publication and delivery state transitions.
- Report version consistency.
- Report correction and withdrawal.
- Duplicate delivery prevention.
- Workflow recovery after interruption.
- Idempotent reprocessing.
- Cancellation and timeout propagation.
- LLM structured output validation.
- Prompt injection resistance tests.
- Budget and deadline enforcement.

Evaluation datasets must be used to measure classification, extraction, event matching, evidence assessment, importance ranking, economic relevance classification, channel-level economic impact assessment, and report quality. The evaluation methodology must report these results separately rather than combining them into one aggregate score.

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
- Separate economic relevance assessment.
- Channel-based economic impact analysis.
- Event dossier generation.
- Report generation and immutable versioning.
- Publication policy and immutable decisions.
- A defined review mechanism for held reports.
- Publication execution records and attempts for publish, replace, and withdraw operations.
- Text delivery with separate delivery records and attempts.
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
10. Market data integration and observed market-reaction classification.
11. Separate assessment semantics, methodology, calibration, and evaluation for importance, economic relevance, and economic impact (GENI-ADR-019).
12. SQLite concurrency and asynchronous persistence strategy.
13. Workflow recovery, idempotency, and retry guarantees.
14. LLM budget, cost tracking, and evaluation.
15. Source acquisition security and content retention.

The current individual ADR documents are listed in:

`docs/adr/README.md`

All nineteen registered decision topics currently have individual ADR documents in this pull-request branch. All nineteen remain Proposed; none is an accepted architectural decision until explicit Project Owner approval is recorded.

The ADR Registry is the authoritative inventory of document availability, status, priorities, and dependencies. The existence of an ADR file does not authorize implementation.

Until the relevant ADRs are accepted, these decisions remain proposed and must not be treated as approved implementation constraints.

## 18. Final Design Statement

The component architecture separates acquisition, article processing, event intelligence, evidence verification, economic analysis, report generation, publication, and delivery.

The system uses explicit interfaces and dependency inversion to keep the product modular, testable, and independent of specific providers.

Application workflows coordinate deterministic processing stages, while the Shared LLM Execution Layer provides controlled language-model capabilities.

The design preserves event identity, evidence provenance, historical traceability, controlled publication, and recoverable execution.

Future expansion must not compromise the simplicity, reliability, and explicit boundaries of the initial product release.