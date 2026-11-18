# GENI-ADR-016 — Persistence, Async Execution, Idempotency, and Recovery

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-016  
**Title:** Persistence, Async Execution, Idempotency, and Recovery  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Collection, event resolution, evidence analysis, reporting, publication, and delivery are multi-step workflows that can fail or restart. In-memory tasks and blind retries may lose work, duplicate domain changes, repeat external side effects, or leave uncertain outcomes. The system requires durable execution state, explicit transaction boundaries, concurrency control, idempotency, leases or equivalent ownership, and reconciliation.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

What persistence and execution guarantees are required to resume interrupted work safely and prevent duplicate domain changes or external side effects?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Persist workflow runs and step states needed for audit and recovery.
- Define atomic transaction boundaries for critical domain transitions.
- Use idempotency keys/fingerprints for repeatable domain operations and external side effects.
- Use leases or equivalent atomic ownership to prevent concurrent duplicate workers.
- Classify retryable, permanent, and unknown-outcome failures.
- Reconcile uncertain external publication/delivery outcomes before side-effecting retries.
- Support cancellation, deadlines, backoff, recovery, and manual escalation.
- Keep processing state separate from domain state.

### 3.2 Technical Constraints
- A database transaction cannot atomically include a remote provider side effect.
- Exactly-once external execution cannot be claimed without provider guarantees.
- Initial deployment may be single-node; distributed queues are not required by default.
- Database-specific behavior is governed by ADR-005.

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

### 4.1 Alternative A — In-memory best-effort workflows

**Description:** Keep state in process memory and retry failures opportunistically.

**Advantages:**
- Simple initial code.

**Disadvantages:**
- Work is lost on restart
- duplicate effects are difficult to prevent.

**Risks:**
- Data loss or repeated external side effects.

**Estimated Complexity:** Low

### 4.2 Alternative B — Distributed workflow platform immediately

**Description:** Adopt a durable orchestration platform from the first release.

**Advantages:**
- Mature workflow features and distributed execution.

**Disadvantages:**
- Operational and development overhead before scale is proven.

**Risks:**
- Premature infrastructure and platform coupling.

**Estimated Complexity:** High

### 4.3 Alternative C — Database-backed durable workflows

**Description:** Persist runs/steps, use bounded async workers, leases, idempotency, and reconciliation.

**Advantages:**
- Recoverable, auditable, compatible with simple deployment.

**Disadvantages:**
- Requires careful transaction and failure design.

**Risks:**
- Database throughput or locking may constrain scale.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | In-memory best-effort workflows | Distributed workflow platform immediately | Database-backed durable workflows |
|---|---|---|---|
| Restart recovery | Low | High | High |
| Initial operational complexity | Low | High | Medium |
| Duplicate-effect control | Weak | Strong if configured | Strong with explicit keys |
| Single-node suitability | High | Low | High |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Durable database-backed workflow state with bounded async execution and explicit idempotency/reconciliation.

Persist workflow runs and step state in the application persistence layer with atomic ownership and explicit transaction boundaries. Use deterministic idempotency keys for repeatable domain operations and durable intent records for external effects. External operations distinguish confirmed success, confirmed failure, and unknown outcome; an unknown outcome must be reconciled before retry. Start with bounded workers and a simple scheduler. Introduce distributed queues or workflow infrastructure only when measured workload, throughput, or availability requirements justify them.

**Rationale:**
- Allows interrupted work to resume from durable checkpoints.
- Prevents duplicate state changes and makes external effects auditable.
- Avoids premature distributed infrastructure while preserving an upgrade path.

**Required logical persistence contracts:**

- `ExecutionLease` is the authoritative ownership record for a ProcessingRun or ProcessingStep. It carries a stable owner identity, expiry/heartbeat state, and a monotonically increasing fencing token. Lease acquisition/renewal is atomic; every worker state change validates the current token so a stale worker cannot commit after ownership changes.
- Run/step lease timestamps are query projections only; they do not establish ownership by themselves.
- `IdempotencyRecord` is unique by `(operation_scope, idempotency_key)` and stores a request fingerprint and operation outcome. Reusing a key with a different fingerprint is a conflict; reusing it with the same fingerprint returns/resumes the existing logical operation.
- Local domain effects and idempotency state share a transaction where possible. External effects use durable intent and explicit reconciliation; unknown outcomes are not treated as confirmed failures and must be reconciled before retry.
- Lease duration, renewal interval, worker topology, and database-specific locking are deployment/implementation choices and remain deferred until measured and formally reviewed.

**Deferred Questions:**
- Lease duration and renewal intervals.
- Queue technology and worker topology.
- Database-specific transaction implementation.
- Quantitative recovery-time and throughput objectives.

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
- Durable and observable workflow execution.
- Safer retry and recovery behavior.
- Supports a simple deployment while preserving correctness.

### 8.2 Negative Consequences
- Additional persistence and operational state.
- More complex transitions and recovery tests.

### 8.3 Technical Trade-Offs
The design does not promise exactly-once execution. It targets at-least-once invocation with idempotent domain effects and explicit reconciliation for external operations. Distributed workflow infrastructure remains a measured future option.

### 8.4 Operational Consequences
Monitor stuck runs, expired leases, retry exhaustion, queue age, reconciliation backlog, and backup/restore health.

### 8.5 Product and Business Consequences
The system is less likely to lose collected news or duplicate publication/delivery after interruption.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Database lock contention | Medium | High | Measure workload, bound concurrency, and define engine escalation criteria. |
| Incorrect idempotency scope | Medium | Critical | Define scope by logical operation, resource, and destination. |
| False success after timeout | Medium | Critical | Use unknown-outcome state and reconciliation. |
| Lost workflow ownership | Medium | High | Use atomic leases, expiry, and compare-and-swap semantics. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- WorkflowOrchestrator
- Repository/UnitOfWork implementations
- PublicationService
- ReportDelivery
- Collection adapters
- ObservabilityService

### 9.2 Affected Data Models and Interfaces
- ProcessingRun
- ProcessingStep
- ExecutionLease
- IdempotencyRecord
- PublicationRecord/Attempt
- DeliveryRecord/Attempt
- CollectionCheckpoint

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-005 | Depends on / Related to | Database choice and transaction semantics constrain persistence. |
| GENI-ADR-009 | Related to | Collection checkpoints and acquisition recovery. |
| GENI-ADR-004 | Related to | Publication side effects require durable intent and reconciliation. |
| GENI-ADR-014 | Related to | Review tasks are durable workflows. |
| GENI-ADR-006 | Related to | Provider calls need bounded timeouts and retry classification. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define run/step lifecycle and state transitions.
- Define transaction boundaries for event decisions, associations, publication, and delivery records.
- Implement atomic worker ownership and stale-lease recovery.
- Add idempotency keys and uniqueness constraints.
- Separate local retry from external-side-effect reconciliation.
- Add failure injection at persistence and external-call boundaries.
- Document backup, restore, and migration operations.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-005 — Database choice and transaction semantics constrain persistence.
- GENI-ADR-009 — Collection checkpoints and acquisition recovery.
- GENI-ADR-004 — Publication side effects require durable intent and reconciliation.
- GENI-ADR-014 — Review tasks are durable workflows.
- GENI-ADR-006 — Provider calls need bounded timeouts and retry classification.

### 10.4 Implementation Sequence
1. Define aggregates and transaction boundaries.
2. Implement durable run/step persistence.
3. Implement leases/ownership and recovery.
4. Implement idempotency records and unique constraints.
5. Implement external operation reconciliation.
6. Add failure-injection, backup, restore, and recovery tests.

### 10.5 Verification Requirements
- Crash before and after each transaction boundary and verify recoverability.
- Run concurrent workers and verify one owner per step.
- Retry the same request and verify no duplicate domain effect.
- Simulate timeout after a provider accepted an operation and verify reconciliation precedes retry.
- Verify cancellation and deadlines do not corrupt committed state.
- Test backup/restore and expired leases.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Workflow run/step history is durable and queryable. | Persistence tests |
| AC-02 | Critical domain changes are transactionally consistent. | Integration tests |
| AC-03 | Concurrent ownership prevents duplicate workers. | Concurrency tests |
| AC-04 | Idempotency prevents duplicate domain effects. | Repeated-request tests |
| AC-05 | Unknown external outcomes require reconciliation before retry. | Failure-injection tests |
| AC-06 | Recovery works after process restart. | Recovery exercise |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Measured write concurrency exceeds engine capacity.
- Multi-process or multi-node deployment becomes necessary.
- Recovery/availability objectives change.
- External target semantics invalidate current idempotency assumptions.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines WorkflowOrchestrator and execution contracts. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines run/step, idempotency, publication and delivery persistence. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines persistence and recovery implementation. |
| `GENI-ADR-005` | Internal | Persistence engine selection. |
| `GENI-ADR-004` | Internal | Publication operation separation. |
| `GENI-ADR-006` | Internal | Provider execution timeout/retry semantics. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Defined logical ExecutionLease fencing and scoped IdempotencyRecord contracts and aligned the data model with recovery requirements. | AI Architecture Assistant |

**End of ADR**
