# GENI-ADR-020 — Data Protection, Privacy Processing Authorization, and Data Subject Rights Architecture

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-020  
**Title:** Data Protection, Privacy Processing Authorization, and Data Subject Rights Architecture  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved

---

## 1. Context and Problem Statement

GENI has a content-rights model for source publications and a separate Data Protection and Privacy Specification (Document 14). Content rights govern permissions attached to publisher/source content. They do not establish whether personal data may be processed for a particular purpose, sent to a particular model provider, transferred to a particular region, retained, or disclosed in response to an individual's request.

The current architecture lacks a complete execution model for privacy authorization, data-subject requests, personal-data lineage, processor governance, and deletion propagation. Treating privacy as a keyword or policy-only concern would leave application workflows unable to enforce the specification.

## 2. Decision Question

What logical architecture shall govern personal-data processing and data-subject rights across domain data, derived artifacts, LLM/provider boundaries, operations, and evidence?

## 3. Requirements and Constraints

- Keep Content Rights authorization and Privacy Processing Authorization independent and conjunctive where both apply.
- Deny external processing when either required authorization is missing, unknown, expired, revoked, or out of scope.
- Represent purposes, data categories, processing operations, destinations, regions, retention and provider posture as versioned policy inputs.
- Support verified data-subject request intake, discovery, action, exception review, verification, response and audit.
- Trace personal data into derived artifacts and external processing without conflating personal-data lineage with article provenance or content-rights lineage.
- Support correction, access, restriction, objection, deletion and applicable export workflows, subject to jurisdiction-specific legal review and documented exceptions.
- Avoid assuming a physical table per logical concept or selecting a database, transport, identity provider, legal basis, jurisdiction, or retention duration in this ADR.
- Preserve data minimization in prompts, logs, traces, evaluation artifacts, backups and provider requests.

## 4. Alternatives Considered

### 4.1 Privacy as Content Rights Extension

Rejected. Publisher content permissions and individual privacy rights have different subjects, purposes, legal bases, scopes and enforcement conditions. Combining them creates unsafe authorization ambiguity.

### 4.2 Privacy as Documentation-Only Policy

Rejected. Policy without service, data and workflow contracts cannot reliably enforce processing restrictions or execute rights requests.

### 4.3 Dedicated Privacy Domain and Cross-Cutting Authorization

Recommended. Introduce a logical Privacy domain, a PrivacyManagementService, an independent PrivacyProcessingAuthorization policy, personal-data lineage, processor/transfer governance records and explicit workflow contracts. Physical persistence and public transport remain implementation decisions.

## 5. Recommended Decision

Adopt the following proposed architecture:

1. **Independent authorization gates.** For an operation involving source content and personal data, ContentRightsService evaluates content permissions and PrivacyProcessingAuthorization evaluates personal-data permissions. Both must independently authorize the exact operation, purpose, recipient/provider, region and policy version. Neither service may grant the other's permission.
2. **PrivacyManagementService.** Owns the data-subject request lifecycle, identity/authority verification coordination, discovery orchestration, legal-hold/exception review, execution coordination, verification evidence and response status. It does not itself decide unresolved legal questions.
3. **Logical privacy records.** Define PersonalDataInventory, ProcessingPurpose, PrivacyProcessingBasis, PrivacyAuthorizationDecision, DataSubjectReference, DataSubjectRequest, DataSubjectRequestAction, PrivacyDeletionRecord, ProcessorRegister, InternationalTransferAssessment and PrivacyImpactAssessment. These are logical records/value objects/aggregates; storage may normalize or combine them according to approved persistence design.
4. **Personal Data Lineage.** Maintain traceable links from personal-data source/reference through processing runs, prompts/requests, provider destinations and derived artifacts/outputs. Use opaque subject linkage tokens with restricted access; do not place direct identifiers in general-purpose telemetry.
5. **Derived-data propagation.** Access, correction, restriction and deletion workflows discover and evaluate dependent derived artifacts, embeddings, reports, evaluation artifacts, caches and provider-side copies. Each target records requested, attempted, completed, unavailable, legally excepted or unverifiable outcomes. A request is not marked complete merely because a source row was deleted.
6. **Processor and transfer register.** Maintain approved processor/subprocessor, service, purpose, data categories, processing region, retention, training-use posture, deletion capability, contract/safeguard references, review date and approval state. Unknown posture blocks the affected external processing.
7. **LLM boundary.** Before any provider call, evaluate content rights and privacy authorization independently; apply minimization/redaction; bind the authorization decision to provider/model, region, purpose, data classification, policy version and request. Re-check on retries or destination/configuration changes.
8. **Operational evidence.** Keep append-only or tamper-evident request/action/authorization/deletion/transfer audit evidence with strict access and minimization. Logs and traces must not become an uncontrolled copy of personal data.
9. **API neutrality.** Define internal command/query contracts first. A public endpoint, UI, support channel or identity mechanism is not selected by this ADR; the authorized intake channel must be specified before production.
10. **Legal review boundary.** Controller/processor roles, lawful bases, applicable rights, deadlines, exceptions, transfer mechanisms, notice obligations and retention periods remain jurisdiction- and fact-dependent open decisions requiring qualified legal/privacy review.

## 6. Rationale

This separation prevents publisher licensing from being mistaken for permission to process personal data. A dedicated workflow makes rights requests actionable and auditable. Personal-data lineage is necessary to find derived and externally processed data. Fail-closed provider controls reduce accidental disclosure when provider terms or transfer posture are unknown.

## 7. Consequences and Trade-Offs

### 7.1 Positive Consequences

- Explicit, independently testable privacy authorization.
- Discoverable relationships between subjects, processing and derived artifacts.
- Repeatable rights-request execution and evidence.
- Provider and transfer posture becomes reviewable and enforceable.
- Clear separation between content rights, privacy rights and article provenance.

### 7.2 Negative Consequences

- Additional domain records, policy evaluation and workflow complexity.
- Data lineage increases write volume and retention considerations.
- Provider deletion and backup reconciliation may be technically unavailable or asynchronous.
- Identity verification and legal exceptions require human governance and jurisdiction-specific procedures.

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Content rights incorrectly treated as privacy permission | Separate services and conjunctive checks; negative tests |
| Incomplete discovery of derived data | Lineage completeness gates, reconciliation and exception reporting |
| Personal data leaks through telemetry | Allowlisted fields, redaction, canary-secret tests and access controls |
| Provider retains data after local deletion | Provider register, deletion capability evidence, follow-up and explicit unverifiable state |
| Legal deadlines or exceptions are guessed | Do not hard-code legal rules before legal review; configurable approved policy |
| Restore reintroduces deleted data | Deletion tombstones/ledger and post-restore reconciliation before serving traffic |

## 9. Impact on Architecture and Documentation

- Document 02: PrivacyManagementService, authorization policy interface, workflows and repository ownership.
- Document 03: logical privacy records, Personal Data Lineage, retention/deletion and persistence boundaries.
- Document 04: privacy implementation stages and production gates.
- Document 08: privacy threat controls and independent provider authorization.
- Document 09: internal privacy commands, queries, authorization and idempotency contracts.
- Document 12: privacy unit, integration, security, provider and restore tests.
- Document 13: DSAR, provider deletion, transfer and restore runbooks.
- Document 14: authoritative privacy policy requirements and unresolved legal decisions.
- Document 07 and ADR Registry: inventory and dependency updates.

## 10. Implementation Implications

Implementation must proceed in dependency order: inventory/classification and purpose register; privacy records and lineage; authorization policy and provider register; request workflow and internal contracts; derived-data and provider deletion orchestration; audit/telemetry controls; tests and operational exercises.

No production personal-data processing is authorized merely by publishing or accepting this ADR. Production gates require implemented controls and evidence.

## 11. Acceptance Criteria

- Content Rights and Privacy Processing Authorization have separate interfaces, decisions and negative tests.
- Every external LLM/provider request involving personal data is bound to a current, immutable, purpose/operation/category/provider/model/region-scoped PrivacyAuthorizationDecision and applicable content-rights decision.
- Personal-data lineage can discover source and derived records for a test subject without broad direct-identifier exposure.
- Rights-request state transitions, idempotency, exception handling and completion evidence are tested.
- Processor/transfer records are required for relevant external processing; unknown posture fails closed.
- Backup restore cannot reintroduce data marked for deletion without reconciliation.
- Logs, traces, prompts and evaluation artifacts pass privacy minimization tests.
- Legal/privacy open decisions are resolved by qualified review before the affected production processing begins.

## 12. Review and Reconsideration

Reconsider if legal review changes the applicable roles/rights, provider capabilities materially change, lineage costs are disproportionate, or implementation evidence shows that the proposed boundaries cannot be reliably enforced.

## 13. References and Supporting Evidence

- GENI-PRIV-014 — Data Protection and Privacy Specification.
- GENI-ARCH-002 — Component Architecture and Interface Contracts.
- GENI-DATA-003 — Data Model and Storage Design.
- GENI-SEC-008 — Security Architecture and Threat Model.
- GENI-API-009 — API and Integration Contracts.
- GENI-EVAL-012 — Testing and Evaluation Strategy.
- GENI-OPS-013 — Deployment, Operations, and Observability.
- GENI-ADR-013 — News Content Access, Full-Text Retention, Licensing, and Republishing.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Initial privacy execution architecture proposal | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Added immutable scoped privacy authorization decision and repository contract | AI Architecture Assistant |

**End of ADR**
