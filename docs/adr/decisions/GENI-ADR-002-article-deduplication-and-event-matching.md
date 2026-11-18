# GENI-ADR-002 — Article Deduplication and Event Matching Separation

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-002  
**Title:** Article Deduplication and Event Matching Separation  
**Status:** Proposed  
**Version:** 1.6
**Date:** 2026-11-18
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence collects articles from multiple international news sources and organizes intelligence around real-world economic and economically relevant events.

A single event may be covered by many publishers. At the same time, the same article may appear multiple times because of repeated collection, URL variations, syndicated publication, content updates, or near-identical copies.

The system must therefore solve two related but fundamentally different problems:

1. **Article Deduplication:** Determine whether two article records represent the same published content or substantially duplicate content.
2. **Event Matching:** Determine whether an article describes, reports on, or provides evidence about an existing real-world event.

These operations have different inputs, objectives, outputs, confidence semantics, and consequences.

For example, consider the following situation:

- A central bank announces an interest-rate decision.
- Several news organizations publish independent reports about the announcement.
- A news agency distributes a report that is republished by multiple publishers.
- A publisher updates its original article with additional information.
- Another publisher reports the subsequent currency and bond market reaction.
- A later article discusses the economic consequences of the decision.

Some articles may be duplicates or syndicated versions of the same reporting. Others are independent reports about the same event. Some may describe consequences or related developments that require separate event relationships.

A system that treats article similarity as event identity may incorrectly merge unrelated events or collapse independent reporting into a single source record.

A system that treats every article as a separate event may create fragmented event histories and repetitive intelligence reports.

The architecture must explicitly separate these responsibilities while preserving the relationships between articles, sources, and events.

## 2. Decision Question

Should article deduplication and event matching be implemented as separate logical processing responsibilities, with independent candidate generation, evaluation, decisions, confidence semantics, and audit history?

If so:

- What should each operation determine?
- Which information may each operation use?
- How should exact duplicates, near-duplicates, and syndicated publications be handled?
- How should uncertain matches be represented?
- How should the two operations interact without becoming dependent on one another's identity assumptions?
- What information must be retained for provenance and future reprocessing?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

The system must:

1. Preserve individual article records and their source identities.
2. Identify repeated collection of the same article.
3. Detect exact and near-duplicate article content.
4. Identify potential syndicated or republished content.
5. Preserve distinct publisher and source attribution.
6. Associate articles with one or more relevant events.
7. Support articles that describe multiple distinct events.
8. Support multiple independent articles associated with the same event.
9. Keep article duplicate decisions separate from event association decisions.
10. Preserve uncertainty when available information is insufficient.
11. Record the reasoning and processing version behind automated decisions.
12. Support reprocessing when matching policies, models, or source information change.
13. Avoid treating duplicate or syndicated publications as independent corroboration.
14. Preserve enough information to reverse or correct erroneous associations.

### 3.2 Non-Functional Requirements

The design should support:

- Deterministic processing where practical.
- Scalable candidate generation.
- Bounded use of LLM-based reasoning.
- Provider-independent similarity and classification capabilities.
- Explainable decisions and traceable provenance.
- Idempotent processing and safe retries.
- Historical decision preservation.
- Incremental adoption of semantic retrieval.
- Persistence technology independence.

### 3.3 Architectural Constraints

- ADR-001 establishes the event-centric intelligence architecture.
- Event identity and lifecycle policies belong to ADR-011.
- Semantic retrieval and embedding storage belong to ADR-012.
- Evidence provenance and uncertainty representation belong to ADR-008.
- Persistence, asynchronous execution, idempotency, and recovery belong to ADR-016.
- The physical data model remains subject to Document 03 and the relevant persistence ADRs.
- Proposed ADRs must not be treated as accepted implementation requirements.

## 4. Terminology

The following terms have specific meanings in this ADR.

| Term | Definition |
|---|---|
| Article | A source publication or independently identifiable published content record. |
| Article Revision | A new observed or retrieved version of an existing article. |
| Exact Duplicate | An article observation whose normalized content or identity matches another article under an explicitly defined exact-match rule. |
| Near-Duplicate | An article whose content substantially overlaps with another article but is not identical. |
| Syndicated Publication | A publication that reproduces or adapts content originating from another publisher or news agency. |
| Duplicate Candidate | An immutable pairwise evaluation of two exact ArticleRevision records; multi-article groups are derived from pairwise candidates and effective decisions. |
| Duplicate Decision | A recorded outcome of duplicate evaluation. |
| Event | A real-world development represented as a domain entity in the intelligence system. |
| Event Candidate | An existing event considered as a possible match for an article. |
| Event Match | An evaluated relationship between an article and an event. |
| Article-Event Association | A recorded relationship between an article and an event. |
| Independent Reporting | Reporting that is independently produced rather than merely copied or syndicated from another source. |
| Source Provenance | Information identifying where content originated, where it was published, and how it entered the system. |

An article duplicate relationship does not establish that two articles concern the same event.

An event match does not establish that two articles are duplicates.

## 5. Options Considered

### Option A — Unified Similarity and Matching Pipeline

Use one general similarity engine to compare articles and determine both duplication and event association.

**Advantages:**

- Fewer apparent processing components.
- Shared candidate-generation infrastructure.
- Simpler initial conceptual model.

**Disadvantages:**

- Conflates different classification objectives.
- Encourages reuse of similarity scores with incompatible meanings.
- Makes it difficult to distinguish copied content from independent reporting.
- Creates a risk of incorrect event merges.
- Makes evaluation and threshold calibration ambiguous.
- Couples article identity decisions to event identity decisions.
- Makes historical corrections more difficult.

**Assessment:** Not recommended.

### Option B — Fully Independent Systems Without Shared Infrastructure

Implement completely separate systems for article deduplication and event matching, including separate candidate-generation infrastructure and similarity services.

**Advantages:**

- Strong separation of responsibilities.
- Independent policies and evaluation.
- Reduced risk of accidental coupling.

**Disadvantages:**

- Duplicated infrastructure.
- Repeated content normalization and feature extraction.
- More operational complexity.
- Potential inconsistency in shared representations.

**Assessment:** Provides strong separation but introduces unnecessary duplication.

### Option C — Separate Logical Responsibilities with Shared Infrastructure

Implement article deduplication and event matching as separate processing responsibilities.

They may share infrastructure such as:

- Text normalization.
- Language detection.
- Tokenization.
- Entity extraction.
- Temporal feature extraction.
- Embedding generation.
- Candidate retrieval infrastructure.
- LLM execution infrastructure.
- Observability and evaluation utilities.

However, each responsibility must retain its own:

- Candidate types.
- Evaluation logic.
- Decision outcomes.
- Confidence semantics.
- Policy and model versions.
- Audit history.
- Acceptance criteria.

**Advantages:**

- Clear separation of domain responsibilities.
- Reuse of common technical infrastructure.
- Independent evaluation and calibration.
- Reduced risk of incorrect event identity decisions.
- Better provenance preservation.
- Incremental implementation without requiring a dedicated vector database.

**Disadvantages:**

- Requires explicit contracts between processing stages.
- Introduces additional decision records and candidate relationships.
- Requires separate evaluation datasets and quality metrics.
- Needs clear rules for syndicated and related publications.

**Assessment:** Recommended.

## 6. Proposed Decision

Adopt **Option C: Separate Logical Responsibilities with Shared Infrastructure**.

Article deduplication and event matching must be separate logical operations within the news intelligence processing workflow.

They may share technical services, data representations, and candidate-retrieval infrastructure, but must not share a single decision model or interpret similarity scores as interchangeable.

### 6.1 Article Deduplication Responsibility

Article deduplication determines whether two article records represent the same or substantially overlapping published content.

It operates primarily on article-level information, including:

- Source identity.
- Publisher identity where available.
- External article identifiers.
- Canonicalized URLs.
- Normalized titles.
- Normalized content.
- Content fingerprints.
- Publication and update timestamps.
- Language.
- Syndication and origin metadata.
- Revision information.

Its output is a duplicate evaluation and, where justified, a recorded duplicate relationship or decision.

It does not determine whether the articles describe the same real-world event.

### 6.2 Event Matching Responsibility

Event matching determines whether an article provides information about an existing real-world event or should be associated with a new event candidate.

It operates on event-related information, including:

- Article content and revisions.
- Named entities.
- Event type and topic.
- Event occurrence time.
- Geographic context.
- Actions and developments described.
- Existing event summaries and timelines.
- Existing event evidence.
- Relevant causal and temporal relationships.
- Available semantic and contextual signals.

Its output is an event matching evaluation and, when sufficiently justified, an article-event association.

It does not determine whether the article is a duplicate of another publication.

### 6.3 Independence of Decisions

The result of article deduplication may inform event matching, but it must not automatically determine the event association.

Similarly, an event match must not automatically establish that two articles are duplicates.

Both operations must retain independently traceable decisions.

## 7. Article Deduplication Design

### 7.1 Candidate Generation

Candidate generation should identify article pairs that may represent duplicate or near-duplicate content. Multi-article duplicate groups must be derived from pairwise candidate evaluations and their effective decisions; a group must not replace the immutable pairwise evidence.

Candidate signals may include:

- Matching external article identifiers within the appropriate source scope.
- Matching canonicalized URLs.
- Matching normalized content hashes.
- Matching normalized titles.
- High textual overlap.
- Similar publication times.
- Shared source or publisher metadata.
- Shared syndication identifiers.
- Similar article structure and distinctive phrases.

Candidate generation is a retrieval step, not a final duplicate decision.

The system should avoid comparing every article with every other article when more efficient source-scoped or indexed retrieval methods are available.

### 7.2 Exact Duplicate Detection

Exact duplicate detection should prioritize deterministic signals.

Potential signals include:

- Matching source-scoped external identifiers.
- Matching canonical URLs where identity is reliable.
- Matching normalized content fingerprints.
- Matching exact content under an explicitly defined normalization policy.

Normalization rules must be versioned or otherwise reproducible.

Normalization must not remove meaningful differences such as:

- Negation.
- Numeric values.
- Dates.
- Named entities.
- Important qualifiers.
- Materially different claims.

A matching hash alone must not be treated as conclusive when the hash was generated from an incomplete or overly aggressive normalization process.

### 7.3 Near-Duplicate Detection

Near-duplicate detection identifies content that substantially overlaps without being exactly identical.

Potential methods include:

- Token-based similarity.
- Shingle or n-gram overlap.
- MinHash or locality-sensitive hashing.
- Structural content comparison.
- Semantic similarity.
- Shared distinctive passages.
- Source and publication metadata.

No single method is required by this ADR.

The selected method must be evaluated against representative article pairs, including unrelated articles that discuss the same event.

Near-duplicate detection must distinguish copied or lightly edited content from independent reporting about the same underlying development.

### 7.4 Syndicated and Republished Content

Syndication requires special treatment.

When a news agency article is republished by multiple publishers:

- Each identifiable publisher publication should retain its own source attribution.
- Original publication or agency attribution should be retained where known.
- The relationship between the original and republished content should be represented where evidence supports it.
- The system must not automatically collapse all publisher records into one source record.
- Syndicated copies must not be counted as independent corroboration.
- Differences introduced by publishers must remain traceable.

A syndicated publication may be considered duplicate or near-duplicate content for analytical grouping purposes while remaining a distinct publication record.

A publication that substantially changes the content, introduces independent reporting, or adds new evidence may require a more nuanced relationship than a simple duplicate label.

The system must not assume that every similar article is syndicated.

### 7.5 Article Revisions

Updates to an article must be distinguished from separate publications.

When the same publisher updates an existing article:

- The article's stable identity should be preserved where the source supports that interpretation.
- A new revision or observed content version should be recorded when material content changes.
- The previous content version should remain available according to retention and rights policies.
- Duplicate evaluation should account for article revisions.
- Event matching should be able to use the relevant revision without losing the history of earlier associations.

The exact article revision persistence model is defined in Document 03 and remains subject to its relevant architecture decisions.


### 7.6 Duplicate Decision and History

Each immutable DuplicateCandidate evaluates one canonical pair of exact ArticleRevision records. Candidate generation and similarity scoring are evidence-producing operations only; neither creates an authoritative duplicate relationship.

The Article Deduplication Workflow must create an immutable DuplicateDecision for a candidate when policy permits a decision. The decision outcome vocabulary is:

| Outcome | Meaning |
|---|---|
| CONFIRMED_DUPLICATE | The exact ArticleRevision pair is confirmed as duplicate or near-duplicate under the recorded policy. |
| NOT_DUPLICATE | The evaluated pair is not considered duplicate under the recorded policy. |
| REVIEW_REQUIRED | Available evidence or policy requires authorized human review; no effective duplicate relationship is authorized by this outcome. |

Each DuplicateDecision must reference exactly one DuplicateCandidate and preserve its outcome, rationale, decision method, policy version, actor, timestamp, confidence semantics where applicable, and superseded decision reference.

A correction or reassessment creates a successor DuplicateDecision for the same candidate. At most one effective decision may exist per candidate. Prior decisions and their evidence must remain immutable and traceable.

A confirmed duplicate relationship is derived only from the effective `CONFIRMED_DUPLICATE` decision for that exact ArticleRevision pair. It must not delete or collapse either Article or ArticleRevision, erase source identity, or imply that two publications are independent corroboration.

**Pairwise decisions are not assumed to be transitive.** In particular, a confirmed near-duplicate relationship between A–B and B–C does not by itself establish that A–C are duplicates. Connected-component or single-link clustering must therefore never be used as the authoritative rule for a duplicate group. Exact-duplicate equivalence may be grouped only when the same documented normalization/fingerprint rule yields an identical exact-content identity. A near-duplicate group may be treated as an authoritative group only when every member pair has an effective `CONFIRMED_DUPLICATE` decision (complete-link condition) or a separately versioned, explicitly authorized group decision is introduced by a future ADR. Otherwise, retain the pairwise edges and present any connected component only as a non-authoritative review/candidate cluster. Conflicting, missing, or superseded pairwise decisions must prevent automatic promotion to an authoritative group. Group reconstruction must be deterministic and must retain the exact pairwise decision and policy provenance used.

The detailed fields, uniqueness rules, referential constraints, and repository contracts are defined in Document 03 and Document 02. Human correction and review are governed by ADR-014.

## 8. Event Matching Design

### 8.1 Candidate Generation

Event matching should retrieve plausible existing events for an article.

Candidate signals may include:

- Shared named entities.
- Event type and topic.
- Temporal proximity.
- Geographic context.
- Similar actions or developments.
- Shared identifiers or official announcements.
- Relevant event summaries.
- Existing event timelines.
- Semantic similarity.
- Causal or contextual relationships.

Candidate generation should prioritize recall sufficiently to avoid missing plausible event relationships.

Candidate retrieval must not automatically create or merge events.

### 8.2 Event Evaluation

Each candidate event must be evaluated against the article's actual content and the available event context.

Evaluation should consider:

- Whether the article describes the same real-world occurrence.
- Whether it describes a continuation or update.
- Whether it describes a consequence or reaction.
- Whether it describes a separate but related development.
- Whether the shared entities and topic are merely coincidental.
- Whether temporal and geographic information is consistent.
- Whether available evidence is sufficient to justify association.

For example, a central bank interest-rate decision and a subsequent currency market reaction may be closely related but are not necessarily the same event.

Their association must follow the event identity and lifecycle policy defined in ADR-011.

### 8.3 Event Association Outcomes

The event matching operation should support explicit outcomes such as:

| Outcome | Meaning |
|---|---|
| MATCH | Sufficient evidence supports association with an existing event. |
| NEW_EVENT_CANDIDATE | No existing event is sufficiently supported; a new event may be proposed. |
| AMBIGUOUS | Multiple possible events exist or the evidence is insufficient to choose reliably. |
| NO_MATCH | Evaluated candidates do not represent the same event. |
| REVIEW_REQUIRED | The case requires human evaluation under the applicable review policy. |

These outcomes are the case-level decision vocabulary used by the current proposed model. Their persistence and relationship to event identity operations are defined by ADR-011 and the EventMatchCase / EventMatchDecision contracts in Document 03. They remain Proposed until approval.

A `NEW_EVENT_CANDIDATE` outcome is a proposal only; it does not create an Event or an ArticleEventLink.

### 8.4 Event-Matching Case and Decision Boundaries

Each matching operation must be scoped to one independently identified development within one immutable ArticleRevision. The persistent unit is EventMatchCase. A single article revision may therefore have multiple cases, each with its own candidate set, review history, and final decision.

EventMatchCandidate records are retrieval and evaluation evidence. Their processing states must not use ACCEPTED or REJECTED to represent the case outcome. Candidate similarity values are not decision confidence and are not probabilities unless independently calibrated.

EventMatchDecision is the immutable, authoritative outcome for one case. A MATCH decision selects exactly one eligible candidate from that case. Non-MATCH outcomes do not authorize an active ArticleEventLink. A later automated reassessment or human correction creates a new decision that references the prior decision it supersedes.

ArticleEventLink must reference the exact EventMatchDecision that authorized its creation. A review task or comment is not a decision. Human review must result in a new EventMatchDecision under the authorization process defined by ADR-014. The complete persistence contract and referential constraints are specified in Document 03.

### 8.5 Multiple Event Associations

An article may describe multiple distinct events.

The system should support multiple article-event relationships where each relationship is justified by the article's content.

For example, an article may discuss:

- A central bank policy decision.
- A separate government fiscal announcement.
- The market reaction to the policy decision.

The system must not force every article into exactly one event.

Association granularity and event boundaries must follow ADR-011.

## 9. Confidence and Score Semantics

Article duplicate similarity and event matching confidence must be represented as separate concepts.

A score from one operation must never be reused as if it were a score from the other.

### 9.1 Duplicate Similarity

Duplicate similarity measures the degree of content overlap or identity evidence between article records.

It may be based on:

- Exact identity signals.
- Textual similarity.
- Structural similarity.
- Semantic similarity.
- Syndication evidence.

The system must document the meaning and limitations of each score.

A high semantic similarity score alone does not establish duplicate identity.

### 9.2 Event Matching Confidence

Event matching confidence represents the strength of evidence supporting the association between an article and a candidate event.

It may consider:

- Entity agreement.
- Temporal consistency.
- Event type agreement.
- Geographic consistency.
- Action and occurrence similarity.
- Contextual evidence.
- Semantic similarity.
- Contradictory evidence.

It must not be derived solely from article duplicate similarity.

### 9.3 Calibration and Versioning

For both operations, record the relevant:

- Algorithm or policy version.
- Model identifier where applicable.
- Feature or signal configuration.
- Evaluation timestamp.
- Candidate inputs.
- Decision outcome.
- Confidence or similarity value, when available.
- Decision rationale or reason codes.

A score must not be described as a probability unless its calculation and calibration justify that interpretation.

Thresholds must be evaluated against representative data and documented error costs.

False duplicate decisions and false event associations have different consequences and must be evaluated separately.

### 9.4 Unknown and Insufficient Information

Missing scores must remain null.

A missing similarity score must not be converted into zero.

An unavailable or failed evaluation must not be treated as a negative match.

Insufficient evidence must result in an explicit unresolved or review outcome rather than a forced decision.

## 10. Processing Order and Interaction

The proposed high-level workflow is:

1. Acquire an article and preserve source metadata.
2. Normalize the article and record its revision or observed content version.
3. Generate article duplicate candidates.
4. Evaluate exact duplicates and near-duplicates and persist immutable DuplicateCandidate records.
5. Run the Article Deduplication Workflow to authorize and persist an immutable DuplicateDecision for each resolved candidate; create successor decisions for corrections and preserve all source records.
6. Prepare article-level features for event matching.
7. Identify each distinct development within the ArticleRevision and create one EventMatchCase per development.
8. Generate and evaluate EventMatchCandidate records within each case.
9. Record one immutable EventMatchDecision per resolved case, or route it for authorized human review.
10. Apply a MATCH decision through EventService and create the ArticleEventLink with its exact decision reference.
11. Apply new-event creation only through the approved event-creation workflow defined by ADR-011.
12. Continue evidence extraction, analysis, and reporting.

This sequence is a logical processing order, not a requirement for one monolithic synchronous pipeline.

Article deduplication may be rerun independently of event matching.

Event matching may be rerun when event information, article revisions, matching policies, or relevant evidence changes.

A duplicate decision must not silently delete the article or prevent its source provenance from being retained.

An article already identified as a duplicate may still contain additional information or material changes that need to be evaluated for event intelligence.

## 11. Data and Persistence Implications

The logical data model must support separate records for article duplicate evaluation and article-event matching.

The following concepts are required at the logical level:

### 11.1 Duplicate Evaluation Concepts

- Article identity and source-scoped identifiers.
- Article revision or content observation.
- Normalized content fingerprint and its normalization version.
- Immutable DuplicateCandidate evaluations scoped to exact ArticleRevision pairs.
- Immutable DuplicateDecision outcomes and supersession history.
- Duplicate similarity and supporting signals.
- Syndication or republication relationships where known.
- Candidate input fingerprints, decision history, and processing/policy versions.

### 11.2 Event Matching Concepts

- Article-event candidate relationships.
- Event matching outcomes.
- Event matching confidence and supporting signals.
- Association decision history.
- Matching policy and model versions.
- Ambiguity and review information.
- Links to the relevant article revision and event context.

### 11.3 Persistence Rules

- Duplicate candidate identity must be stable and canonicalized so that the same pair is not repeatedly created in reverse order.
- Article-event associations must be independently identifiable.
- Historical decisions must remain traceable.
- Reprocessing must not create duplicate domain effects.
- A corrected decision must preserve the prior decision history.
- Source and article records must not be deleted merely because another article is considered a duplicate.
- DuplicateCandidate is immutable evaluation evidence; DuplicateDecision is the authoritative final outcome. Its effective decision and supersession chain must be persisted separately.
- Physical tables, constraints, indexes, and repository interfaces must be defined consistently in Document 03 and Document 02.

This ADR does not mandate a particular database engine or physical table layout.

## 12. Failure Handling, Reprocessing, and Idempotency

Both processing responsibilities must support safe retries and independent recovery.

### 12.1 Article Deduplication Failures

Examples include:

- Content extraction failure.
- Normalization failure.
- Fingerprint generation failure.
- Candidate retrieval failure.
- Similarity evaluation timeout.
- Insufficient content for reliable comparison.

A failure must not be recorded as a negative duplicate decision.

The operation should remain retryable where appropriate.

### 12.2 Event Matching Failures

Examples include:

- Entity extraction failure.
- Event candidate retrieval failure.
- Missing or conflicting event context.
- Similarity service failure.
- LLM evaluation timeout.
- Incomplete event history.

A failure must not automatically create a new event or force an association.

The operation should retain its incomplete or retryable status.

### 12.3 Idempotency

Repeated execution with the same logical inputs and processing versions must not create duplicate candidate records, duplicate associations, or conflicting decision history.

Processing identity should account for relevant inputs, including:

- Article identifier and revision.
- Event identifier and relevant event version.
- Matching policy version.
- Algorithm or model version.
- Relevant feature configuration.

### 12.4 Reprocessing

Changes to normalization rules, similarity methods, matching thresholds, models, or event context may justify reprocessing.

Reprocessing must be traceable and must not silently overwrite historical decisions.

The recovery and execution guarantees are governed by ADR-016.

## 13. Evaluation and Quality Requirements

Article deduplication and event matching must have separate evaluation datasets and metrics.

### 13.1 Article Deduplication Evaluation

Evaluation should include:

- Exact duplicate articles.
- Near-duplicate articles.
- Syndicated copies.
- Updated articles.
- Different articles about the same event.
- Similar headlines with different claims.
- Articles in different languages.
- Articles with incomplete content.
- Articles with different publication timestamps.
- Rewritten articles containing additional evidence.

Relevant metrics include:

- Precision.
- Recall.
- F1 score.
- False duplicate rate.
- Missed duplicate rate.
- Candidate retrieval recall.
- Performance by source and content category.

False duplicate decisions deserve particular attention because they may suppress independent reporting or distort source provenance.

### 13.2 Event Matching Evaluation

Evaluation should include:

- Multiple reports about one event.
- Separate events involving the same entities.
- Events occurring close together in time.
- Policy announcements and their subsequent reactions.
- Continuations and consequences.
- Articles covering multiple events.
- Similar events in different countries.
- Conflicting reports.
- Insufficiently described events.
- Events requiring later merge or split operations.

Relevant metrics include:

- Candidate retrieval recall.
- Match precision.
- Match recall.
- False association rate.
- Missed association rate.
- Ambiguity detection quality.
- New-event proposal quality.
- Human review rate.
- Event fragmentation and incorrect merge rates.

### 13.3 Independent Corroboration Evaluation

The system must be evaluated for its ability to avoid counting syndicated or copied content as independent corroboration.

Evaluation should examine:

- Known news agency syndication chains.
- Republished articles with minor editorial changes.
- Independent reports about the same event.
- Publications sharing a source but adding independent reporting.
- Articles with partially overlapping evidence.

The number of articles associated with an event must not be used as a direct substitute for the number of independent sources.

### 13.4 Acceptance Expectations

Before production use, the implementation must demonstrate that:

1. Article duplicate decisions are independent of event matching decisions.
2. Exact duplicate detection is reproducible under a recorded normalization policy.
3. Near-duplicate evaluation does not automatically collapse independent reporting.
4. Syndicated publications retain source attribution.
5. Independent reporting about the same event remains distinguishable.
6. Similarity scores have separate documented meanings.
7. Uncertain duplicate and event matching cases remain unresolved or enter review.
8. Reprocessing preserves historical decision traceability.
9. Duplicate article records are not silently deleted.
10. Event associations are consistent with the event identity policy in ADR-011.
11. Duplicate and event matching quality can be measured independently.
12. Syndicated copies are not counted as independent corroboration.

Exact numerical thresholds must be established through representative evaluation data and product risk requirements rather than invented in this ADR.

## 14. Security and Responsible Processing

Article content is untrusted external input.

Deduplication and event matching must treat article text as data, not as executable instructions.

LLM-assisted evaluation, if used, must:

- Separate article content from system instructions.
- Use constrained structured outputs.
- Avoid granting arbitrary tool access to content-analysis stages.
- Validate outputs against explicit schemas.
- Preserve input and model provenance.
- Handle prompt-injection attempts as untrusted content.
- Avoid treating instructions embedded in articles as authorized workflow commands.

Candidate generation and similarity services must also be protected against resource exhaustion caused by unusually large or malformed content.

Source URL acquisition and external content retrieval must follow the security requirements established by the acquisition architecture.

## 15. Consequences

### 15.1 Positive Consequences

- Article identity and event identity remain separate.
- Independent reporting is less likely to be incorrectly collapsed.
- Duplicate detection can evolve without changing event identity policy.
- Event matching can evolve without changing article deduplication semantics.
- Syndication relationships and source provenance can be preserved.
- Evaluation becomes more meaningful and measurable.
- Uncertain decisions can be handled explicitly.
- Semantic retrieval can be introduced incrementally.
- The system can reprocess articles and event relationships independently.

### 15.2 Negative Consequences

- More logical processing stages are required.
- Separate candidate and decision records increase data-model complexity.
- Independent evaluation datasets must be maintained.
- The system needs explicit policies for syndication and article revisions.
- Some articles may remain unresolved until additional evidence becomes available.
- Candidate retrieval and decision processing require observability and operational monitoring.

### 15.3 Trade-Offs

The proposed design deliberately favors traceability and correct domain semantics over minimizing the number of processing components.

The system may temporarily retain unresolved duplicate candidates or event matches rather than making an unsupported automatic decision.

This is preferable to silently deleting source records, merging unrelated events, or overstating independent corroboration.

## 16. Dependencies and Related ADRs

| Reference | Relationship |
|---|---|
| GENI-ADR-001 | Establishes the event-centric intelligence architecture that requires separate article and event identities. |
| GENI-ADR-008 | Defines evidence provenance and uncertainty representation used by both operations. |
| GENI-ADR-011 | Defines event identity, matching, continuation, merging, and splitting rules. |
| GENI-ADR-012 | Defines semantic retrieval, similarity calculation, and embedding storage options. |
| GENI-ADR-016 | Defines persistence, asynchronous execution, idempotency, and recovery. |
| GENI-ADR-017 | Defines LLM budgets, usage tracking, and evaluation strategy. |
| GENI-ADR-014 | Defines human review and authorized correction of ambiguous or incorrect event associations. |
| GENI-ADR-018 | Defines language and translation constraints relevant to multilingual duplicate detection and event matching. |
| Document 02 | Defines the component and interface contracts that must preserve the separation. |
| Document 03 | Defines the logical data model and persistence implications. |
| Document 04 | Defines implementation sequencing and delivery priorities. |

### 16.1 Scope Boundaries

This ADR does not decide:

- The final event identity model.
- Event continuation, merge, or split rules.
- Specific event matching thresholds.
- A mandatory embedding model.
- A mandatory vector database.
- The final duplicate detection algorithm.
- The final physical database schema.
- The exact human review interface.
- The final source reliability scoring model.

These matters belong to the related ADRs and implementation specifications.

## 17. Implementation and Migration Implications

Implementation should introduce the two responsibilities as distinct application-level capabilities.

Suggested logical service boundaries:

- `ArticleDeduplicationService`
- `EventMatchingService`

These names describe logical responsibilities and do not mandate specific classes, packages, or deployment units.

Shared technical capabilities may include:

- `TextNormalizationService`
- `EntityExtractionService`
- `CandidateRetrievalService`
- `SimilarityEvaluationService`
- Shared LLM execution infrastructure
- Shared observability and evaluation utilities

The shared infrastructure must not obscure the independent decision contracts.

The implementation roadmap should:

1. Establish stable article identity and source provenance.
2. Implement deterministic exact duplicate signals.
3. Introduce immutable duplicate candidate evaluation over exact ArticleRevision pairs.
4. Implement the Article Deduplication Workflow and immutable DuplicateDecision supersession history.
5. Preserve syndication and revision relationships where known.
6. Implement event candidate retrieval separately.
6. Introduce event association decisions under ADR-011.
7. Add near-duplicate and semantic capabilities as evaluation justifies them.
8. Add independent metrics and monitoring for both operations.
9. Validate provenance and independent corroboration behavior.
10. Test recovery and idempotency under ADR-016.

Existing records, if any, must not be automatically merged or deleted merely because a new deduplication policy is introduced.

Any migration that changes existing article or event associations must preserve historical traceability and provide a reviewable reconciliation process.

## 18. Open Questions

The following questions remain unresolved and require further design or implementation evidence:

1. What exact normalization rules should be used for content fingerprints?
2. Which source-scoped external identifiers can be trusted for exact article identity?
3. How should article revisions be represented when publishers reuse URLs?
4. How should syndication origin be established when attribution is incomplete?
5. Which near-duplicate method should be used in the first operational release?
6. How should multilingual duplicate detection handle translations and localized rewrites?
7. Which features should be mandatory for event candidate generation?
8. How should candidate retrieval balance recall, latency, and computational cost?
9. Which cases require human review rather than automated decisions?
10. How should duplicate relationships be revised when later evidence reveals independent reporting?
11. How should duplicate and event matching evaluations be maintained as the source set evolves?
12. How should policy changes trigger controlled reprocessing of historical articles?

These questions must be resolved through implementation specifications, evaluation, or related ADRs as appropriate.

## 19. Decision Status and Approval

This ADR is currently **Proposed**.

The recommendation is to adopt separate logical responsibilities for article deduplication and event matching, supported by reusable technical infrastructure.

No implementation should treat this proposal as a formally accepted architectural constraint until the designated decision owner approves it.

Upon acceptance:

- Document 02 must reflect the separate component responsibilities and contracts.
- Document 03 must reflect the required logical data relationships.
- Document 04 must align the implementation sequence with the decision.
- ADR-011 must define event identity and lifecycle behavior consistently.
- ADR-012 must define semantic retrieval decisions without conflating article duplication with event matching.
- Relevant evaluation and operational specifications must define independent quality criteria.

## 20. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-16 | Proposed | Initial proposal separating article deduplication and event matching. | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Clarified per-ArticleRevision EventMatchCase scope, candidate/decision separation, immutable EventMatchDecision, exact ArticleEventLink provenance, and human-review outcome handling. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Clarified duplicate candidate and decision separation and the need to preserve duplicate decision history. | AI Architecture Assistant |
| 1.3 | 2026-11-18 | Proposed | Defined immutable DuplicateCandidate evaluations over exact ArticleRevision pairs and a separate immutable DuplicateDecision with supersession history. | AI Architecture Assistant |
| 1.4 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |
| 1.5 | 2026-11-18 | Proposed | Defined pairwise duplicate decision outcomes, immutable supersession, and group derivation from effective pairwise decisions. | AI Architecture Assistant |

**End of ADR-002**
