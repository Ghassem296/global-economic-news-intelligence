# GENI-ADR-011 — Event Identity, Matching, Continuation, Merging, and Splitting

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-011  
**Title:** Event Identity, Matching, Continuation, Merging, and Splitting  
**Status:** Proposed  
**Version:** 1.3  
**Date:** 2026-11-18  
**Decision Owner:** Product Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence uses an event-centric architecture in which real-world economic and financially relevant developments are the primary units of intelligence organization.

Articles are independent source records. Multiple articles may describe the same event, different aspects of an event, subsequent developments, or separate events connected by a broader economic situation.

The system therefore needs reliable rules for determining event identity and maintaining event relationships over time.

Consider the following examples:

- A central bank announces an interest-rate decision.
- Several publishers report the announcement.
- The central bank governor provides additional clarification.
- Bond yields and currency markets react.
- A subsequent meeting produces a different policy decision.
- A government announces a separate fiscal measure in response to the same economic conditions.

These developments are related, but they are not necessarily the same event.

Without explicit event identity rules, the system may:

- Merge distinct developments into one event because they share entities or topics.
- Create duplicate events for different reports about the same occurrence.
- Treat a consequence as an update to its cause.
- Confuse an ongoing process with a single occurrence.
- Incorrectly associate historical articles with current events.
- Lose provenance when an event is merged or split.
- Change event identity without preserving historical relationships.
- Generate inconsistent reports and timelines.

The problem becomes more complex as new information arrives. An event that initially appears independent may later be recognized as part of an existing event. Conversely, an event initially treated as one occurrence may need to be separated into multiple events when additional evidence becomes available.

The architecture must support these corrections without silently destroying historical information or invalidating previously generated reports.

Event identity must therefore be treated as an explicit domain concept rather than a side effect of article similarity or LLM classification.

This ADR establishes the proposed rules for event identity, event matching, continuation, merging, splitting, and historical traceability.

## 2. Decision Question

How should Global Economic News Intelligence define and maintain the identity of real-world events when multiple articles and subsequent developments are processed over time?

Specifically:

1. What constitutes the same event?
2. How should a new article be evaluated against existing events?
3. How should the system distinguish an event update from a separate but related event?
4. When should an event be created, continued, merged, or split?
5. How should uncertain event relationships be handled?
6. How should event identity changes preserve historical references, evidence, reports, and provenance?
7. Which decisions must be deterministic, which may use LLM assistance, and which require human review?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Every event must have a stable internal identifier.
- Event identity must represent a specific real-world occurrence or bounded development, not merely a broad topic.
- Multiple articles may be associated with the same event.
- One article may substantively cover multiple events.
- The system must distinguish duplicate reporting from event continuation.
- The system must distinguish event continuation from a separate related event.
- The system must support candidate generation and event matching.
- Event matching decisions must be recorded and traceable.
- The system must support uncertain and ambiguous event relationships.
- The system must support event creation, continuation, merging, and splitting.
- Event identity changes must preserve historical information.
- The system must support event-level timelines.
- The system must preserve source attribution and article-event relationship provenance.
- Existing reports must remain traceable to the event identity and source material used when they were generated.
- The system must support manual correction of incorrect event associations.
- Event matching must be repeatable and auditable using recorded inputs and policy versions.

### 3.2 Technical Constraints

- Event identity must not depend on a particular LLM provider.
- Event matching must support deterministic signals and optional semantic signals.
- Event matching must not require a dedicated vector database in the initial implementation.
- Matching policies and thresholds must be versioned.
- Candidate generation must be separable from final event association.
- Event identity operations must be transactionally consistent where practical.
- Merge and split operations must be idempotent.
- The system must preserve historical identifiers and relationships.
- Event identity decisions must be recoverable after processing failures.
- The design must support asynchronous article ingestion and event processing.

### 3.3 Business and Product Constraints

- The product focuses on economic intelligence and financially relevant developments.
- International political, regulatory, geopolitical, and corporate developments may qualify when they have meaningful economic relevance.
- The system must avoid repetitive reporting of the same underlying occurrence.
- Reports should distinguish facts about an event from interpretations and forecasts.
- Event importance must not be inferred solely from article volume.
- The architecture must support both rapidly developing events and longer-running economic developments.
- Incorrect event merges can materially damage the credibility of published intelligence.

### 3.4 Security and Privacy Constraints

- Article content must be treated as untrusted data.
- LLM-generated content must not directly execute event identity operations.
- Structured validation is required before any event association, merge, or split is persisted.
- External article content must not be allowed to override system instructions or matching policy.
- Event history and identity operations must be auditable.
- Access to restricted source content must follow applicable rights and licensing requirements.

### 3.5 Operational and Cost Constraints

- Candidate generation should minimize unnecessary expensive LLM calls.
- Event matching must be observable and measurable.
- Ambiguous cases must not create uncontrolled manual workload.
- Failed event processing must be recoverable.
- Event updates must not repeatedly trigger unnecessary full analysis.
- Merge and split operations must have explicit operational procedures.
- The initial implementation should avoid unnecessary distributed infrastructure.

### 3.6 Legal and Content-Rights Constraints

- Event identity must not imply ownership of source material.
- Event records may retain permitted metadata and derived information subject to applicable restrictions.
- Article provenance must remain available when content retention is limited.
- Event merging and splitting must not bypass content deletion, licensing, or retention requirements.

### 3.7 Explicit Non-Goals

This ADR does not finalize:

- The exact event matching algorithm.
- The final numerical similarity or confidence thresholds.
- The embedding model or vector database.
- The complete event lifecycle and editorial status policy.
- The event importance calculation methodology.
- The full article deduplication algorithm.
- The complete claim verification methodology.
- The final publication and human-review workflow.
- The initial persistence technology.

These topics are addressed by related ADRs or subsequent implementation specifications.

## 4. Alternatives Considered

### 4.1 Alternative A: Article-Based Grouping Without Persistent Event Identity

**Description:**

Process articles independently and group related articles temporarily during report generation. Do not maintain persistent event identities.

**Advantages:**

- Simple initial implementation.
- No need for explicit event lifecycle management.
- Fewer identity operations.
- Lower initial data-model complexity.

**Disadvantages:**

- No stable event identity across processing runs.
- Difficult to maintain event history.
- Repeated reports may reconstruct inconsistent groups.
- Historical event relationships cannot be reliably preserved.
- Event-level monitoring becomes difficult.
- Merging and splitting cannot be audited as domain operations.

**Risks:**

- Duplicate event reporting.
- Inconsistent intelligence across time.
- Loss of continuity between successive articles.
- Expensive reconstruction of historical relationships.

**Estimated Complexity:** Low initially; High as event intelligence develops.

### 4.2 Alternative B: Permanent Event Identity With Automatic Similarity-Based Association

**Description:**

Assign stable event identifiers and automatically associate articles with the most similar existing event using a similarity score and fixed thresholds.

**Advantages:**

- Straightforward automation.
- Consistent event identifiers.
- Reduced manual intervention.
- Relatively simple matching workflow.

**Disadvantages:**

- Similarity does not necessarily establish event identity.
- Shared entities, locations, and topics may produce false matches.
- Similarity thresholds may behave differently across languages and event categories.
- Automatic decisions may conceal uncertainty.
- Incorrect associations can contaminate event dossiers and reports.
- Merge and split corrections still require additional mechanisms.

**Risks:**

- Silent incorrect event merges.
- False continuity between separate developments.
- Difficult-to-reverse historical contamination.
- Overconfidence in model-generated matching decisions.

**Estimated Complexity:** Medium initially; High for reliable production operation.

### 4.3 Alternative C: Persistent Event Identity With Explicit Matching Decisions and Controlled Identity Operations

**Description:**

Maintain stable event identities and treat event matching as an explicit decision process.

The system generates candidates using deterministic and optional semantic signals. A matching policy evaluates the candidates and produces a structured outcome.

Confirmed associations are persisted separately from candidate relationships.

Uncertain cases remain unresolved or enter review according to policy.

Event continuation, merging, and splitting are explicit domain operations that preserve identity history and provenance.

**Advantages:**

- Stable event identities.
- Explicit separation between candidate similarity and confirmed identity.
- Better control over false merges.
- Traceable event relationships.
- Supports automated matching and human correction.
- Preserves historical reports and event history.
- Allows matching strategies to evolve without changing domain identity semantics.

**Disadvantages:**

- More domain concepts and state transitions.
- Requires explicit identity-operation handling.
- More complex data model and testing.
- Ambiguous cases may require operational review.
- Historical identity resolution requires additional queries and rules.

**Risks:**

- Poorly defined matching policies can create inconsistent outcomes.
- Review queues may grow if uncertainty handling is too conservative.
- Incorrect merge or split operations can affect multiple downstream records.

**Estimated Complexity:** Medium to High.

### 4.4 Alternative D: Fully Human-Controlled Event Association

**Description:**

Require a human reviewer to confirm every article-event relationship and all event identity changes.

**Advantages:**

- Human judgment for complex cases.
- Reduced dependence on automated matching.
- Explicit accountability for identity decisions.

**Disadvantages:**

- High operational cost.
- Slow processing.
- Poor suitability for near-real-time monitoring.
- Difficult to scale across international news sources.
- Human reviewers may still make inconsistent decisions.

**Risks:**

- Processing delays.
- Review backlogs.
- Inconsistent event grouping across reviewers.

**Estimated Complexity:** High operationally.

## 5. Evaluation and Comparison

| Evaluation Criterion | Alternative A | Alternative B | Alternative C | Alternative D |
|---|---|---|---|---|
| Stable Event Identity | Low | High | High | High |
| Automated Processing | Medium | High | High | Low |
| False-Merge Protection | Low | Low | High | High |
| Historical Traceability | Low | Medium | High | High |
| Ambiguity Handling | Low | Low | High | High |
| Human Workload | Low initially | Low initially | Controlled | High |
| Reversibility | Low | Medium | High | Medium |
| Implementation Complexity | Low | Medium | High | High |
| Long-Term Maintainability | Low | Medium | High | Medium |
| Support for Event Evolution | Low | Medium | High | Medium |

### 5.1 Evaluation Priorities

The most important criteria are:

1. Correct event identity.
2. Protection against incorrect merges.
3. Historical traceability.
4. Ability to correct mistakes.
5. Suitability for automated processing.
6. Operational scalability.

The product's credibility depends more on preserving correct event identity than on maximizing automatic matching coverage.

A system that leaves an uncertain article unassociated is preferable to one that silently contaminates an event dossier with unrelated material.

Similarity scores may help generate and rank candidates, but they must not independently determine whether two records represent the same real-world event.

No universal numerical thresholds are established by this ADR. Thresholds require evaluation against representative, multilingual event-matching datasets.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Persistent Event Identity With Explicit Matching Decisions and Controlled Identity Operations.

### 6.1 Event Identity Definition

An Event represents a specific real-world occurrence or a bounded development that can be independently identified, monitored, evidenced, and analyzed.

An Event is not simply:

- A topic.
- An entity.
- A country or geographical region.
- A broad economic trend.
- A collection of articles with similar keywords.
- A general narrative without a defined occurrence or development.

Examples of distinct event identities include:

| Subject | Event Interpretation |
|---|---|
| Central bank interest-rate announcement | One specific policy decision |
| Subsequent central bank clarification | Potentially a continuation or a separate event, depending on its substance |
| A later central bank policy meeting | A distinct event |
| Government fiscal package announcement | A distinct policy event |
| Currency market reaction to an announcement | A related market observation, not automatically a separate primary event |
| A later government response to the same economic conditions | A separate event when it represents a distinct decision or occurrence |

The event identity decision must consider the underlying occurrence, not merely the subject matter of the reporting.

### 6.2 Event Identity Attributes

An event should have sufficient attributes to support identity assessment.

Proposed attributes include:

- Stable internal event identifier.
- Canonical event title.
- Concise event description.
- Event category or type.
- Primary entities.
- Relevant geographical scope.
- Occurrence time or estimated time range.
- Temporal precision.
- Event-defining facts.
- Identity status.
- Current event version.
- Creation and update timestamps.
- Identity-policy version where applicable.

Not every attribute must be available when an event is first detected.

Missing information must remain explicitly unknown rather than being fabricated or inferred with unjustified precision.

### 6.3 Event Identity Versus Event Lifecycle

Event identity and event lifecycle are related but distinct concepts.

**Event identity** answers:

- Is this the same event?
- Has this event been merged into another identity?
- Has this event been split into multiple successor identities?
- Which historical records refer to the same identity?

**Event lifecycle** answers:

- Is the event being enriched?
- Is it actively monitored?
- Has it been resolved?
- Should it be archived?

An event can remain the same event while moving through different lifecycle stages.

Lifecycle status must not be used as a substitute for identity status.

Detailed event lifecycle and transition policy should be documented in the relevant event lifecycle specification and coordinated with the product workflow.

### 6.4 Event Matching Principles

Event matching must evaluate whether a candidate article or development describes an existing event.

The matching process should consider multiple independent signals, including:

- Event-defining occurrence.
- Primary entities.
- Action or development type.
- Geographic scope.
- Temporal relationship.
- Relevant facts and quantities.
- Source-provided context.
- Semantic similarity.
- Existing event history.

No single signal is sufficient in every situation.

In particular:

- Shared entities do not prove event identity.
- Shared topics do not prove event identity.
- Similar publication dates do not prove event identity.
- High semantic similarity does not prove event identity.
- Different publishers do not automatically imply independent events.
- Different article wording does not automatically imply different events.

The system must evaluate whether the underlying real-world occurrence is the same.

### 6.5 Matching Outcomes

The matching process should produce one of the following structured outcomes:

| Outcome | Meaning |
|---|---|
| `MATCH` | The candidate is sufficiently supported as describing an existing event. |
| `NEW_EVENT_CANDIDATE` | No existing event is sufficiently supported; creation of a new event may be proposed for a separate authorized workflow. |
| `AMBIGUOUS` | Multiple plausible event identities exist or the evidence is insufficient to distinguish them. |
| `NO_MATCH` | The candidate does not match the evaluated event. |
| `REVIEW_REQUIRED` | The case requires an explicit review decision under the applicable policy. |

`NO_MATCH` is a case-level outcome recorded after evaluating the case's candidate set. It means that none of the evaluated candidate Events matches the single development represented by that EventMatchCase. It does not prevent another EventMatchCase for a different development in the same ArticleRevision from resolving to a different Event.

`NEW_EVENT_CANDIDATE` is not permission to create an event by itself. The decision must carry a stable, preassigned `proposed_event_reference` that will become the Event identifier. Creation is allowed only when the decision is still effective and a versioned EventCreationPolicy authorizes it, including any required human review. The initial EventHistory record must retain the source EventMatchCase, NEW_EVENT_CANDIDATE decision, EventCreationPolicy version, actor/authorization reference, and idempotency key. Retrying the same authorized creation must return the same Event. After creation, the Event is recorded as an EventMatchCandidate in the original case and a successor MATCH decision must select it before an ArticleEventLink is activated.

`AMBIGUOUS` must not be silently converted into `MATCH`.

### 6.6 Candidate Generation, Matching Cases, and Confirmation

Candidate generation, case-level decision, and application of an article-event association are three distinct operations.

The matching unit is an EventMatchCase scoped to exactly one immutable ArticleRevision and one independently identified development within that revision. An article revision may therefore create multiple EventMatchCase records. Each case owns its own candidate set, decision history, and review context.

The proposed sequence is:

1. Normalize an ArticleRevision and identify each distinct development described in it.
2. Create or retrieve one EventMatchCase for each development scope.
3. Retrieve plausible existing events for that case.
4. Persist EventMatchCandidate records with their signals, scores, method, and matching-policy version.
5. Evaluate candidate eligibility and case-level evidence.
6. Create an immutable EventMatchDecision for the case.
7. If the outcome is AMBIGUOUS or REVIEW_REQUIRED, route the case to the authorized human-review workflow defined by ADR-014.
8. Record the human outcome as a new EventMatchDecision that supersedes the previous effective decision; do not mutate the previous decision.
9. Apply an eligible MATCH decision through EventService and create an ArticleEventLink that references that exact decision.
10. Handle NEW_EVENT_CANDIDATE through a separate event-creation policy; the matching decision alone does not create an Event.

EventMatchCandidate is a candidate/evaluation record, not a decision. Candidate status must describe processing and must not use ACCEPTED or REJECTED to represent the case outcome. Each evaluated candidate is an immutable, versioned evaluation identified by its case, candidate Event, matching-policy version, and input fingerprint; a changed policy or input creates a new candidate record. Candidate similarity, decision confidence, and reviewer certainty are distinct values.

EventMatchDecision is the authoritative case-level outcome. MATCH must select exactly one eligible candidate from the same case. A non-MATCH outcome must not authorize an active ArticleEventLink.

Candidate generation must not directly modify event identity or persistent article-event associations. A candidate relationship must never be treated as a confirmed association.

### 6.7 Event Continuation

An existing event may receive new information without becoming a different event.

An article should be considered a potential continuation when it provides additional information about the same underlying occurrence or bounded development.

Examples include:

- An official clarification of an existing announcement.
- Additional details about the same decision.
- Confirmation of a previously reported result.
- Updated information about the same incident.
- New reporting about the immediate consequences of the same occurrence, when those consequences do not constitute a distinct event under the domain policy.

A continuation should update the event dossier while preserving the event identifier.

A continuation may create a new event version or history entry. It must not overwrite previously recorded evidence or historical analysis.

### 6.8 Related but Distinct Events

A new event must be created when the new development represents a distinct real-world occurrence or decision, even if it is causally, geographically, institutionally, or temporally related to an existing event.

Examples include:

- A subsequent policy decision at a later meeting.
- A separate government response to an earlier economic announcement.
- A new corporate acquisition following an earlier regulatory decision.
- A distinct market intervention following a previous market event.
- A separate incident arising from a broader geopolitical situation.

Related events may be linked through explicit event relationships.

The existence of a relationship must not collapse their identities.

Proposed relationship types include:

- `RELATED_TO`
- `CAUSED_BY`
- `RESULTED_FROM`
- `RESPONDS_TO`
- `PRECEDES`
- `FOLLOWS`
- `PART_OF`
- `SUPERSEDES`

The final relationship taxonomy should be validated during domain-model implementation.

### 6.9 One Article and Multiple Events

An article may describe multiple distinct events.

The system must support many-to-many article-event relationships.

For each association, the system should record:

- ArticleRevision identifier.
- EventMatchCase identifier.
- Event identifier.
- Relationship type or editorial role.
- Association status and active/deactivated timestamps.
- Exact EventMatchDecision identifier authorizing the link.
- Superseding decision identifier when deactivated.
- Relevant article section or evidence span, where available.
- Confidence or assessment metadata, where applicable.
- Policy and model version.
- Creation and review timestamps.

A broad article about several policy announcements must not force those announcements into one event merely because they appear in the same publication.

### 6.10 Event Merging

Two event identities may be merged when sufficient evidence establishes that they represent the same underlying occurrence.

A merge is an explicit identity operation, not an ordinary similarity update.

The merge operation should:

1. Identify the source event identities.
2. Identify the surviving canonical event identity.
3. Record the evidence and rationale for the merge.
4. Preserve all original event identifiers.
5. Preserve article-event association history.
6. Preserve event history and provenance.
7. Reconcile conflicting event attributes without silently discarding information.
8. Record the operation's actor, time, policy version, and affected records.
9. Update current identity resolution.
10. Trigger controlled downstream reconciliation where required.

The surviving identity should be selected according to a documented policy. The system must not assume that the newest or oldest event is always the correct survivor.

Merged event identities must not be physically deleted merely because they are no longer the canonical identity.

Historical references to a merged identity must remain resolvable.

A merge must be idempotent. Repeating the same logical merge operation must not produce duplicate history entries or duplicate downstream effects.

### 6.11 Event Splitting

An event must be split when an existing identity is found to contain multiple distinct real-world events.

Examples include:

- Two separate policy announcements incorrectly grouped together.
- A broad incident later determined to contain multiple independently identifiable occurrences.
- An event dossier combining a cause and a separate consequence that should have distinct identities.
- An incorrect automatic merge discovered during review.

A split operation should:

1. Identify the original event identity.
2. Define the successor event identities.
3. Determine which articles, claims, evidence, and observations belong to each successor.
4. Preserve uncertain associations where allocation cannot be established.
5. Record the split rationale and supporting evidence.
6. Preserve the original event identity and historical record.
7. Create explicit successor relationships.
8. Reconcile existing reports and analyses through controlled versioning.
9. Record the operation's actor, time, and affected records.
10. Make the split operation auditable and recoverable.

The original event identity must not simply be deleted and replaced.

The original identity should receive an explicit identity disposition indicating that it has been split or superseded by successor identities.

Historical reports generated before the split must remain traceable to the original event state and its source material.

### 6.12 Uncertainty and Human Review

When the system cannot establish event identity with sufficient support, it must preserve uncertainty.

The system should not force an association merely to complete a workflow.

Depending on the applicable operational policy:

- An ambiguous candidate may remain unresolved.
- A new event may be created only when sufficient independent evidence supports it.
- The candidate may enter a review queue.
- A previously confirmed association may be flagged for reassessment.
- A human reviewer may confirm, reject, merge, or split identities within authorized boundaries.

Human decisions must be recorded with their rationale and provenance.

The system must distinguish automated decisions from human-approved decisions.

### 6.13 Event Identity Resolution

The system must provide a way to resolve historical event identifiers to their current canonical identity.

Resolution must support:

- Original event identifier.
- Current canonical event identifier.
- Merge history.
- Split history.
- Successor relationships.
- Identity operation history.

A merged identity may resolve to one canonical identity.

A split identity may resolve to multiple successors and must not be silently resolved to an arbitrary single event.

Where a historical identity has multiple successors, callers must use the explicit successor relationships and relevant evidence to determine the appropriate current event.

### 6.14 Recommendation Summary

The recommended architecture establishes persistent event identity, explicit matching decisions, controlled identity operations, and historical traceability.

The core rule is:

**Event identity is a domain decision supported by evidence, not an automatic consequence of article similarity.**

## 7. Final Decision

This ADR is currently **Proposed**.

**Selected Alternative:** Not yet formally selected.

**Decision Status:** Proposed

**Decision Owner:** Product Owner

**Approved By:** Not yet approved

**Approval Date:** N/A

**Decision Rationale:**

Alternative C is recommended because it supports automated event intelligence while protecting identity integrity, provenance, and historical traceability.

The recommendation separates candidate similarity from confirmed event identity and treats merging and splitting as explicit domain operations.

The Product Owner must explicitly accept or reject this recommendation.

**Conditions or Restrictions:**

- No event identity policy is considered formally approved until this ADR is accepted.
- No universal matching thresholds are established by this ADR.
- Event matching must preserve uncertainty.
- Event identity operations must be auditable.
- Existing event and article history must not be silently deleted or rewritten.
- Implementation must remain consistent with ADR-001 and ADR-002.

**Deferred Questions:**

- Exact matching thresholds and calibration.
- Detailed event lifecycle states and transitions.
- Final event relationship taxonomy.
- Review ownership and escalation policy.
- Detailed reconciliation of previously published reports after merge or split.
- Final event identity data model and database constraints.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Stable event identities across processing runs.
- Explicit distinction between matching and similarity.
- Reduced risk of incorrect event merges.
- Better support for event continuation and development tracking.
- Historical traceability after merge and split operations.
- Improved provenance for event-level analysis and reporting.
- More reliable correction of incorrect associations.
- Support for automated processing without requiring automatic decisions in every case.

### 8.2 Negative Consequences

- Additional event identity and history records.
- More complex matching and association workflows.
- Additional validation and consistency requirements.
- Potential human-review workload for ambiguous cases.
- More complex historical resolution after splitting events.
- Additional work to reconcile downstream analyses and reports.

### 8.3 Technical Trade-Offs

The architecture favors correctness and traceability over maximum automatic matching coverage.

It requires explicit candidate records and identity operations rather than a simple similarity threshold.

Matching policies may evolve, but domain identity must remain independent of the specific algorithm or provider.

The system may initially leave more relationships unresolved until matching quality has been evaluated.

### 8.4 Operational Consequences

Operations must support:

- Inspection of candidate-event decisions.
- Review of ambiguous relationships.
- Event merge and split procedures.
- Recovery of interrupted identity operations.
- Monitoring of false matches and unresolved candidates.
- Reconciliation of affected reports and analyses.

Identity-changing operations require stronger validation than ordinary event updates.

### 8.5 Product and Business Consequences

The system can maintain coherent event dossiers over time.

However, reports may occasionally be delayed when event identity is uncertain or a consequential merge or split requires review.

The product should communicate uncertainty rather than presenting an uncertain event relationship as established fact.

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Incorrect event merge | Medium | High | Conservative matching policy, explicit confirmation, review, and reversible identity history |
| Duplicate event creation | Medium | Medium | Candidate generation, duplicate-event evaluation, and periodic reconciliation |
| Incorrect event split | Medium | High | Evidence-based split procedure, audit history, and controlled downstream reconciliation |
| Ambiguous cases accumulate | Medium | Medium | Review prioritization, policy tuning, and operational monitoring |
| Historical reports become misleading | Medium | High | Preserve report versions and original event references |
| Matching behavior changes after model updates | Medium | High | Versioned policies, regression tests, and explicit reprocessing |
| Concurrent identity operations conflict | Low to Medium | High | Atomic ownership, transaction boundaries, and idempotency |
| LLM-generated identity decision is unsupported | Medium | High | Structured outputs, independent validation, and restricted authority |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- Article Processing Pipeline
- Article Deduplication
- Event Candidate Generation
- Event Matching Service
- Event Identity Service
- Event Management Service
- Event Relationship Management
- Event History Management
- Review Service
- Analysis Pipeline
- Reporting Pipeline
- Processing Orchestration
- Observability and Evaluation

### 9.2 Affected Data Models and Interfaces

Proposed domain entities include:

- `Event`
- `EventVersion`
- `EventHistory`
- `EventMatchCandidate`
- `EventMatchDecision`
- `ArticleEventLink`
- `EventRelationship`
- `EventIdentityOperation`
- `EventIdentityAlias` or equivalent identity-resolution structure
- `EventReviewRecord`

The exact physical schema and repository boundaries must be defined in the data model and component architecture documents after the relevant ADRs are reviewed.

Proposed application operations include:

- `generate_event_candidates`
- `evaluate_event_match`
- `confirm_event_association`
- `reject_event_association`
- `create_event`
- `continue_event`
- `merge_events`
- `split_event`
- `resolve_event_identity`
- `record_event_identity_decision`

These are logical operations, not finalized implementation signatures.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-001 | Depends on / Related to | Establishes the event-centric architecture and separation of Article and Event. |
| GENI-ADR-002 | Depends on / Related to | Separates article deduplication from event matching. |
| GENI-ADR-008 | Related to | Defines evidence provenance and uncertainty representation supporting identity decisions. |
| GENI-ADR-012 | Related to | Defines semantic retrieval and similarity capabilities used in candidate generation. |
| GENI-ADR-016 | Related to | Defines idempotency, transactions, and recovery for identity operations. |
| GENI-ADR-004 | Related to | Publication policy must account for material event identity corrections. |
| GENI-ADR-014 | Related to | Human review may be required for ambiguous or consequential identity changes. |
| GENI-ADR-017 | Related to | Matching and evaluation operations may consume LLM resources and require usage tracking. |

## 10. Implementation Implications

### 10.1 Required Implementation Work

If accepted, implementation should include:

- Stable event identifiers.
- Explicit event candidate records.
- Structured event matching decisions.
- Separate confirmed article-event associations.
- Event continuation handling.
- Event relationship records.
- Event merge operations.
- Event split operations.
- Identity resolution.
- Historical event versions and operation records.
- Review integration for uncertain cases.
- Matching policy and model version tracking.
- Evaluation datasets for event matching.
- Operational monitoring for identity changes.

### 10.2 Migration or Compatibility Requirements

If an existing implementation contains event records without explicit identity history:

- Existing event identifiers must be preserved.
- Historical article-event associations must be retained.
- Migration must not silently merge or split events.
- Ambiguous existing relationships should be marked for review or remain unchanged.
- Any identity reconciliation must create an auditable operation.
- Existing reports must preserve their historical references.

The initial implementation may not require a large-scale migration, but the data model must not prevent future identity corrections.

### 10.3 Dependencies

- ADR-001: Event-centric architecture.
- ADR-002: Article deduplication and event matching separation.
- ADR-008: Evidence provenance and uncertainty.
- ADR-012: Semantic retrieval and similarity capabilities.
- ADR-016: Persistence, idempotency, and recovery.
- ADR-014: Human review operations where required.
- Component and data model contract updates.

### 10.4 Implementation Sequence

1. Define the Event domain contract and stable identity.
2. Define event candidate and matching-decision contracts.
3. Implement candidate generation independently of association persistence.
4. Implement matching evaluation and structured outcomes.
5. Implement confirmed article-event associations.
6. Implement event continuation and history recording.
7. Implement explicit event relationships.
8. Implement controlled merge and split operations.
9. Implement identity resolution and historical lookup.
10. Integrate review handling for ambiguous cases.
11. Add regression and evaluation datasets.
12. Add operational monitoring and recovery procedures.

### 10.5 Verification Requirements

Verification must demonstrate that:

- Similar articles about distinct events are not automatically merged.
- Different articles about the same occurrence can be associated with one event.
- An article can be linked to multiple distinct events.
- Continuation preserves event identity.
- Related but distinct developments retain separate identities.
- Merge operations preserve original identifiers and provenance.
- Split operations preserve the original identity and create traceable successors.
- Ambiguous cases remain unresolved or enter review.
- Repeated processing does not create duplicate identity operations.
- Interrupted operations can be recovered safely.
- Historical reports remain traceable after identity changes.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Every event has a stable internal identifier. | Domain and repository tests |
| AC-02 | Event identity is independent of article similarity scores. | Architecture inspection and tests |
| AC-03 | Multiple articles can be associated with one event. | Relationship tests |
| AC-04 | One article can be associated with multiple events. | Relationship tests |
| AC-05 | Candidate generation does not automatically create confirmed associations. | Workflow tests |
| AC-06 | Matching produces explicit structured outcomes. | Contract tests |
| AC-07 | An ambiguous candidate is not silently confirmed. | Matching policy tests |
| AC-08 | Event continuation preserves the event identifier. | Domain tests |
| AC-09 | Related but distinct events can maintain separate identities. | Scenario tests |
| AC-10 | Event merge preserves original identifiers and history. | Transaction and integration tests |
| AC-11 | Event split preserves the original identity and records successor relationships. | Transaction and integration tests |
| AC-12 | Historical identity resolution supports merged identities. | Repository tests |
| AC-13 | Split identities can resolve to multiple successors without arbitrary selection. | Repository and domain tests |
| AC-14 | Identity operations are idempotent. | Repeated-operation tests |
| AC-15 | Identity decisions record relevant evidence and policy versions. | Audit-record tests |
| AC-16 | Historical reports remain traceable after identity changes. | Reporting integration tests |
| AC-17 | LLM output cannot directly execute unvalidated identity operations. | Security and workflow tests |
| AC-18 | Identity operations can be recovered after interrupted processing. | Failure-injection and recovery tests |
| AC-19 | Matching quality can be evaluated against labeled examples. | Evaluation pipeline |
| AC-20 | Human identity corrections are auditable. | Review workflow tests |

Implementation verification is deferred until this ADR is formally accepted and the relevant capabilities are implemented.

## 12. Review and Reconsideration

### 12.1 Review Triggers

This ADR should be reviewed when:

- The event-centric domain model changes materially.
- Matching evaluation reveals unacceptable false-merge or false-split rates.
- New event categories require different identity semantics.
- Multilingual matching introduces significant ambiguity.
- Event merge or split operations create unacceptable operational complexity.
- New storage or processing constraints affect identity history.
- Publication and correction policies require different historical behavior.
- A major change is made to the event matching algorithm.

### 12.2 Review Schedule

**Review Date:** Not scheduled

**Review Owner:** Product Owner

### 12.3 Reconsideration Conditions

The recommendation should be reconsidered if persistent event identities and explicit identity operations prove disproportionately complex for the actual product requirements.

Any replacement approach must still demonstrate how it preserves source provenance, historical report traceability, and correction of incorrect event relationships.

## 13. References and Supporting Evidence

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Establishes the event-centric product architecture. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines component boundaries and event-processing responsibilities. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines the proposed Event, Article, relationship, and history data model. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines implementation sequencing and dependencies. |
| `docs/adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` | Internal ADR | Establishes the foundational event-centric recommendation. |
| [GENI-ADR-002](GENI-ADR-002-article-deduplication-and-event-matching.md) | Related Proposed ADR | Defines the separation of article deduplication and event matching; the ADR is published in this repository. |

The recommendation in this ADR is an architectural proposal based on the project's documented requirements and domain analysis.

No empirical event-matching accuracy, calibrated confidence threshold, or production performance measurement is claimed.

Such measurements must be obtained through a representative evaluation dataset before final matching thresholds are adopted.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-16 | Proposed | Initial proposal covering event identity, matching, continuation, merging, splitting, and historical traceability. | AI Architecture Assistant | 
| 1.1 | 2026-11-18 | Proposed | Defined per-revision matching cases, immutable case-level decisions, candidate boundaries, review supersession, and decision-authorized ArticleEventLink creation. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Clarified case-level NO_MATCH semantics and immutable, fingerprinted candidate-evaluation history. | AI Architecture Assistant |
| 1.3 | 2026-11-18 | Proposed | Defined preassigned event identity, versioned EventCreationPolicy, creation provenance/idempotency, and the successor MATCH requirement. | AI Architecture Assistant |

---

**End of ADR**