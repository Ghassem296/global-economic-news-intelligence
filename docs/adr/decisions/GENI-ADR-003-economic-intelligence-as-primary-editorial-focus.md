# GENI-ADR-003 — Economic Intelligence as the Primary Editorial Focus

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-003  
**Title:** Economic Intelligence as the Primary Editorial Focus  
**Status:** Proposed  
**Version:** 1.2  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

The product monitors international news but is not intended to become a general-purpose news aggregator. Its value is to explain economically meaningful developments, their transmission mechanisms, affected actors and markets, supporting evidence, and uncertainty. Political, geopolitical, corporate, regulatory, and social developments may be relevant when they have a defensible economic connection. Without an explicit editorial boundary, the system may over-collect general news or exclude upstream developments that materially affect trade, fiscal conditions, energy, supply chains, employment, or economic policy.

This ADR is a proposal for formal review. It does not approve a production implementation or override an existing accepted decision.

## 2. Decision Question

What editorial principle should determine which developments are in scope and how non-economic developments may be included without turning the product into a general news platform?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Prioritize economic developments and explain their relevance through explicit economic channels.
- Include non-economic subject matter when a meaningful economic connection is established or reasonably assessable.
- Distinguish event importance, economic relevance, and economic impact.
- Preserve unknown or not-established relevance rather than forcing every story into an economic category.
- Version topic taxonomies and editorial assessment policy.

### 3.2 Technical Constraints
- Event-centric aggregation remains the primary intelligence model.
- Topic classification, economic relevance, importance, and impact remain separate responsibilities.
- No universal numeric threshold is assumed without a representative evaluation set.
- Initial release is text-based and operationally simple.

### 3.3 Business and Product Constraints
- The initial product remains text-based economic intelligence.
- The approach must support incremental implementation and traceable quality evaluation.
- Proposed technology and policy choices are not mandatory until formally accepted.

### 3.4 Security and Privacy Constraints
- External source content and model outputs are untrusted until validated.
- Apply least privilege to tools, services, and external integrations.
- Do not expose secrets or unnecessary protected content through ordinary logs.

### 3.5 Operational and Cost Constraints
- The initial deployment should avoid unnecessary distributed infrastructure.
- Operational cost and complexity must be measured against expected workload.
- Timeouts, retries, recovery, and observability must be explicitly designed.

### 3.6 Legal and Content-Rights Constraints
- Technical access to source content does not imply permission to store, process externally, transform, quote, or republish it.
- Applicable licensing, privacy, contract, and jurisdictional requirements must be reviewed before production use.

### 3.7 Explicit Non-Goals
- This ADR does not select unmeasured numeric thresholds or invent performance claims.
- This ADR does not approve a database, provider, model, or external service unless explicitly stated as a proposed conditional choice.
- This ADR does not replace the approval process defined in the ADR governance document.

## 4. Alternatives Considered

### 4.1 Alternative A — General-purpose news platform

**Description:** Treat broad international news as the primary product and attach economic summaries as one category.

**Advantages:**
- Broad discovery and coverage
- simple inclusion by source availability.

**Disadvantages:**
- Dilutes the economic-intelligence purpose
- increases collection, review, and analysis cost.

**Risks:**
- Product scope may expand without a clear quality boundary.

**Estimated Complexity:** High

### 4.2 Alternative B — Economics and financial-market news only

**Description:** Restrict collection to items already labeled as economics or financial-market news.

**Advantages:**
- Narrower initial scope
- simpler source and topic filtering.

**Disadvantages:**
- Misses upstream geopolitical, regulatory, corporate, or social developments with material economic effects.

**Risks:**
- Important leading indicators may be systematically excluded.

**Estimated Complexity:** Low initially

### 4.3 Alternative C — Economic intelligence as editorial focus

**Description:** Prioritize economic events and include broader developments when a defensible economic connection or transmission pathway exists.

**Advantages:**
- Matches product mission
- includes upstream drivers
- permits explicit uncertainty.

**Disadvantages:**
- Requires maintained editorial rules and evaluation
- boundary cases remain.

**Risks:**
- Weak relevance rules may over-include tangential stories.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | General-purpose news platform | Economics and financial-market news only | Economic intelligence as editorial focus |
|---|---|---|---|
| Fit with product purpose | Low | Medium | High |
| Upstream economic coverage | Medium | Low | High |
| Editorial scope control | Low | High | High |
| Risk of general-news drift | High | Low | Medium |
| Evaluation complexity | Low | Medium | Medium |

The principal evaluation priorities are:
- Prioritize economic developments and explain their relevance through explicit economic channels.
- Include non-economic subject matter when a meaningful economic connection is established or reasonably assessable.
- Distinguish event importance, economic relevance, and economic impact.
- Preserve unknown or not-established relevance rather than forcing every story into an economic category.

Unmeasured latency, throughput, quality, and cost are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Economic intelligence as the editorial focus.

The product should determine editorial inclusion according to economic relevance and analytical usefulness. This is an editorial-scope assessment, not an overall event-importance ranking: Event Importance remains a separate assessment of the event's general significance and monitoring priority, while Economic Impact remains a separate assessment of realized or potential consequences. Non-economic subject matter may be included when a demonstrated or plausible transmission pathway connects it to economic activity, policy, institutions, or markets. The system must label the strength and uncertainty of that connection and must not infer realized impact or overall importance from relevance alone.

**Rationale:**
- Aligns source selection, analysis, reporting, and evaluation with one product purpose.
- Avoids the blind spots of a financial-news-only filter.
- Provides an explicit boundary for broader political and geopolitical coverage.

**Assumptions:**
- The intended audience values explanation of economic consequences rather than general headlines.
- The product will cover macroeconomics, policy, trade, industry, energy, public finance, and financially relevant geopolitical risk.
- Editorial inclusion rules will evolve through reviewed examples.

**Deferred Questions:**
- Exact relevance taxonomy and category boundaries.
- Quantitative relevance thresholds and ranking weights.
- Source-specific inclusion rules and coverage targets.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The authorized decision owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded; see the recommendation in Section 6.

**Conditions or Restrictions:**
- Keep this ADR in Proposed status until explicit approval is recorded.
- Do not treat deferred questions or illustrative examples as accepted implementation values.
- Any implementation assumption made before approval must be reversible, documented, and assigned a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Clear product identity and editorial boundary.
- Coverage of upstream developments without becoming a general news feed.
- Better alignment between data collection and analysis.

### 8.2 Negative Consequences
- Requires ongoing editorial policy maintenance.
- Some developments will remain ambiguous and require monitoring or review.

### 8.3 Technical Trade-Offs
A broader relevance boundary improves coverage of leading indicators but raises the risk of weak or speculative inclusion. A narrow boundary improves precision but can miss early-stage economic risks. The trade-off must be measured rather than resolved through a universal score.

### 8.4 Operational Consequences
Taxonomy and editorial policy changes require versioned rollout, representative regression cases, and controlled reprocessing.

### 8.5 Product and Business Consequences
Reports should explain why a broader political or geopolitical development is included and distinguish demonstrated links from plausible but uncertain pathways.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Editorial scope drift | Medium | High | Use an approved taxonomy, explicit non-goals, and periodic review. |
| Exclusion of upstream risks | Medium | High | Include indirect transmission paths and evaluate geopolitical cases. |
| False economic attribution | Medium | High | Require evidence-linked relevance rationale and separate impact assessment. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- TopicClassifier
- EconomicRelevanceAssessor
- ImportanceRanker
- ImpactAnalyzer
- EventDetector
- ReportGenerator

### 9.2 Affected Data Models and Interfaces
- TopicClassification
- Analysis records for relevance, importance, and impact
- Event dossier and report provenance

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-001 | Depends on / Related to | Establishes the event-centric domain model used for editorial aggregation. |
| GENI-ADR-008 | Related to | Provides evidence and uncertainty rules for economic relevance claims. |
| GENI-ADR-015 | Related to | Defines how measured market data may support market-impact analysis. |
| GENI-ADR-019 | Related to | Defines separate importance, relevance, and impact assessment methodology. |

These relationships do not imply that any related Proposed ADR has been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define an editorial scope policy and economic-topic taxonomy.
- Create reviewed examples for direct, indirect, contextual, not-established, and unknown relevance.
- Make the relevance assessment explain its transmission pathway and evidence.
- Measure both false inclusion and false exclusion on a representative dataset.
- Update source priorities and report templates to reflect product scope.

### 10.2 Migration or Compatibility Requirements
Existing data and implementation choices must be inspected before migration is designed. No production migration is claimed by this proposal. Any schema or interface migration must preserve historical traceability and must be tested from the current baseline.

### 10.3 Dependencies
- GENI-ADR-001 — Establishes the event-centric domain model used for editorial aggregation.
- GENI-ADR-008 — Provides evidence and uncertainty rules for economic relevance claims.
- GENI-ADR-015 — Defines how measured market data may support market-impact analysis.
- GENI-ADR-019 — Defines separate importance, relevance, and impact assessment methodology.

### 10.4 Implementation Sequence
1. Approve the editorial scope and non-goals.
2. Define initial topic and transmission-channel taxonomy.
3. Create a reference dataset including geopolitical and non-economic upstream developments.
4. Implement classification and relevance assessment as separate tasks.
5. Evaluate and revise the policy before automated ranking depends on it.

### 10.5 Verification Requirements
- Review a mixed dataset of economic, political, geopolitical, corporate, and general-news examples.
- Verify that a high-importance event can have unknown or low economic relevance.
- Verify that an upstream non-economic event can be included with an explicit transmission pathway.
- Measure false inclusion and false exclusion separately.

Implementation verification remains deferred until this ADR is accepted and the corresponding capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | The product documentation identifies economic intelligence as the primary editorial focus. | Document review |
| AC-02 | Non-economic events are included only with an explicit economic relevance rationale or a clearly labeled unresolved case. | Policy and workflow tests |
| AC-03 | Importance, economic relevance, and economic impact are not treated as interchangeable values. | Schema and component contract tests |
| AC-04 | Editorial policy and taxonomy versions are retained with classifications and assessments. | Persistence tests |
| AC-05 | A reference evaluation set measures false inclusion and exclusion. | Evaluation report |

Any quantitative threshold must be grounded in representative datasets, operational measurements, contractual requirements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Material change in product audience or objectives.
- Evidence of systematic false inclusion or exclusion.
- Expansion into new economic domains or jurisdictions.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Material change in product audience or objectives. Evidence of systematic false inclusion or exclusion. Expansion into new economic domains or jurisdictions.

Reconsider this recommendation when its core assumptions are no longer valid or measured evidence demonstrates that it does not meet project requirements. A replacement decision must be recorded in a new or superseding ADR.

## 13. References and Supporting Evidence

The references below are internal project documents used to establish the current documented context. They are not claimed as empirical performance measurements or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Defines product scope and the distinction between event importance, economic relevance, and impact. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines classification, relevance assessment, and event-intelligence component boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines versioned Analysis and classification data. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines staged implementation and evaluation. |
| `docs/adr/README.md` | Internal | Registers this decision topic and its dependencies. |

External legal review, provider measurements, market-data coverage measurements, and model-quality benchmarks remain outstanding wherever relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Initial proposal prepared for architecture review | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Clarified editorial inclusion versus Event Importance and Economic Impact to align with GENI-ADR-019. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |

**End of ADR**
