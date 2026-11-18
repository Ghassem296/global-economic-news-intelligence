# GENI-OPS-013 — Deployment, Operations, and Observability

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-OPS-013  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

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

---

**Document ID:** GENI-OPS-013  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  
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


**End of Document**
