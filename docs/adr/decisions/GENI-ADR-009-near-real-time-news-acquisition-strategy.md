# GENI-ADR-009 — Near-Real-Time News Acquisition Strategy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-009  
**Title:** Near-Real-Time News Acquisition Strategy  
**Status:** Proposed  
**Version:** 1.0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Sources differ in update frequency, access method, rate limits, publication timestamp quality, reliability, and latency. Fixed high-frequency polling wastes requests and may violate source restrictions, while manual or batch-only collection may miss time-sensitive economic developments. The platform needs measurable freshness without claiming that all sources provide real-time or complete coverage.

This ADR is a proposal for formal review; it does not approve a production implementation.

## 2. Decision Question

How should sources be acquired with useful freshness while respecting source capabilities, access rights, rate limits, reliability, and operating cost?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Source-specific acquisition adapters and configurable schedules.
- Use authorized push/change notifications where provider semantics are reliable; otherwise use polling.
- Persist checkpoints, pagination state, and collection provenance.
- Record publication, observation, retrieval, and processing timestamps independently.
- Apply bounded retries, backoff, per-source limits, and replay/reconciliation where supported.
- Detect delayed, revised, missing, and duplicated publications without losing source identity.

### 3.2 Technical Constraints
- No universal polling interval or freshness guarantee is assumed.
- RSS, APIs, web pages, and webhooks have different permissions and delivery semantics.
- Collection must be idempotent and resumable.
- Rights restrictions defined by ADR-013 apply before retrieval and retention.

### 3.3 Business and Product Constraints
- The initial product remains text-based economic intelligence.
- The architecture must support incremental delivery and traceable evaluation.
- Proposed decisions remain provisional until explicitly approved.

### 3.4 Security and Privacy Constraints
- External source content and generated model output are untrusted until validated.
- Least-privilege access, secret protection, and explicit external permissions are mandatory.
- Operational logs must avoid unnecessary protected content.

### 3.5 Operational and Cost Constraints
- Avoid unnecessary distributed infrastructure in the initial release.
- Measure operational complexity and cost against expected workload.
- Timeouts, retries, recovery, and observability must be explicit.

### 3.6 Legal and Content-Rights Constraints
- Technical access does not imply permission to store, process externally, transform, quote, or republish source content.
- Source terms, licensing, privacy, and jurisdictional requirements must be reviewed before production use.

### 3.7 Explicit Non-Goals
- No unmeasured numerical threshold or performance guarantee is established by this proposal.
- No provider or infrastructure technology is mandatory solely because it appears as an alternative.
- This ADR does not replace the formal approval process.

## 4. Alternatives Considered

### 4.1 Alternative A — Uniform frequent polling

**Description:** Poll every source at one fixed short interval.

**Advantages:**
- Simple scheduling model.

**Disadvantages:**
- Wasteful and may violate provider limits
- does not guarantee freshness.

**Risks:**
- Rate limiting, source blocking, and noisy collection.

**Estimated Complexity:** Low

### 4.2 Alternative B — Source-specific polling

**Description:** Configure polling intervals and checkpoints per source.

**Advantages:**
- Simple and source-aware
- low adapter complexity.

**Disadvantages:**
- Can still miss rapid updates and needs manual tuning.

**Risks:**
- Configuration may become stale.

**Estimated Complexity:** Low to Medium

### 4.3 Alternative C — Hybrid push and adaptive polling

**Description:** Use reliable authorized push where available and source-specific polling elsewhere, with reconciliation and backoff.

**Advantages:**
- Better freshness potential and request efficiency.

**Disadvantages:**
- More adapter and operational complexity.

**Risks:**
- Push gaps or poor tuning create blind spots.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Uniform frequent polling | Source-specific polling | Hybrid push and adaptive polling |
|---|---|---|---|
| Freshness potential | Medium | Medium | High where supported |
| Request efficiency | Low | Medium | High potential |
| Source-limit compliance | Variable | High with configuration | High with adapter policy |
| Operational simplicity | High | High | Medium |

The requirements in Section 3 are the evaluation criteria. Unmeasured latency, quality, throughput, and costs are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Hybrid push and source-specific polling, with explicit freshness measurement.

Define an acquisition adapter contract that declares supported modes, replay semantics, authentication, rate limits, timestamp quality, and access restrictions. Prefer authorized push notifications only when their delivery and replay behavior are understood. Otherwise use source-specific polling, durable checkpoints, bounded retries, backoff, and periodic reconciliation when permitted. The system records publication time, observation time, retrieval time, and processing time separately. No universal freshness SLA is established by this ADR.

**Rationale:**
- Avoids unnecessary high-frequency polling.
- Makes source limitations explicit and auditable.
- Supports measured freshness by source rather than unsupported global promises.

**Deferred Questions:**
- Initial source list and adapter mode per source.
- Source-specific freshness objectives and alert thresholds.
- Whether adaptive polling is automatic or operator-configured.
- Provider-specific webhook replay and authentication guarantees.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The Project Owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review; see Section 6 for the recommendation.

**Conditions or Restrictions:**
- Keep this ADR Proposed until explicit approval is recorded.
- Do not treat deferred questions as settled implementation details.
- Any interim implementation choice must be reversible, documented, and assigned a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Better freshness where supported by sources.
- Reduced unnecessary polling.
- Measurable source reliability and freshness.

### 8.2 Negative Consequences
- Additional adapter types and monitoring.
- Push delivery may still be incomplete or delayed.

### 8.3 Technical Trade-Offs
Prefer source capability-aware acquisition over a universal short polling interval. Push notifications are not assumed reliable without documented authentication, replay, and reconciliation semantics.

### 8.4 Operational Consequences
Per-source health, freshness, limit consumption, checkpoint age, and adapter failures must be observable. Configuration changes are versioned.

### 8.5 Product and Business Consequences
Users get timely intelligence where source capabilities permit it; the product does not promise universal real-time coverage.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Rate-limit violation | Medium | High | Per-source budgets, backoff, and alerts. |
| Missed push notification | Medium | High | Provider replay or permitted periodic reconciliation. |
| Unreliable publication timestamp | Medium | Medium | Preserve raw timestamp and record quality/provenance. |
| Uncontrolled collection cost | Medium | Medium | Measure marginal value and tune source schedules. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- SourceRegistry
- NewsCollector
- SourceHealthService
- WorkflowOrchestrator
- ObservabilityService

### 9.2 Affected Data Models and Interfaces
- Source configuration and rights profile
- CollectionCheckpoint
- AcquisitionRecord
- SourceHealthRecord
- ProcessingRun

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-013 | Depends on | Defines access and content-rights restrictions. |
| GENI-ADR-016 | Depends on / Related to | Defines durable checkpoints, idempotency, retries, and recovery. |
| GENI-ADR-002 | Related to | Defines article identity and duplicate handling after acquisition. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Inventory interfaces, terms, authentication, rate limits, replay support, and timestamp semantics per source.
- Implement checkpointed polling for the first source set.
- Add push adapters only when their semantics and authorization are documented.
- Measure source-level freshness, completeness, request failures, and rate-limit events.
- Implement safe backoff, replay, and duplicate acquisition prevention.

### 10.2 Migration or Compatibility Requirements
Inspect the current implementation and data before designing any migration. This ADR does not claim that a migration has been executed. Any transition must preserve provenance and historical state.

### 10.3 Dependencies
- GENI-ADR-013 — Defines access and content-rights restrictions.
- GENI-ADR-016 — Defines durable checkpoints, idempotency, retries, and recovery.
- GENI-ADR-002 — Defines article identity and duplicate handling after acquisition.

### 10.4 Implementation Sequence
1. Simulate delayed, duplicated, missing, and out-of-order notifications.
2. Verify source rate limits and retry backoff.
3. Verify replay does not create duplicate acquisition records.
4. Verify checkpoints advance only after durable processing.
5. Measure publication-to-observation delay on a representative source dataset.

### 10.5 Verification Requirements
- Simulate delayed, duplicated, missing, and out-of-order notifications.
- Verify source rate limits and retry backoff.
- Verify replay does not create duplicate acquisition records.
- Verify checkpoints advance only after durable processing.
- Measure publication-to-observation delay on a representative source dataset.

Implementation verification remains deferred until the ADR is accepted and the capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Every source declares its acquisition mode, restrictions, and limits. | Configuration/contract inspection |
| AC-02 | Publication, observation, retrieval, and processing timestamps remain distinct. | Data-model tests |
| AC-03 | Polling/push retries do not create duplicate domain effects. | Idempotency tests |
| AC-04 | Rate-limit handling and backoff are observable. | Integration tests |
| AC-05 | Freshness metrics are available per source without unsupported guarantees. | Operational test |

Quantitative thresholds require representative datasets, operational measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Before implementing the dependent capability.
- Material changes in product scope, legal constraints, provider capabilities, workload, or operational scale.
- Evaluation evidence shows that the recommendation does not meet requirements.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider this proposal when its assumptions are invalidated or measured evidence shows that it fails project requirements. Replacements must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

References are internal project documents used to establish documented context. They are not empirical benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Acquisition and processing pipeline. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | NewsCollector and SourceRegistry boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Checkpoint and acquisition provenance model. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Initial source strategy and acquisition stage. |
| `GENI-ADR-013` | Internal | Source access and content rights. |
| `GENI-ADR-016` | Internal | Idempotency and recovery. |

External legal, provider, and measured performance evidence must be added where material during formal review.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |

**End of ADR**
