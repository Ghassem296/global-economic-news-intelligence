# GENI-ADR-014 — Human Review, Corrections, and Withdrawals

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-014  
**Title:** Human Review, Corrections, and Withdrawals  
**Status:** Proposed  
**Version:** 1.2  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Automated extraction, event matching, evidence assessment, report generation, and publication can be ambiguous or wrong. Some cases require human judgment due to uncertainty, material consequences, rights constraints, or policy exceptions. Direct edits to authoritative records would destroy traceability. The product needs a review workflow that records the subject, reviewer authority, evidence context, rationale, outcome, and successor decision or corrective operation.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

How should human review be triggered, authorized, recorded, and applied to event matching and reporting, and how should corrections and withdrawals preserve prior history?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Define triggers for duplicate ambiguity, event-matching ambiguity, low confidence, high impact, rights restrictions, policy exceptions, and reported errors.
- Persist review tasks with typed subject references, reason, priority, assignment, timestamps, and status.
- Record reviewer identity and authorization through the security layer.
- Separate review outcome from the authoritative successor domain decision.
- Use immutable successor decisions for material corrections.
- Preserve incorrect article-event links as deactivated historical associations rather than deleting them.
- Support review of DuplicateCandidate outcomes requiring human judgment and create immutable successor DuplicateDecision records for material corrections.
- Coordinate report correction, publication replacement, and withdrawal through explicit operations.
- Support escalation, reassignment, overdue detection, and audit.

### 3.2 Technical Constraints
- Reviewer identity and authorization belong to the security layer.
- Event identity is governed by ADR-011; publication policy by ADR-004; content rights by ADR-013.
- External withdrawal may be unsupported by some publication targets.

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

### 4.1 Alternative A — No human review

**Description:** Allow automated workflows to complete every case.

**Advantages:**
- Low operating burden
- high automation.

**Disadvantages:**
- Cannot resolve consequential ambiguity or exceptions.

**Risks:**
- Systematic mistakes may persist without accountable intervention.

**Estimated Complexity:** Low

### 4.2 Alternative B — Direct privileged override

**Description:** Allow privileged operators to edit domain records directly.

**Advantages:**
- Fast for one-off incidents.

**Disadvantages:**
- Weak lineage and unclear authorization
- history can be overwritten.

**Risks:**
- Silent corruption and inconsistent accountability.

**Estimated Complexity:** Low initially; high risk

### 4.3 Alternative C — Persistent review workflow with successor decisions

**Description:** Create review tasks and apply outcomes only through authorized domain services and immutable successor decisions.

**Advantages:**
- Auditable
- clear authority
- preserves history.

**Disadvantages:**
- Requires queue operations, access control, and workflow integration.

**Risks:**
- Review queues can become bottlenecks.

**Estimated Complexity:** Medium to High

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | No human review | Direct privileged override | Persistent review workflow with successor decisions |
|---|---|---|---|
| Auditability | Low | Low | High |
| Correction traceability | Low | Low | High |
| Authority control | Low | Medium | High |
| Operational workload | Low | Variable | Explicit and measurable |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Persistent review workflow with immutable successor decisions.

A review task must reference the immutable decision, assessment, report version, or publication operation under review. It records reason, priority, evidence/context, assignment, reviewer identity, authorization, rationale, and outcome. A material outcome creates a new authoritative decision or corrective operation through the relevant domain service. The review record is not itself permission to change event identity or publish a report. Corrections preserve the original decision and association; publication replacement or withdrawal remains a separate external operation.

**Rationale:**
- Prevents unaudited edits to authoritative records.
- Makes reviewer authority and accountability explicit.
- Preserves decision lineage and external publication history.

**Deferred Questions:**
- Detailed reviewer role matrix and separation-of-duties requirements.
- Review service-level objectives, queue capacity, and escalation intervals.
- Whether the first review interface is internal tooling or an external platform.
- Target-specific withdrawal limitations and manual escalation.

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
- Accountable review and correction process.
- Preserved audit trail and decision lineage.
- Consistent authority across event matching and publication.

### 8.2 Negative Consequences
- Adds workflow, security, and operational complexity.
- Human review can delay event association or publication.

### 8.3 Technical Trade-Offs
Prefer traceable corrective operations over mutable overrides. Emergency handling may be expedited, but actor, authorization, reason, and state transition must still be recorded.

### 8.4 Operational Consequences
Queues require ownership, escalation, overdue detection, secure access, and operational reporting. External publication effects require independent reconciliation.

### 8.5 Product and Business Consequences
Ambiguous or high-risk items may be delayed, but corrections become explainable and auditable.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Unauthorized override | Low to Medium | Critical | Role-based authorization, separation of duties, immutable history. |
| Review backlog | Medium | High | Queue ownership, prioritization, deadlines, and escalation metrics. |
| External withdrawal cannot be completed | Medium | High | Distinguish request from confirmed result and provide manual escalation. |
| Conflicting concurrent reviews | Low to Medium | High | Optimistic concurrency and non-branching successor constraints. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- ReviewService
- ArticleDeduplicator and Article Deduplication Workflow
- EventService
- PublicationPolicy
- ReportVersionService
- PublicationService
- Authorization service

### 9.2 Affected Data Models and Interfaces
- ReviewRecord
- ReviewAction
- DuplicateCandidate
- DuplicateDecision
- EventMatchDecision
- ArticleEventLink
- ReportVersion
- PublicationRecord
- EventHistory

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-002 | Related to | Defines event-matching ambiguity and, with the data model, candidate/decision history; this ADR defines the human review operation for duplicate decisions. |
| GENI-ADR-004 | Depends on / Related to | Defines publication gates that may route reports to review. |
| GENI-ADR-008 | Related to | Provides evidence and uncertainty context. |
| GENI-ADR-011 | Depends on / Related to | Defines event identity and association correction semantics. |
| GENI-ADR-013 | Related to | Rights restrictions may require correction, deletion, or withdrawal. |
| GENI-ADR-016 | Related to | Review tasks require durable state and idempotent processing. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define review types, triggers, reason codes, priorities, and statuses.
- Persist review tasks and assignment history.
- Expose only evidence and source content permitted by rights policy.
- Enforce reviewer authorization and separation of duties where required.
- Apply article-deduplication outcomes through the Article Deduplication Workflow, event-matching outcomes through EventService/Event Resolution Workflow, and report outcomes through PublicationPolicy, ReportVersionService, or PublicationService.
- Preserve old decisions, links, and report versions; create successor lineage.
- Monitor overdue, abandoned, conflicting, and failed corrective tasks.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-002 — Defines matching ambiguity and decision history.
- GENI-ADR-004 — Defines publication gates that may route reports to review.
- GENI-ADR-008 — Provides evidence and uncertainty context.
- GENI-ADR-011 — Defines event identity and association correction semantics.
- GENI-ADR-013 — Rights restrictions may require correction, deletion, or withdrawal.
- GENI-ADR-016 — Review tasks require durable state and idempotent processing.

### 10.4 Implementation Sequence
1. Define reviewer roles and authorization boundaries.
2. Implement persistent review queue and task lifecycle.
3. Integrate duplicate-candidate review with the Article Deduplication Workflow and immutable DuplicateDecision supersession.
4. Integrate event-match review with Event Resolution workflow and EventService.
5. Integrate report review with PublicationPolicy and ReportVersionService.
6. Integrate correction, replacement, and withdrawal with PublicationService.
7. Add audit, escalation, and incident exercises.

### 10.5 Verification Requirements
- Test unauthorized actors cannot complete or approve reviews.
- Test a review record alone cannot create an event association or publish a report.
- Test article-deduplication review creates a successor DuplicateDecision for the same candidate.
- Test material review outcomes create successor decisions without mutating originals.
- Test corrected links preserve the old inactive link and create a traceable successor.
- Test report correction creates a new version and separate publication replacement operation.
- Test recovery, reassignment, and duplicate review submissions.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Review tasks are persistent and queryable by status, assignee, due date, and subject. | Repository tests |
| AC-02 | Reviewer identity and permissions are validated. | Security tests |
| AC-03 | Material review outcomes create immutable successor decisions. | Lineage tests |
| AC-04 | Association corrections retain the deactivated prior link. | Integration tests |
| AC-05 | Report correction and external publication withdrawal are distinct operations. | Lifecycle tests |
| AC-06 | Review backlog, overdue items, and failed corrective actions are observable. | Operational tests |
| AC-07 | Duplicate-candidate review creates a successor DuplicateDecision without mutating the prior decision or source articles. | Duplicate-decision lineage tests |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- A material error or rights incident reveals missing review controls.
- Review volume exceeds capacity or service objectives.
- Authorization or publication-target capabilities change.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Defines review, publication, and correction boundaries. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines the shared ReviewService and Event Resolution workflow responsibilities. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines review records and immutable decisions. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines review and correction stages. |
| `GENI-ADR-004` | Internal | Publication decisions and quality gates. |
| `GENI-ADR-011` | Internal | Event identity and corrections. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Date | Version | Status | Change |
|---|---|---|---|
| 2026-11-18 | 1.0 | Proposed | Expanded ADR proposal prepared for architecture review |
| 2026-11-18 | 1.1 | Proposed | Aligned event-matching review records and workflow references with the component architecture; removed undefined service and record types. |
| 2026-11-18 | 1.2 | Proposed | Extended typed human review to article-deduplication decisions and defined successor DuplicateDecision handling. |

**End of ADR**
