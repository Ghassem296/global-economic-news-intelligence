# GENI-ADR-005 — Initial Persistence Technology and Migration Strategy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-005  
**Title:** Initial Persistence Technology and Migration Strategy  
**Status:** Proposed  
**Version:** 1.7  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

GENI requires durable relational relationships across articles, revisions, events, evidence, decisions, reports, and workflow records. On 2026-11-26, the Project Owner explicitly directed that PostgreSQL be the target relational database for GENI. This supersedes the earlier SQLite-first planning preference and removes SQLite from the active initial-engine selection. The PostgreSQL target is an owner-selected architectural direction; production qualification, exact engine/driver/tool versions, transaction and concurrency strategy, and operational readiness remain gated by the PostgreSQL-specific proof-of-concept and formal ADR acceptance.

This ADR is a proposal for formal review. It does not approve a production implementation or override an existing accepted decision.

## 2. Decision Question

What persistence architecture and selection criteria should govern the initial database, repository boundary, migration strategy, and future database portability?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Use a relational model for strongly related domain records and integrity constraints.
- Keep domain/application logic independent of database-specific types and SQL dialects.
- Use explicit transaction boundaries for critical aggregate and workflow state transitions.
- Version schema changes and test forward migration, rollback or recovery, and backup/restore.
- Prove concurrency, async-access, and workload assumptions before selecting the initial engine.
- Preserve referential integrity, uniqueness, and audit-history requirements.

### 3.2 Technical Constraints
- PostgreSQL is the Project Owner-selected target relational engine; production use remains gated by qualification and formal ADR acceptance.
- SQLite is not an active implementation or comparison target for the initial GENI persistence layer.
- Repositories must preserve aggregate and transaction boundaries rather than simply wrap every table.
- External side effects require durable intent and reconciliation, not a long database transaction.

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

### 4.1 Alternative A — SQLite-first implementation (not selected)

**Description:** Select SQLite immediately and design the first release around its transaction and write-concurrency characteristics.

**Advantages:**
- Simple local deployment
- low operational overhead
- suitable for small single-node workloads.

**Disadvantages:**
- Single-writer constraints and concurrent-write behavior may limit throughput.

**Risks:**
- Workload growth may require early redesign or migration.

**Estimated Complexity:** Low initially

### 4.2 Alternative B — PostgreSQL-first implementation (owner-selected target)

**Description:** Use PostgreSQL from the first release and operate a client-server database.

**Advantages:**
- Stronger multi-client concurrency and mature operational capabilities.

**Disadvantages:**
- Requires database service operations, backups, access control, and deployment management.

**Risks:**
- Operational complexity may be premature for an early single-node product.

**Estimated Complexity:** Medium

### 4.3 Alternative C — Portable relational boundary with evidence-based engine selection (superseded)

**Description:** Define relational contracts, repositories, migrations, and transaction semantics first; select SQLite or PostgreSQL after a workload and deployment proof.

**Advantages:**
- Avoids premature commitment while preserving explicit selection criteria.

**Disadvantages:**
- Requires a comparative proof-of-concept and careful avoidance of false portability claims.

**Risks:**
- Abstraction can hide engine-specific behavior if tests are inadequate.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | SQLite-first implementation | PostgreSQL-first implementation | Portable relational boundary with evidence-based engine selection |
|---|---|---|---|
| Initial operational simplicity | High | Medium | High with selected engine |
| Concurrent write capacity | Limited by design | High | Measured before selection |
| Transactional capabilities | Adequate for constrained workloads | Strong | Must be proven |
| Migration portability | Low to Medium | Medium | Designed and tested, not assumed |
| Operational burden | Low | Medium to High | Depends on selected engine |

The principal evaluation priorities are:
- Use a relational model for strongly related domain records and integrity constraints.
- Keep domain/application logic independent of database-specific types and SQL dialects.
- Use explicit transaction boundaries for critical aggregate and workflow state transitions.
- Version schema changes and test forward migration, rollback or recovery, and backup/restore.

Unmeasured latency, throughput, quality, and cost are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative B — PostgreSQL-first implementation, explicitly selected by the Project Owner on 2026-11-26.

Implement the persistence boundary against PostgreSQL only: repository contracts, UnitOfWork, versioned migrations, database constraints, and PostgreSQL-specific integration tests. Do not introduce SQLite as a second supported engine or maintain a dual-dialect abstraction merely for hypothetical portability. Before production activation, qualify PostgreSQL against the approved workload profile and mandatory correctness, concurrency, async, migration, backup/restore, recovery, security, and operational checks in GENI-ADR-005-POC-001. Exact PostgreSQL version, driver, query/ORM layer, migration tool, async strategy, isolation/locking approach, pool configuration, and deployment topology remain open until supported by qualification evidence.

**Rationale:**
- Records the Project Owner's explicit PostgreSQL direction.
- Provides a client-server relational engine for concurrent application access and mature operational controls.
- Keeps domain/application contracts independent of database-specific implementation details without promising cross-engine portability.
- Makes production readiness dependent on reproducible PostgreSQL-specific evidence.

**Assumptions:**
- PostgreSQL is the sole target for initial persistence implementation.
- Workload, concurrency, availability, retention, RPO/RTO, hosting, and budget values remain unknown until explicitly approved.
- Relational integrity, transaction consistency, and recoverability take precedence over unmeasured performance claims.

**Deferred Questions:**
- Exact PostgreSQL version and supported upgrade policy.
- Driver and ORM/query-layer selection.
- Migration tool and execution policy.
- Async access, transaction isolation, lock/fencing strategy, and connection-pool limits.
- Quantitative throughput, concurrency, availability, RPO/RTO, and retention targets.

A recommendation/owner direction is not production authorization. Formal ADR acceptance follows the qualification evidence.

## 7. Final Decision

**Selected Alternative:** Alternative B — PostgreSQL-first implementation (Project Owner direction recorded 2026-11-26)  
**Decision Status:** Proposed — owner-selected target; production qualification and formal ADR acceptance pending  
**Decision Owner:** Project Owner  
**Approved By:** Project Owner direction recorded in repository history; formal ADR acceptance pending  
**Approval Date:** 2026-11-26

**Decision Rationale:** The Project Owner explicitly selected PostgreSQL as the target database. This direction does not establish measured capacity or production readiness; those claims remain subject to the PostgreSQL-specific PoC and formal ADR acceptance.

**Conditions or Restrictions:**
- PostgreSQL is the sole target for new persistence implementation; do not add a parallel SQLite adapter.
- Production activation requires passing the PostgreSQL qualification gates and formal acceptance of this ADR.
- Do not treat deferred versions, drivers, migration tools, async strategies, or numeric workload targets as approved implementation values.
- Database-specific implementation must remain behind infrastructure boundaries.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Establishes PostgreSQL as the single target for persistence implementation and removes ambiguity about a parallel SQLite path.
- Clarifies transactional and repository boundaries while keeping database-specific behavior inside infrastructure adapters.
- Makes migration, concurrency, backup, restore, and recovery qualification explicit and testable.

### 8.2 Negative Consequences
- PostgreSQL introduces database-service operations, access control, monitoring, backup, restore, upgrade, and maintenance responsibilities that are heavier than an embedded database.
- Production readiness cannot be claimed until the PostgreSQL-specific PoC and formal ADR acceptance are complete.
- Exact driver, query/ORM layer, migration tool, async strategy, and transaction/locking configuration remain open and must be selected from reproducible evidence.

### 8.3 Technical Trade-Offs
The recommendation favors deliberate portability of logical contracts, not lowest-common-denominator SQL. Database-specific features may be used behind infrastructure boundaries when justified and tested. Switching engines later remains a planned migration project, not an automatic consequence of repository abstraction.

### 8.4 Operational Consequences
The selected engine must have documented backup, restore, monitoring, migration, concurrency, and upgrade procedures. Production capacity must be monitored against the original workload assumptions.

### 8.5 Product and Business Consequences
Database choice should not change user-facing domain semantics or the traceability of events and reports.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| False portability | Medium | High | Run repository contract tests and document engine-specific behavior. |
| Unqualified PostgreSQL activation | Medium | Critical | Keep production activation blocked until the PostgreSQL PoC passes its correctness, workload, recovery, security, and operational gates and this ADR is formally accepted. |
| Operationally premature PostgreSQL | Low to Medium | Medium | Compare operational capacity and deployment constraints. |
| Migration drift | Medium | High | Version migrations, review schema changes, and test clean installs. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- Repository implementations
- UnitOfWork / transaction boundary
- Migration tooling
- WorkflowOrchestrator
- Persistence adapters

### 9.2 Affected Data Models and Interfaces
- All relational domain entities
- Migration history
- Transaction and processing records

### 9.3 Affected Documents
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-016 | Depends on / Related to | Defines persistence consistency, async execution, idempotency, and recovery. |
| GENI-ADR-001 | Related to | The event-centric domain model determines relational aggregates and relationships. |
| GENI-ADR-002 | Related to | Deduplication and event matching require reliable unique constraints and transactions. |

These relationships do not imply that any related Proposed ADR has been accepted.

## 9.1 Required persistence proof-of-concept protocol

The PostgreSQL qualification test method, workload-profile template, mandatory correctness/failure matrix, measurement controls, decision method, and evidence-artifact requirements are defined in GENI-ADR-005-POC-001, `docs/adr/evidence/GENI-ADR-005-persistence-proof-of-concept-protocol.md`.

That protocol is part of the evidence required to resolve this ADR. It is not itself evidence that PostgreSQL has passed. The workload profile and numeric pass thresholds must be approved before qualification results are examined. All tests must use synthetic data and reproducible configurations; no real source content, personal data, production secrets, or provider calls are permitted.

The PoC must test the persistence semantics required by GENI-ADR-016, including atomic idempotency state, lease ownership, fencing, unknown-outcome recovery, and stale-worker rejection. GENI-ADR-016 remains a separate Proposed decision: the PoC may validate candidate-engine behavior against the proposed contract, but it does not accept ADR-016 or authorize production durable execution.

The evidence package must include raw results and failed runs, exact versions/configuration, workload profile, commit SHA, migration and backup/restore logs, and a reproducible qualification analysis. A narrative statement that a test passed without reproducible artifacts is insufficient.

---

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Approve and complete the workload profile and predeclare mandatory thresholds using the GENI-ADR-005 PoC protocol.
- Implement an isolated PostgreSQL schema/migration prototype using the logical repository contracts and synthetic workload.
- Execute every applicable correctness/failure case in PoC-001 before considering performance results.
- Measure operation-class throughput/latency, lock contention, async behavior, resource use, migration, backup/restore, crash recovery, and operational effort under controlled and recorded configurations.
- Retain raw outputs, failed runs, exact environment/configuration, commit SHA, and a reproducible analysis; do not report unrun tests as passing.
- Document PostgreSQL-specific constraints and migration implications; PostgreSQL is the owner-selected target, while qualification and production acceptance remain pending.
- Keep the production database dependency, ORM/driver, migration tool, and async strategy unselected until the ADR is formally Accepted.

### 10.2 Migration or Compatibility Requirements
Existing data and implementation choices must be inspected before migration is designed. No production migration is claimed by this proposal. Any schema or interface migration must preserve historical traceability and must be tested from the current baseline.

### 10.3 Dependencies
- GENI-ADR-016 — Defines persistence consistency, async execution, idempotency, and recovery.
- GENI-ADR-001 — The event-centric domain model determines relational aggregates and relationships.
- GENI-ADR-002 — Deduplication and event matching require reliable unique constraints and transactions.

### 10.4 Implementation Sequence
1. Define critical aggregates, write sets, and transaction boundaries from the approved domain contracts.
2. Approve the PostgreSQL workload profile and predeclare mandatory thresholds before measurement.
3. Build an isolated, synthetic-data PostgreSQL proof-of-concept without enabling production use.
4. Execute the correctness/failure matrix first; stop performance qualification if a hard correctness gate fails.
5. Measure concurrency, latency, locking, async behavior, recovery, and operational effort against the approved workload profile.
6. Retain reproducible artifacts and submit the results for formal ADR-005 acceptance; only then select and record exact production tooling and configuration.

### 10.5 Verification Requirements
- Test foreign keys, unique constraints, and transactional invariants against PostgreSQL.
- Simulate concurrent aggregate updates and workflow ownership using synthetic fixtures.
- Test crash recovery, backup consistency, restore, stale-worker fencing, and idempotent replay.
- Run migrations from an empty PostgreSQL database and from every supported prior schema.
- Verify repository contract behavior against the single supported PostgreSQL target; do not imply multi-engine support.

Implementation verification remains deferred until this ADR is accepted and the corresponding capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | PostgreSQL is qualified against an approved workload profile and documented operational requirements before production activation. | Review of GENI-ADR-005 PoC-001 evidence |
| AC-02 | Domain and application layers do not expose database-specific types. | Code review and dependency tests |
| AC-03 | Critical state transitions have explicit transaction boundaries. | Repository integration tests |
| AC-04 | Migrations are versioned and tested from empty and prior schemas. | CI migration tests |
| AC-05 | Backup and restore procedures are tested. | Recovery exercise |
| AC-06 | Portability claims are limited to behavior proven by repository contract tests. | Architecture review |
| AC-07 | The PostgreSQL qualification PoC is executed with an approved workload profile, predeclared thresholds, raw reproducible evidence, and all mandatory correctness gates. | Review of GENI-ADR-005 PoC-001 artifacts |
| AC-08 | The exact PostgreSQL version, driver, query/ORM layer, migration/async strategy, transaction model, and operational procedures are explicitly recorded only after formal ADR acceptance. | Accepted ADR and synchronized implementation baseline |

Any quantitative threshold must be grounded in representative datasets, operational measurements, contractual requirements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Write concurrency exceeds measured initial capacity.
- Multi-process or multi-node deployment becomes necessary.
- Backup, recovery, or availability requirements change.
- The selected engine reaches end-of-life or loses required capabilities.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Write concurrency exceeds measured initial capacity. Multi-process or multi-node deployment becomes necessary. Backup, recovery, or availability requirements change. The selected engine reaches end-of-life or loses required capabilities.

Reconsider this recommendation when its core assumptions are no longer valid or measured evidence demonstrates that it does not meet project requirements. A replacement decision must be recorded in a new or superseding ADR.

## 13. References and Supporting Evidence

The references below are internal project documents used to establish the current documented context. They are not claimed as empirical performance measurements or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines repository and workflow boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines relational entities, integrity constraints, and transactions. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Records PostgreSQL as the owner-selected target, subject to qualification and formal ADR acceptance. |
| `GENI-ADR-016` | Internal | Defines persistence and recovery behaviors that constrain engine selection. |
| `docs/adr/evidence/GENI-ADR-005-persistence-proof-of-concept-protocol.md` | Internal evidence protocol | Defines the reproducible workload, correctness/failure matrix, measurement controls, and required decision artifacts; it contains no test results. |

External legal review, provider measurements, market-data coverage measurements, and model-quality benchmarks remain outstanding wherever relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Initial proposal prepared for architecture review | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Aligned decision and review authority terminology with the Project Owner role defined in GENI-GOV-005. | AI Architecture Assistant |
| 1.3 | 2026-11-24 | Proposed | Added reproducible PoC protocol, predeclared workload/threshold requirements, correctness gates, and evidence-artifact criteria; database selection remains pending. | AI Architecture Assistant |
| 1.4 | 2026-11-24 | Proposed | Added the stable GENI-ADR-005-POC-001 identifier to the ADR evidence reference. | AI Architecture Assistant |
| 1.5 | 2026-11-26 | Proposed | Records the Project Owner-selected PostgreSQL target and PostgreSQL-specific qualification gate; production acceptance remains pending reproducible evidence. | AI Architecture Assistant |
| 1.6 | 2026-11-27 | Proposed | Removes stale SQLite-selection language and aligns consequences, implementation sequence, verification, and acceptance criteria with the owner-selected PostgreSQL target and its remaining qualification gates. | AI Architecture Assistant |
| 1.7 | 2026-11-27 | Proposed | References the explicit owner-approved workload-profile template in PoC-001 §3.2; numeric values and thresholds remain unset until Project Owner approval. | AI Architecture Assistant |

**End of ADR**
