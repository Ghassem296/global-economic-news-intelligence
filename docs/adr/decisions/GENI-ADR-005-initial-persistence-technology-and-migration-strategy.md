# GENI-ADR-005 — Initial Persistence Technology and Migration Strategy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-005  
**Title:** Initial Persistence Technology and Migration Strategy  
**Status:** Proposed  
**Version:** 1.3  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

GENI requires durable relational relationships across articles, revisions, events, evidence, decisions, reports, and workflow records. The project documents currently identify SQLite as an initial candidate and PostgreSQL as a possible future option, but the actual database, ORM, migration tooling, and concurrency strategy remain unapproved. A premature technology choice may constrain transactional consistency, concurrent processing, migrations, or deployment operations.

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
- SQLite is a candidate, not an approved selection.
- PostgreSQL is a possible future engine, not a guaranteed drop-in migration target.
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

### 4.1 Alternative A — SQLite-first implementation

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

### 4.2 Alternative B — PostgreSQL-first implementation

**Description:** Use PostgreSQL from the first release and operate a client-server database.

**Advantages:**
- Stronger multi-client concurrency and mature operational capabilities.

**Disadvantages:**
- Requires database service operations, backups, access control, and deployment management.

**Risks:**
- Operational complexity may be premature for an early single-node product.

**Estimated Complexity:** Medium

### 4.3 Alternative C — Portable relational boundary with evidence-based engine selection

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

**Recommended Alternative:** Alternative C — Portable relational boundary with evidence-based initial engine selection.

Establish a relational persistence architecture with repository and unit-of-work boundaries, explicit domain transactions, versioned migrations, and database-specific integration tests. Do not declare SQLite or PostgreSQL accepted solely from the current documentation. Select the initial physical engine after a proof-of-concept that measures the expected write concurrency, workload, backup/recovery needs, async access, deployment constraints, and operational capacity. SQLite may be selected if these tests demonstrate that its single-node concurrency and operational model satisfy the initial workload; otherwise use PostgreSQL.

**Rationale:**
- Keeps the logical data model and domain logic stable.
- Makes the database selection evidence-based rather than aspirational.
- Preserves a path to another relational engine without claiming automatic portability.
- Makes engine-specific constraints visible through integration tests.

**Assumptions:**
- Initial operation may be single-node, but the expected concurrent writers must be measured.
- Relational integrity and transaction consistency are more important than early distributed scale.
- The project can perform a small persistence proof-of-concept before final engine selection.

**Deferred Questions:**
- Final database engine and version.
- ORM/query and async driver selection.
- Migration tool selection.
- Quantitative throughput and concurrent-write targets.

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
- Avoids premature commitment to a physical database.
- Clarifies transactional and repository boundaries.
- Makes migration and recovery testable.

### 8.2 Negative Consequences
- Requires an explicit proof-of-concept before implementation can be finalized.
- Some database behavior cannot be abstracted away.
- Multiple test backends can increase CI effort.

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
| Premature SQLite selection | Medium | High | Prove expected concurrent write workload before selection. |
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

The comparative test method, workload-profile template, mandatory correctness/failure matrix, measurement controls, decision method, and evidence-artifact requirements are defined in `docs/adr/evidence/GENI-ADR-005-persistence-proof-of-concept-protocol.md`.

That protocol is part of the evidence required to resolve this ADR. It is not itself evidence that either engine has passed. The workload profile and numeric pass thresholds must be approved before comparative results are examined. All tests must use synthetic data and reproducible configurations; no real source content, personal data, production secrets, or provider calls are permitted.

The PoC must test the persistence semantics required by GENI-ADR-016, including atomic idempotency state, lease ownership, fencing, unknown-outcome recovery, and stale-worker rejection. GENI-ADR-016 remains a separate Proposed decision: the PoC may validate candidate-engine behavior against the proposed contract, but it does not accept ADR-016 or authorize production durable execution.

The evidence package must include raw results and failed runs, exact versions/configuration, workload profile, commit SHA, migration and backup/restore logs, and a comparative analysis. A narrative statement that a test passed without reproducible artifacts is insufficient.

---

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Approve and complete the workload profile and predeclare mandatory thresholds using the GENI-ADR-005 PoC protocol.
- Implement comparable, isolated schema/migration prototypes for SQLite and PostgreSQL if both remain candidates; use the same logical repository contracts and synthetic workload.
- Execute every applicable correctness/failure case in PoC-001 before considering performance results.
- Measure operation-class throughput/latency, lock contention, async behavior, resource use, migration, backup/restore, crash recovery, and operational effort under controlled and recorded configurations.
- Retain raw outputs, failed runs, exact environment/configuration, commit SHA, and a reproducible analysis; do not report unrun tests as passing.
- Document engine-specific constraints and migration implications before final selection.
- Keep the production database dependency, ORM/driver, migration tool, and async strategy unselected until the ADR is formally Accepted.

### 10.2 Migration or Compatibility Requirements
Existing data and implementation choices must be inspected before migration is designed. No production migration is claimed by this proposal. Any schema or interface migration must preserve historical traceability and must be tested from the current baseline.

### 10.3 Dependencies
- GENI-ADR-016 — Defines persistence consistency, async execution, idempotency, and recovery.
- GENI-ADR-001 — The event-centric domain model determines relational aggregates and relationships.
- GENI-ADR-002 — Deduplication and event matching require reliable unique constraints and transactions.

### 10.4 Implementation Sequence
1. Define critical aggregates and transaction boundaries.
2. Define repository and migration interfaces.
3. Build a small persistence proof-of-concept for the expected workload.
4. Measure concurrency, latency, locking, recovery, and operational effort.
5. Record the selected engine and exact versions in a follow-up decision or approved revision.
6. Run migrations and backup/restore tests in CI.

### 10.5 Verification Requirements
- Test all foreign keys, unique constraints, and transactional invariants against the selected engine.
- Simulate concurrent ingestion, matching, and workflow updates.
- Test crash recovery, backup consistency, and restore.
- Run migration from an empty database and from the prior schema version.
- Verify repository contract tests on every supported engine.

Implementation verification remains deferred until this ADR is accepted and the corresponding capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | The initial database engine is selected using a documented workload and operational comparison. | Architecture decision review |
| AC-02 | Domain and application layers do not expose database-specific types. | Code review and dependency tests |
| AC-03 | Critical state transitions have explicit transaction boundaries. | Repository integration tests |
| AC-04 | Migrations are versioned and tested from empty and prior schemas. | CI migration tests |
| AC-05 | Backup and restore procedures are tested. | Recovery exercise |
| AC-06 | Portability claims are limited to behavior proven by repository contract tests. | Architecture review |
| AC-07 | The comparative PoC protocol is executed with an approved workload profile, predeclared thresholds, raw reproducible evidence, and all mandatory correctness gates. | Review of GENI-ADR-005 PoC-001 artifacts |
| AC-08 | The selected engine, exact versions, driver, migration/async strategy, transaction model, and operational procedures are explicitly recorded only after formal ADR acceptance. | Accepted ADR and synchronized implementation baseline |

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
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Lists SQLite and other technologies as candidates pending ADR approval. |
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

**End of ADR**
