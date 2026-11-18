# GENI-ADR-016 — Persistence, Async Execution, Idempotency, and Recovery

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-016  
**Title:** Persistence, Async Execution, Idempotency, and Recovery  
**Version:** 0.2  
**Status:** Proposed  
**Priority:** P1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Collection, enrichment, matching, analysis, and publication are multi-step workflows that may fail or restart. Concurrent workers can race on state transitions. External side effects can time out after succeeding, so blind retries may duplicate publications or deliveries. A global exactly-once guarantee is not realistic across independent systems.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision. The existence of this document does not imply acceptance.

## 2. Decision Question

Which persistence, execution, idempotency, and recovery guarantees should the initial platform provide?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Durable workflow state and restartability.
- Atomic ownership/leases for concurrent workers.
- Idempotent domain effects and stable operation keys.
- Explicit distinction between internal transactions and external side effects.
- Recovery and reconciliation after uncertain outcomes.
- Operational simplicity proportional to the initial deployment.

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

### 4.1 A — In-memory tasks and best-effort retries

**Advantages:** Minimal infrastructure and simple development.

**Disadvantages:** Lost state after process termination; weak duplicate prevention and auditability.

**Risk:** Very High

### 4.2 B — Distributed workflow/queue platform immediately

**Advantages:** Mature distributed execution and scaling options.

**Disadvantages:** Operational complexity and service dependency may be premature.

**Risk:** Medium

### 4.3 C — Durable database-backed workflows with bounded async execution

**Advantages:** Supports restart, audit, and idempotent effects within a simple deployment.

**Disadvantages:** Requires careful transaction, lease, and reconciliation design.

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

Use durable ProcessingRun and ProcessingStep records, bounded asynchronous concurrency, atomic worker leases, and idempotency keys scoped to logical operations. Persist domain state and workflow outcomes in the same transaction where they share a database boundary. For external publication/delivery, persist operation intent and attempts separately; if outcome is uncertain, reconcile with the target before retrying. State guarantees honestly: at-least-once execution with idempotent domain effects and target-specific side-effect guarantees, not universal exactly-once execution.

### 6.1 Decision Boundaries

- Define workflow run/step identity, state transitions, input fingerprints, deadlines, lease owner, lease expiry, and retry count.
- Use atomic lease acquisition and expiry recovery; prevent simultaneous ownership of one active step.
- Define idempotency key scope for ingestion, matching decisions, publication operations, and deliveries.
- Use database transactions for case decision creation, effective-decision pointer updates, and link activation/deactivation.
- Keep external network calls outside long-running database transactions.
- Persist publication/delivery intent and each attempt; reconcile unknown outcomes before a retry.
- Define retryable versus permanent errors, exponential backoff, dead-letter/manual-intervention path, and observability.
- Test recovery after process crash at each side-effect boundary.

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

- Define workflow run/step identity, state transitions, input fingerprints, deadlines, lease owner, lease expiry, and retry count.
- Use atomic lease acquisition and expiry recovery; prevent simultaneous ownership of one active step.
- Define idempotency key scope for ingestion, matching decisions, publication operations, and deliveries.
- Use database transactions for case decision creation, effective-decision pointer updates, and link activation/deactivation.
- Keep external network calls outside long-running database transactions.
- Persist publication/delivery intent and each attempt; reconcile unknown outcomes before a retry.
- Define retryable versus permanent errors, exponential backoff, dead-letter/manual-intervention path, and observability.
- Test recovery after process crash at each side-effect boundary.

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

- Define workflow run/step identity, state transitions, input fingerprints, deadlines, lease owner, lease expiry, and retry count.
- Use atomic lease acquisition and expiry recovery; prevent simultaneous ownership of one active step.
- Define idempotency key scope for ingestion, matching decisions, publication operations, and deliveries.
- Use database transactions for case decision creation, effective-decision pointer updates, and link activation/deactivation.
- Keep external network calls outside long-running database transactions.
- Persist publication/delivery intent and each attempt; reconcile unknown outcomes before a retry.
- Define retryable versus permanent errors, exponential backoff, dead-letter/manual-intervention path, and observability.
- Test recovery after process crash at each side-effect boundary.

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

- A crashed workflow can resume without corrupting completed domain state.
- Two workers cannot concurrently own the same unexpired lease.
- Repeated identical ingestion does not duplicate articles or revisions.
- Creating a decision and updating its case effective-decision pointer is atomic.
- An uncertain publication/delivery outcome is reconciled before a new side-effecting attempt.
- Retries preserve the same logical operation and idempotency key.
- Backup/restore tests cover in-progress workflow and pending external operation states.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | A crashed workflow can resume without corrupting completed domain state. | Architecture review and automated tests where applicable |
| AC-02 | Two workers cannot concurrently own the same unexpired lease. | Architecture review and automated tests where applicable |
| AC-03 | Repeated identical ingestion does not duplicate articles or revisions. | Architecture review and automated tests where applicable |
| AC-04 | Creating a decision and updating its case effective-decision pointer is atomic. | Architecture review and automated tests where applicable |
| AC-05 | An uncertain publication/delivery outcome is reconciled before a new side-effecting attempt. | Architecture review and automated tests where applicable |
| AC-06 | Retries preserve the same logical operation and idempotency key. | Architecture review and automated tests where applicable |
| AC-07 | Backup/restore tests cover in-progress workflow and pending external operation states. | Architecture review and automated tests where applicable |

Quantitative thresholds must be established using representative evaluation data or operational measurements. This ADR intentionally does not invent numerical targets.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- Workload requires multiple nodes or a distributed queue.
- Measured contention exceeds the selected database's capacity.
- A target's idempotency or reconciliation behavior changes.
- Recovery objectives or availability requirements materially increase.

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
