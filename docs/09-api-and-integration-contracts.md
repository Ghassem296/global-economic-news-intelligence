# GENI-API-009 — API and Integration Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-API-009  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

---

## 1. Purpose and Scope

Defines minimum contracts required before workflows, repositories, provider adapters, or external APIs are implemented. It supplements Document 02, Section 6.1. It does not select a public HTTP API, transport framework, or complete set of method signatures. The first slice prioritizes internal application/repository contracts; external APIs require a concrete product need.

## 2. Contract Layers

- **Domain:** value objects, identifiers, invariants, decisions, state transitions.
- **Application/workflow:** typed commands, queries, results, side effects, failure outcomes.
- **Repository:** persistence operations, transaction participation, concurrency, query semantics.
- **Provider adapter:** normalized requests/responses, errors, capabilities, quotas, rate limits.
- **External API:** transport schemas, authentication, authorization, pagination, compatibility.

Transport DTOs must not become domain models by accident. Provider-specific types must not leak into domain/application layers.

## 3. Common Contract Requirements

Every command defines operation name/schema version; field types, required/optional/null semantics, identifier formats and limits; actor/authorization scope; correlation/causation IDs; idempotency key and uniqueness scope where applicable; deadline/cancellation; result and explicit unknown/no-result outcomes; validation errors/retry classification; and audit/data classification. A successful HTTP response does not prove an asynchronous workflow or external delivery completed.

## 4. Error Contract

Errors are machine-classifiable and must not expose secrets, stack traces, or restricted content.

| Code | Meaning | Retry guidance |
|---|---|---|
| VALIDATION_ERROR | Invalid schema/domain input | Do not retry unchanged input |
| AUTHENTICATION_REQUIRED | No valid identity | Retry after authentication |
| AUTHORIZATION_DENIED | Actor not permitted | Do not retry without changed authorization |
| NOT_FOUND | Resource absent or not visible | Usually do not retry |
| CONFLICT | State/version/uniqueness conflict | Reload and resolve; no blind retry |
| RATE_LIMITED | Quota exceeded | Bounded retry per provider guidance |
| DEPENDENCY_UNAVAILABLE | Dependency unavailable | Bounded retry only when safe |
| TIMEOUT_OUTCOME_UNKNOWN | External completion may have occurred | Reconcile before retry |
| BUDGET_EXCEEDED | Approved budget exhausted | Never bypass or silently change provider |
| RIGHTS_NOT_ALLOWED | Operation denied/expired/revoked/unknown | Fail closed |
| INTERNAL_ERROR | Unexpected failure | Use correlation ID; retry only if safe |

The canonical envelope includes code, safe message, correlation ID, optional field details, and retry classification. Exact serialized names/status mappings follow the selected transport.

## 5. Idempotency, Transactions, and Concurrency

Read-only queries should be repeatable. State-changing commands define idempotency scope and uniqueness. Retries return/reference the same logical operation where promised and never duplicate side effects. Timeout after external action means outcome unknown, not failed; reconcile before successor operation. Multi-record transitions identify UnitOfWork/transaction boundaries. Optimistic concurrency identifies expected aggregate/version and returns CONFLICT for stale writes. Append-only history is never overwritten. Align with GENI-ADR-016 and Documents 02/03.

## 6. Retry, Timeout, and Rate Limits

Each adapter/workflow declares connect/read/overall deadlines, retryable errors, max attempts, backoff/jitter, rate-limit handling, and cancellation. Retries are bounded and cannot multiply side effects. Non-idempotent operations require reconciliation or explicit idempotency. Missing provider retry metadata must not cause unbounded retries.

## 7. Pagination

Every collection query defines stable ordering/tie-breaker; page-size bounds/default; cursor or offset semantics; filter validation; consistency expectations; and behavior when access is revoked or records change between pages. Unbounded external collection reads are prohibited. Choose cursor/offset explicitly per query.

## 8. First-Slice Contract Readiness

Before implementation, define method-level contracts for SourceRepository; ArticleRepository and ArticleRevisionRepository; EventRepository; EventMatchCaseRepository, EventMatchCandidateRepository, EventMatchDecisionRepository; ArticleEventLinkRepository; EvidenceRepository; AnalysisRepository; ReportRepository; PublicationDecisionRepository; and ProcessingRunRepository.

For every method record purpose, typed input/output, required/null fields, validation, authorization, transaction, idempotency/uniqueness, concurrency/version, ordering/pagination, errors, retry classification, and audit effects. This does not require one repository per table; aggregate boundaries remain authoritative. Event resolution distinguishes candidate evaluation from the case-level decision. Publication distinguishes decision, operation, attempt, and reconciliation.

## 9. Provider Integration

Each adapter declares provider/API version, authentication method and secret reference (never secret value), capability limitations, mapping/provenance, timeout/rate-limit/retry/quota, normalized errors, processing/data-residency constraints, content rights, health behavior, and contract fixtures. Provider success is not proof of fact, license, or permission to retain/republish.

## 10. Security, Compatibility, and Testing

External endpoints require authenticated identities, resource-level authorization, validated input, limits, and minimal disclosure. Public API authentication/scopes, CORS, webhook signature verification, and rate limiting must be defined before exposure. Breaking changes require explicit versioning/migration policy. Internal contracts require versioning when persisted records/messages outlive a deployment.

Tests include schema/serialization, repository contracts, rollback, stale writes, idempotent replay, retry classification, timeout-unknown reconciliation, authorization, pagination, and provider contracts. Fixtures include malformed/missing/null inputs, duplicate commands, stale references, revoked rights, provider errors, and partial failures.

## 11. Open Decisions

Whether a public API is needed; transport/framework/authentication; exact first-slice signatures/DTOs; cursor encoding; webhook guarantees/signature; and provider-specific retry/rate-limit values. No transport, framework, or numeric limit is approved here.

## 12. Related Documents

Documents 02, 03, 08, and 12; GENI-ADR-004, 013, 016, and 017.

## 13. Internal Privacy Command and Query Contracts

The initial rights-request interface is an internal application contract; a public HTTP endpoint is not required by this specification. An approved UI, support channel or operator adapter may submit commands only after intake authentication and authority procedures are approved.

### 13.1 Commands

| Command | Required inputs | Result and invariant |
|---|---|---|
| SubmitDataSubjectRequest | request type, opaque subject reference, jurisdiction/policy context, intake channel, correlation ID, idempotency key | durable request ID/status; legal applicability is not inferred |
| RecordRequestVerification | request ID, method/reference, outcome, actor | append-only verification action; failed verification blocks disclosure/destructive action |
| DiscoverSubjectData | request ID, scoped discovery request | lineage-backed target manifest with completeness/limitations |
| ApproveRequestException | request/action ID, exception category, rationale, authority, expiry | auditable human decision; never generated by an LLM |
| ExecuteDataSubjectAction | request/action ID, target, action, expected version, idempotency key | target-level outcome; service-owned writes |
| VerifyRequestCompletion | request ID and target outcome evidence | cannot close with pending/failed/unverifiable required targets absent approved exception |
| RecordProcessorDeletionOutcome | request/action ID, processor, external reference, outcome/evidence | durable acknowledgement or explicit unavailable/unverifiable state |

### 13.2 Queries

GetDataSubjectRequestStatus returns scoped safe status; GetSubjectDataDiscoverySummary returns category/count/completeness metadata and discloses record contents only after verified authority; GetProcessorProcessingPosture returns approved purpose/region/retention/training-use/deletion capability; GetPrivacyAuthorizationDecision returns decision/policy references to authorized callers.

### 13.3 Common contract requirements

Commands require authenticated actor/service identity, resource-scoped authorization, schema version, correlation/causation IDs, idempotency for state changes, expected aggregate version where needed, safe errors, audit context and data classification. Do not expose direct identifiers or discovered contents in ordinary errors. Destructive operations require explicit policy checks. Unknown completion after external action must be reconciled before retry.

### 13.4 LLM provider request contract

Provider adapters receive minimized payload plus privacy authorization reference, content-rights decision reference when applicable, purpose ID, data category/classification, provider/model, processing region, policy version and transfer-assessment reference. Reject missing or stale references. These fields are authorization metadata, not proof of legal compliance. No public route, transport, legal deadline or jurisdictional right is selected here.

See Documents 02, 03, 08, 12, 13 and 14; GENI-ADR-020.

---

**Document ID:** GENI-API-009  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  


**End of Document**