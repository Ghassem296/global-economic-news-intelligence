# GENI-ADR-001 — Event-Centric Intelligence Architecture

**Project:** Global Economic News Intelligence
**ADR ID:** GENI-ADR-001
**Title:** Event-Centric Intelligence Architecture
**Status:** Proposed
**Version:** 1.0
**Date:** 2026-11-16
**Decision Owner:** Product Owner
**Prepared By:** AI Architecture Assistant
**Approved By:** Not yet approved
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence is designed to monitor international economic and financially relevant developments, identify significant events, correlate reporting from multiple sources, and produce evidence-based intelligence reports.

A single important economic development may be reported by many publishers.

For example, a central bank interest-rate decision may generate separate articles covering:

- The official policy announcement.
- Statements from central bank officials.
- Market reactions.
- Analyst interpretations.
- Currency and bond movements.
- International economic implications.
- Subsequent policy clarification.

These articles may describe different aspects of the same underlying development. Treating each article as an independent intelligence item would fragment the information, produce repetitive reports, and make it difficult to maintain a coherent understanding of how the event develops over time.

The system therefore needs a primary organizational model that distinguishes individual published articles from the real-world events those articles describe.

The central architectural question is whether intelligence should be organized primarily around individual articles or around correlated real-world events.

An event-centric architecture would allow the system to aggregate relevant articles, evidence, entities, claims, analysis, and updates into a coherent event dossier.

However, event-centric processing also introduces challenges:

- Determining whether two articles describe the same event.
- Distinguishing a new event from a continuation or consequence of an existing event.
- Avoiding incorrect event merges.
- Recognizing when an existing event must be split.
- Preserving the original source material and its provenance.
- Maintaining a reliable event history.
- Handling uncertainty when the available evidence is insufficient.

These challenges must be addressed through dedicated event-intelligence policies and supporting ADRs.

If no architectural decision is made, different system components may adopt incompatible organizational models. This could result in duplicated intelligence, inconsistent reporting, fragmented event histories, and unreliable cross-source analysis.

## 2. Decision Question

Should Global Economic News Intelligence organize its primary intelligence workflow around real-world economic and economically relevant events, with individual articles retained as independent source records linked to those events?

If so, what foundational architectural principles should govern the relationship between articles, events, evidence, analysis, and reports?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- The system must collect and retain individual news articles as independent source records.
- The system must identify and represent meaningful real-world events.
- Multiple articles may be associated with one event.
- An article may be associated with multiple events when it substantively covers more than one distinct development.
- The system must preserve the relationship between an article and the event or events it supports.
- The system must support event dossiers containing relevant articles, entities, claims, evidence, analysis, and history.
- The system must support event updates as new information becomes available.
- The system must distinguish a new event from a continuation of an existing event.
- The system must preserve uncertainty when event identity or article-event relationships cannot be established confidently.
- The system must support reports that summarize an event using multiple sources.
- The system must preserve source attribution and evidence provenance.

### 3.2 Technical Constraints

- The architecture must support asynchronous acquisition and processing.
- Event processing must not require all information to be available in a single article.
- Article ingestion and event intelligence must be independently recoverable.
- The architecture must support deterministic workflows and structured LLM outputs.
- LLM-generated classifications, claims, and analysis must not be treated as verified facts without appropriate supporting evidence.
- Event identity must remain stable when additional articles are associated with an existing event.
- Storage and retrieval technology must remain subject to separate architectural decisions.
- The architecture must not require a particular vector database, embedding provider, or LLM vendor.

### 3.3 Business and Product Constraints

- Economic intelligence is the primary editorial focus.
- Political and geopolitical developments are relevant when they have meaningful economic, financial, trade, fiscal, monetary, or market implications.
- The product must reduce repetitive coverage of the same underlying development.
- Reports should provide a coherent understanding of developments rather than merely reproduce article summaries.
- The system is intended to operate internationally and must accommodate multiple publishers and languages.
- The system should support near-real-time processing without promising guaranteed real-time coverage.

### 3.4 Security and Privacy Constraints

- Collected article content must be treated as untrusted input.
- Source content must not be interpreted as instructions to the system or its LLM components.
- Source attribution and provenance must be preserved.
- Access to external source content must follow applicable technical, contractual, and legal restrictions.
- The architecture must not assume that technical access to an article grants permission to store or republish its full text.

### 3.5 Operational and Cost Constraints

- The architecture should support incremental processing rather than repeatedly processing every article associated with an event.
- Event updates should be idempotent where practical.
- Expensive LLM operations should be bounded by execution budgets and appropriate processing policies.
- The system should support monitoring of event-processing failures and ambiguous matches.
- The initial implementation should avoid unnecessary infrastructure complexity.

### 3.6 Legal and Content-Rights Constraints

- Article storage and retention must comply with applicable content rights and licensing restrictions.
- The event dossier should distinguish permitted source metadata, extracted information, quotations, and licensed content.
- The event-centric model must not imply permission to republish source material.
- Detailed content acquisition, retention, and republication policies are addressed separately.

### 3.7 Explicit Non-Goals

This ADR does not decide:

- The exact event matching algorithm.
- The numerical thresholds for event matching or confidence scoring.
- The detailed event lifecycle and transition rules.
- The rules for merging or splitting existing events.
- The embedding model or vector storage technology.
- The initial database technology.
- The complete article retention and licensing policy.
- The market data provider or market-impact calculation methodology.
- The final report publication and human-review workflow.

These concerns require separate decisions or detailed specifications.

## 4. Alternatives Considered

### 4.1 Alternative A: Article-Centric Intelligence Architecture

**Description:**

Treat each collected article as the primary intelligence object.

Each article is processed independently, and reports or summaries are generated directly from individual articles. Relationships between articles may be added as secondary metadata.

**Advantages:**

- Simple initial data model.
- Straightforward ingestion and processing.
- Article-level processing is relatively easy to isolate.
- Fewer initial event-management requirements.
- Suitable for products primarily focused on article discovery or summarization.

**Disadvantages:**

- Multiple articles about the same development produce fragmented intelligence.
- Repeated reporting can generate duplicate or repetitive outputs.
- Cross-source corroboration becomes more difficult.
- Event evolution is difficult to represent coherently.
- Historical context and consequences are distributed across separate records.
- The system may confuse the number of articles with the significance of an event.

**Risks:**

- Duplicate reporting and fragmented intelligence.
- Inconsistent conclusions across articles covering the same event.
- Poor support for event-level monitoring and updates.
- Additional complexity when event-level capabilities are introduced later.

**Estimated Complexity:** Low initially; potentially High as event-level capabilities are added.

### 4.2 Alternative B: Event-Centric Intelligence Architecture

**Description:**

Treat real-world events as the primary intelligence objects.

Articles remain independent source records and are linked to one or more events. Event dossiers aggregate relevant source material, evidence, claims, entities, analysis, and history.

The event becomes the primary unit for intelligence processing, monitoring, and reporting.

**Advantages:**

- Consolidates multiple reports about the same development.
- Supports cross-source corroboration.
- Provides a coherent view of event evolution.
- Enables event-level importance ranking and monitoring.
- Supports historical context and impact analysis.
- Reduces repetitive reporting.
- Aligns with the product's objective of generating economic intelligence rather than simply summarizing articles.

**Disadvantages:**

- Requires event detection and matching capabilities.
- Introduces event identity and lifecycle management.
- Incorrect matches can combine unrelated developments.
- Missed matches can fragment one event across multiple dossiers.
- Requires explicit uncertainty handling and event-history management.
- More complex than article-centric processing during initial development.

**Risks:**

- False event merges may contaminate analysis and reports.
- False event splits may fragment the evidence base.
- Incorrect event relationships may propagate through downstream processing.
- Event matching may require additional computation and operational monitoring.

**Estimated Complexity:** Medium to High.

### 4.3 Alternative C: Hybrid Article-and-Event Architecture

**Description:**

Treat articles and events as two co-equal primary intelligence objects.

Both article-level and event-level processing produce independent intelligence outputs. The system maintains separate reporting and analysis workflows for each object type.

**Advantages:**

- Supports article-level and event-level products.
- Provides flexibility for different use cases.
- Allows users to consume individual article intelligence and event dossiers.
- Can accommodate products that require both independent article analysis and event aggregation.

**Disadvantages:**

- Creates two potentially competing primary intelligence workflows.
- Increases data-model and orchestration complexity.
- May duplicate analysis and reporting responsibilities.
- Requires additional rules to determine which object takes precedence.
- May increase implementation and maintenance costs.

**Risks:**

- Inconsistent results between article-level and event-level analysis.
- Duplicated processing and storage.
- Unclear ownership of intelligence outputs.
- Greater architectural complexity than required by the initial product scope.

**Estimated Complexity:** High.

## 5. Evaluation and Comparison

| Evaluation Criterion | Article-Centric | Event-Centric | Hybrid |
|---|---|---|---|
| Product Fit | Low | High | Medium to High |
| Cross-Source Corroboration | Limited | Strong | Strong |
| Event Evolution Tracking | Weak | Strong | Strong |
| Initial Implementation Complexity | Low | Medium to High | High |
| Long-Term Maintainability | Limited for event intelligence | High if matching is reliable | Medium |
| Duplicate Intelligence Risk | High | Lower | Medium |
| Event Identity Requirements | Minimal | Significant | Significant |
| Historical Context | Fragmented | Consolidated | Consolidated |
| Processing Flexibility | High at article level | High at event level | High |
| Reversibility | Medium | Medium | Medium |
| Alignment with Product Purpose | Low | High | Medium to High |

### 5.1 Evaluation Priorities

The most important criteria are:

1. **Product Fit:** The system is intended to produce economic intelligence, not simply article summaries.
2. **Cross-Source Corroboration:** Multiple independent sources should contribute to a more complete understanding of an event.
3. **Event Evolution:** The system must represent how a development changes over time.
4. **Evidence Integrity:** Every important claim must retain its source and supporting evidence.
5. **Operational Reliability:** Incorrect event matching must not silently contaminate downstream analysis.
6. **Maintainability:** The architecture should provide clear boundaries between article acquisition and event intelligence.

Article-centric processing is simpler initially, but does not adequately support the product's primary objective.

The hybrid alternative offers flexibility but introduces two competing intelligence workflows that are not justified by the initial product scope.

The event-centric alternative provides the strongest alignment with the intended product.

## 6. Recommended Decision

**Recommended Alternative:** Alternative B — Event-Centric Intelligence Architecture

The recommended architecture is event-centric, with articles retained as independent source records.

### 6.1 Core Architectural Principles

#### Principle 1: Article and Event Are Separate Domain Entities

An Article represents a published source item.

An Event represents a meaningful real-world development.

Neither entity should be treated as a substitute for the other.

#### Principle 2: Articles Are Linked to Events

The relationship between articles and events must support multiple articles per event and, where justified, multiple events per article.

The relationship must preserve relevant association metadata and confidence where applicable.

#### Principle 3: Articles Remain Independently Traceable

Each article must retain its own:

- Source identity.
- Original URL or source reference.
- Publication metadata.
- Original language.
- Acquisition and processing history.
- Content fingerprint or deduplication metadata where applicable.
- Provenance information.

Associating an article with an event must not remove its independent identity.

#### Principle 4: Events Are the Primary Intelligence Aggregation Unit

An event dossier should be capable of aggregating:

- Related articles.
- Relevant entities.
- Claims and assessments.
- Supporting and contradicting evidence.
- Event timeline and history.
- Economic and financial context.
- Market observations where available.
- AI-generated analysis.
- Report versions and publication decisions.

The exact persistence structure is addressed in the data model and relevant ADRs.

#### Principle 5: Event Matching Must Preserve Uncertainty

The system must not automatically merge two events solely because their articles have similar wording or semantic similarity.

Event matching must consider relevant context, including:

- Event type.
- Entities involved.
- Geographic scope.
- Temporal context.
- Economic subject.
- Underlying development.
- Available supporting evidence.

Where confidence is insufficient, the system must preserve ambiguity rather than silently create an incorrect association.

#### Principle 6: Event Updates Must Preserve History

New information may update an existing event dossier.

However, previous information, evidence, and analysis must remain traceable.

An update must not silently overwrite historical facts or previously published conclusions.

#### Principle 7: Intelligence Must Be Evidence-Based

The system must distinguish:

- Verified or independently corroborated facts.
- Claims attributed to sources.
- AI-generated analysis.
- Forecasts and projections.
- Unknown or unverified information.

An event dossier must not imply that every statement within it has the same evidential status.

#### Principle 8: Reports Are Derived from Event Intelligence

Event-level reports should be generated from the available event dossier and its supporting evidence.

A report must preserve references to its underlying sources and analysis.

The report must not be treated as an independent source of truth.

### 6.2 Recommended Processing Flow

The recommended high-level processing flow is:

1. Acquire articles from registered sources.
2. Normalize article metadata and permitted content.
3. Identify exact and near-duplicate articles.
4. Classify article topics and extract relevant entities.
5. Detect candidate events and evaluate their relationship to existing events.
6. Associate articles with events when sufficient evidence exists.
7. Extract claims and establish evidence relationships.
8. Enrich event dossiers with relevant context and historical information.
9. Generate event-level analysis.
10. Evaluate publication eligibility and review requirements.
11. Generate and deliver reports according to publication policy.
12. Continue monitoring events as new information arrives.

This flow is a logical processing model. It does not require every stage to execute synchronously or as one indivisible transaction.

### 6.3 Why the Other Alternatives Were Not Selected

**Alternative A — Article-Centric:**

Rejected as the primary architecture because it does not adequately support event evolution, cross-source corroboration, or consolidated economic intelligence.

Article-level processing remains necessary as an acquisition and normalization capability.

**Alternative C — Hybrid:**

Not recommended because it creates two competing primary intelligence workflows and adds complexity without a sufficiently justified initial product requirement.

Article-level capabilities may still exist as supporting functions without making articles and events co-equal primary intelligence objects.

### 6.4 Assumptions Supporting the Recommendation

- The primary product output is event-based economic intelligence.
- Multiple sources will frequently report on the same underlying development.
- The system needs to monitor how events evolve over time.
- Event-level analysis provides more value than isolated article summaries.
- Event identity and matching can be improved through explicit policies, evidence, and evaluation.
- The system can preserve ambiguity when automatic matching is not sufficiently reliable.

**Recommendation Prepared By:** AI Architecture Assistant

**Recommendation Date:** 2026-11-16

## 7. Final Decision

This ADR is currently a proposal and has not been formally approved.

**Selected Alternative:** Pending formal approval; Alternative B is recommended.

**Decision Status:** Proposed

**Decision Owner:** Product Owner

**Approved By:** Not yet approved

**Approval Date:** N/A

**Decision Rationale:**

The recommended event-centric architecture best aligns with the product's objective of producing coherent, evidence-based economic intelligence from multiple international sources.

It establishes a clear distinction between published articles and real-world events while providing a foundation for event-level corroboration, historical tracking, analysis, and reporting.

The recommendation does not authorize a specific event matching algorithm, database, embedding technology, or publication mechanism. These decisions remain within the scope of their respective ADRs.

**Conditions or Restrictions:**

- Article and Event must remain separate domain entities.
- Event matching must preserve uncertainty.
- Source provenance must remain traceable.
- Event updates must preserve historical information.
- The detailed event identity and lifecycle policy must be addressed by GENI-ADR-011.
- Article deduplication must remain distinct from event matching under GENI-ADR-002.

**Deferred Questions:**

- Exact event identity and matching rules.
- Event continuation, merging, and splitting.
- Event lifecycle states and permitted transitions.
- Semantic similarity and embedding strategy.
- Detailed evidence and claim data structures.
- Market data integration.
- Publication and human-review policy.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- The primary intelligence model aligns with the product's purpose.
- Multiple sources can contribute to a consolidated event dossier.
- Event evolution can be represented over time.
- Cross-source corroboration becomes a first-class capability.
- Duplicate intelligence and repetitive reporting can be reduced.
- Historical context and economic implications can be evaluated at event level.
- The architecture provides a foundation for event monitoring and future intelligence capabilities.

### 8.2 Negative Consequences

- Event detection and matching introduce additional processing complexity.
- Event identity requires explicit domain rules.
- Incorrect associations may affect downstream analysis.
- Event history and revisions require additional data-management responsibilities.
- Event-level processing may increase LLM and infrastructure costs.
- Quality evaluation becomes more complex than evaluating article summaries alone.

### 8.3 Technical Trade-Offs

The architecture prioritizes event-level coherence over the simplicity of independent article processing.

This requires a more sophisticated relationship model and explicit handling of uncertain event associations.

The system should favor preserving separate candidate events over automatically merging uncertain matches.

This may temporarily produce duplicate event candidates, but reduces the risk of contaminating an event dossier with unrelated information.

### 8.4 Operational Consequences

The system will require:

- Monitoring of event detection and matching quality.
- Monitoring of unresolved article-event associations.
- Event-level processing and recovery mechanisms.
- Traceable event history.
- Evaluation datasets for event matching and event identity.
- Operational visibility into failed or ambiguous event-processing steps.

### 8.5 Product and Business Consequences

The primary user-facing intelligence object becomes the event dossier rather than the individual article.

Individual article access remains available for source inspection, verification, and attribution.

The system can support article-level discovery as a secondary capability without changing the primary intelligence model.

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Incorrect event merge | Medium | High | Explicit matching policy, confidence handling, evidence checks, and evaluation |
| Event fragmentation | Medium | Medium to High | Candidate matching, periodic reconciliation, and event-history tracking |
| Incorrect article-event association | Medium | High | Traceable association records and reversible association operations |
| Loss of historical information | Low to Medium | High | Append-only event history and versioned analysis |
| Excessive processing cost | Medium | Medium | Incremental processing, bounded LLM execution, and deduplication |
| Inconsistent event interpretation | Medium | High | Shared event taxonomy, explicit policies, and evaluation datasets |

These likelihood and impact assessments are initial qualitative estimates and must be revisited as operational evidence becomes available.

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- NewsCollector
- ArticleNormalizer
- ArticleDeduplicator
- TopicClassifier
- EntityExtractor
- EntityResolver
- ClaimExtractor
- EventDetector
- EventMatcher
- EventService
- EventHistoryService
- EvidenceService
- EvidenceAnalyzer
- ImportanceRanker
- ImpactAnalyzer
- HistoricalContextService
- ReportGenerator
- PublicationPolicy
- WorkflowOrchestrator

### 9.2 Affected Data Models and Interfaces

The architecture requires conceptual support for:

- Article
- Event
- ArticleEventLink
- Entity
- Claim
- Evidence
- Analysis
- Report
- EventHistory

The exact attributes, relationships, constraints, and persistence mechanisms are defined in the data model and relevant technical ADRs.

### 9.3 Affected Documents

- `01-product-and-system-architecture.md`
- `02-component-architecture-and-interfaces.md`
- `03-data-model-and-storage-design.md`
- `04-implementation-plan-and-roadmap.md`
- `07-architecture-decision-records.md`
- `docs/adr/README.md`

The generic Agent Template documents remain reference documents and are not required to implement the event-centric domain model.

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-002 | Related to | Defines article deduplication separately from event matching. |
| GENI-ADR-004 | Related to | Defines publication decisions and quality gates. |
| GENI-ADR-008 | Related to | Defines evidence provenance and uncertainty. |
| GENI-ADR-011 | Depends on / Extends | Defines event identity, continuation, merging, and splitting. |
| GENI-ADR-012 | Related to | Defines semantic retrieval and similarity calculation. |
| GENI-ADR-014 | Related to | Defines review, corrections, and withdrawals. |
| GENI-ADR-015 | Related to | Defines market data integration and impact classification. |
| GENI-ADR-016 | Related to | Defines processing reliability and recovery. |

## 10. Implementation Implications

### 10.1 Required Implementation Work

Once accepted, implementation should establish:

- Separate Article and Event domain entities.
- A persistent relationship between articles and events.
- Event-level aggregation interfaces.
- Traceable article-event association operations.
- Event history and update tracking.
- Event-level evidence and analysis relationships.
- Event-oriented report generation.

### 10.2 Migration or Compatibility Requirements

No existing production data migration is currently identified.

The initial implementation should establish the event-centric model before substantial production data accumulates.

If article-centric prototype data already exists when implementation begins, a migration strategy must be documented before that data is converted.

### 10.3 Dependencies

Implementation depends on:

- Acceptance of this ADR.
- Definition of the article deduplication and event matching boundary.
- Definition of event identity and lifecycle policies.
- Alignment of the data model and component contracts.
- Establishment of evidence provenance requirements.
- A functioning event-processing workflow.

### 10.4 Implementation Sequence

A recommended implementation sequence is:

1. Define Article and Event domain contracts.
2. Define the ArticleEventLink relationship.
3. Implement article acquisition and normalization.
4. Implement article-level deduplication.
5. Implement basic event detection and candidate matching.
6. Implement explicit handling of ambiguous associations.
7. Implement event dossier aggregation.
8. Add event history and evidence relationships.
9. Integrate event-level analysis and report generation.
10. Evaluate event matching and dossier quality using representative datasets.

This sequence is subject to the implementation roadmap and the accepted decisions of related ADRs.

### 10.5 Verification Requirements

The implementation should demonstrate that:

- Multiple articles can be associated with one event.
- One article can be associated with multiple events when justified.
- Articles remain independently identifiable and traceable.
- Article deduplication does not automatically merge events.
- Uncertain event associations are not silently treated as confirmed.
- Event updates preserve relevant historical information.
- Event dossiers retain source and evidence provenance.
- Reports can be traced back to their supporting event information.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Article and Event exist as separate domain entities. | Domain model inspection and automated tests |
| AC-02 | The model supports multiple articles associated with one event. | Relationship tests |
| AC-03 | The model supports justified multiple-event associations for one article. | Relationship tests |
| AC-04 | Article identity is preserved independently of event associations. | Persistence and integration tests |
| AC-05 | Article deduplication and event matching are separate operations. | Component and workflow tests |
| AC-06 | Ambiguous event associations can remain unresolved. | Event-matching tests |
| AC-07 | Event updates preserve historical traceability. | Event-history tests |
| AC-08 | Event-level reports can retain references to supporting sources. | Report provenance tests |
| AC-09 | Event dossiers distinguish source claims from AI-generated analysis. | Evidence and analysis tests |

These criteria define the expected architecture and implementation behavior. Detailed thresholds and test datasets must be defined in the relevant specifications and evaluation plans.

Implementation verification is deferred until the ADR is formally accepted and the relevant capabilities are implemented.

## 12. Review and Reconsideration

### 12.1 Review Triggers

This decision should be reviewed if:

- The product scope changes to prioritize independent article intelligence.
- Event-level intelligence no longer provides sufficient product value.
- Event matching proves operationally unreliable despite reasonable improvements.
- New product requirements justify separate article-level and event-level intelligence workflows.
- Significant changes to source acquisition or data licensing affect the event dossier model.
- New technical constraints make the recommended architecture impractical.

### 12.2 Review Schedule

**Review Date:** Before implementation of the event-intelligence workflow.

**Review Owner:** Product Owner

### 12.3 Reconsideration Conditions

The architecture may be reconsidered if evaluation demonstrates that event-centric aggregation cannot meet the product's reliability or operational requirements.

Any replacement architecture must preserve historical traceability and explicitly address the consequences of changing the primary intelligence model.

## 13. References and Supporting Evidence

| Reference | Type | Relevance |
|---|---|---|
| `01-product-and-system-architecture.md` | Internal | Defines product purpose and high-level architecture. |
| `02-component-architecture-and-interfaces.md` | Internal | Defines component responsibilities and contracts. |
| `03-data-model-and-storage-design.md` | Internal | Defines the domain model and persistence requirements. |
| `04-implementation-plan-and-roadmap.md` | Internal | Defines implementation stages and dependencies. |
| GENI-ADR-002 | Related ADR | Article deduplication and event matching separation. |
| GENI-ADR-011 | Related ADR | Event identity and lifecycle policies. |
| GENI-ADR-012 | Related ADR | Semantic retrieval and similarity calculation. |

The references above identify relevant project materials. They do not imply that the referenced ADRs have been accepted.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-16 | Proposed | Initial proposal for an event-centric intelligence architecture. | AI Architecture Assistant |

---

**End of ADR**