# GENI-ADR-014 — Human Review, Corrections, and Withdrawals

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-014  
**Title:** Human Review, Corrections, and Withdrawals  
**Version:** 0.2  
**Status:** Proposed  
**Priority:** P0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Automated extraction, matching, analysis, and publication can be incomplete or incorrect. The platform needs accountable human review for ambiguous and high-risk cases, plus correction and withdrawal paths that preserve the original evidence and decisions. A review comment must not be mistaken for an authorized domain decision.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision. The existence of this document does not imply acceptance.

## 2. Decision Question

How should review tasks, authorization, outcomes, corrections, and withdrawals be modeled across event matching and publication workflows?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Explicit separation between review tasks and authoritative domain decisions.
- Role-based authorization and accountability.
- Immutable historical decision and report lineage.
- A review must not bypass publication policy or event identity rules.
- External withdrawal and replacement outcomes require confirmation and reconciliation.

### 3.2 Technical Constraints

- Domain contracts must not depend on a specific external provider unless explicitly approved.
- All relevant policies, schemas, and derived outputs must be versioned.
- Critical state transitions must be auditable and testable.
- Missing or unavailable information must remain explicit.

### 3.3 Business and Product Constraints

- The initial product must remain operationally simple.
- Implementation sequencing must follow documented dependencies.
- Product claims must not exceed the capability or evidence actually available.

### 3.4 Security and Privacy Constraints

- External source content and model output are untrusted input.
- Credentials and sensitive operational data must not be exposed in ordinary logs.
- Access to privileged actions must follow least-privilege authorization.

### 3.5 Operational and Cost Constraints

- Concurrency, retries, resource usage, and external service calls must be bounded.
- Operational metrics must make failure and uncertainty visible.
- Numeric thresholds must be based on measurements or explicit policy approval.

### 3.6 Legal and Content-Rights Constraints

- Technical access does not imply permission to store, process, transform, or republish content.
- Source terms, licensing, privacy, and jurisdictional requirements must be reviewed where applicable.

### 3.7 Explicit Non-Goals

- This ADR does not set unmeasured numeric service levels or model-quality thresholds.
- This ADR does not select a vendor or provider where comparative evidence is unavailable.
- This ADR does not approve its recommendation; explicit Project Owner approval remains required.

## 4. Alternatives Considered

### 4.1 A — Fully automated decisions

**Advantages:** High throughput and low human operating cost.

**Disadvantages:** Unresolved ambiguity and high-risk corrections can pass without accountable review.

**Risk:** High

### 4.2 B — Human approval for every operation

**Advantages:** Strong human oversight.

**Disadvantages:** Operational bottleneck; unnecessary review of routine low-risk actions.

**Risk:** High

### 4.3 C — Policy-driven review with typed subjects and domain-specific decisions

**Advantages:** Human effort is focused on ambiguous, risky, or corrective cases; domain decisions remain explicit.

**Disadvantages:** Requires a review queue, authorization model, and audit trail.

**Risk:** Medium


## 5. Evaluation and Comparison

The following qualitative comparison is an architectural assessment, not a measured benchmark.

| Criterion | Alternative A | Alternative B | Alternative C |
|---|---|---|---|
| Fit with product requirements | Limited / context-dependent | Partial | Strongest overall fit |
| Operational complexity | Low | Medium | Medium |
| Auditability and traceability | Limited | Partial | Strong |
| Ability to evolve | Low to Medium | Medium | High |
| Principal trade-off | Simplicity or incomplete capability | Partial separation | More explicit contracts and governance |

The recommendation favors Alternative C because it preserves the domain distinctions and operational controls required by the product. Any quantitative comparison must be performed against representative workload and evaluation data.

## 6. Recommended Decision

Use a generic ReviewRecord task model with a typed subject reference, review type, reason, priority, status, assignment, due time, reviewer, outcome, and audit history. ReviewRecord is not an authoritative decision. For event matching, the reviewer outcome creates a new EventMatchDecision that supersedes the previous effective decision. For publication, the outcome creates a new PublicationDecision. Corrections create new immutable report or association versions. Withdrawal is a separate authorized external operation and is complete only when the target confirms it or a documented reconciliation/manual path resolves the outcome.

### 6.1 Decision Boundaries

- Define review types and permitted subject types, including EventMatchCase and report/publication decision subjects.
- Define roles and permissions for assignment, review, approval, correction, rejection, and withdrawal authorization.
- Record task creation, assignment, reassignment, comments, outcome, actor, and timestamps without overwriting prior actions.
- Link each event-matching review to the case and exact decision under review.
- Link each publication review to the report version and exact PublicationDecision under review.
- Ensure a review completion triggers a new domain decision where policy requires it.
- Preserve before/after references for corrected associations and reports.
- Use the publication operation lifecycle for target withdrawal; reconcile unknown external outcomes before retry.

### 6.2 Assumptions and Open Questions

- The recommendation is based on the current product and architecture documents.
- Any numeric threshold, provider selection, or legal interpretation not supported by evidence remains open.
- The Project Owner may accept, reject, or request revision of this recommendation.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded. The recommendation in Section 6 is awaiting review.

**Conditions or Restrictions:**

- Do not treat this proposal as an accepted architectural constraint.
- Do not implement irreversible changes solely on the basis of this recommendation.
- Record any interim implementation assumption and its review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Makes the relevant domain or operational boundary explicit.
- Improves traceability and repeatability.
- Provides a basis for measurable verification and future revision.

### 8.2 Negative Consequences

- Adds implementation and documentation work.
- Some policy details remain open pending data, legal review, or operational measurements.
- Dependent components may need coordinated changes after approval.

### 8.3 Technical Trade-Offs

Alternative C favors explicit contracts and traceability over the smallest possible implementation. Provider-specific behavior or domain-specific exceptions must remain visible rather than being hidden behind an abstraction that implies guarantees the system does not have.

### 8.4 Operational Consequences

The implementation will require monitoring, recovery, and review procedures appropriate to the selected capability. Failure modes and unknown outcomes must be observable.

### 8.5 Product and Business Consequences

The recommendation is intended to support the product's evidence-based economic intelligence purpose. It must not create user-facing promises that exceed actual source coverage, data quality, or review capacity.

### 8.6 Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Proposal mistaken for approval | Keep status Proposed until explicit approval is recorded. |
| Over-specification without evidence | Leave thresholds and provider choices open until measured. |
| Cross-document inconsistency | Synchronize affected documents and registry after approval. |
| Implementation cannot satisfy a proposed guarantee | Report the conflict and revise the ADR rather than silently weakening the contract. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- Define review types and permitted subject types, including EventMatchCase and report/publication decision subjects.
- Define roles and permissions for assignment, review, approval, correction, rejection, and withdrawal authorization.
- Record task creation, assignment, reassignment, comments, outcome, actor, and timestamps without overwriting prior actions.
- Link each event-matching review to the case and exact decision under review.
- Link each publication review to the report version and exact PublicationDecision under review.
- Ensure a review completion triggers a new domain decision where policy requires it.
- Preserve before/after references for corrected associations and reports.
- Use the publication operation lifecycle for target withdrawal; reconcile unknown external outcomes before retry.

### 9.2 Affected Data Models and Interfaces

The relevant interfaces, persistence fields, constraints, and version metadata must be updated only after the proposal is approved and the implementation design is reviewed.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

See the related ADR references in the registry. These dependencies do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work

- Define review types and permitted subject types, including EventMatchCase and report/publication decision subjects.
- Define roles and permissions for assignment, review, approval, correction, rejection, and withdrawal authorization.
- Record task creation, assignment, reassignment, comments, outcome, actor, and timestamps without overwriting prior actions.
- Link each event-matching review to the case and exact decision under review.
- Link each publication review to the report version and exact PublicationDecision under review.
- Ensure a review completion triggers a new domain decision where policy requires it.
- Preserve before/after references for corrected associations and reports.
- Use the publication operation lifecycle for target withdrawal; reconcile unknown external outcomes before retry.

### 10.2 Migration or Compatibility Requirements

No runtime or database migration is authorized by this proposal. If accepted, existing records and historical provenance must be inspected before a migration is designed. Migration must preserve audit history and must be tested from the current baseline.

### 10.3 Dependencies

Implementation sequencing must respect the dependencies recorded in the ADR Registry and the related decision documents.

### 10.4 Implementation Sequence

1. Obtain explicit Project Owner approval.
2. Update affected architecture and data-model contracts.
3. Define versioned interfaces and migration requirements.
4. Implement the smallest end-to-end slice.
5. Add focused automated and integration tests.
6. Validate operational behavior and update implementation status separately from ADR status.

### 10.5 Verification Requirements

- A reviewer cannot approve a task outside their authorization scope.
- Every required review task identifies one typed subject and the decision under review.
- A completed event-matching review creates a new EventMatchDecision; it does not mutate the prior decision.
- A completed publication review creates a new PublicationDecision where eligibility changes.
- No review outcome directly calls a publication target or bypasses PublicationPolicy.
- A correction preserves previous report and ArticleEventLink history.
- A withdrawal is not marked externally complete without confirmation or documented reconciliation.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | A reviewer cannot approve a task outside their authorization scope. | Architecture review and automated tests where applicable |
| AC-02 | Every required review task identifies one typed subject and the decision under review. | Architecture review and automated tests where applicable |
| AC-03 | A completed event-matching review creates a new EventMatchDecision; it does not mutate the prior decision. | Architecture review and automated tests where applicable |
| AC-04 | A completed publication review creates a new PublicationDecision where eligibility changes. | Architecture review and automated tests where applicable |
| AC-05 | No review outcome directly calls a publication target or bypasses PublicationPolicy. | Architecture review and automated tests where applicable |
| AC-06 | A correction preserves previous report and ArticleEventLink history. | Architecture review and automated tests where applicable |
| AC-07 | A withdrawal is not marked externally complete without confirmation or documented reconciliation. | Architecture review and automated tests where applicable |

Quantitative thresholds must be established using representative evaluation data or operational measurements. This ADR intentionally does not invent numerical targets.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- A new review category or authorization role is introduced.
- Review backlog or time-to-resolution becomes operationally unacceptable.
- A security or editorial incident reveals a missing review gate.
- Legal or contractual obligations change correction/withdrawal handling.

### 12.2 Review Schedule

**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions

Reconsider this proposal if its assumptions become invalid, evaluation results contradict the recommendation, or product/legal/operational requirements materially change. A replacement of an accepted decision requires a new ADR or an explicitly approved superseding record.

## 13. References and Supporting Evidence

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`
- Related decision topics are listed in the ADR Registry.

The current internal documents establish architectural context. They do not substitute for external legal advice, provider capability verification, or empirical performance measurements.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 0.1 | 2026-11-18 | Proposed | Initial proposal drafted | AI Architecture Assistant |
| 0.2 | 2026-11-18 | Proposed | Expanded alternatives, evaluation, implementation, risks, and verification criteria | AI Architecture Assistant |

**End of ADR**
