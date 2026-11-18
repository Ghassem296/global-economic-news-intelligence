# GENI-ADR-004 — Publication Decisions, Quality Gates, and Automated Publishing Policy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-004  
**Title:** Publication Decisions, Quality Gates, and Automated Publishing Policy  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

GENI must produce reports from evolving events and evidence while preventing unsupported, legally restricted, insecure, or materially misleading content from being published. Report generation, publication eligibility, actual publication at an external target, human review, and recipient delivery are different operations. The architecture now models PublicationDecision separately from PublicationRecord and DeliveryRecord; this ADR defines the policy boundary and the conditions under which automated publication may be allowed.

This ADR is a proposal for formal review. It does not approve a production implementation or override an existing accepted decision.

## 2. Decision Question

What quality, evidence, rights, security, and authorization gates must be satisfied before a report version can be published automatically, held for review, rejected, replaced, or withdrawn?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Every report version must receive an immutable publication eligibility decision before publication.
- Support PUBLISH, PUBLISH_WITH_CAVEATS, HOLD_FOR_REVIEW, and REJECT outcomes.
- Record decision reasons, policy version, evidence/provenance checks, caveats, and supersession history.
- Publication execution must be a separate authorized operation and must not be inferred from a policy decision.
- Publication must respect content rights, source restrictions, security validation, report integrity, and duplicate-publication controls.
- Publication targets and recipient-delivery destinations must be classified and recorded independently.

### 3.2 Technical Constraints
- Human review and correction procedures are separately governed by GENI-ADR-014.
- Content access and republication restrictions are governed by GENI-ADR-013.
- Uncertainty and evidence provenance are governed by GENI-ADR-008.
- An external publication side effect cannot generally share a database transaction.

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

### 4.1 Alternative A — Automatic publication after generation

**Description:** Publish every successfully generated report unless a technical failure occurs.

**Advantages:**
- Lowest operational friction and fast publication.

**Disadvantages:**
- Does not provide explicit content quality or rights gates.

**Risks:**
- Unsupported or restricted content may be published without review.

**Estimated Complexity:** Low

### 4.2 Alternative B — Mandatory human approval for every report

**Description:** Require an authorized person to approve every report version before external publication.

**Advantages:**
- Strong human oversight
- straightforward escalation.

**Disadvantages:**
- High operating burden
- slows routine low-risk publication.

**Risks:**
- Review backlog may delay time-sensitive intelligence.

**Estimated Complexity:** High

### 4.3 Alternative C — Policy-gated automation with selective review

**Description:** Apply explicit quality and rights gates; automate eligible low-risk cases and route uncertain or high-risk cases to review.

**Advantages:**
- Balances speed, traceability, and control
- supports different report risk classes.

**Disadvantages:**
- Requires a policy engine, evaluation, monitoring, and review capacity.

**Risks:**
- Poorly calibrated gates may still misclassify risk.

**Estimated Complexity:** Medium to High

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Automatic publication after generation | Mandatory human approval for every report | Policy-gated automation with selective review |
|---|---|---|---|
| Publication safety | Low | High | High if gates are validated |
| Timeliness | High | Low to Medium | High for eligible reports |
| Auditability | Low | High | High |
| Operational workload | Low | High | Medium |
| Risk of unreviewed errors | High | Low | Controlled but non-zero |

The principal evaluation priorities are:
- Every report version must receive an immutable publication eligibility decision before publication.
- Support PUBLISH, PUBLISH_WITH_CAVEATS, HOLD_FOR_REVIEW, and REJECT outcomes.
- Record decision reasons, policy version, evidence/provenance checks, caveats, and supersession history.
- Publication execution must be a separate authorized operation and must not be inferred from a policy decision.

Unmeasured latency, throughput, quality, and cost are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Policy-gated automated publication with selective human review.

Use an explicit, versioned publication policy that evaluates report validity, provenance, evidence quality, uncertainty, material contradictions, rights permissions, security checks, and target-specific requirements. The policy returns one of the four defined outcomes. Only an effective PUBLISH or PUBLISH_WITH_CAVEATS decision authorizes a PublicationService operation. A decision is not proof of publication. Actual publish, replace, and withdraw operations are recorded separately and must reconcile uncertain target outcomes.

**Rationale:**
- Separates the authorization decision from an external side effect.
- Allows automation only within measured and approved risk boundaries.
- Preserves human review for ambiguous or consequential reports.
- Aligns publication controls with rights and evidence provenance.

**Assumptions:**
- The initial product can define explicit quality and rights gates for supported report types.
- At least one authorized review path can be operationally maintained.
- Publication adapters can report success, failure, or unknown outcome, or have a documented reconciliation procedure.

**Deferred Questions:**
- Exact numeric thresholds for each quality gate.
- Which report classes may be auto-published initially.
- Target-specific capabilities and guarantees.
- Final review staffing and service-level objectives.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The authorized decision owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Product Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded; see the recommendation in Section 6.

**Conditions or Restrictions:**
- Keep this ADR in Proposed status until explicit approval is recorded.
- Do not treat deferred questions or illustrative examples as accepted implementation values.
- Any implementation assumption made before approval must be reversible, documented, and assigned a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Explicit quality and authorization boundary.
- Selective automation without removing human oversight.
- Auditable publication rationale and policy evolution.

### 8.2 Negative Consequences
- Policy development and review operations add complexity.
- Conservative gates can delay valid reports.
- Quality thresholds require representative data.

### 8.3 Technical Trade-Offs
Automation improves timeliness but transfers risk to policy quality. Mandatory review reduces some risks but can make timely reporting impractical. The recommended hybrid approach requires measured false-allow/false-block rates and should begin conservatively.

### 8.4 Operational Consequences
Policy changes require versioning, regression evaluation, monitoring of blocked/held/published distributions, and a controlled rollback mechanism.

### 8.5 Product and Business Consequences
Reports can be published quickly when eligibility is established while clearly uncertain or restricted cases are withheld.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| False approval | Medium | Critical | Use conservative blocking defaults, review sampling, and rollback controls. |
| Review backlog | Medium | High | Define queue ownership, prioritization, deadlines, and capacity monitoring. |
| Rights-policy drift | Medium | Critical | Revalidate permissions at operation time and retain policy version. |
| Unclear target result | Medium | High | Require idempotency or reconciliation before retry. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- PublicationPolicy
- ReviewService
- ReportVersionService
- PublicationService
- ReportDelivery
- ObservabilityService

### 9.2 Affected Data Models and Interfaces
- PublicationDecision
- ReviewRecord
- PublicationRecord
- PublicationAttempt
- ReportVersion
- DeliveryRecord

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md
- GENI-ADR-013
- GENI-ADR-014

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-008 | Depends on / Related to | Evidence provenance and uncertainty are inputs to quality gates. |
| GENI-ADR-013 | Depends on | Rights permissions must be checked before publication or distribution. |
| GENI-ADR-014 | Depends on / Related to | Defines human review, correction, and withdrawal operations. |
| GENI-ADR-016 | Related to | Publication side effects require durable operations, idempotency, and reconciliation. |
| GENI-ADR-019 | Related to | Assessment semantics and confidence must not be collapsed into publication eligibility. |

These relationships do not imply that any related Proposed ADR has been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define policy inputs and immutable decision schema.
- Define policy evaluation and reason-code catalog.
- Define report-class risk profiles and target restrictions.
- Integrate review routing for HOLD_FOR_REVIEW.
- Ensure publication execution validates the effective decision and rights state.
- Add audit and reconciliation controls for publish, replace, and withdraw.

### 10.2 Migration or Compatibility Requirements
Existing data and implementation choices must be inspected before migration is designed. No production migration is claimed by this proposal. Any schema or interface migration must preserve historical traceability and must be tested from the current baseline.

### 10.3 Dependencies
- GENI-ADR-008 — Evidence provenance and uncertainty are inputs to quality gates.
- GENI-ADR-013 — Rights permissions must be checked before publication or distribution.
- GENI-ADR-014 — Defines human review, correction, and withdrawal operations.
- GENI-ADR-016 — Publication side effects require durable operations, idempotency, and reconciliation.
- GENI-ADR-019 — Assessment semantics and confidence must not be collapsed into publication eligibility.

### 10.4 Implementation Sequence
1. Define risk classes and mandatory blocking gates.
2. Define decision and reason schemas.
3. Implement policy evaluation as a side-effect-free component.
4. Implement review integration and effective-decision validation.
5. Implement publication adapter execution separately.
6. Evaluate against a human-reviewed report dataset before enabling automation.

### 10.5 Verification Requirements
- Test each decision outcome and verify that only authorized outcomes can reach PublicationService.
- Test missing or revoked rights, missing provenance, contradictory evidence, and security failures.
- Test that a decision does not create a PublicationRecord by itself.
- Test that delivery status cannot change publication state.
- Measure false-allow and false-block rates on reviewed reports.

Implementation verification remains deferred until this ADR is accepted and the corresponding capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Every report version has an immutable decision tied to a policy version. | Persistence and policy tests |
| AC-02 | HOLD_FOR_REVIEW creates a persistent review task and cannot publish automatically. | Workflow tests |
| AC-03 | REJECT blocks publication and any unauthorized delivery path. | Policy integration tests |
| AC-04 | PUBLISH_WITH_CAVEATS preserves caveats in the publication representation. | Adapter contract tests |
| AC-05 | Publication success is confirmed by a target result, not by a decision or delivery record. | Integration tests |
| AC-06 | Gate quality is evaluated on reviewed examples before automated production use. | Evaluation report |

Any quantitative threshold must be grounded in representative datasets, operational measurements, contractual requirements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- A serious incorrect or rights-infringing publication.
- Change in source licenses, target capabilities, or publication channel.
- Material changes in report types or intended audience.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Product Owner

### 12.3 Reconsideration Conditions
A serious incorrect or rights-infringing publication. Change in source licenses, target capabilities, or publication channel. Material changes in report types or intended audience.

Reconsider this recommendation when its core assumptions are no longer valid or measured evidence demonstrates that it does not meet project requirements. A replacement decision must be recorded in a new or superseding ADR.

## 13. References and Supporting Evidence

The references below are internal project documents used to establish the current documented context. They are not claimed as empirical performance measurements or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Defines publication policy, review, publication operations, and separate delivery. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines PublicationPolicy, ReviewService, PublicationService, and workflow contracts. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines immutable decisions, publication operations, attempts, and delivery records. |
| `docs/adr/decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` | Internal | Defines provenance and uncertainty constraints. |
| `docs/adr/decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` | Internal | Defines content rights and reuse restrictions. |

External legal review, provider measurements, market-data coverage measurements, and model-quality benchmarks remain outstanding wherever relevant.

## 14. Decision History

| Date | Version | Status | Change |
|---|---|---|---|
| 2026-11-18 | 1.0 | Proposed | Initial proposal prepared for architecture review |
| 2026-11-18 | 1.1 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. |

**End of ADR**
