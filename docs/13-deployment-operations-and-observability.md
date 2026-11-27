# GENI-OPS-013 — Deployment, Operations, and Observability

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-OPS-013  
**Version:** 1.9  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-27

---

## 1. Purpose and Status

Defines operational architecture and readiness requirements for deployment, observability, backup/recovery, incident response, and procedures. It does not select a cloud, host, database, container platform, or production topology. The initial product is text-first; distributed infrastructure/microservices require measured need and an accepted ADR.

## 2. Environment Separation

Distinguish Development, Test/CI, Staging, and Production. Use isolated credentials and controlled fixtures in CI; production-like but non-publishing configuration in staging; restricted access, protected secrets, monitored workloads, and approved content policies in production. Never copy production secrets or restricted data into developer/CI environments.

## 3. Logical Runtime Responsibilities

Provide logical capabilities required by approved workflows: application/API entry points if exposed; scheduled acquisition; bounded workflow/background processing; persistence/migrations; LLM/provider adapters with budgets/deadlines; review/publication coordination; observability/health controls.

Whether these run in one process, separate workers, containers, or managed services remains a deployment decision. Minimize initial complexity while preserving durable work state, idempotency, and recovery.

## 4. Configuration and Release

Configuration is typed, validated, environment-specific, and versioned where it affects domain behavior. Inject secrets through protected mechanisms; never commit them. Startup fails clearly for invalid required configuration; unsafe defaults must not enable public or privileged behavior.

A release identifies source commit, artifact, dependency lock state, schema/migration version, policy/config versions, and evaluation results. Use repeatable deployment, pre-checks, migration compatibility review, health verification, and rollback/forward-fix plan. Destructive migrations require verified backup and recovery plan.

## 5. Observability

Structured logs include timestamp, severity, component, environment, correlation ID, workflow/run/step IDs, outcome, duration, retry class, and safe error code. Exclude credentials, tokens, full article bodies, raw provider payloads, and unnecessary personal data.

Define metrics for acquisition success/failure/freshness; queue depth/age/throughput/duration/retries; event matching and review volumes; LLM calls/latency/tokens/cost provenance/budget denials/fallback; publication/delivery/unknown outcomes/reconciliation backlog; database health/transaction failures/storage/backups; and security events/authorization denials/rate limits. Every metric has owner, definition, cardinality policy, and dashboard/alert purpose. High-cardinality IDs belong in logs/traces, not unbounded metric labels.

Trace/correlation should connect acquisition, normalization, article processing, event resolution, evidence assessment, report generation, publication decision, and delivery. Preserve causation across async boundaries; no secrets or unrestricted source content in trace attributes.

## 6. Health and Alerts

Separate liveness, readiness, and functional health. A single source outage need not make the entire application unready; expose component-level degradation. Candidate alerts include critical-source staleness, sustained acquisition failures, queue-age growth, repeated workflow failures, database integrity errors, budget exhaustion/cost drift, provider outage, unresolved publication outcomes, failed backup/restore, rights-revocation propagation failure, and security incidents.

Thresholds, windows, escalation, and on-call responsibilities derive from measured objectives and operating capacity, not invented here.

## 7. Reliability, Backup, and Recovery

Preserve durable workflow state and GENI-ADR-016 idempotency/reconciliation. Define/test backup scope/frequency/encryption/access/retention; restore and integrity verification; interrupted workflow recovery; external-operation reconciliation; replay without duplicate side effects; migration recovery; and rights-driven restriction/deletion across storage, caches, indexes, queues, derived artifacts, and supported processors.

Project Owner selects RPO/RTO after workload, data criticality, and cost are understood. Do not publish unsupported guarantees.

### 7.1 Backup protection requirements

A production backup procedure must define and verify all of the following before activation:

- **Scope:** database contents, schema/migration history, required cluster-level roles and grants, tablespaces/configuration where applicable, and the separate evidence needed to reconstruct the service. A per-database logical dump does not by itself preserve cluster-global objects.
- **Creation:** use a supported, repeatable backup mechanism with a consistent database snapshot. Record source database identity, server version, schema/migration version, source commit, start/end time, outcome, and artifact identifier without recording secrets or restricted row content.
- **Confidentiality and integrity:** protect backup data with authenticated encryption using an approved key-management process. Verify integrity/authenticity before decryption or restore. Encryption keys must not be stored beside backups or in logs; define custody, access, rotation, revocation, and recovery of keys separately from backup retention.
- **Access:** use dedicated least-privilege backup and restore identities. Restrict filesystem/object-store permissions, administrative access, download, and restore operations; audit access and denied attempts. Separate backup creation from approval to restore into an exposed environment.
- **Retention and resilience:** define owner-approved frequency, retention, deletion, off-site/independent failure-domain copies, immutability where required, and disposal evidence. Do not invent retention periods or recovery objectives. Retention automation must fail closed when policy is absent or invalid, preserve legal holds and active immutability windows, and maintain the approved minimum number of verified copies. A candidate planner is not deletion authorization; every deletion must be separately authorized and auditable.
- **Monitoring:** alert on missed, incomplete, unexpectedly small, unverifiable, or expired backups; record backup age, duration, size, integrity result, and restore-test status.

### 7.2 Restore and recovery procedure

A restore must first target an isolated environment with no production traffic or external side effects. Verify artifact identity and authenticated integrity before decryption. Restore database objects and required cluster-global objects using an explicitly reviewed ownership/privilege plan; do not silently discard or broaden grants. Treat the database dump and cluster-global dump as separate recovery artifacts. Restore user-defined roles and memberships into an isolated target before restoring database ACLs; retain or deliberately map the destination bootstrap administrator, and never import role passwords from a no-password globals dump. Validate role attributes and memberships, then separately validate tablespaces, configuration, extensions, ownership, grants, and any external identity dependencies. Do not expose the restored instance until the full target-specific recovery manifest is reconciled. Apply only the migration path approved for the target release, then verify schema history, database constraints, application-level invariants, and representative reads/writes. Reconcile privacy deletion/restriction tombstones and external-operation ledgers before data is exposed or processing resumes. Quarantine any unresolved reconciliation result and require the authorized operator's recorded sign-off. Preserve the restore logs and verification evidence.

A failed or interrupted restore must not be treated as successful because the database process is accepting connections. Define cleanup of partial targets, safe retry behavior, escalation, and rollback/forward recovery before operational use.

### 7.3 Current PostgreSQL PoC evidence boundary

The isolated PostgreSQL PoC exercises a full logical database backup during concurrent activity, isolated database restore, migration-history/application-invariant verification, private file permissions, and an experimental encrypted/authenticated envelope. POC-19 additionally restores user-defined roles and role membership from `pg_dumpall --globals-only --no-role-passwords` into a clean PostgreSQL 18.7 instance, retaining the destination bootstrap administrator and verifying role attributes and membership. POC-20 verifies two distinct identities: a dedicated backup login inheriting `pg_read_all_data` can create a full logical database dump with file mode `0600` but cannot write application rows; a separate restore login owns only the isolated target database, restores the dump there, and is denied writes to the source database. Both identities lack superuser, CREATEDB, and CREATEROLE privileges. The restore verifies synthetic application rows and migration history. POC-21 is covered by four standalone unit tests, independent of PostgreSQL service availability, and exercises a pure retention planner using synthetic fixtures: it requires an explicit policy, preserves the minimum verified-copy count, legal holds, and active immutability windows, excludes unverified artifacts from automatic deletion, and returns oldest-first candidates. The planner also rejects malformed/future-dated metadata, checks exact immutability expiry boundaries, and returns deterministic order for tied timestamps. It does not delete, schedule, or enforce retention; its example values are not production policy. POC-22 injects a failure after partial migration DDL and verifies transactional rollback removes the schema change and leaves no applied-migration record. This is a PoC runner test, not approval of production migration tooling or rollback procedures. POC-23 reruns already-applied migrations and confirms the migration history and original timestamps do not change. These are correctness experiments on synthetic data only. The ephemeral test passphrase is not a key-management design. The tests do not establish production backup encryption, KMS/HSM custody, production credential provisioning/rotation/revocation, separate restore authorization, off-site storage, immutability, retention enforcement, separate restore-identity authorization, tablespace/configuration recovery, full cluster recovery, role-password/secret recovery, privacy-ledger reconciliation, or an approved RPO/RTO. Those controls remain release gates under GENI-ADR-005 and this document.

## 8. Capacity and Cost

Measure source count/poll frequency, throughput, payload size, concurrency, database growth, indexing/embedding workload, LLM tokens/cost, provider quotas, and delivery volume. Start with bounded concurrency, queue limits, per-source/provider limits, request-size limits, deadlines, and budgets. Scale out only when evidence shows the simpler deployment cannot meet an approved objective.

## 9. Runbooks and Incident Management

Maintain runbooks for provider/source failure and credential rotation; queue backlog/stuck workflow; backup/restore/migration/integrity; LLM outage/budget exhaustion; publication timeout/duplicate risk/reconciliation; rights revocation/deletion; security incident; and release rollback.

Each runbook states trigger/severity, prerequisites, authorized operator, safe diagnostics, recovery action, verification, escalation, and audit evidence. Destructive or externally visible actions require explicit authorization.

## 10. Production Readiness Gate

Require documented topology; environment/secret controls; tested migrations/rollback; dashboards/actionable alerts; backup and successful restore evidence; recovery/reconciliation exercises; security/rights checks; assigned runbook owners; capacity/cost measurements; and release evaluation evidence. Document presence alone does not complete a gate: cite an actual test, operational artifact, or accepted exception.

## 11. Open Decisions

Hosting model/region/network; process/worker/scheduler; database/backup tooling under GENI-ADR-005; monitoring/logging/tracing providers; RPO/RTO/service objectives/on-call; deployment/migration strategy; and log/trace/evaluation retention. Resolve using workload evidence and approval where architecture changes.

## 12. Related Documents

Documents 04, 08, 09, and 12; GENI-ADR-005, 013, 016, and 017.

## 13. Privacy Operations Runbooks

These runbooks are required before enabling personal-data processing in production. Each identifies an authorized owner, trigger/severity, prerequisites, approval boundary, safe diagnostics, execution, target-level verification, escalation and retained evidence.

### 13.1 Data-subject request

Intake through the approved channel; verify identity/authority; determine scope under approved jurisdictional policy; run lineage-backed discovery; review holds/exceptions with authorized humans; execute actions idempotently; reconcile every target; prepare a safe response; record dispatch and closure. Never infer statutory deadlines or exemptions.

### 13.2 Provider/model deletion and restriction

Discover provider requests through PersonalDataLineage and LLM usage metadata; verify current provider deletion capability and contract posture; submit authorized action; capture external reference/acknowledgement; retry only under safe idempotency/reconciliation; mark unavailable or unverifiable outcomes explicitly. Local deletion does not prove provider deletion.

### 13.3 Backup restore reconciliation

Before restored data is exposed or reprocessed, replay deletion/restriction tombstones and action ledger against restored stores, caches and derived artifacts. Produce reconciliation evidence, quarantine unresolved targets and require authorized sign-off before traffic resumes. Exercise on a representative restore.

### 13.4 Privacy incident and transfer control

Contain suspected disclosure/unauthorized transfer; preserve minimized evidence; identify affected purposes, records, processors and regions through lineage; revoke credentials/authorization as appropriate; engage designated privacy/legal owner to assess notification obligations under applicable law; document decisions and corrective actions. Do not invent notification deadlines.

Runbook publication is not evidence of successful exercise. See Documents 02, 03, 08, 09, 12 and 14; GENI-ADR-020.

---

**Document ID:** GENI-OPS-013  
**Version:** 1.9  
**Status:** Draft — Under Architecture Review  


**Revision Note (v1.3):** Adds explicit cluster-global role/membership restore guidance and records the POC-19 evidence boundary. It distinguishes tested user-defined role recovery from untested tablespace, configuration, password/secret, and full-cluster recovery.

**Revision Note (v1.4):** Records POC-20's synthetic-data evidence for a read-only `pg_read_all_data` backup identity and clarifies that production credential lifecycle, retention enforcement, restore identity separation, and full cluster recovery remain untested.

**Revision Note (v1.5):** Clarifies the tested separation between the read-only backup identity and the target-scoped restore identity. The test does not approve production credential provisioning, rotation/revocation, restore authorization, or full cluster recovery.

**Revision Note (v1.6):** Adds the POC-21 retention-planning evidence boundary and fail-closed operational requirements. The planner does not delete backups, schedule work, or define production retention values; owner-approved retention and enforcement remain release gates.

**Revision Note (v1.7):** Records four standalone retention unit tests that run without PostgreSQL and validate malformed/future-dated metadata, immutability expiry boundaries, and deterministic ordering. The planner remains non-destructive; owner-approved production retention and enforcement remain release gates.

**Revision Note (v1.8):** Records POC-22's successful synthetic failed-migration rollback test. It verifies partial DDL and migration-history changes roll back together; production migration tooling, recovery procedures, and operator authorization remain open.

**Revision Note (v1.9):** Records POC-23's successful idempotent reapplication of migrations 001–003, preserving migration history and original timestamps. This does not approve production migration tooling or a production rollback strategy.

**End of Document**