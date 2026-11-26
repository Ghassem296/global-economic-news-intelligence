# GENI-ADR-005 Evidence — Persistence Proof-of-Concept Protocol

**Project:** Global Economic News Intelligence  
**Evidence ID:** GENI-ADR-005-POC-001  
**Related ADR:** GENI-ADR-005 — Initial Persistence Technology and Migration Strategy  
**Version:** 1.3
**Status:** Proposed PostgreSQL qualification protocol — production qualification not yet passed  
**Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Last Updated:** 2026-11-24

---

## 1. Purpose and authority

This protocol defines a reproducible PostgreSQL qualification proof-of-concept (PoC). The Project Owner selected PostgreSQL as GENI's target relational engine on 2026-11-26; this protocol verifies whether the proposed PostgreSQL implementation satisfies the approved workload, correctness, recovery, security, and operational requirements before production activation.

It is a test plan, not test evidence, a benchmark result, or production approval. The engine direction is owner-selected, but no qualification result may be reported as measured until the test has actually run and its raw artifacts, environment, commit SHA, and analysis are retained.

The PoC supplies the evidence required for the Project Owner to complete formal acceptance of GENI-ADR-005. Passing this protocol does not automatically accept the ADR or authorize production deployment.

## 2. Questions the PoC must answer

1. Can the selected PostgreSQL version enforce the required relational integrity and append-only history?
2. Can PostgreSQL preserve the documented UnitOfWork write sets under success, conflict, cancellation, and injected failure?
3. What happens under the approved number of concurrent readers and writers, including lock contention and stale aggregate updates?
4. Can asynchronous application workers access PostgreSQL safely without blocking the event loop or exhausting connections?
5. Can idempotency, lease ownership, fencing tokens, and recovery survive process termination and competing workers?
6. Can a clean install, schema upgrade, backup, restore, and post-restore integrity check be repeated reliably?
7. Can the project reliably operate PostgreSQL, including deployment, security, monitoring, maintenance, backup, restore, and recovery?
8. Does PostgreSQL satisfy every approved workload and operational requirement without relying on unverified portability assumptions?

## 3. Preconditions: define the workload before measuring

### 3.1 Previously stated initial planning baseline

The project owner's earlier planning direction establishes the following provisional baseline for the first deployment:

- Single application instance and local/early-validation deployment.
- A limited set of reputable international news sources.
- Simple scheduling; no distributed task queue in the initial stage.
- SQLite is the preferred initial candidate for operational simplicity.
- PostgreSQL is a later-scale alternative to reconsider if multiple application instances, higher write concurrency, larger datasets, or concurrent workers become necessary.

These are planning assumptions and a preference, not an Accepted ADR, a measured workload, or production authorization. The PoC must test whether SQLite actually satisfies the workload and correctness requirements. PostgreSQL remains a comparative challenger; the project must not build unnecessary distributed infrastructure merely to benchmark it.

No numeric article volume, concurrent-writer count, event/report volume, retention duration, availability target, RPO/RTO, hosting specification, or budget has been established in the available project decisions. These values remain unknown and must not be invented. The Project Owner must derive and approve any numeric workload and operational thresholds before the comparative results are examined. If those figures remain unavailable, the PoC may complete correctness and operational-feasibility tests, but it cannot claim workload capacity or final engine selection.

The Project Owner must record a workload profile before running comparative benchmarks. Unknown values remain explicitly unknown; they must not be filled with convenient guesses.

| Profile field | Required evidence |
|---|---|
| Deployment topology | Single process, multiple processes, hosts, regions, and expected growth |
| Concurrent writers | Expected normal, peak, and burst writer counts, with derivation |
| Concurrent readers | Expected normal, peak, and burst reader counts, with derivation |
| Ingestion workload | Expected articles/revisions per time interval and burst pattern |
| Domain workload | Expected duplicate evaluations, event-match decisions, evidence, analyses, and report writes |
| Read workload | Main query shapes, pagination, history access, and read/write mix |
| Dataset profile | Representative row counts, relationship cardinalities, payload-size distribution, and retention horizon |
| Async behavior | Worker count, task duration, cancellation, deadlines, and connection lifecycle |
| Availability | Required service availability and acceptable maintenance windows |
| Recovery | Approved Recovery Point Objective (RPO) and Recovery Time Objective (RTO), if defined |
| Operations | Hosting constraints, backup destination, monitoring, restore operator, and maintenance capacity |
| Security | Access-control, encryption, secret-management, backup-protection, and audit requirements |
| Cost | Hosting, storage, operations, support, and migration cost assumptions |

The workload profile must identify the source and confidence of each value. Product aspirations are not workload measurements. If a mandatory target has not been approved, record it as an unresolved decision and do not declare a candidate compliant with it.

## 4. Candidate implementations and fairness controls

Evaluate the PostgreSQL implementation against the logical repository contracts, domain write sets, synthetic fixtures, application revision, and approved workload profile. SQLite comparison runs are out of scope because it is no longer an active candidate.

For each run, capture:

- Repository commit SHA and clean/dirty working-tree state.
- Operating system, kernel, CPU, RAM, storage device/filesystem, and available disk space.
- Database engine and exact version; relevant compile/build options.
- Driver, ORM/query layer, migration tool, and exact versions.
- Python/runtime version and dependency lockfile hash.
- Connection/pool configuration and worker topology.
- PostgreSQL transaction isolation, connection limits, pool settings, checkpoint/autovacuum-relevant configuration, durability settings, and deployment/storage characteristics.
- Dataset seed, row counts, payload distribution, workload generator version, and test duration.
- Warm-up, repetitions, cache state, measurement method, raw output, errors, and deviations.

Do not compare different hardware, durability guarantees, transaction semantics, dataset sizes, or application behavior as if they were equivalent. Any engine-specific tuning must be documented and reviewed; default and tuned results must be distinguished. WAL must be an explicit SQLite test variant, not silently assumed. PostgreSQL durability must not be weakened merely to improve benchmark numbers.

## 5. Mandatory correctness and failure matrix

Correctness gates are pass/fail. A fast result cannot compensate for a violated invariant.

| ID | Scenario | Required observation |
|---|---|---|
| POC-01 | Foreign keys enabled and invalid references attempted | Invalid relationships are rejected by the database |
| POC-02 | Canonical unique keys and duplicate idempotency replay | One logical record/effect; same key with different fingerprint is a conflict |
| POC-03 | Immutable candidate/decision append and successor chain | History is preserved; at most one effective successor under concurrent attempts |
| POC-04 | Atomic EventMatchDecision and ArticleEventLink write set | Injected failure leaves neither a partial decision/link state nor an inconsistent projection |
| POC-05 | Atomic EvidenceLocation, AnalysisInput/AnalysisEvidenceLink, and Report provenance child writes through parent repositories | A failure rolls back the entire parent aggregate write set |
| POC-06 | Optimistic concurrency with two stale writers | At most one update succeeds for the same expected aggregate version; the other receives a typed conflict |
| POC-07 | Competing lease acquisition/renewal | Ownership is atomic; one current owner is authoritative |
| POC-08 | Stale worker resumes after lease takeover | A stale fencing token cannot commit any protected state change |
| POC-09 | Process termination during a transaction | Transaction is wholly committed or rolled back; no partial write set |
| POC-10 | Process termination after durable local commit but before acknowledgement | Same-fingerprint retry safely returns/resumes the existing logical operation |
| POC-11 | Concurrent read/write workload | No lost updates, dirty reads, or violations of the documented isolation contract |
| POC-12 | Async load and cancellation | Event loop remains responsive; cancellation and connection cleanup are deterministic |
| POC-13 | Clean migration from empty database | All migrations apply in order and schema constraints are present |
| POC-14 | Upgrade from each supported prior schema | Data, history, constraints, and application compatibility are preserved |
| POC-15 | Backup during representative activity and restore to isolated target | Restored database passes integrity checks and application-level invariant checks |
| POC-16 | Crash/restart and recovery exercise | Durable operations are discoverable and recoverable without blind duplicate effects |
| POC-17 | Backup protection and access-control review | Backup access, encryption, retention, and restore permissions meet approved security policy |
| POC-18 | Query plans and representative read paths | Required queries are correct and their plans/latency are recorded; no unsupported performance claim |

Tests must use synthetic data with no personal data, licensed source text, production credentials, or external provider calls. Failure injection must be deterministic and repeatable.

## 6. Performance and operational measurements

After correctness gates pass, measure PostgreSQL using the approved workload profile:

- Throughput by operation class, not only aggregate transactions per second.
- Median, p95, and p99 latency for reads and writes.
- Lock wait, busy/serialization errors, retries, deadlocks, and transaction duration.
- Queue depth, connection utilization, worker idle/busy time, and event-loop responsiveness.
- CPU, memory, disk I/O, database size, index size, and backup size.
- Migration duration and restore duration.
- Recovery behavior and data loss, measured against approved RPO/RTO.
- Operational steps, manual interventions, failure modes, and maintenance burden.

Record warm-up separately. Run enough repetitions to show variability; publish the raw observations and method. Do not select a candidate from a single run or from a synthetic microbenchmark that does not represent the workload.

No numeric pass threshold is defined in this protocol. Predeclared thresholds must be approved from the workload profile, product requirements, and operational policy before the comparative results are examined. Do not invent thresholds after seeing the results to make a preferred engine pass.

## 7. Decision method

Apply the following order:

1. **Hard correctness gates:** Any reproducible integrity, atomicity, fencing, migration, or recovery failure is a blocker until fixed and retested.
2. **Mandatory workload gates:** A candidate must satisfy every approved workload, deployment, security, availability, backup, and recovery requirement.
3. **Operational feasibility:** Confirm that the project can reliably deploy, monitor, back up, restore, secure, upgrade, and support the candidate.
4. **Comparative evidence:** Compare performance, resource use, cost, complexity, and growth headroom using the same workload and documented methodology.
5. **Selection:** If only one candidate passes all mandatory gates, recommend it with limitations. If both pass, select based on the approved workload and operational trade-offs; the simpler operational model may be preferred only when it meets all requirements. If neither passes, do not select either: revise the architecture or requirements and repeat the PoC.

A repository abstraction is not proof of portability. Portability is limited to repository behaviors exercised by contract tests on every supported engine. Engine-specific locking, isolation, migrations, indexes, and backup procedures remain explicitly documented.

## 8. Required evidence artifacts

The completed PoC package must include:

- Approved workload profile and target thresholds, with owners and sources.
- Reproducible setup instructions and exact candidate versions/configurations.
- Synthetic dataset generator, seed, and dataset summary.
- Correctness/failure test results for every POC-01 through POC-18 case.
- Raw benchmark output and machine-readable summary (CSV or JSON).
- Backup/restore and migration logs, including integrity-check output.
- Deviations, failed runs, fixes, and retest links.
- Operational runbook drafts and estimated recurring effort/cost with assumptions.
- Comparative analysis, limitations, and recommendation.
- Commit SHA and CI evidence for the exact tested revision.

### 8.1 Results register

| Field | PostgreSQL |
|---|---|---|
| Exact version/configuration | Not run | Not run |
| Workload profile ID | Not established |
| Correctness matrix | Not run | Not run |
| Migration/upgrade | Not run |
| Backup/restore | Not run |
| Concurrency and async | Not run |
| Performance results | Not measured | Not measured |
| Operational assessment | Not assessed | Not assessed |
| Mandatory gates | Not evaluated | Not evaluated |

This register must be updated only from actual retained evidence. “Not run” must never be rewritten as “pass” based on design review or documentation.

## 9. Approval and implementation boundary

Until the PoC is complete and GENI-ADR-005 is formally Accepted:

- Do not add a production database dependency or select an ORM, driver, migration tool, or async database strategy.
- Do not create production migrations or claim database-backed repository implementation.
- Do not treat SQLite as the default merely because it is convenient for local development.
- Do not treat PostgreSQL as selected merely because it supports higher concurrency.
- Pure domain contracts, synthetic fixtures, and database-independent repository interfaces may continue only within their approved scope.
- Any temporary experimental adapter must be isolated, explicitly non-production, and must not leak database-specific types into domain/application contracts.

After qualification and formal acceptance, record the exact PostgreSQL version, driver, query/ORM layer, migration tool, async strategy, transaction/locking model, connection lifecycle, supported deployment topology, and tested backup/restore procedure in the implementation baseline and update the affected documents.

---

## 10. Change history

| Version | Date | Status | Change Summary |
|---|---|---|---|
| 1.0 | 2026-11-24 | Proposed | Initial reproducible persistence PoC protocol; no engine selected |
| 1.1 | 2026-11-24 | Proposed | Clarified the stale-worker fencing acceptance criterion for machine-checkable alignment. |
| 1.2 | 2026-11-24 | Proposed | Recorded the previously stated single-instance/local SQLite-first planning baseline while preserving unknown workload figures and the unselected ADR status. |\n| 1.3 | 2026-11-26 | Proposed | Re-scoped the protocol to qualify the Project Owner-selected PostgreSQL target; removed SQLite comparative testing while preserving workload, correctness, recovery, and production-approval gates. |

**End of Evidence Protocol**
