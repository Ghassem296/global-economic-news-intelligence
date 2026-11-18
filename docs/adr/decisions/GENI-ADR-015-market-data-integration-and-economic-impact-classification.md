# GENI-ADR-015 — Market Data Integration and Economic Impact Classification

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-015  
**Title:** Market Data Integration and Economic Impact Classification  
**Status:** Proposed  
**Version:** 1.0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

GENI may compare events with market observations and analyze consequences across currencies, rates, commodities, equities, sectors, trade, and macroeconomic indicators. Observed price changes do not prove event causality, and a market reaction is not equivalent to broader economic impact. Market-data access also involves licensing, instrument identity, timestamp alignment, session calendars, provider quality, and missing observations.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

How should market observations be sourced, normalized, aligned with events, and used to distinguish measured market reactions from source-reported responses and analytical causal interpretations?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Treat market observations as source-attributed measurements with instrument, value, unit, time, and provider provenance.
- Preserve bid/ask/mid/close or other price-type semantics where applicable.
- Normalize instrument identity, currency, units, time zones, trading sessions, and baseline context.
- Distinguish observed market reaction, source-reported reaction, inferred implication, and unknown.
- Do not infer causality from temporal proximity alone.
- Evaluate licensing and external-processing rights for market data.
- Keep broader economic-impact methodology distinct from market-observation ingestion.

### 3.2 Technical Constraints
- Market-data rights are independent of news-content rights.
- No provider, instrument universe, timeframe, or frequency is selected here.
- ADR-019 defines broader assessment semantics; this ADR focuses on market observations and reactions.
- A dedicated time-series platform is not automatically required.

### 3.3 Business and Product Constraints
- The initial product remains event-centric economic intelligence with text reports as its first release.
- The design must support incremental implementation and explicit evaluation.
- Proposals remain provisional until the decision owner records approval.

### 3.4 Security and Privacy Constraints
- Source content and model output are untrusted until validated.
- Only authorized application services and reviewers may change authoritative state.
- Secrets and unnecessary protected content must not appear in ordinary logs.

### 3.5 Operational and Cost Constraints
- Avoid unnecessary distributed infrastructure in the initial release.
- Measure cost and complexity against workload and reliability requirements.
- Failures, retries, recovery, and audit must be observable.

### 3.6 Legal and Content-Rights Constraints
- Access does not itself authorize retention, external processing, transformation, quotation, or republication.
- Source terms, licensing, privacy, and jurisdictional restrictions must be reviewed before production use.

### 3.7 Explicit Non-Goals
- This ADR does not invent unmeasured numerical thresholds or performance guarantees.
- This ADR does not approve a provider, database, or model merely by listing it as an alternative.
- This proposal does not supersede the ADR approval process.

## 4. Alternatives Considered

### 4.1 Alternative A — Price movement as event impact

**Description:** Treat a price movement after an event as its measured impact.

**Advantages:**
- Simple narrative and low data-model complexity.

**Disadvantages:**
- Confuses measurement with causation and ignores confounders.

**Risks:**
- False causal attribution and misleading reports.

**Estimated Complexity:** Low

### 4.2 Alternative B — No market-data integration

**Description:** Use news sources and qualitative analysis only.

**Advantages:**
- Avoids market-feed cost and licensing.

**Disadvantages:**
- Cannot independently verify market reactions.

**Risks:**
- Reports may present source claims without independent market context.

**Estimated Complexity:** Low

### 4.3 Alternative C — Provenance-aware observations plus separate analysis

**Description:** Ingest authorized measurements, preserve context, and assess causality separately.

**Advantages:**
- Traceable measurement
- supports uncertainty and multiple channels.

**Disadvantages:**
- Requires provider, instrument, time, and licensing integration.

**Risks:**
- Incomplete data or bad alignment may mislead analysts.

**Estimated Complexity:** Medium to High

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Price movement as event impact | No market-data integration | Provenance-aware observations plus separate analysis |
|---|---|---|---|
| Measurement integrity | Low | Not available | High |
| Causal validity | Low | Avoids claim | Separate assessment required |
| Data cost | Low | Low | Provider dependent |
| Traceability | Low | Medium | High |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Provenance-aware market observations with separate impact and causality assessment.

Represent market data as independently sourced observations with instrument identity, measurement type, units, provider, observation time, session/calendar context, and baseline where available. A market-reaction assessment may describe a measured movement or source-reported reaction, but causal contribution requires separate analysis with evidence, comparison, uncertainty, and confounder discussion. Broader economic-impact analysis remains channel-based and is governed by GENI-ADR-019. Provider, instrument universe, and acquisition frequency remain open until rights and coverage are verified.

**Rationale:**
- Separates measurement from inference and causal explanation.
- Preserves context required to interpret prices and indicators.
- Supports economic channels without collapsing them into one market score.

**Deferred Questions:**
- Market-data provider and licensing terms.
- Initial instrument universe and frequency.
- Calendar, session, and baseline methodology.
- Causal-attribution methodology and evaluation dataset.
- Time-series storage and retention design.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The Project Owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review; Section 6 contains the recommendation.

**Conditions or Restrictions:**
- Maintain Proposed status until explicit approval is recorded.
- Do not treat deferred questions or example values as settled implementation details.
- Any temporary implementation assumption must be reversible and documented with a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Measured market context with traceable provenance.
- Clear boundary between observed reaction and causal interpretation.
- Ability to extend into wider economic indicators.

### 8.2 Negative Consequences
- Market-data licensing and normalization add cost.
- Causal attribution remains difficult and may remain uncertain.

### 8.3 Technical Trade-Offs
Market data improves measurement but does not resolve causality. Initial release may use a limited set of authorized indicators or defer integration while preserving a logical observation contract.

### 8.4 Operational Consequences
Provider health, stale data, coverage gaps, revisions, licensing changes, and timestamp quality must be monitored.

### 8.5 Product and Business Consequences
Reports can state what markets actually did while separately explaining what may have caused the movement and what remains unknown.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| False causal attribution | Medium | Critical | Require separate causal assessment and confounder analysis. |
| Provider rights violation | Medium | Critical | Review licensing before storage and processing. |
| Time/session misalignment | Medium | High | Normalize time zones and calendars; preserve raw timestamps. |
| Incomplete provider coverage | Medium | Medium | Record missingness and avoid extrapolation. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- MarketDataCollector (future/optional)
- MarketObservationNormalizer
- ImpactAnalyzer
- EvidenceService
- ObservabilityService

### 9.2 Affected Data Models and Interfaces
- MarketObservation
- InstrumentReference
- MarketDataSource
- MarketReactionAssessment
- EconomicImpact Analysis

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-008 | Depends on / Related to | Defines uncertainty and provenance for observations and causal claims. |
| GENI-ADR-013 | Depends on | Defines source-rights controls. |
| GENI-ADR-016 | Related to | Defines reliable collection and persistence. |
| GENI-ADR-019 | Related to | Defines broader economic-impact semantics. |
| GENI-ADR-009 | Related to | Defines acquisition scheduling and source health. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define instrument identity and market-observation contracts.
- Inventory providers, licenses, coverage, timestamps, and correction policies.
- Normalize price types, units, currencies, and session context.
- Preserve raw provider reference and normalized observation versions.
- Separate observed movement from event-attribution analysis.
- Create reference cases for non-trading hours, missing prices, revisions, and confounding events.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-008 — Defines uncertainty and provenance for observations and causal claims.
- GENI-ADR-013 — Defines source-rights controls.
- GENI-ADR-016 — Defines reliable collection and persistence.
- GENI-ADR-019 — Defines broader economic-impact semantics.
- GENI-ADR-009 — Defines acquisition scheduling and source health.

### 10.4 Implementation Sequence
1. Define market observation schema and instrument reference.
2. Review provider coverage and rights.
3. Implement one limited authorized data source if justified.
4. Normalize and persist provenance-rich observations.
5. Build separate market reaction and event attribution assessment.
6. Evaluate data quality and causal-assessment limits.

### 10.5 Verification Requirements
- Verify each observation has source, instrument, value, unit, and timestamp context.
- Test timezone and trading-session alignment.
- Test missing, stale, corrected, and outlier observations.
- Verify temporal proximity alone does not produce causal statements.
- Evaluate provider coverage on representative instruments.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Market observations retain provider and instrument provenance. | Data model tests |
| AC-02 | Price type, units, time, and session context are explicit. | Normalization tests |
| AC-03 | Observed movement is separate from causal attribution. | Analysis contract tests |
| AC-04 | Rights checks precede acquisition and retention. | Rights integration tests |
| AC-05 | Missing/stale/corrected observations are represented explicitly. | Data quality tests |
| AC-06 | Broader economic impact remains distinct from market reaction. | Cross-document review |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Market-data requirements or provider coverage materially change.
- Measured reporting gaps justify adding market data.
- Licensing terms or retention requirements change.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Distinguishes market reaction from economic impact. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines impact analysis responsibilities. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines MarketObservation and evidence links. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines market-data and analysis stages. |
| `GENI-ADR-008` | Internal | Evidence and uncertainty. |
| `GENI-ADR-019` | Internal | Assessment semantics. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |

**End of ADR**
