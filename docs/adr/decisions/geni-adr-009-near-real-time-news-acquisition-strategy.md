# GENI-ADR-009 — Near-Real-Time News Acquisition Strategy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-009  
**Title:** Near-Real-Time News Acquisition Strategy  
**Version:** 0.2  
**Status:** Proposed  
**Priority:** P1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

The platform depends on heterogeneous news sources. They differ in update cadence, access mechanism, rate limits, reliability, terms of use, and latency. A uniform high-frequency polling strategy wastes resources and can violate source constraints; manual-only collection cannot support the intended monitoring workflow.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision. The existence of this document does not imply acceptance.

## 2. Decision Question

Which acquisition model provides useful freshness while preserving source-specific access rules, checkpoint correctness, and operational isolation?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Source-specific access capability and contractual restrictions.
- Freshness requirements must be measurable per source rather than expressed as an unsupported global real-time promise.
- Incremental and idempotent ingestion.
- Failure isolation, rate-limit compliance, and observability.
- Low operational complexity for the initial deployment.

### 3.2 Technical Constraints

- Domain contracts must not depend on a specific external provider unless explicitly approved.
- All relevant policies, schemas, and derived outputs must be versioned.
- Critical state transitions must be auditable and testable.
- Missing or unavailable information must remain explicit.

### 3.3 Business and Product Constraints

- The initial product must remain operationally simple.
- Implementation sequencing must follow documented dependencies.
- Product claims must not exceed the capability or evidence actually available.

### 3.4 Security and Privacy Constraints

- External source content and model output are untrusted input.
- Credentials and sensitive operational data must not be exposed in ordinary logs.
- Access to privileged actions must follow least-privilege authorization.

### 3.5 Operational and Cost Constraints

- Concurrency, retries, resource usage, and external service calls must be bounded.
- Operational metrics must make failure and uncertainty visible.
- Numeric thresholds must be based on measurements or explicit policy approval.

### 3.6 Legal and Content-Rights Constraints

- Technical access does not imply permission to store, process, transform, or republish content.
- Source terms, licensing, privacy, and jurisdictional requirements must be reviewed where applicable.

### 3.7 Explicit Non-Goals

- This ADR does not set unmeasured numeric service levels or model-quality thresholds.
- This ADR does not select a vendor or provider where comparative evidence is unavailable.
- This ADR does not approve its recommendation; explicit Project Owner approval remains required.

## 4. Alternatives Considered

### 4.1 A — Uniform frequent polling

**Advantages:** Simple scheduler and consistent behavior.

**Disadvantages:** Wasteful for slow sources; may exceed source limits and still miss push updates.

**Risk:** High

### 4.2 B — Manual or infrequent batch collection

**Advantages:** Low operational load and easy to control.

**Disadvantages:** Insufficient freshness and weak continuous monitoring.

**Risk:** Medium

### 4.3 C — Source-aware polling with optional supported push

**Advantages:** Adapts cadence to source capabilities; supports incremental checkpoints and failure isolation.

**Disadvantages:** Requires source metadata, scheduler policy, and per-adapter tests.

**Risk:** Medium


## 5. Evaluation and Comparison

The following qualitative comparison is an architectural assessment, not a measured benchmark.

| Criterion | Alternative A | Alternative B | Alternative C |
|---|---|---|---|
| Fit with product requirements | Limited / context-dependent | Partial | Strongest overall fit |
| Operational complexity | Low | Medium | Medium |
| Auditability and traceability | Limited | Partial | Strong |
| Ability to evolve | Low to Medium | Medium | High |
| Principal trade-off | Simplicity or incomplete capability | Partial separation | More explicit contracts and governance |

The recommendation favors Alternative C because it preserves the domain distinctions and operational controls required by the product. Any quantitative comparison must be performed against representative workload and evaluation data.

## 6. Recommended Decision

Adopt source-aware scheduled polling as the baseline. Each SourceAdapter declares supported acquisition methods and operational constraints. Use incremental checkpoints, per-source schedules, bounded concurrency, rate limiting, backoff, and health monitoring. Add webhooks or push feeds only where the source officially supports them and the integration has been validated. Do not label the product real-time unless the source and measured end-to-end latency support that claim.

### 6.1 Decision Boundaries

- SourceAdapter contract exposes capabilities, fetch window, checkpoint format, rate limits, and content-access restrictions.
- CollectionScheduler selects due sources and applies per-source concurrency and freshness policy.
- CollectionCheckpoint advances only after acquired records are durably persisted and deduplicated.
- SourceHealthRecord tracks success, errors, latency, rate limiting, and consecutive failures.
- Retry policy distinguishes transient network errors, rate limits, permanent access denial, malformed payloads, and rights restrictions.
- Collection metrics report last successful fetch, oldest unprocessed item, observed lag, and source availability.

### 6.2 Assumptions and Open Questions

- The recommendation is based on the current product and architecture documents.
- Any numeric threshold, provider selection, or legal interpretation not supported by evidence remains open.
- The Project Owner may accept, reject, or request revision of this recommendation.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded. The recommendation in Section 6 is awaiting review.

**Conditions or Restrictions:**

- Do not treat this proposal as an accepted architectural constraint.
- Do not implement irreversible changes solely on the basis of this recommendation.
- Record any interim implementation assumption and its review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Makes the relevant domain or operational boundary explicit.
- Improves traceability and repeatability.
- Provides a basis for measurable verification and future revision.

### 8.2 Negative Consequences

- Adds implementation and documentation work.
- Some policy details remain open pending data, legal review, or operational measurements.
- Dependent components may need coordinated changes after approval.

### 8.3 Technical Trade-Offs

Alternative C favors explicit contracts and traceability over the smallest possible implementation. Provider-specific behavior or domain-specific exceptions must remain visible rather than being hidden behind an abstraction that implies guarantees the system does not have.

### 8.4 Operational Consequences

The implementation will require monitoring, recovery, and review procedures appropriate to the selected capability. Failure modes and unknown outcomes must be observable.

### 8.5 Product and Business Consequences

The recommendation is intended to support the product's evidence-based economic intelligence purpose. It must not create user-facing promises that exceed actual source coverage, data quality, or review capacity.

### 8.6 Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Proposal mistaken for approval | Keep status Proposed until explicit approval is recorded. |
| Over-specification without evidence | Leave thresholds and provider choices open until measured. |
| Cross-document inconsistency | Synchronize affected documents and registry after approval. |
| Implementation cannot satisfy a proposed guarantee | Report the conflict and revise the ADR rather than silently weakening the contract. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- SourceAdapter contract exposes capabilities, fetch window, checkpoint format, rate limits, and content-access restrictions.
- CollectionScheduler selects due sources and applies per-source concurrency and freshness policy.
- CollectionCheckpoint advances only after acquired records are durably persisted and deduplicated.
- SourceHealthRecord tracks success, errors, latency, rate limiting, and consecutive failures.
- Retry policy distinguishes transient network errors, rate limits, permanent access denial, malformed payloads, and rights restrictions.
- Collection metrics report last successful fetch, oldest unprocessed item, observed lag, and source availability.

### 9.2 Affected Data Models and Interfaces

The relevant interfaces, persistence fields, constraints, and version metadata must be updated only after the proposal is approved and the implementation design is reviewed.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

See the related ADR references in the registry. These dependencies do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work

- SourceAdapter contract exposes capabilities, fetch window, checkpoint format, rate limits, and content-access restrictions.
- CollectionScheduler selects due sources and applies per-source concurrency and freshness policy.
- CollectionCheckpoint advances only after acquired records are durably persisted and deduplicated.
- SourceHealthRecord tracks success, errors, latency, rate limiting, and consecutive failures.
- Retry policy distinguishes transient network errors, rate limits, permanent access denial, malformed payloads, and rights restrictions.
- Collection metrics report last successful fetch, oldest unprocessed item, observed lag, and source availability.

### 10.2 Migration or Compatibility Requirements

No runtime or database migration is authorized by this proposal. If accepted, existing records and historical provenance must be inspected before a migration is designed. Migration must preserve audit history and must be tested from the current baseline.

### 10.3 Dependencies

Implementation sequencing must respect the dependencies recorded in the ADR Registry and the related decision documents.

### 10.4 Implementation Sequence

1. Obtain explicit Project Owner approval.
2. Update affected architecture and data-model contracts.
3. Define versioned interfaces and migration requirements.
4. Implement the smallest end-to-end slice.
5. Add focused automated and integration tests.
6. Validate operational behavior and update implementation status separately from ADR status.

### 10.5 Verification Requirements

- Repeated collection with the same checkpoint and input does not create duplicate Article records.
- A rate-limited source is backed off without blocking unrelated sources.
- Checkpoint advancement is atomic with successful persistence of the corresponding ingestion batch.
- Unsupported push mechanisms are not enabled by configuration alone.
- Source access restrictions and permitted content fields are retained in acquisition provenance.
- Collection lag and source failures are observable per source.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | Repeated collection with the same checkpoint and input does not create duplicate Article records. | Architecture review and automated tests where applicable |
| AC-02 | A rate-limited source is backed off without blocking unrelated sources. | Architecture review and automated tests where applicable |
| AC-03 | Checkpoint advancement is atomic with successful persistence of the corresponding ingestion batch. | Architecture review and automated tests where applicable |
| AC-04 | Unsupported push mechanisms are not enabled by configuration alone. | Architecture review and automated tests where applicable |
| AC-05 | Source access restrictions and permitted content fields are retained in acquisition provenance. | Architecture review and automated tests where applicable |
| AC-06 | Collection lag and source failures are observable per source. | Architecture review and automated tests where applicable |

Quantitative thresholds must be established using representative evaluation data or operational measurements. This ADR intentionally does not invent numerical targets.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- A source changes its API/feed or access terms.
- Measured freshness is outside a product-defined service objective.
- Source volume makes polling cost or latency unacceptable.
- The project introduces a new source class with push/webhook capability.

### 12.2 Review Schedule

**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions

Reconsider this proposal if its assumptions become invalid, evaluation results contradict the recommendation, or product/legal/operational requirements materially change. A replacement of an accepted decision requires a new ADR or an explicitly approved superseding record.

## 13. References and Supporting Evidence

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`
- Related decision topics are listed in the ADR Registry.

The current internal documents establish architectural context. They do not substitute for external legal advice, provider capability verification, or empirical performance measurements.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 0.1 | 2026-11-18 | Proposed | Initial proposal drafted | AI Architecture Assistant |
| 0.2 | 2026-11-18 | Proposed | Expanded alternatives, evaluation, implementation, risks, and verification criteria | AI Architecture Assistant |

**End of ADR**
