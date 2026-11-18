# GENI-ADR-012 — Semantic Retrieval, Similarity Calculation, and Embedding Storage

**ADR ID:** GENI-ADR-012  
**Title:** Semantic Retrieval, Similarity Calculation, and Embedding Storage  
**Version:** 0.1  
**Status:** Proposed — Awaiting Project Owner Review  
**Priority:** P1  
**Created:** 2026-11-18  
**Last Updated:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approval:** No approval has been recorded.

## 1. Context and Problem Statement

Event matching and historical retrieval may benefit from semantic representations, but similarity is not identity proof. A dedicated vector database adds cost and should not be mandatory before need is measured.

This is a proposed decision document. Its recommendation does not become an approved architectural constraint until the Project Owner explicitly accepts it.

## 2. Decision Question

How should semantic retrieval and embedding storage be introduced while preserving explainability and database independence?

## 3. Requirements and Constraints

- Preserve provenance, auditability, and historical traceability.
- Keep domain decisions separate from candidate generation, processing state, and external side effects.
- Version policies and derived assessments that may change over time.
- Represent uncertainty and unavailable information explicitly.
- Keep infrastructure replaceable where the domain does not require a specific provider.
- Do not treat a recommendation, draft, or implementation progress as approval.

## 4. Alternatives Considered

A. No semantic retrieval. B. Mandatory managed vector database from day one. C. Pluggable semantic retrieval with rebuildable embeddings and staged infrastructure.

## 5. Recommended Decision

Define a provider-independent embedding interface and persist model/version/dimension/input provenance. Begin with lexical, entity, temporal, and optional semantic signals using a simple local storage strategy appropriate to measured volume. Keep relational records authoritative and embeddings/indexes rebuildable. Add a dedicated vector service only when recall, latency, scale, or operations justify it.

This is the recommended direction for review, not a final accepted decision.

## 6. Rationale

C enables semantic recall without making vector infrastructure part of domain identity. Candidate similarity remains a signal, never a final event decision.

## 7. Final Decision

**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Decision Date:** Not decided  
**Approval Record:** No explicit approval has been recorded.  
**Decision Rationale:** Pending Project Owner review.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Establishes explicit architectural boundaries and reviewable direction.
- Improves traceability between requirements, data contracts, workflows, and implementation.
- Makes unresolved assumptions and validation requirements visible.

### 8.2 Negative Consequences

- Introduces documentation and validation work before implementation.
- Some thresholds, provider choices, and operational parameters remain open until evidence is available.
- Dependent documents may require coordinated updates after approval.

### 8.3 Risks and Mitigations

- **Proposal mistaken for approval:** Keep status Proposed and require an explicit approval record.
- **Premature over-specification:** Leave unmeasured thresholds and provider choices open.
- **Cross-document drift:** Run consistency checks before merge and after acceptance.

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components, Data, and Workflows

Record model, version, dimensions, normalization, source revision, generation time, distance metric, and index version; evaluate multilingual behavior; support re-embedding and index rebuild.

### 9.2 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`, where sequencing is affected
- `docs/adr/README.md`

### 9.3 Related ADRs

- `GENI-ADR-002`
- `GENI-ADR-008`
- `GENI-ADR-011`
- `GENI-ADR-016`

Related Proposed ADRs are dependencies or context only; their presence does not imply approval.

## 10. Implementation Implications

Implementation must not assume this proposal is accepted. After approval, translate it into versioned interfaces, data constraints, workflow behavior, and implementation tasks. Any material deviation discovered during implementation must be brought to the decision owner and recorded.

## 11. Acceptance and Verification Criteria

Embeddings can be regenerated; incompatible dimensions are not mixed; similarity is not treated as calibrated probability; candidate recall/precision are measured on a versioned dataset.

Verification must include focused unit/integration tests, data-integrity tests where applicable, and review of affected architecture documents. Quantitative thresholds must come from representative evaluation data, operational measurements, or formal policy review rather than being invented in this ADR.

## 12. Review and Reconsideration

Review before implementing the dependent capability, or earlier if product scope, legal restrictions, provider capabilities, operational scale, or evaluation results materially change.

**Review Owner:** Project Owner  
**Review Date:** Not scheduled

## 13. References and Supporting Evidence

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 0.1 | 2026-11-18 | Proposed | Initial proposal drafted; approval pending | AI Architecture Assistant |
