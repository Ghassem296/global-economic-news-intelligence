# GENI-ADR-005 Evidence — Persistence Proof-of-Concept Protocol

**Project:** Global Economic News Intelligence  
**Evidence ID:** GENI-ADR-005-POC-001  
**Related ADR:** GENI-ADR-005 — Initial Persistence Technology and Migration Strategy  
**Version:** 1.7
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

### 3.1 Owner-selected PostgreSQL target

PostgreSQL is the Project Owner-selected target relational engine. The initial baseline remains a Single application instance and local/early-validation deployment; this is a planning topology, not a measured capacity or a production deployment authorization.

The Project Owner explicitly selected PostgreSQL as GENI's target relational engine on 2026-11-26. The initial qualification topology assumes a single application instance and local/early-validation deployment; any move beyond that topology requires an updated workload profile. This supersedes the earlier SQLite-first planning assumption. SQLite is not an active candidate or implementation target. The initial deployment topology, workload volumes, concurrent readers/writers, retention, availability, RPO/RTO, hosting, and budget must still be explicitly established; no numeric values may be invented.

The engine direction is an owner decision, not a measured capacity claim or production authorization. The PoC qualifies PostgreSQL itself and verifies that the selected configuration meets approved workload and operational requirements. The project must not introduce distributed infrastructure or numeric service guarantees without evidence.

No numeric article volume, concurrent-writer count, event/report volume, retention duration, availability target, RPO/RTO, hosting specification, or budget has been established in the available project decisions. These values remain unknown and must not be invented. The Project Owner must approve any numeric workload and operational thresholds before results are examined. If those figures remain unavailable, the PoC may complete correctness and operational-feasibility tests, but it cannot claim workload capacity or final production readiness.

The Project Owner must record a workload profile before running qualification measurements. Unknown values remain explicitly unknown; they must not be filled with convenient guesses.

The workload profile must identify the source and confidence of each value. Product aspirations are not workload measurements. If a mandatory target has not been approved, record it as an unresolved decision and do not declare a candidate compliant with it.

### 3.2 Workload-profile record template

Create one versioned workload-profile record before any qualification measurement. The following fields are mandatory. A field without an approved value must remain `UNSET — Project Owner input required`; do not substitute a convenient default or infer a numeric target from product aspirations.

| Profile field | Required content | Current state |
|---|---|---|
| Profile identity | Profile ID, version, owner, approval date, and evidence references for each approved value | UNSET |
| Deployment topology | Application instance count, worker topology, hosting model, and whether the local/early-validation baseline remains applicable | Single application instance is a planning baseline only; owner confirmation required |
| Article workload | Average and peak articles per day, burst window, payload-size distribution, source mix, and expected growth horizon | UNSET |
| Concurrent access | Concurrent readers, writers, background workers, and expected contention patterns | UNSET |
| Domain workload mix | Expected rates and proportions for article/revision writes, duplicate evaluation/decisions, event matching, evidence, analysis, report versions, and workflow state transitions | UNSET |
| Read workload | Critical query classes, read/write ratio, pagination patterns, and expected hot-key or skew behavior | UNSET |
| Dataset shape | Synthetic row counts by aggregate, relationship cardinalities, index expectations, and retained-data horizon | UNSET |
| Recovery objectives | Approved RPO, RTO, backup frequency, backup retention, restore target, and acceptable recovery intervention | UNSET |
| Availability and operations | Availability objective, maintenance window, monitoring/alerting expectations, and operator support capacity | UNSET |
| Resource and cost envelope | CPU, memory, storage/IOPS, network, hosting constraints, and approved recurring cost ceiling | UNSET |
| Correctness gates | Required outcomes for every POC-01 through POC-18 scenario; all are hard gates, not weighted scores | Defined in §5; owner approval of profile pending |
| Performance thresholds | Predeclared per-operation throughput and p50/p95/p99 latency limits, lock/retry limits, resource ceilings, and measurement duration/repetition policy | UNSET |
| Migration and recovery thresholds | Approved clean-install/upgrade, backup, restore, and crash-recovery limits | UNSET |

For every non-UNSET value, record its unit, source, confidence, owner, and rationale. Distinguish measured workload observations from estimates and product requirements. Any estimate must be explicitly labeled and approved; it must not be represented as measured evidence.

The workload profile must be approved before benchmark results are collected or examined. If the owner has not approved numeric workload or performance thresholds, correctness and operational-feasibility experiments may be recorded separately, but no workload-capacity or final production-readiness claim may be made. Updating the workload profile after seeing results requires a new profile version and a documented reason; thresholds must not be retrofitted to make an observed result pass.

## 4. Candidate implementations and fairness controls

Evaluate only the PostgreSQL implementation against the same logical repository contracts, domain write sets, synthetic fixtures, application revision, and approved workload profile. SQLite comparison runs are out of scope.

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

Do not compare different hardware, durability guarantees, transaction semantics, dataset sizes, or application behavior as if they were equivalent. Any engine-specific tuning must be documented and reviewed; default and tuned results must be distinguished. PostgreSQL durability must not be weakened merely to improve benchmark numbers.

### 4.1 Provisional PoC-only toolchain boundary

The PoC must execute against a real, isolated PostgreSQL instance; a design-only review is not a substitute for integration evidence. To avoid blocking the experiment on production approval, the PoC may provisionally select a candidate PostgreSQL major/minor version, Python driver, query/ORM layer (or direct SQL), migration tool, async execution approach, and connection-pool configuration solely for the disposable PoC environment. These are experimental candidates, not approved production selections.

Before a run, record the exact candidate versions, source, rationale, configuration, lockfile or immutable image digest, and any known limitations. Keep the candidate stack in a dedicated PoC dependency group/environment and isolated test infrastructure. Do not add it to the production runtime dependency set, expose its types through domain/application ports, create production migrations, connect to production systems, or use production data/secrets. A candidate may be changed between PoC revisions only with a recorded reason and a new run identity; results from different stacks must not be merged as if they were one run.

**First experimental candidate run (2026-11-27):** PostgreSQL 18.7 (`postgres:18.7`, image digest `sha256:64c8b0d31e4ab6ea665e8426ea406a94bf52de3c05b3a4a8bf713704eefa9328`), CPython 3.15.2, Psycopg 3.3.9 with its binary extra, native `AsyncConnection`, direct SQL (no ORM), and a small versioned SQL migration runner. The immutable image digest and exact Python/package versions were captured in GitHub Actions run `45940666045` for commit `218bdac2e7c0c0c923fa20e2b7ab86c830bd2373`. This is a provisional PoC stack only; it is not the selected production toolchain.

The PoC may report correctness and operational-feasibility evidence for its exact experimental stack. It may report capacity/performance compliance only against an approved workload profile and thresholds. No experimental result automatically approves the candidate for production. Production promotion requires completed evidence review and formal acceptance of GENI-ADR-005; ADR-016 remains independently Proposed unless separately accepted.

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

Record warm-up separately. Run enough repetitions to show variability; publish the raw observations and method. Do not claim qualification from a single run or from a synthetic microbenchmark that does not represent the workload.

No numeric pass threshold is defined in this protocol. Predeclared thresholds must be approved from the workload profile, product requirements, and operational policy before results are examined. Do not invent thresholds after seeing the results to make a preferred engine pass.

## 7. Decision method

Apply the following order:

1. **Hard correctness gates:** Any reproducible integrity, atomicity, fencing, migration, or recovery failure is a blocker until fixed and retested.
2. **Mandatory workload gates:** PostgreSQL must satisfy every approved workload, deployment, security, availability, backup, and recovery requirement.
3. **Operational feasibility:** Confirm that the project can reliably deploy, monitor, back up, restore, secure, upgrade, and support PostgreSQL.
4. **Comparative evidence:** Review measured performance, resource use, cost, complexity, and growth headroom using the approved workload and documented methodology.
5. **Selection:** If every mandatory PostgreSQL gate passes, submit the reproducible evidence for formal ADR-005 acceptance. If any mandatory gate fails, do not authorize production activation; revise the implementation or requirements and repeat the affected tests.

A repository abstraction is not proof of portability. This project targets PostgreSQL only; engine-specific locking, isolation, migrations, indexes, and backup procedures remain explicitly documented. Engine-specific locking, isolation, migrations, indexes, and backup procedures remain explicitly documented.

## 8. Required evidence artifacts

The completed PoC package must include:

- Approved workload profile and target thresholds, with owners and sources.
- Reproducible setup instructions and exact PostgreSQL version/configuration.
- Synthetic dataset generator, seed, and dataset summary.
- Correctness/failure test results for every POC-01 through POC-18 case.
- Raw benchmark output and machine-readable summary (CSV or JSON).
- Backup/restore and migration logs, including integrity-check output.
- Deviations, failed runs, fixes, and retest links.
- Operational runbook drafts and estimated recurring effort/cost with assumptions.
- Qualification analysis, limitations, and recommendation.
- Commit SHA and CI evidence for the exact tested revision.

### 8.1 Results register

| Field | PostgreSQL |
|---|---|
| Exact version/configuration | PostgreSQL 18.7; image `sha256:64c8b0d31e4ab6ea665e8426ea406a94bf52de3c05b3a4a8bf713704eefa9328`; CPython 3.15.2; Psycopg 3.3.9; direct SQL; native async connection; versioned SQL migration runner (PoC-only) |
| Workload profile ID | Not established; no capacity claim permitted |
| Correctness matrix | 16 test methods passed for POC-01–14, a POC-16 reconnect smoke test, and POC-18 query-plan capture; POC-15 and POC-17 not run; full POC-16 process-restart exercise remains pending |
| Migration/upgrade | POC-13 clean install and POC-14 data-preserving schema upgrade passed |
| Backup/restore | Not run (POC-15 pending) |
| Concurrency and async | POC-03, POC-07, POC-08, POC-11, and POC-12 passed in the isolated test run |
| Performance results | Not measured; workload profile and thresholds remain unset; POC-18 captured a query plan only |
| Operational assessment | Not assessed; POC-17 security/backup-control review pending |
| Mandatory gates | Partial correctness evidence only; PostgreSQL not qualified; ADR-005 remains Proposed |

The first run completed successfully in GitHub Actions run `45940666045` (commit `218bdac2e7c0c0c923fa20e2b7ab86c830bd2373`). The machine-readable artifact `postgres-poc-218bdac2e7c0c0c923fa20e2b7ab86c830bd2373` was uploaded with archive SHA-256 `faaa2560cde47b80af85998bff06edfb6816401aa4500336a4a086ef9763a707`. The 16 passing test methods establish only the scenarios explicitly listed above. In particular, a new-connection read is not a process-crash/restart exercise; backup/restore and the security/backup-control review remain unrun. Workload values and performance thresholds remain unset. PostgreSQL is not production-qualified and ADR-005 remains Proposed. “Not run” must never be rewritten as “pass” based on design review or documentation.

## 9. Approval and implementation boundary

Until the PoC is complete and GENI-ADR-005 is formally Accepted:

- Do not add a production database dependency or treat any PoC-only ORM, driver, migration tool, or async strategy as a production selection.
- Do not create production migrations or claim database-backed repository implementation.
- Do not treat SQLite as the default merely because it is convenient for local development.
- Do not treat PostgreSQL as production-qualified merely because it supports higher concurrency.
- Pure domain contracts, synthetic fixtures, and database-independent repository interfaces may continue only within their approved scope.
- A temporary experimental adapter and its dependencies must be isolated, explicitly non-production, recorded as PoC-only, and must not leak database-specific types into domain/application contracts.

After qualification and formal acceptance, review the experimental evidence and explicitly select or replace the production PostgreSQL version, driver, query/ORM layer, migration tool, async strategy, transaction/locking model, connection lifecycle, supported deployment topology, and backup/restore procedure. Record only the accepted production choices in the implementation baseline and update the affected documents.

---

## 10. Change history

| Version | Date | Status | Change Summary |
|---|---|---|---|
| 1.0 | 2026-11-24 | Proposed | Initial reproducible persistence PoC protocol; no engine selected |
| 1.1 | 2026-11-24 | Proposed | Clarified the stale-worker fencing acceptance criterion for machine-checkable alignment. |
| 1.2 | 2026-11-24 | Proposed | Recorded the previously stated single-instance/local SQLite-first planning baseline while preserving unknown workload figures and the unselected ADR status. |
| 1.3 | 2026-11-26 | Proposed | Re-scoped the protocol to qualify the Project Owner-selected PostgreSQL target; removed SQLite comparative testing while preserving workload, correctness, recovery, and production-approval gates. |

| 1.4 | 2026-11-27 | Proposed | Clarifies that PostgreSQL is already the owner-selected target but is not production-qualified by virtue of its concurrency capabilities; qualification remains evidence-based. |
| 1.5 | 2026-11-27 | Proposed | Adds an explicit owner-approved workload-profile template with unset values, evidence provenance, and a prohibition on inventing or retrofitting numeric thresholds. |
| 1.6 | 2026-11-27 | Proposed | Defines provisional, isolated PoC-only technology candidates and explicitly separates experimental evidence from production tool/dependency approval. |
| 1.7 | 2026-11-27 | Proposed | Records the first reproducible PostgreSQL 18.7/Psycopg 3.3.9 PoC run and its 16 passing test methods, while explicitly retaining backup/restore, security review, full restart, workload, performance, and production-acceptance gates as open. |

**End of Evidence Protocol**
