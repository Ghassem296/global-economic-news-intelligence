# Global Economic News Intelligence
## Product & System Architecture

**Document ID:** GENI-ARCH-001
**Version:** 1.1
**Status:** Draft — Under Architecture Review
**Project:** Global Economic News Intelligence
**Last Updated:** 2026-11-16

---

## 1. Purpose

This document defines the product architecture and high-level system design of Global Economic News Intelligence.

The system collects international economic news, identifies related developments, correlates articles into events, evaluates their significance, and generates structured intelligence reports.

The system is event-centric rather than article-centric.

Its primary objective is not simply to summarize individual news articles, but to develop an evidence-based understanding of important economic developments by combining information from multiple sources over time.

The initial product release focuses on text-based intelligence.

Audio and video generation are future product capabilities and must not introduce unnecessary complexity into the initial architecture.

This document establishes the architectural direction. Decisions that require formal approval through Architecture Decision Records (ADRs) remain provisional until their corresponding ADRs are accepted.

## 2. Product Vision

Global Economic News Intelligence is an automated economic news intelligence platform.

It continuously monitors international news sources and transforms unstructured news content into structured, traceable, and useful economic intelligence.

The platform should help users understand:

- What happened?
- What is changing?
- Why does it matter economically?
- Which countries, institutions, industries, and markets are affected?
- What evidence supports the reported development?
- What are the possible consequences?
- What remains uncertain?
- How has the situation evolved?

The platform prioritizes economic developments while monitoring political and geopolitical developments when they have meaningful economic implications.

The system must distinguish reported information, verified evidence, analytical interpretation, and forecasts.

## 3. Product Scope

### 3.1 Initial Product Release — Text Intelligence

The initial release includes:

- International news source management.
- Automated news collection.
- Article normalization and language identification.
- Article deduplication.
- Topic classification.
- Entity extraction.
- Claim extraction.
- Event detection and matching.
- Event lifecycle management.
- Evidence collection and source attribution.
- Economic relevance assessment.
- Economic impact analysis.
- Importance ranking.
- Event dossier generation.
- Structured text reports.
- Publication quality gates.
- Automated publication for eligible reports.
- Review handling for reports that cannot be safely published automatically.
- Basic monitoring, evaluation, and observability.

The initial release must be operationally simple and must not require audio, video, advanced personalization, or mandatory cloud infrastructure.

### 3.2 Future Product Releases

#### Release 2 — Audio

- Text-to-speech generation.
- Audio briefings.
- Scheduled economic news summaries.
- Audio report storage and delivery.

#### Release 3 — Video

- Automated video scripts.
- Visual asset selection.
- Charts and data visualizations.
- Video generation.
- Video publishing and delivery.

#### Release 4 — Advanced Intelligence

- User personalization.
- Advanced event forecasting.
- Historical event comparisons.
- Market and economic indicator integrations.
- Advanced alerting.
- Advanced multilingual capabilities.
- Personalized monitoring and delivery.

These capabilities must not become mandatory dependencies of the initial release.

Product releases describe user-facing capability increments. Development phases describe engineering execution steps. These two concepts must not be treated as interchangeable.

## 4. Product Principles

### 4.1 Event-Centric Intelligence

An article is an information source. An event is the subject of intelligence analysis.

Multiple articles may describe the same event.

An event may evolve over time and receive new information from additional articles.

The system must maintain a clear distinction between:

- Article identity.
- Event identity.
- Article-to-event relationships.
- Event history.
- Event analysis versions.

Event identity must remain stable when additional articles or analytical updates are associated with the event.

### 4.2 Economic Priority

Economic topics receive the highest product priority.

Political and geopolitical developments are included when they affect or may materially affect:

- Economic policy.
- International trade.
- Financial markets.
- Energy markets.
- Supply chains.
- Public debt.
- Monetary policy.
- Industrial activity.
- Economic stability.

### 4.3 Source Traceability

Every factual statement in a published report must be traceable to one or more source articles or evidence records, to the extent supported by the available source material.

The system must preserve:

- Original source identity.
- Article URL and canonical URL when available.
- Publication time, when available.
- Collection time.
- Original source language.
- Available source content and its permitted storage representation.
- Relevant source claims.
- Evidence references.
- Processing and analytical history.

A generated statement must not be presented as an independently verified fact merely because an LLM generated it.

### 4.4 Controlled Automation

The target operating mode is automatic processing and publication.

Automation does not mean treating every generated conclusion as verified.

The system must distinguish:

- Directly supported facts.
- Source-attributed claims.
- Independently corroborated claims.
- Conflicting information.
- AI-generated interpretation.
- Forecasts and uncertain scenarios.

Reports that do not satisfy publication requirements must be held, rejected, or published with explicit caveats according to the publication policy.

A held report must have a defined review destination and an observable review state. A review outcome must be recorded before the report can proceed to publication or rejection.

### 4.5 Provider Independence

Business logic must not depend on a specific LLM provider, news provider, database engine, or delivery channel.

Provider integrations must be replaceable through explicit interfaces.

### 4.6 Workflow-First Execution

The product is primarily a deterministic, workflow-driven intelligence system.

Its processing stages, state transitions, and publication rules must be explicitly defined.

LLM-based reasoning is used for tasks that benefit from language understanding and analytical synthesis.

General-purpose autonomous agent behavior must not be introduced without a clearly justified product requirement.

## 5. System Architecture

The system consists of the following major subsystems:

1. Source Management
2. News Acquisition
3. News Processing
4. Event Intelligence
5. Event Management
6. Evidence and Verification
7. Shared LLM Execution Layer
8. Analysis and Scoring
9. Report Generation
10. Publication and Delivery
11. Scheduling and Workflow Orchestration
12. Platform Services

Subsystem boundaries must remain explicit. Detailed contracts and data ownership are defined in the Component Architecture and Data Model documents.

### 5.1 Source Management

Responsibilities:

- Register news sources.
- Store source metadata.
- Configure collection methods.
- Define source reliability metadata.
- Enable or disable sources.
- Track collection health.
- Manage source-specific collection policies.
- Record access restrictions and known content limitations.
- Maintain source language and geographic coverage metadata.

Source types may include:

- RSS feeds.
- Public news APIs.
- Licensed news APIs.
- Approved web sources.
- Other explicitly supported providers.

The source registry must not assume that every source supports the same collection mechanism.

Source reliability must be treated as an assessed attribute with a documented methodology, not as an unquestionable fact.

### 5.2 News Acquisition

Responsibilities:

- Schedule collection jobs.
- Fetch new articles.
- Handle pagination and feed updates.
- Track collection checkpoints.
- Handle transient network failures.
- Respect source-specific access restrictions.
- Preserve original article references.
- Record collection metadata.
- Apply URL and network security controls.
- Identify incomplete or unavailable article content.

Collection should be incremental whenever the source supports it.

Near-real-time operation means frequent scheduled collection and processing. It does not guarantee instantaneous delivery.

Acquisition must distinguish between:

- Article metadata.
- Article title and snippet.
- Retrieved article text.
- Licensed or otherwise authorized full text.
- Content that is unavailable or restricted.

Technical accessibility does not imply permission to store, reproduce, or republish content.

The system must follow applicable source terms, licenses, and content restrictions. Full-text acquisition and retention policies require a separate documented decision.

External URL fetching must use defensive controls against server-side request forgery (SSRF), unsafe redirects, private network access, oversized responses, and excessive connection times.

### 5.3 News Processing

Responsibilities:

- Normalize incoming articles.
- Extract canonical URLs.
- Normalize timestamps.
- Identify source language.
- Preserve original language and content references.
- Remove irrelevant or unusable content.
- Detect duplicate and near-duplicate articles.
- Classify topics.
- Extract entities and entity references.
- Extract candidate claims.
- Extract relevant economic indicators and quantities when available.
- Record processing outcomes and confidence.

Article deduplication and event matching are separate operations.

Article deduplication identifies repeated or substantially equivalent publications. Event matching determines whether different articles describe the same real-world development.

The processing system must support multilingual source content from the initial release. Language identification and preservation of the original content are initial-release requirements.

Translation may be used as an intermediate processing aid, but translated text must not silently replace the original source content.

### 5.4 Event Intelligence

Responsibilities:

- Identify candidate events.
- Match articles to existing events.
- Detect new event developments.
- Evaluate event continuity.
- Identify possible event relationships.
- Recommend event creation, association, merging, or splitting.
- Evaluate economic relevance.
- Identify material changes in event understanding.

Event matching must not rely exclusively on exact text similarity or an LLM judgment.

The intended architecture is a hybrid approach combining:

- Deterministic matching rules.
- Entity and attribute comparisons.
- Temporal and geographic context.
- Textual similarity.
- Semantic similarity where appropriate.
- Confidence evaluation.
- Explicit decision thresholds.

A new article must not automatically create a new event merely because its wording differs from previously collected articles.

Likewise, similar wording alone must not cause unrelated developments to be merged.

Event matching decisions must preserve the ability to review ambiguous cases and correct earlier associations.

The detailed event identity, matching, merge, split, and semantic retrieval policy belongs in the Event Intelligence and Correlation Specification and the corresponding ADRs.

### 5.5 Event Management

Responsibilities:

- Create events.
- Maintain stable event identity.
- Associate articles with events.
- Maintain event timelines.
- Track event lifecycle status.
- Record material changes in event understanding.
- Manage event relationships.
- Identify event resolution.
- Preserve event history and analytical revisions.

An event must remain identifiable even when its source articles, evidence, or analysis are updated.

Event lifecycle status must be separated from event history.

A material update is a recorded event-history occurrence, not necessarily a persistent lifecycle status.

### 5.6 Evidence and Verification

Responsibilities:

- Maintain evidence records.
- Link evidence to claims.
- Track source attribution.
- Identify corroborating sources.
- Identify contradictory claims.
- Assess source independence.
- Preserve verification status.
- Record the basis of verification decisions.

The system must not treat multiple articles repeating the same original claim as independent corroboration.

Evidence records must preserve their origin and relationship to the relevant source material.

The system must distinguish:

- A claim made by a source.
- Evidence directly available in source material.
- Independent corroboration.
- Contradictory evidence.
- An analytical conclusion derived from evidence.

Claim extraction and evidence verification are separate responsibilities.

Article Processing extracts candidate claims from individual articles. Evidence and Verification evaluates and relates those claims across articles and other permitted evidence sources.

Where technically feasible, factual report statements should retain sentence-level or claim-level provenance references.

The system must not imply that a statement is fully verified when its supporting material is incomplete or unavailable.

### 5.7 Shared LLM Execution Layer

The Shared LLM Execution Layer provides reusable LLM integration capabilities without introducing a general-purpose conversational Agent architecture into the product.

Responsibilities:

- Provider-independent model invocation.
- Structured output validation.
- Model and task configuration.
- Input and output token accounting.
- Per-run and per-task budget enforcement.
- Deadline enforcement.
- Bounded retries for appropriate transient failures.
- Cancellation propagation.
- Provider error normalization.
- Usage and cost recording when available.
- Prompt and model version tracking.

Business workflows must call this layer through explicit interfaces.

The layer must not own economic news domain logic, event identity, article processing state, or publication policy.

LLM outputs are untrusted until validated against the required schema and business rules.

Autonomous tool execution, general conversation memory, MCP integration, and conversational agent loops are not initial-release requirements. They may be introduced only through a documented requirement and an accepted architectural decision.

### 5.8 Analysis and Scoring

Responsibilities:

- Evaluate event importance.
- Evaluate economic relevance.
- Analyze potential economic consequences.
- Identify affected countries, institutions, industries, and markets.
- Identify risks and uncertainties.
- Separate observed information from inferred conclusions.
- Maintain analytical versions and methodology references.

Importance and economic impact are separate concepts.

Importance measures the overall significance of an event.

Economic impact describes the nature and potential magnitude of its economic consequences.

Analysis must distinguish at least three categories of market and economic impact:

1. **Observed Market Reaction:** A reaction supported by actual market data available to the system.
2. **Source-Reported Reaction:** A reaction reported by a news source but not independently verified by integrated market data.
3. **AI-Inferred Economic Impact:** A potential or expected consequence inferred from available evidence and analytical reasoning.

The system must not describe an inferred impact as an observed market reaction.

In the absence of reliable market data, the system may describe possible economic consequences but must explicitly identify them as analytical assessments.

Scoring dimensions may include:

- Geographic scope.
- Number and significance of affected entities.
- Institutional significance.
- Market relevance.
- Time sensitivity.
- Magnitude of development.
- Potential duration.
- Economic transmission channels.

Scoring methodology, scales, calibration, thresholds, and versioning must be formally specified and evaluated.

Unknown or unavailable information must not automatically be interpreted as zero impact or zero importance.

### 5.9 Report Generation

Responsibilities:

- Build structured event dossiers.
- Generate concise summaries.
- Explain economic significance.
- Present affected entities and markets.
- Include supporting evidence.
- Express uncertainty.
- Separate facts, source claims, analysis, and forecasts.
- Produce immutable report versions.
- Preserve references to the analysis and evidence used to generate each version.

Reports must be reproducible to the extent supported by retained inputs, model configuration, prompts, and processing metadata.

A revised report must create a new version rather than silently overwriting the previously generated content.

### 5.10 Publication and Delivery

Responsibilities:

- Evaluate publication eligibility.
- Apply publication quality gates.
- Publish eligible reports.
- Route held reports to a review queue.
- Record review outcomes.
- Distribute event updates.
- Prevent duplicate publication.
- Maintain delivery status.
- Support corrections and withdrawals.
- Support future delivery channels.

Publication and delivery are separate responsibilities.

A report may be generated without being approved for publication.

The publication policy must support:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

A held report must be associated with a review record or queue entry containing its status, reason, timestamps, and eventual outcome.

The initial implementation must define who or what consumes the review queue. If no human reviewer is available, the system must not silently publish held content.

Published reports must support correction, supersession, and withdrawal. Previous versions and publication history must remain traceable.

Delivery operations must be idempotent so that retries do not produce unintended duplicate publications.

### 5.11 Scheduling and Workflow Orchestration

Responsibilities:

- Schedule source collection.
- Start processing workflows.
- Track job execution.
- Manage checkpoints.
- Enforce concurrency limits.
- Handle retries and deadlines.
- Support cancellation.
- Recover interrupted work.
- Record execution outcomes.
- Prevent unintended duplicate processing.

Workflow orchestration must separate job state from domain state.

A failed processing job must not automatically imply that an article or event is invalid.

The system must support safe reprocessing when extraction, classification, matching, or analysis logic changes.

Operations that may be retried must have defined idempotency behavior.

The initial scheduler and orchestration implementation should avoid unnecessary distributed infrastructure.

### 5.12 Platform Services

Responsibilities:

- Application configuration.
- Persistence.
- Logging.
- Tracing and metrics.
- Health checks.
- Runtime lifecycle.
- Backup and recovery support.
- Operational monitoring.
- Secret management.

The initial deployment should avoid unnecessary infrastructure dependencies.

The persistence implementation must remain behind repository and infrastructure interfaces.

## 6. High-Level Data Flow

The main processing pipeline is:

1. Source collection scheduling.
2. Article acquisition.
3. Article normalization.
4. Language identification.
5. Article deduplication.
6. Topic classification.
7. Entity extraction.
8. Candidate claim extraction.
9. Candidate event detection.
10. Event matching.
11. Event association or new event creation.
12. Evidence enrichment and verification.
13. Event importance assessment.
14. Economic impact analysis.
15. Event dossier generation.
16. Publication policy evaluation.
17. Review routing when required.
18. Report publication and delivery.
19. Event monitoring and subsequent updates.

The pipeline must support controlled reprocessing when classification, extraction, matching, scoring, or analysis logic changes.

Reprocessing must preserve historical outputs and must not silently overwrite previously published reports.

## 7. Event-Centric Domain Model

The primary domain entities include:

- Source
- Article
- ArticleProcessingRecord
- Event
- ArticleEventLink
- Entity
- EntityAlias
- Claim
- Evidence
- Analysis
- Report
- PublicationDecision
- ReviewRecord
- DeliveryRecord
- ProcessingRun
- EventHistory

Additional entities may be introduced when justified by explicit requirements.

### 7.1 Article

Represents one collected publication.

An article preserves source identity, publication metadata, collection metadata, language information, and permitted content references.

Article identity is independent of event identity.

### 7.2 Event

Represents a real-world development or a connected sequence of developments.

An event may be associated with multiple articles.

Event identity must be stable and must not be derived solely from a headline or article URL.

### 7.3 ArticleEventLink

Represents the relationship between an article and an event.

The relationship may include:

- Relevance.
- Association confidence.
- Relationship type.
- Association timestamp.
- Matching method and version.
- Review or correction metadata where applicable.

An article may be associated with more than one event when justified.

### 7.4 Claim and Evidence

A Claim represents an assertion extracted from or attributed to a source, or an analytical assertion generated by the system.

An Evidence record represents material used to support, qualify, or contradict a claim.

Claims and evidence must preserve source attribution and provenance.

A source claim is not automatically an established fact.

### 7.5 Analysis

Represents a versioned analytical assessment of an event.

An analysis must identify its relevant evidence, methodology, model configuration where applicable, and uncertainty.

### 7.6 Event Dossier

An event dossier is a structured representation of the current understanding of an event.

It includes:

- Event summary.
- Timeline.
- Related articles.
- Entities.
- Claims.
- Evidence.
- Economic relevance.
- Impact analysis.
- Importance.
- Uncertainty.
- Current lifecycle status.
- Analysis history.
- Report history.

## 8. Economic Topic Taxonomy

The initial taxonomy includes:

| Category | Description |
|---|---|
| Monetary Policy | Central banks, interest rates, inflation policy |
| Financial Markets | Equities, bonds, currencies, credit, liquidity |
| Macroeconomics | GDP, inflation, employment, growth, recession |
| Trade & Industry | International trade, tariffs, manufacturing, supply chains |
| Energy & Resources | Oil, gas, electricity, commodities, critical minerals |
| Fiscal Policy & Public Debt | Government budgets, taxation, sovereign debt |
| Geopolitical Economic Risk | Sanctions, conflict, political instability affecting economies |

The taxonomy must be extensible.

An article may have multiple topic classifications, each with an associated confidence and classification methodology.

Classification results must be versioned so that changes in taxonomy or classification logic can be evaluated and reprocessed.

## 9. Importance and Economic Impact

Importance and economic impact are separate concepts.

**Importance** measures the overall significance of an event.

**Economic impact** describes the nature and potential magnitude of its economic consequences.

Importance dimensions may include:

- Geographic scope.
- Number of affected entities.
- Institutional significance.
- Market relevance.
- Time sensitivity.
- Development magnitude.
- Potential duration.

Economic impact dimensions may include:

- Inflation.
- Interest rates.
- Currency.
- Trade.
- Energy.
- Employment.
- Public finance.
- Financial stability.
- Industrial production.

The system must distinguish measured data from qualitative analysis and model-generated estimates.

Scoring must have a documented scale, methodology, version, and evaluation process.

Scores must not imply a level of precision unsupported by the available evidence.

Missing information must be represented as unknown or unavailable rather than automatically converted to zero.

## 10. Event Lifecycle

The event lifecycle uses persistent business states:

- `DETECTED`
- `ENRICHING`
- `ACTIVE`
- `MONITORING`
- `RESOLVED`
- `ARCHIVED`

Definitions:

- `DETECTED`: A candidate event has been identified but has not yet passed the required enrichment and validation stages.
- `ENRICHING`: Relevant articles, entities, claims, and evidence are being collected and evaluated.
- `ACTIVE`: The event is sufficiently established and remains ongoing.
- `MONITORING`: No major new development is currently available, but the event remains relevant and may change.
- `RESOLVED`: The event has reached a meaningful conclusion according to its domain-specific resolution criteria.
- `ARCHIVED`: The event is retained primarily for historical reference.

Not every event must pass through every state.

State transitions must be validated against an explicit transition policy.

`UPDATED` is not a persistent lifecycle state. It represents a material event-history occurrence that records a significant change in the event's information, evidence, or analytical understanding.

Event history must preserve relevant transitions, updates, corrections, and resolution information.

The complete transition rules and event identity policy require formal specification.

## 11. Publication Policy

Every generated report receives a publication decision.

| Decision | Meaning |
|---|---|
| `PUBLISH` | Sufficient quality and evidence for publication |
| `PUBLISH_WITH_CAVEATS` | Publish with explicit limitations or uncertainty |
| `HOLD_FOR_REVIEW` | Do not publish automatically; route to review |
| `REJECT` | Invalid, irrelevant, or insufficiently useful output |

Publication decisions should consider:

- Evidence quality.
- Source diversity.
- Source independence.
- Source reliability.
- Claim consistency.
- Event confidence.
- Analysis completeness.
- Duplicate publication risk.
- Report validity.
- Provenance completeness.
- Security and content-policy checks.

Publication decisions must be recorded independently of report content and delivery outcomes.

A held report must remain unpublished until an authorized review outcome permits further action.

A rejected report must retain its decision and reason for auditability.

Published reports must support correction, supersession, and withdrawal.

Automatic publication must never bypass security, quality, or provenance requirements.

## 12. Report Structure

A text event report should contain:

1. Headline.
2. Executive Summary.
3. What Happened?
4. Latest Developments.
5. Timeline.
6. Key Entities.
7. Economic Significance.
8. Potential Market and Sector Impact.
9. Supporting Evidence.
10. Conflicting or Unconfirmed Information.
11. Risks and Uncertainties.
12. Analytical Assessment.
13. Sources.

Each report must identify:

- Publication time.
- Report version.
- Event identity.
- Analysis version.
- Relevant source references.
- Publication decision.
- Applicable caveats.

Forecasts and scenarios must be explicitly labeled.

The language of the report is a product-level output policy and must not be confused with the original language of source articles.

The initial product output language is English.

## 13. Persistence Strategy

SQLite is the proposed initial persistence implementation.

Reasons include:

- Low operational complexity.
- Local development support.
- Suitability for an initial single-instance deployment.
- Simple backup and migration workflows.

The SQLite decision remains subject to formal approval through its ADR.

Persistence must be accessed through repository interfaces.

The domain model must not depend directly on SQLite.

PostgreSQL may be introduced later if justified by concurrency, deployment, operational, or scaling requirements.

The initial persistence design must explicitly address:

- SQLite journal mode and write concurrency.
- Busy timeout and transaction boundaries.
- The selected asynchronous database access approach.
- Database migration management.
- Backup and restore procedures.
- Recovery after interrupted jobs.
- Idempotent processing and delivery.

Raw article content, normalized metadata, event records, evidence, analysis, reports, publication decisions, review records, delivery records, and processing history must have explicit persistence responsibilities.

Content retention and full-text storage must comply with applicable access rights, source terms, and licensing restrictions.

## 14. Non-Functional Requirements

### 14.1 Reliability

- Collection failures must not corrupt existing records.
- Processing should be restartable.
- Duplicate ingestion must be controlled.
- Retried operations must have defined idempotency behavior.
- Interrupted jobs must be recoverable.
- Failed operations must have observable outcomes.
- Previously published reports must not be silently overwritten.

### 14.2 Performance

- Collection and processing should use bounded asynchronous concurrency.
- Large article content must not be passed indiscriminately to LLMs.
- Event processing should avoid unnecessary repeated analysis.
- LLM execution must enforce deadlines and resource budgets.
- Expensive semantic operations should be performed selectively.

### 14.3 Security

- Secrets must not be stored in source control.
- External content is untrusted.
- URL acquisition must defend against SSRF and unsafe redirects.
- External content must be treated as data, never as trusted instructions.
- LLM analysis stages must not receive unrestricted tool execution.
- Structured output must be validated before use.
- Source access must follow applicable terms and restrictions.
- Access to publication and review operations must be controlled.

Prompt injection defenses must include strict separation between instructions and retrieved content, constrained output schemas, and least-privilege execution.

### 14.4 Observability

The system must track:

- Collection success and failure.
- Processing duration.
- Article ingestion volume.
- Duplicate and near-duplicate rates.
- Classification outcomes.
- Event detection volume.
- Event matching confidence and outcomes.
- Event creation, merge, and split operations.
- Evidence and verification outcomes.
- Publication decisions.
- Review queue status and age.
- LLM usage and cost when known.
- Retry and recovery outcomes.
- Report delivery outcomes.

### 14.5 Maintainability

- Domain logic must be independent of infrastructure.
- Components must have explicit interfaces.
- Provider integrations must be replaceable.
- Tests must not require paid external services.
- Business workflows must remain independently testable.
- Architectural decisions must be documented and traceable.

### 14.6 Traceability

Every published report must be traceable to its event, analysis, evidence, and source articles.

The system must preserve the provenance of source claims and analytical conclusions.

Where a statement cannot be supported by retained evidence, the report must communicate the limitation.

### 14.7 Evaluation

Evaluation must begin with the first end-to-end implementation slice.

The system must establish evaluation procedures for:

- Article deduplication.
- Topic classification.
- Entity extraction.
- Claim extraction.
- Event matching.
- Evidence attribution.
- Importance assessment.
- Publication decisions.
- Report quality.

Evaluation datasets, acceptance thresholds, and regression procedures must be documented separately and incorporated into development milestones.

## 15. Development Phases

Development phases describe engineering execution and are separate from product release numbers.

The detailed development roadmap is maintained in the Implementation Plan and Development Roadmap document.

The high-level implementation sequence is:

### Development Phase A — Foundation and First End-to-End Slice

- Project structure and configuration.
- Domain boundaries and core interfaces.
- Initial persistence.
- Source registration.
- Basic news acquisition.
- A minimal processing workflow.
- Initial LLM execution integration.
- A small end-to-end path from source article to traceable draft report.
- Initial evaluation and observability.

### Development Phase B — Core News Intelligence

- Article normalization.
- Language identification.
- Deduplication.
- Topic classification.
- Entity extraction.
- Claim extraction.
- Event detection and matching.
- Event lifecycle and history.
- Evidence management.
- Event matching evaluation.

### Development Phase C — Analysis and Publication

- Importance assessment.
- Economic impact analysis.
- Event dossier generation.
- Publication quality gates.
- Review handling.
- Report versioning.
- Delivery and duplicate-publication prevention.
- Corrections and withdrawal support.

### Development Phase D — Operational Readiness

- Recovery and reprocessing.
- Security validation.
- Backup and restore.
- Cost controls.
- Regression evaluation.
- Deployment and operational monitoring.

The exact phase boundaries, dependencies, and acceptance criteria are governed by the development roadmap.

## 16. Initial Release Acceptance Criteria

The initial release is functionally complete when the following capabilities are demonstrated through repeatable tests:

1. Sources can be registered, configured, enabled, and disabled.
2. Articles can be collected from supported source types.
3. Acquisition records preserve source identity and collection timestamps.
4. Article content availability and access limitations are represented explicitly.
5. Articles are normalized consistently.
6. Original source language is identified and preserved.
7. Duplicate and near-duplicate articles can be detected according to the approved deduplication policy.
8. Articles can be classified using the approved economic taxonomy.
9. Entities and aliases can be extracted and associated with articles.
10. Candidate claims can be extracted with source attribution.
11. Related articles can be associated with existing events using the approved event matching policy.
12. Ambiguous event matches can be identified rather than silently forced into an incorrect association.
13. Events maintain stable identity across updates.
14. Event history records material changes and lifecycle transitions.
15. Claims and evidence are traceable to source material.
16. Reports distinguish source claims, supported facts, analysis, and forecasts.
17. Economic significance is explicitly evaluated.
18. Importance assessment uses a documented and versioned methodology.
19. Market reactions are not presented as observed without supporting market data.
20. Publication policy is enforced.
21. Held reports are routed to a defined review mechanism.
22. Reports can be generated, versioned, corrected, and withdrawn.
23. Reports can be delivered without unintended duplicate publication.
24. Processing failures and recovery operations are observable.
25. The system can restart without corrupting existing data.
26. Reprocessing does not silently overwrite historical analytical or publication records.
27. LLM execution respects configured budgets, deadlines, and output validation.
28. External content is handled as untrusted input.
29. The initial system operates without mandatory distributed or cloud infrastructure.

Quantitative acceptance thresholds for extraction quality, event matching, classification, and report quality must be established in the evaluation specification before the relevant capabilities are considered production-ready.

## 17. Architectural Constraints

The implementation must preserve these constraints:

- The system is event-centric.
- Article identity and event identity remain separate.
- Article deduplication and event matching remain separate operations.
- Core business logic is provider-independent.
- Processing is workflow-first and deterministic wherever practical.
- LLM reasoning is used selectively and through a shared execution boundary.
- External content is untrusted.
- Evidence provenance is mandatory.
- Reports and analyses are versioned.
- Publication is subject to explicit quality gates.
- Held reports must not be silently published.
- Event lifecycle state is separate from event-history occurrences.
- Processing state is separate from domain state.
- Phase 1 is text-only.
- Original source language and content references are preserved.
- SQLite is the proposed initial database implementation, not a domain-level dependency.
- Full-text acquisition and storage must respect applicable rights and restrictions.
- Advanced infrastructure is deferred until justified by requirements.

## 18. Architecture Governance and Open Decisions

The following decisions must be formally reviewed and recorded through ADRs before the corresponding implementation choices are treated as approved:

1. Workflow-first architecture and the scope of the shared LLM execution layer.
2. Event identity, matching, creation, merging, and splitting.
3. Article deduplication and event correlation separation.
4. Semantic search, embedding generation, and vector storage.
5. News acquisition, full-text access, content retention, and licensing.
6. Publication quality gates, human review, correction, and withdrawal.
7. Market data integration and market-impact classification.
8. Persistence technology, SQLite concurrency, and migration strategy.
9. Recovery, idempotency, and workflow execution guarantees.
10. LLM budgets, cost tracking, and evaluation methodology.

Until the relevant ADRs are accepted, related architectural statements in this document represent the current proposed direction rather than formally approved implementation decisions.

The ADR registry is maintained in `docs/adr/README.md`.

## 19. Final Architecture Statement

Global Economic News Intelligence is an event-centric, workflow-first economic news intelligence platform.

It transforms international news into structured, evidence-based event dossiers and automated text reports.

The architecture prioritizes:

- Economic relevance.
- Stable event identity.
- Evidence provenance.
- Source transparency.
- Controlled automation.
- Provider independence.
- Reproducible processing.
- Operational simplicity.
- Incremental extensibility.

The initial implementation must remain operationally simple while preserving clear boundaries for future audio, video, analytics, market-data integrations, and advanced intelligence capabilities.

The system must never confuse a source claim with an established fact, an analytical inference with an observed market reaction, or an automated output with verified truth.