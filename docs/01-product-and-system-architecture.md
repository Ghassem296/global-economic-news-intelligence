# Global Economic News Intelligence
## Product and System Architecture

**Document ID:** GENI-ARCH-001  
**Version:** 1.11  
**Status:** Draft — Under Architecture Review  
**Project:** Global Economic News Intelligence  
**Last Updated:** 2026-11-18

---

## 1. Purpose

This document defines the product architecture and high-level system design of Global Economic News Intelligence (GENI).

The system collects international economic news, identifies related developments, correlates articles into events, evaluates their significance, and generates structured intelligence reports.

The system is event-centric rather than article-centric.

Its primary objective is not simply to summarize individual news articles, but to develop an evidence-based understanding of important economic developments by combining information from multiple sources over time.

The initial product release focuses on text-based intelligence.

Audio and video generation are future product capabilities and must not introduce unnecessary complexity into the initial architecture.

This document establishes the proposed architectural direction. Architectural decisions requiring formal approval through Architecture Decision Records (ADRs) remain provisional until their corresponding ADRs are accepted.

## 2. Product Vision

Global Economic News Intelligence is an automated economic news intelligence platform.

It monitors international news sources and transforms unstructured news content into structured, traceable, and useful economic intelligence.

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
- Importance assessment.
- Event dossier generation.
- Structured text reports.
- Publication quality gates.
- Automated publication for eligible reports.
- Review handling for reports that cannot be safely published automatically.
- Basic monitoring, evaluation, and observability.

The initial release must remain operationally simple and must not require audio, video, advanced personalization, or mandatory cloud infrastructure.

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

Product releases describe user-facing capability increments. Development phases describe engineering execution steps. These concepts must not be treated as interchangeable.

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

Event identity must remain stable when additional articles or analytical updates are associated with an event.

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

Every factual statement in a published report must be traceable to one or more source articles or evidence records, to the extent supported by available source material.

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

The target operating mode is automatic processing and publication for reports that satisfy defined requirements.

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

General-purpose autonomous agent behavior must not be introduced without a clearly justified product requirement and an accepted architectural decision.

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

Subsystem boundaries must remain explicit.

Detailed component responsibilities, interface contracts, and data ownership are defined in:

- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`

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

The system must follow applicable source terms, licenses, and content restrictions.

Full-text acquisition and retention policies are governed by the relevant content-access ADR and applicable project requirements.

External URL fetching must use defensive controls against:

- Server-side request forgery (SSRF).
- Unsafe redirects.
- Private network access.
- Oversized responses.
- Excessive connection times.

### 5.3 News Processing

Responsibilities:

- Normalize incoming articles.
- Create immutable ArticleRevision records for material content changes and maintain the Article current projection atomically.
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

Article deduplication identifies repeated or substantially equivalent publications.

Event matching determines whether different articles describe the same real-world development.

The processing system must support multilingual source content from the initial release. Language identification and preservation of original content are initial-release requirements.

Translation is optional and may be used only under an approved language policy and applicable content-rights authorization. When enabled, it must create a separately versioned derived artifact linked to the exact ArticleRevision, preserving source/output languages, translator/provider and model/configuration provenance, and quality status. Translated text must never replace the original source revision. Cross-language matching must not depend on an unsupported or unevaluated translation.

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

The proposed approach is a hybrid method combining:

- Deterministic matching rules.
- Entity and attribute comparisons.
- Temporal and geographic context.
- Textual similarity.
- Semantic similarity through a replaceable candidate-retrieval adapter where appropriate.
- Confidence evaluation.
- Explicit decision thresholds.

Semantic retrieval is optional and must be evaluated against a lexical baseline. Its adapter may generate candidates but must never make the final event decision or create an article-event association. Embedding provider/storage and quantitative thresholds remain subject to GENI-ADR-012 and must not be assumed approved while that ADR is Proposed.

A new article must not automatically create a new event merely because its wording differs from previously collected articles.

Likewise, similar wording alone must not cause unrelated developments to be merged.

Event matching decisions must preserve the ability to review ambiguous cases and correct earlier associations.

Detailed event identity, matching, continuation, merging, and splitting policies are governed by the corresponding ADRs and the component and data-model specifications.

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

Autonomous tool execution, general conversation memory, MCP integration, and conversational agent loops are not initial-release requirements.

They may be introduced only through a documented requirement and an accepted architectural decision.

### 5.8 Analysis and Scoring

Responsibilities:

- Assess the overall importance of an event.
- Assess the event's economic relevance independently of its overall importance.
- Analyze the nature, direction, scale, and timing of potential or realized economic consequences.
- Identify affected countries, institutions, industries, sectors, and markets.
- Identify economic transmission mechanisms, risks, and uncertainties.
- Distinguish observed outcomes, source-reported effects, analytical inferences, and forecasts.
- Maintain separate versioned assessment results and methodology references.

The system must produce three distinct assessments. They answer different questions and must not be collapsed into one score.

**Event Importance** answers: *How significant is this event overall, and how much attention or monitoring priority does it warrant?*

Importance concerns the event's overall significance and urgency. It may consider institutional significance, geographic and population scope, novelty or materiality, time sensitivity, and expected duration. It is not a measurement of economic relevance, the magnitude of economic consequences, or the probability that a forecast will occur.

**Economic Relevance** answers: *How directly and materially is this event connected to economic activity, policy, institutions, or markets?*

Economic relevance evaluates the existence and strength of plausible economic transmission pathways. It identifies whether the connection is direct, indirect, contextual, not established, or unknown. It does not measure the size, direction, or certainty of the resulting economic effect.

**Economic Impact** answers: *What economic consequences have occurred or may occur, through which channels, with what direction, magnitude, and time horizon?*

Economic impact evaluates consequences across relevant channels such as inflation, interest rates, growth, employment, currencies, trade, energy, public finance, industrial production, and financial stability. It must distinguish potential from realized effects and describe affected entities, geography, direction, magnitude, duration, and uncertainty where supported.

A high-importance event may have low or unestablished economic relevance. An event may be highly economically relevant even when its eventual impact is not yet known. A material economic impact must not be inferred solely from a high importance or relevance assessment.

The system must distinguish at least the following evidence states for economic effects:

1. **Observed Economic Effect:** An outcome supported by an identified economic or market data source.
2. **Source-Reported Effect:** An effect described by a source but not independently confirmed by the system's integrated data.
3. **Inferred Potential Effect:** A possible consequence derived through explicit analytical reasoning and evidence.
4. **Unknown:** Available information is insufficient to characterize the effect.

Observed market reaction is a narrower concept than economic impact. A measured price or yield movement may be an observed market reaction, but the movement's causal relationship to an event remains a separate analytical question. Market observations must not be treated as proof that the event caused the observed movement. Market-data acquisition is optional: provider, instrument universe, frequency, licensing, and retention remain subject to GENI-ADR-015. Without an authorized and suitable observation source, market reaction must remain unknown/unavailable rather than inferred as measured.

Importance, economic relevance, and economic impact must be stored and evaluated as separate versioned assessment results. A single composite score must not silently combine them. Numeric scores are optional and may be used only when their scale, direction, methodology, version, calibration, and evaluation criteria are explicit. Qualitative levels and structured dimensions may be more appropriate than a single number.

Assessment confidence, forecast probability, economic-effect magnitude, and overall importance are different quantities. They must not share a field or be described as interchangeable. Missing or unavailable information must remain unknown rather than being converted to zero, neutral impact, or low importance.

Assessment methodologies, scales, calibration, thresholds, and acceptance criteria require formal specification and evaluation before they are used for automated production ranking or publication decisions.

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

A revised report must create a new version rather than silently overwriting previously generated content.

### 5.10 Publication and Delivery

Responsibilities:

- Evaluate publication eligibility.
- Apply publication quality and security gates.
- Execute approved publication, replacement, and withdrawal operations.
- Route held reports to an operational review queue.
- Preserve publication-operation and attempt history.
- Distribute reports or notifications through separate delivery operations.
- Prevent unintended duplicate publication and delivery.
- Record external publication and delivery references.
- Support corrections, supersession, and withdrawal.
- Support future publication targets and delivery channels.

Publication and delivery are separate business operations with separate records, state transitions, retry policies, and observability.

**Publication** makes an approved report version available at a configured publication target, such as a public website, public API, or public content feed. A channel must be explicitly classified as a publication target when it makes content publicly or generally available.

**Delivery** sends a report, a publication link, or a notification to a configured recipient or delivery destination, such as an email recipient or subscriber channel. A destination may support more than one operation, but each operation must be classified and recorded separately.

A publication decision is an authorization outcome, not proof that publication occurred. A report is considered published at a target only when a corresponding publication operation has a confirmed successful result.

The publication policy must support:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

A held report must be associated with a review record or queue entry containing its status, reason, timestamps, and eventual outcome. An authorized review outcome must be recorded. Approval after review must result in a new publication decision; the earlier decision and review history must not be overwritten.

The publication execution workflow must create a durable publication-operation record before making an external side effect. The operation must identify the report version, publication target, stable publication key (the logical publication slot within that target), operation type, applicable publication decision, and idempotency key. Each external attempt must be recorded separately. A single target may host many independent publication keys; replacement and withdrawal must operate only within the referenced key.

Publication operations must distinguish:

- `PUBLISH`: make an approved report version available at a target.
- `REPLACE`: publish a corrected or superseding report version in place of an earlier publication.
- `WITHDRAW`: remove or formally withdraw an existing publication where the target supports it.

A replacement must reference the earlier publication it supersedes and use the same publication target and publication key. The previous publication remains the effective publication for that key until the replacement is confirmed successful. A failed replacement must not silently invalidate the previous publication.

A withdrawal must reference the publication being withdrawn and preserve its reason and authorization context. If a target cannot physically remove content, the system must record the limitation and apply the approved withdrawal or tombstone procedure.

A timeout or connection failure must not be assumed to mean that an external publication failed. When the target outcome is uncertain, the operation must enter reconciliation before another side-effecting attempt is made. Retries must reuse the same logical operation and idempotency key.

Delivery must remain independent from publication. A delivery failure must not reverse a successful publication, and a successful delivery must not imply that a public publication exists. A delivery that sends a publication link must reference a confirmed successful publication operation. Direct delivery of report content may be allowed independently when the relevant delivery policy authorizes it.

The initial implementation must define the publication targets, authorized withdrawal mechanism, review owner, and supported delivery destinations. Secrets and credentials must be referenced through secure configuration and must not be stored in destination references or ordinary metadata.

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

### 5.13 Content Rights Management

Content rights management is a cross-cutting policy capability governing what the system may do with information obtained from external sources. It is distinct from network access control, source reliability assessment, publication eligibility, and recipient delivery authorization.

The proposed capability must:

- Maintain versioned source rights profiles and applicable license/contract references.
- Record how a content artifact was accessed and which source/content revision it refers to.
- Evaluate permission separately for metadata access, full-text access, temporary processing, persistent storage, internal analysis, external LLM processing, embedding/translation, derived-output generation, quotation, customer distribution, and republication.
- Apply retention, expiration, restriction, and deletion requirements to original content and derived artifacts.
- Preserve an auditable basis, policy version, outcome, and handling constraints for each material rights assessment.
- Block restricted operations when permission is unknown, denied, expired, revoked, or requires review.

A source being publicly reachable or previously collected does not establish permission for every subsequent operation. Rights checks must occur before content retrieval/storage, external provider transmission, and distribution as applicable. Temporary processing must not create an unauthorized retained copy in caches, queues, logs, backups, or external providers.

The capability does not provide legal advice or infer permissions from technical accessibility. The Project Owner must approve the initial source-rights policy and its evidence basis. The detailed rights model and operations remain provisional under GENI-ADR-013 until accepted.

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
10. Create an EventMatchCase for each distinct development identified in an ArticleRevision.
11. Generate and evaluate EventMatchCandidate records within each case.
12. Record an immutable EventMatchDecision for each resolved case, or route the case for authorized human review.
13. Apply an eligible MATCH decision through EventService and create the corresponding ArticleEventLink.
14. Propose new event creation only through the approved event-creation workflow.
15. Evidence enrichment and verification.
16. Economic relevance assessment.
17. Event importance assessment.
18. Economic impact analysis.
19. Event dossier generation.
20. Publication policy evaluation.
21. Review routing when required.
22. Report publication and delivery.
23. Event monitoring and subsequent updates.

Importance, economic relevance, and economic impact assessments must remain separate outputs even when they share source evidence or analytical execution resources.

The pipeline must support controlled reprocessing when classification, extraction, matching, scoring, or analysis logic changes.

Reprocessing must preserve historical outputs and must not silently overwrite previously published reports.

## 7. Event-Centric Domain Model

The primary domain entities include:

- Source
- Article
- ArticleProcessingRecord
- ArticleRevision
- EventMatchCase
- EventMatchCandidate
- EventMatchDecision
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

### 7.2 ArticleRevision

Represents an immutable, meaningful observed version of an Article's published content.

Each ArticleRevision belongs to exactly one Article and preserves the content/version metadata used by downstream extraction, evidence, and event matching. A material change to the publication creates a new revision; unchanged repeated collection does not. An EventMatchCase must reference the exact ArticleRevision it evaluates. Later revisions must not silently rewrite or reuse the earlier revision's cases, evidence spans, or decisions.

### 7.3 Event

Represents a real-world development or a connected sequence of developments.

An event may be associated with multiple articles.

Event identity must be stable and must not be derived solely from a headline or article URL.

### 7.4 Event Matching Case and Decision

Event matching is performed independently for each development identified within an immutable ArticleRevision. Each EventMatchCase may contain multiple EventMatchCandidate records, but candidates are proposals for evaluation and are not decisions.

An immutable EventMatchDecision records the authoritative outcome for one case. A single article revision may therefore produce multiple independent matching decisions. Ambiguous cases are routed for authorized human review; the review outcome must be recorded as a new decision that supersedes the previous effective decision.

### 7.5 ArticleEventLink

Represents an applied association between an ArticleRevision and an Event. Every link must reference the exact EventMatchCase and EventMatchDecision with outcome MATCH that authorized its creation.

A link must not be created from a candidate score, a review comment, or a non-MATCH outcome. Corrections deactivate the previous link with an explicit superseding decision and preserve the original association history. An article revision may have multiple event links when separate matching cases justify them.

### 7.6 Claim and Evidence

A Claim represents an assertion extracted from or attributed to a source, or an analytical assertion generated by the system.

An Evidence record represents material used to support, qualify, or contradict a claim.

Claims and evidence must preserve source attribution and provenance.

A source claim is not automatically an established fact.

### 7.7 Analysis

Represents a versioned analytical assessment of an event.

An analysis must identify its relevant evidence, methodology, model configuration where applicable, and uncertainty.

### 7.8 Event Dossier

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
| Trade and Industry | International trade, tariffs, manufacturing, supply chains |
| Energy and Resources | Oil, gas, electricity, commodities, critical minerals |
| Fiscal Policy and Public Debt | Government budgets, taxation, sovereign debt |
| Geopolitical Economic Risk | Sanctions, conflict, political instability affecting economies |

The taxonomy must be extensible.

An article may have multiple topic classifications, each with an associated confidence and classification methodology.

Classification results must be versioned so that changes in taxonomy or classification logic can be evaluated and reprocessed.

## 9. Importance, Economic Relevance, and Economic Impact

### 9.1 Event Importance

Importance measures the overall significance of an event and its priority for attention, monitoring, and editorial coverage.

Potential dimensions include:

- Institutional or public significance.
- Geographic and population scope.
- Novelty and materiality of the development.
- Time sensitivity and urgency.
- Expected duration or persistence.
- Relevance to the product's stated monitoring priorities.

Importance must not be calculated by simply adding economic relevance and economic impact. The importance methodology must state whether economic considerations contribute to the assessment and how double-counting is prevented.

### 9.2 Economic Relevance

Economic relevance measures the strength of the event's connection to economic activity, policy, institutions, or markets.

The assessment should identify:

- Direct economic links, such as a central-bank rate decision or a change in a fiscal measure.
- Indirect links, such as geopolitical developments that may affect trade routes or supply chains.
- Contextual links where an economic connection is relevant background but not yet a demonstrated transmission pathway.
- Whether a material economic connection has not been established.
- Whether available information is insufficient to make the assessment.

The result must identify the relevant transmission channels, affected entities, geographic scope, and supporting evidence where available. Relevance does not establish that an effect has occurred or determine its magnitude.

### 9.3 Economic Impact

Economic impact describes realized or potential consequences of an event.

An impact assessment should identify, where supported:

- Economic channel or dimension.
- Affected country, institution, sector, industry, market, or group.
- Direct or indirect transmission mechanism.
- Direction of effect, such as positive, negative, mixed, neutral, or unclear.
- Magnitude or defensible range, with its unit and reference context where applicable.
- Expected or observed time horizon and duration.
- Evidence status: observed, source-reported, inferred, or unknown.
- Supporting and conflicting evidence.
- Uncertainty and limitations.

A single aggregate impact number must not conceal materially different effects across countries, sectors, instruments, or time horizons. An aggregate score may be introduced only through an explicit, evaluated methodology.

### 9.4 Market Reaction and Causality

An observed market reaction requires identifiable market data, instrument identity, measurement time, source, and a suitable comparison or baseline where relevant.

A market reaction is not, by itself, proof of event causality. The system must distinguish a measured market movement from a source's explanation of that movement and from the system's own causal interpretation.

When no suitable market data is available, the system may describe potential market implications as analysis, but must not label them as observed market reactions.

### 9.5 Scoring and Uncertainty Rules

Each assessment type must use its own versioned result schema and methodology. Numeric scales, if used, must define their valid range, direction, interpretation, comparability, and calibration status.

An assessment confidence value expresses the strength of support for the assessment; it is not the event's importance, the magnitude of impact, or the probability of a forecast unless a separately defined and calibrated probability is explicitly provided.

Unknown, unavailable, contradictory, and not-applicable inputs must remain distinguishable. Missing information must not automatically lower a score, become zero impact, or be interpreted as evidence that no effect exists.

The methodology and quantitative acceptance thresholds for importance, economic relevance, and economic impact must be documented and evaluated independently.

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

The complete transition rules and event identity policy are subject to the relevant ADRs and detailed specifications.

## 11. Publication Policy

Every generated report receives an immutable publication decision. A publication decision describes whether a report version is eligible for publication; it does not record the external publication operation itself.

| Decision | Meaning |
|---|---|
| `PUBLISH` | The report version meets the requirements for publication |
| `PUBLISH_WITH_CAVEATS` | The report version may be published only with explicit caveats and limitations |
| `HOLD_FOR_REVIEW` | Do not publish; route to an authorized review process |
| `REJECT` | The report version is not eligible for publication |

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
- Applicable content-access and licensing restrictions.

A decision must preserve its reasons, policy version, timestamp, and relationship to any decision it supersedes. A changed outcome creates a new decision rather than mutating the earlier record.

A `HOLD_FOR_REVIEW` decision must create or reference an operational review task. The report remains unpublished until an authorized review outcome permits further processing. An approval, approval with caveats, or other material review outcome must be represented by a new effective publication decision. A review record alone is not a publication authorization.

For `PUBLISH_WITH_CAVEATS`, the caveats must be explicit, persisted, and included in the published representation. The publication execution must not silently omit them.

## 11.1 Publication Execution

Publication execution is a separate workflow from policy evaluation and review.

Only a report version with an effective `PUBLISH` or `PUBLISH_WITH_CAVEATS` decision may be submitted for publication. The execution must also verify that the decision has not been superseded or invalidated and that all required review, rights, security, and target-specific conditions are satisfied.

Each logical publication operation must record:

- The report version.
- The effective publication decision, when required.
- The publication target.
- The operation type: `PUBLISH`, `REPLACE`, or `WITHDRAW`.
- The target publication reference for replacement or withdrawal.
- A stable idempotency key.
- The operation status and timestamps.
- External references and outcome information.
- Each individual attempt and any recovery or reconciliation action.

A successful publication operation is the evidence that the report version became available at the specified target and publication key. The effective publication state must be derived from the successful operation chain for that target and key, not inferred from the policy decision or from a delivery record.

A new corrected report must be a new immutable report version. Publishing it as a replacement must reference the earlier publication. The earlier publication remains effective if replacement fails; it becomes superseded only after the target confirms the replacement.

A withdrawal must reference the currently effective publication for the same target and publication key and retain its reason and authorization context. A failed or uncertain withdrawal must not be represented as completed.

If an external request times out after it may have succeeded, the operation must be marked for reconciliation. The system must query or otherwise reconcile the target before retrying a side effect. Where the target does not support idempotency or status lookup, the duplicate-publication risk and manual reconciliation path must be documented.

## 11.2 Delivery

Delivery is the separate act of sending report content, a confirmed publication link, or a notification to a recipient or delivery destination.

Delivery may occur after publication or independently when an approved delivery policy permits direct distribution of report content. A delivery that contains a publication link must reference a confirmed successful publication operation.

Delivery status and history must not change publication status. Publication status and history must not be inferred from delivery status. Each operation must have its own idempotency key, attempts, external reference, and recovery handling.

A rejected or held report must not be delivered through a path that bypasses its applicable publication or distribution policy.

Automatic publication must never bypass security, quality, provenance, review, or content-rights requirements.

## 12. Report Structure

A text event report should contain:

1. Headline.
2. Executive Summary.
3. What Happened?
4. Latest Developments.
5. Timeline.
6. Key Entities.
7. Event Importance — why the development deserves attention or follow-up.
8. Economic Relevance — the direct, indirect, or contextual economic transmission pathways.
9. Observed Market Reaction, when supported by actual market observations.
10. Economic Impact — realized or potential consequences by channel, direction, magnitude, and time horizon where supported.
11. Supporting Evidence.
12. Conflicting or Unconfirmed Information.
13. Risks and Uncertainties.
14. Analytical Assessment.
15. Sources.

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

SQLite is a candidate for the initial persistence proof-of-concept, not a selected or approved database engine. ADR-005 requires the initial engine to be selected after testing the expected workload, concurrent writers, transaction behavior, backup/restore requirements, deployment model, and operational capacity.

SQLite may be selected if those tests demonstrate that its single-instance concurrency and operational model satisfy the initial workload. PostgreSQL remains an alternative for the initial selection if the measured requirements exceed SQLite's suitable operating envelope; it may also be a later migration target if requirements grow.

Until ADR-005 is formally accepted, no implementation or document may treat either engine as the approved production choice.

Persistence must be accessed through repository interfaces.

The domain model must not depend directly on a specific database engine.

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
- Importance, economic relevance, and economic impact assessment outcomes, including unknown/insufficient-data rates and methodology versions.
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
- Economic relevance assessment.
- Economic impact assessment by channel and evidence status.
- Publication decisions.
- Report quality.

Evaluation datasets, acceptance thresholds, and regression procedures must be documented separately and incorporated into development milestones.

## 15. Development Phases

Development phases describe engineering execution and are separate from product release numbers.

The detailed development roadmap is maintained in:

`docs/04-implementation-plan-and-roadmap.md`

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
- Economic relevance assessment and its initial evaluation.
- Event matching evaluation.

### Development Phase C — Analysis and Publication

- Importance assessment.
- Economic impact analysis by channel.
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
17. Event importance is assessed independently using a documented and versioned methodology.
18. Economic relevance is assessed separately, including its direct or indirect transmission pathways and an explicit unknown/not-established outcome.
19. Economic impact is analyzed by channel, direction, magnitude, time horizon, evidence status, and uncertainty where supported.
20. Observed market reactions are supported by market data and are not presented as proof of event causality.
21. Publication policy is enforced and publication decisions are immutable and versioned.
22. Held reports are routed to a defined review mechanism, and review approval cannot bypass a new effective publication decision.
23. Reports can be generated and corrected through immutable report versions with traceable report-level lineage.
24. Publication, replacement, and withdrawal are recorded as separate idempotent operations, and publication success is confirmed by the target rather than inferred from a policy decision.
25. Uncertain external publication outcomes are reconciled before another side-effecting attempt; a failed replacement does not invalidate the previous confirmed publication.
26. Delivery operations are recorded separately from publication, prevent unintended duplicate delivery, and do not change publication status.
27. Processing failures and recovery operations are observable.
28. The system can restart without corrupting existing data.
29. Reprocessing does not silently overwrite historical analytical, report, publication, or delivery records.
30. LLM execution respects configured budgets, deadlines, and output validation.
31. External content is handled as untrusted input.
32. The initial system operates without mandatory distributed or cloud infrastructure.

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
- Publication eligibility decisions, external publication operations, and recipient delivery operations are distinct and independently traceable.
- Held reports must not be silently published.
- Publication replacement and withdrawal must preserve external-operation history and require confirmed outcomes.
- Event lifecycle state is separate from event-history occurrences.
- Processing state is separate from domain state.
- Phase 1 is text-only.
- Original source language and content references are preserved.
- SQLite and PostgreSQL remain candidates under GENI-ADR-005. No database engine is approved until the required workload and concurrency proof-of-concept is completed and the ADR is accepted.
- Full-text acquisition and storage must respect applicable rights and restrictions.
- Content permission is operation-specific; unknown or unverified rights must not authorize restricted access, retention, external processing, quotation, or distribution.
- Rights checks, publication decisions, and recipient-distribution authorization are separate controls.
- Advanced infrastructure is deferred until justified by requirements.

These constraints describe the current proposed architecture. Any change to an accepted architectural constraint must follow the applicable ADR and documentation governance processes.

## 18. Architecture Governance and Open Decisions

Architectural decisions must be documented and tracked through the ADR governance process.

The project has nineteen registered architectural decision topics, and all nineteen have individual ADR documents published in the GitHub `main` branch.

All nineteen ADRs currently have status Proposed. None is an accepted architectural decision until the Project Owner explicitly records approval.

The topics cover:

- Event-centric architecture, article deduplication, and event identity/matching.
- Editorial focus, importance, economic relevance, and economic impact.
- Evidence provenance and uncertainty.
- LLM execution, deterministic workflows, budgets, and evaluation.
- News acquisition, multilingual processing, and content rights.
- Persistence, semantic retrieval, idempotency, and recovery.
- Publication quality gates, human review, corrections, withdrawals, and delivery channels.
- Market data integration and impact classification.

The complete list of decision topics and their current tracking status is maintained in:

`docs/adr/README.md`

Until the relevant ADRs are accepted, related architectural statements in this document represent the current proposed direction rather than formally approved implementation decisions.

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