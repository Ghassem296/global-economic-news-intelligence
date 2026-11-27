# GENI-ADR-005 Evidence — Persistence Proof-of-Concept Protocol

**Project:** Global Economic News Intelligence  
**Evidence ID:** GENI-ADR-005-POC-001  
**Related ADR:** GENI-ADR-005 — Initial Persistence Technology and Migration Strategy  
**Version:** 1.30
**Status:** Proposed PostgreSQL qualification protocol — production qualification not yet passed  
**Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Last Updated:** 2026-11-27

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
| Correctness gates | Required outcomes for every POC-01 through POC-31 scenario; all are hard gates, not weighted scores | Defined in §5; owner approval of profile pending |
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

**Experimental candidate stack (2026-11-27):** PostgreSQL 18.7 (`postgres:18.7`, image digest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`), CPython 3.15.2, Psycopg 3.3.9 with its binary extra, native `AsyncConnection`, direct SQL (no ORM), and a small versioned SQL migration runner. The immutable image digest and exact Python/package versions were captured in successful GitHub Actions run `45941330079` for commit `d0f8cec8f0df07373bf69178bd626d477a2edb9e`. This is a provisional PoC stack only; it is not the selected production toolchain.

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
| POC-19 | Restore user-defined cluster-global roles and memberships into a clean instance | Role attributes and memberships are restored without importing role passwords or replacing the destination bootstrap administrator |
| POC-20 | Separate least-privilege backup and restore identities | Backup identity can dump but cannot write; restore identity can restore only into its owned isolated target and cannot write to the source database |
| POC-21 | Fail-closed backup retention planning | Explicit policy, minimum verified-copy count, legal holds, immutability windows, invalid metadata, and deterministic candidate ordering are enforced; no deletion occurs |
| POC-22 | Failed migration after partial DDL execution | Transaction rollback removes all partial schema changes and does not record the failed migration as applied |
| POC-23 | Reapply every already-applied migration | Repeated migration execution is idempotent; schema-migration records and original application timestamps remain unchanged |
| POC-24 | Concurrent migration runners and complete SQL-file execution | Advisory-lock serialization prevents duplicate migration application; PL/pgSQL bodies containing internal semicolons execute intact |
| POC-25 | Article current-revision ownership | A composite foreign key rejects a current-revision pointer to a revision owned by another Article |
| POC-26 | Decision case and outcome integrity | A decision cannot reference a missing case or an outcome outside the constrained vocabulary |
| POC-27 | Source-identity lookup index integrity | Exactly one unique source-identity lookup index exists; a redundant non-unique index is absent |
| POC-28 | Atomic legacy Article revision backfill candidate | An invalid deferred current-revision pointer rolls back both revision insert and pointer update; a valid same-Article pair commits together |
| POC-29 | Concurrent ArticleRevision append and current-projection compare-and-swap | Two writers using the same expected Article version cannot both advance the current pointer; the losing transaction rolls back its revision insert, leaving one new revision and one consistent current pointer |
| POC-30 | New Article and first ArticleRevision creation order | A revision may be inserted before its new Article projection within one UnitOfWork because the owner FK is deferred until commit; the Article/current-revision pair commits atomically, while a revision with no parent Article is rejected at commit |
| POC-31 | Concurrent same-key idempotency claims and domain effects | Two workers using the same operation scope, key, and fingerprint produce one claim and one replay of the same completed result; the protected domain effect commits exactly once, and a different fingerprint is rejected |

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
- Correctness/failure test results for every currently defined POC-01 through POC-31 case.
- Raw benchmark output and machine-readable summary (CSV or JSON).
- Backup/restore and migration logs, including integrity-check output.
- Deviations, failed runs, fixes, and retest links.
- Operational runbook drafts and estimated recurring effort/cost with assumptions.
- Qualification analysis, limitations, and recommendation.
- Commit SHA and CI evidence for the exact tested revision.

### 8.1 Results register

| Field | PostgreSQL |
|---|---|
| Exact version/configuration | PostgreSQL 18.7; linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`; CPython 3.15.2; Psycopg 3.3.9; OpenSSL CLI AES-256-CBC/PBKDF2 (200,000 iterations) plus HMAC-SHA256 encrypt-then-MAC envelope; native async connection; six versioned SQL migrations (PoC-only) |
| Workload profile ID | Not established; no capacity claim permitted |
| Correctness matrix | All 34 test methods passed: 30 PostgreSQL integration methods plus four standalone retention-policy unit tests. The four retention tests run independently of PostgreSQL service availability. POC-22 verifies failed-migration rollback of both partial DDL and its migration-history entry; POC-23 verifies idempotent reapplication of migrations 001–006 without changing recorded application timestamps. POC-24 verifies concurrent whole-file migration execution, including a PL/pgSQL body with internal semicolons. POC-25 verifies the composite same-Article current-revision foreign key rejects cross-Article pointers. POC-26 verifies the decision-case foreign key and exercised outcome CHECK constraint. POC-27 verifies that the redundant source-identity index is absent and only the required unique lookup index remains. POC-28 verifies that a legacy Article with a null current-revision pointer can be backfilled atomically: an invalid deferred pointer rolls back both the inserted revision and pointer update, while a valid same-Article revision and pointer commit together. POC-29 races two ArticleRevision append transactions against the same expected Article version; exactly one advances the current pointer, and the stale writer's revision insert is rolled back. POC-30 verifies the deferred ArticleRevision-owner FK required by the service's revision-before-Article-projection create order; the pair commits atomically, while an orphan revision fails at commit. POC-31 uses a transactional CLAIMED-to-COMPLETED idempotency record: PostgreSQL's scoped unique key serializes concurrent claims, identical retries replay the same result, a mismatched fingerprint conflicts, and only the winning claim applies the domain effect. POC-15 through POC-21 retain the backup/restore, child-process restart, least-privilege, cluster-role, and fail-closed retention-planner evidence described below. These are isolated correctness checks, not proof of complete cluster recovery or production qualification. Production key custody/rotation, retention-policy enforcement, off-site protection, restore authorization, tablespace recovery, role-password/secret recovery, full cluster recovery, and formal security review remain open |
| Migration/upgrade | POC-13 clean install of migrations 001–006 and POC-14 data-preserving upgrade through migrations 002–006 passed |
| Backup/restore | Full-database `pg_dump`/`pg_restore` during an observed concurrent-write window passed; restored application rows and all six migration records verified. Experimental encrypted/authenticated envelope, tamper/wrong-key rejection, and private file permissions passed. Production KMS/HSM custody, rotation, retention, off-site/immutable storage, restore authorization, full cluster-global-object recovery (including tablespaces and configuration), and operator procedures remain untested; user-defined role and membership restore is covered by POC-19; database dump with a least-privilege read-only backup role is covered by POC-20 |
| Concurrency and async | POC-03, POC-07, POC-08, POC-11, POC-12, and POC-31 passed in the isolated test run |
| Performance results | Not measured; workload profile and thresholds remain unset; POC-18 captured a query plan only |
| Operational assessment | Partial: concurrent-write logical backup/restore, ephemeral encryption/authentication, private backup-file permissions, and read-only least-privilege role smoke passed. Production key management, retention, off-site/immutable storage, restore authorization, monitoring, alerting, and operator runbook exercise remain pending |
| Mandatory gates | All 34 PoC test methods passed (30 PostgreSQL integration methods plus four standalone retention-policy unit tests), including POC-22 through POC-31 migration, domain-integrity, atomic legacy-revision-backfill, concurrent ArticleRevision compare-and-swap, deferred owner-FK create-order, and concurrent idempotency-claim checks. Qualification remains partial: production key management, retention/off-site controls, restore authorization, full cluster/tablespace recovery, approved workload profile, performance thresholds, formal security review, and ADR-005 acceptance remain open |

The follow-up run completed successfully in GitHub Actions run `45941330079` (commit `d0f8cec8f0df07373bf69178bd626d477a2edb9e`). All 18 test methods passed. The machine-readable artifact `postgres-poc-d0f8cec8f0df07373bf69178bd626d477a2edb9e` was uploaded with archive SHA-256 `70d12c61e62accfb54c162dad5e5c5ea6bf966656828f6fb67c8e855de0311b9`. The latest protection-enhanced run completed successfully in GitHub Actions run `45942169818` on commit `13555a16fe4eb26cb665c3505e37d1f3c5190fe7`; all 18 test methods passed, and artifact `postgres-poc-13555a16fe4eb26cb665c3505e37d1f3c5190fe7` was uploaded with archive SHA-256 `e78d8e607d07165de480d2e8f631f0ed518dbfae673abf07be4feedf5992fb52`. POC-15 checks remote and local backup file mode `0600`, uses an ephemeral random passphrase for an AES-256-CBC/PBKDF2 envelope, verifies a separate HMAC-SHA256 authentication tag before decryption, and checks that wrong-key and modified-ciphertext tags do not verify before restoring the database. The test uses a disposable key only; it is not a KMS/HSM or production key-custody implementation. POC-16 uses a child process and fresh process to verify committed state after restart; POC-17 checks a read-only least-privilege role. Production key management/rotation, retention, off-site/immutable storage, restore authorization, cluster-global-object recovery, formal security review, monitoring, and operator runbooks remain open. POC-18 captures a query plan only; no latency, throughput, capacity, or workload compliance is claimed. The approved workload profile and thresholds remain unset. PostgreSQL is not production-qualified and ADR-005 remains Proposed.

The least-privilege database backup run completed successfully in GitHub Actions run `45943882536` on commit `5d5167b8661db50c0c2de56abecfbb6f4963cf07`; all 20 test methods passed. The machine-readable artifact `postgres-poc-5d5167b8661db50c0c2de56abecfbb6f4963cf07` was uploaded with archive SHA-256 `4b2e52b82b33f8a078930ec4f5df699cdf07b089d45c644ae7d81dc82c104554`. POC-20 verified that a dedicated login role inheriting `pg_read_all_data` could dump the synthetic database, could not write application rows, and lacked superuser, CREATEDB, and CREATEROLE attributes; the dump had file mode `0600` and restored application rows plus migration history into an isolated database. The refined POC-20 rerun completed successfully in GitHub Actions run `45944498523` on commit `ee82192a9b8c5dedbc1c8480076cf44338d57ae4`; all 20 test methods passed. The machine-readable artifact `postgres-poc-ee82192a9b8c5dedbc1c8480076cf44338d57ae4` was uploaded with archive SHA-256 `134b8871f1400918e6297654de08c8611821954d1137670e4f5500d111bd00d4`. The refined test uses distinct backup and restore identities: the backup role is read-only and can dump the database; the restore role owns only the isolated target database, can restore there, and is denied writes to the source database. Both are non-superuser and lack CREATEDB/CREATEROLE. This does not establish production credential custody/rotation/revocation, backup retention enforcement, production restore authorization, cluster-wide restore, or production authorization.

The refactored retention-planner suite completed successfully in GitHub Actions run `45946823488` on commit `41a6254e36c56e45477309c76f31f532f0b907c4`; all 24 test methods passed, comprising 20 PostgreSQL integration methods and four standalone retention-policy unit tests. The machine-readable artifact `postgres-poc-41a6254e36c56e45477309c76f31f532f0b907c4` was uploaded with archive SHA-256 `ec66adfe28fc205b1e72568f4fe27734df7feab44319d37f60af4d39d930c1be`. The standalone tests validate strict input metadata, reject future-dated artifacts and invalid policy values, check exact immutability expiry behavior, and enforce deterministic tie ordering. The initial run exposed an incorrect expected candidate order; the assertion was corrected to chronological order and the complete rerun passed. This remains synthetic, non-destructive PoC evidence only.

POC-22's failed-migration rollback test completed successfully in GitHub Actions run `45947579755` on commit `a1ed856641d9c029f92fabb50005f1bd0f44addc`; all 25 test methods passed, comprising 21 PostgreSQL integration methods and four standalone retention-policy unit tests. The machine-readable artifact `postgres-poc-a1ed856641d9c029f92fabb50005f1bd0f44addc` was uploaded with archive SHA-256 `8f8ff8a98a6ae944d2eb6132b3dc4037d8d409f379a5e5bab5814461748a5b38`. POC-22 injected a failure after creating a table and inserting a row, then verified the DDL and migration-history entry were both rolled back. This tests transactional migration atomicity in the PoC runner; it does not establish a production migration toolchain, rollback policy, or recovery runbook.

POC-23's migration reapplication idempotency test completed successfully in GitHub Actions run `45948260054` on commit `49a7690e40dbac2c5e0a1afd0cf8229e78a10ed6`; all 26 test methods passed, comprising 22 PostgreSQL integration methods and four standalone retention-policy unit tests. The machine-readable artifact `postgres-poc-49a7690e40dbac2c5e0a1afd0cf8229e78a10ed6` was uploaded with archive SHA-256 `3f7c2a1d92fdfedcede614923edc8359a409c76c8d66cd2948e59c9c8b3f06b9`. POC-23 verifies reapplying migrations 001–003 leaves the migration history and original `applied_at` timestamps unchanged. This is evidence for the PoC runner only, not approval of a production migration framework or release/rollback policy.

The refactored retention-planner test suite completed successfully in GitHub Actions run `45946823488` on commit `41a6254e36c56e45477309c76f31f532f0b907c4`; all 24 test methods passed, comprising 20 PostgreSQL integration methods and four standalone retention-policy unit tests. The machine-readable artifact `postgres-poc-41a6254e36c56e45477309c76f31f532f0b907c4` was uploaded with archive SHA-256 `ec66adfe28fc205b1e72568f4fe27734df7feab44319d37f60af4d39d930c1be`. The standalone tests validate strict input metadata, reject future-dated artifacts and invalid policy values, check exact immutability expiry behavior, and enforce deterministic tie ordering. The initial run exposed an incorrect expected candidate order; the assertion was corrected to chronological order and the complete rerun passed. This remains synthetic, non-destructive PoC evidence only.

The cluster-global role restore run completed successfully in GitHub Actions run `45943124060` on commit `bcb01f142d46ff57142baa019f0531a8a4faf95d`; all 19 test methods passed. The machine-readable artifact `postgres-poc-bcb01f142d46ff57142baa019f0531a8a4faf95d` was uploaded with archive SHA-256 `2614565d170abccf424a27898267d04dcef03f358e3032f7ec2405bf163ef897`. POC-19 restored user-defined roles and membership into a clean PostgreSQL 18.7 instance using the pinned image digest, retained the destination's bootstrap `postgres` administrator, and verified role attributes and membership. The dump omitted role passwords. It does not qualify password/secret recovery, tablespaces, configuration, full cluster recovery, or production restore authorization.


The latest reproducible 30-test execution completed successfully on 2026-11-27 in GitHub Actions run `45955820635` against commit `fe0975033b81227c95c75d6564897a9beafe70fc`: 26 PostgreSQL integration methods plus four standalone retention-policy unit tests. The uploaded machine-readable evidence artifact is `postgres-poc-fe0975033b81227c95c75d6564897a9beafe70fc` (artifact ID `15178617050`, archive SHA-256 `e403f15e2d4bd49d7261d0831a706d5f47a7caa179925e1ac4ea67d84139d7f9`). The run used PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`. POC-24 through POC-27 are included. This is a successful correctness PoC run only; it does not satisfy the outstanding production security, workload, operational, formal ADR-005 acceptance, or legacy current-revision backfill gates.


The latest reproducible 31-test execution completed successfully on 2026-11-27 in GitHub Actions run `45961988925` against commit `428e6b6d3ea142175373246bba209476c50cd5c6`: 27 PostgreSQL integration methods plus four standalone retention-policy unit tests. POC-28 verifies an atomic legacy Article revision backfill candidate using synthetic data, including rollback on an invalid deferred current-revision pointer. The uploaded machine-readable evidence artifact is `postgres-poc-428e6b6d3ea142175373246bba209476c50cd5c6` (artifact ID `15180889132`, archive SHA-256 `c306b10267d9bd46988c5bf8cf15b2af0ddcb7add4bf191ab8edfbb98f7d9fe0`). The run used PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`. This remains PoC-only correctness evidence; it does not select or approve the production legacy-data backfill policy, make current_revision_id non-null, or satisfy production qualification and formal ADR-005 acceptance.

The latest reproducible 32-test execution completed successfully on 2026-11-27 in GitHub Actions run `45963235373` against commit `5c9e34af98a97326c22ac756f306225493f91e29`: 28 PostgreSQL integration methods plus four standalone retention-policy unit tests. POC-29 verifies concurrent ArticleRevision append and Article current-pointer compare-and-swap: exactly one writer commits for the shared expected version, while the stale writer's revision insert rolls back. The uploaded machine-readable evidence artifact is `postgres-poc-5c9e34af98a97326c22ac756f306225493f91e29` (artifact ID `15182595241`, archive SHA-256 `5eac19ecfcb8c73cd40af1b54187f0eea28001371fd0e9bb11198df0eaf553b5`). The run used PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`. This is isolated PoC correctness evidence only; it does not implement a production repository/UnitOfWork adapter, establish workload performance, authorize production use, or satisfy formal ADR-005 acceptance.

The latest reproducible rerun completed successfully on 2026-11-27 in GitHub Actions run `45980652401` against commit `fd30de42a32c577ca8745055355583e8b0baa30a`: all 32 test methods passed (28 PostgreSQL integration methods plus four standalone retention-policy unit tests). The uploaded evidence artifact is `postgres-poc-fd30de42a32c577ca8745055355583e8b0baa30a` (artifact ID `15189785653`). The run used PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`. POC-29 again verifies one-winner ArticleRevision append/current-pointer compare-and-swap with rollback of the losing writer. This remains isolated correctness evidence only; workload thresholds, production security/operations, formal ADR-005 acceptance, and production activation remain open.

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
| 1.8 | 2026-11-27 | Proposed | Records the follow-up run with all 18 PoC test methods passing, including full-database logical backup/restore, child-process restart/reconnect, and least-privilege role smoke tests; retains concurrent-write backup, backup security/retention, workload, performance, and production-acceptance gates. |
| 1.9 | 2026-11-27 | Proposed | Records the successful concurrent-write full-database backup/restore exercise and three-migration clean-install/upgrade run; all 18 tests pass, while backup security/retention, workload, performance, and formal production-acceptance gates remain open. |
| 1.10 | 2026-11-27 | Proposed | Records experimental backup encryption/authentication, wrong-key/tamper detection, private file permissions, and successful restore in the latest 18-test run; production key management, retention, off-site protection, restore authorization, workload/performance, and formal acceptance remain open. |
| 1.11 | 2026-11-27 | Proposed | Records the successful 19-test run, adding clean-instance restoration and verification of user-defined PostgreSQL roles and role membership; full cluster recovery, secrets, tablespaces, production key management, retention, authorization, workload/performance, and formal acceptance remain open. |
| 1.12 | 2026-11-27 | Proposed | Records the successful 20-test run, adding a dedicated read-only backup role that can dump and restore synthetic database contents while lacking write, superuser, CREATEDB, and CREATEROLE privileges; production credential custody, retention, restore authorization, full cluster recovery, workload/performance, and formal acceptance remain open. |
| 1.13 | 2026-11-27 | Proposed | Refines POC-20 to use distinct backup and restore identities; verifies the restore identity can restore only into its isolated owned target and cannot write to the source database. Production credential lifecycle, retention, off-site protection, restore authorization, full cluster recovery, workload/performance, and formal acceptance remain open. |
| 1.14 | 2026-11-27 | Proposed | Records the successful 21-test run and a PoC-only fail-closed retention planner covering explicit policy, minimum verified-copy count, legal holds, immutability windows, unverified backups, and deterministic candidate ordering. No deletion, scheduler, production retention values, or enforcement is implemented; all production recovery, credential, workload, and formal acceptance gates remain open. |
| 1.16 | 2026-11-27 | Proposed | Records 25 passing test methods: 21 PostgreSQL integration methods and four standalone retention-policy unit tests. POC-22 verifies a failed migration rolls back partial DDL and does not record the migration as applied. Production migration tooling and recovery policy remain unapproved. |
| 1.17 | 2026-11-27 | Proposed | Records 26 passing test methods: 22 PostgreSQL integration methods and four standalone retention-policy unit tests. POC-23 verifies reapplying migrations 001–003 leaves migration history and original application timestamps unchanged. Production migration tooling and recovery policy remain unapproved. |
| 1.18 | 2026-11-27 | Proposed | Refreshes the results register to the latest successful 30-test run on commit `fe0975033b81227c95c75d6564897a9beafe70fc`; adds POC-24 through POC-27 and records the pinned PostgreSQL image digest and artifact evidence. Production qualification and formal ADR acceptance remain open. |
| 1.19 | 2026-11-27 | Proposed | Records the latest successful 31-test run and POC-28's atomic legacy Article revision backfill candidate test. The test is synthetic PoC evidence only; production backfill policy, non-null enforcement, security, workload, and formal ADR-005 acceptance remain open. |
| 1.20 | 2026-11-27 | Proposed | Refreshes the latest reproducible 31-test PostgreSQL 18.7 / Python 3.15 PoC evidence to run `45961720585` on commit `7e124789d02a95992c28fb559a625155bbf43a96`, artifact `15180963314`. All 31 tests pass; POC-28 remains synthetic candidate evidence only, and production qualification, workload thresholds, security/operations, and formal ADR-005 acceptance remain open. |
| 1.21 | 2026-11-27 | Proposed | Refreshes the latest reproducible 31-test PostgreSQL 18.7 / Python 3.15 PoC evidence to run `45961988925` on commit `428e6b6d3ea142175373246bba209476c50cd5c6`, artifact `15180889132`. All 31 tests pass; POC-28 remains synthetic candidate evidence only, and production qualification, workload thresholds, security/operations, and formal ADR-005 acceptance remain open. |
| 1.22 | 2026-11-27 | Proposed | Adds POC-29 and records its successful execution: 32 total test methods (28 PostgreSQL integration and four retention-policy unit tests), run `45962990616`, artifact `15181591814`. Production workload/security/operations qualification and formal ADR-005 acceptance remain open. |
| 1.23 | 2026-11-27 | Proposed | Refreshes the latest 32-test POC-29 evidence to run `45963235373` on commit `5c9e34af98a97326c22ac756f306225493f91e29`, artifact `15182595241`. All 32 methods pass; production qualification and formal ADR-005 acceptance remain open. |
| 1.24 | 2026-11-27 | Proposed | Corrects the workload-profile correctness-gate range to include POC-29 and reconciles the mandatory-gates summary with the latest 32-method result (28 PostgreSQL integration methods plus four standalone retention-policy unit tests). Production qualification and formal ADR-005 acceptance remain open. |
| 1.25 | 2026-11-27 | Proposed | Records the successful 32-method rerun on commit `fd30de42a32c577ca8745055355583e8b0baa30a`, run `45980652401`, artifact `15189785653`. POC-29 remains synthetic concurrency evidence; workload, production security/operations, and formal ADR-005 acceptance gates remain open. |


**End of Evidence Protocol**


An earlier reproducible 32-test execution completed successfully on 2026-11-27 in GitHub Actions run `45981896934` against exact main commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70`: all 32 test methods passed (28 PostgreSQL integration methods plus four standalone retention-policy unit tests). The uploaded machine-readable evidence artifact is `postgres-poc-1a02755f8356aa2263246c9c08ab13bfdd41bc70` (artifact ID `15189922078`). The artifact records PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`; it reports `successful: true`, with no failures or skipped tests. This rerun verifies the current main commit but does not expand the PoC's scope or close any production qualification gate. Workload profile and thresholds, production key custody/rotation, retention enforcement, off-site/immutable protection, restore authorization, full cluster/tablespace/configuration/secret recovery, formal security review, and formal ADR-005 acceptance remain open.



The latest reproducible 34-test execution completed successfully on 2026-11-27 in GitHub Actions run `45990509038` against source-code snapshot `962ab7ed99f1653e027deb731ee48d7e74a98a8a`: all 34 test methods passed (30 PostgreSQL integration methods plus four standalone retention-policy unit tests). The uploaded machine-readable evidence artifact is `postgres-poc-962ab7ed99f1653e027deb731ee48d7e74a98a8a` (artifact ID `15193098149`). The artifact records PostgreSQL 18.7, Psycopg 3.3.9, CPython 3.15.2, and the pinned linux/amd64 image manifest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`; it reports `successful: true`, with no failures or skipped tests. POC-31 verifies that two concurrent workers using the same scoped key/fingerprint produce one claim and one replay of the same result, with exactly one domain counter increment; the existing POC-02 now exercises database-backed replay and fingerprint conflict, and POC-10 verifies the committed domain write and idempotency result survive a lost acknowledgement. Migration 006 models the atomic CLAIMED-to-COMPLETED record lifecycle in this disposable PoC only. This remains PoC-only evidence; production migration strategy, workload profile/thresholds, production security/operations, and formal ADR-005 acceptance remain open.

**Revision Note (v1.28):** Adds POC-30 for atomic first-Article/ArticleRevision creation using a deferred owner foreign key, adds PostgreSQL migration 005, and refreshes the reproducible result to 33 methods (29 PostgreSQL integration plus four standalone retention-policy unit tests) on snapshot `4ce279e7786270475ae2618c484f2404c47b82a4`, run `45983781671`, artifact `15190297773`. This is isolated correctness evidence only; production qualification and formal ADR-005 acceptance remain open.


**Revision Note (v1.29):** Re-runs the unchanged 33-method PostgreSQL correctness/recovery PoC against snapshot `4cd09ad5203552d0b2df851ad0aa76f892779c20` (GitHub Actions run `45984540878`, artifact `15191416174`). All 29 PostgreSQL integration methods and four standalone retention-policy unit tests passed. This is a freshness re-verification only; it adds no new PoC scope and closes no production qualification or formal ADR-005 acceptance gate.

**Revision Note (v1.30):** Adds POC-31 for concurrent same-key idempotency claims and one-time domain effects, upgrades POC-02 to exercise database-backed replay/fingerprint conflict, and strengthens POC-10 to verify commit-before-lost-ack replay without duplicating the ArticleRevision write. Adds PoC-only migration 006 for the transactional CLAIMED-to-COMPLETED record lifecycle. The exact source-code snapshot `962ab7ed99f1653e027deb731ee48d7e74a98a8a` passed all 34 methods (30 PostgreSQL integration plus four standalone retention-policy tests) in run `45990509038`, artifact `15193098149`. PostgreSQL qualification, production tooling, workload thresholds, security/operations, and formal ADR-005 acceptance remain open.
