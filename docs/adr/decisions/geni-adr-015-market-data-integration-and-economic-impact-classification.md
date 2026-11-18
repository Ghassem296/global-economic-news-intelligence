# GENI-ADR-015 — Market Data Integration and Economic Impact Classification

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-015  
**Title:** Market Data Integration and Economic Impact Classification  
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

Economic intelligence may compare events with market observations across currencies, rates, commodities, equities, and other instruments. Market data varies in coverage, timestamps, units, licensing, and quality. A price movement after an event is an observation, not by itself proof that the event caused the movement.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision. The existence of this document does not imply acceptance.

## 2. Decision Question

How should market observations be acquired and aligned with events, and how should observed reactions be separated from potential or causal economic impact?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Market data must have provenance, timestamps, units, and licensing metadata.
- Instrument identity and market calendars must be explicit.
- Observed reactions, inferred mechanisms, forecasts, and causal claims must remain distinct.
- Missing or stale data must remain unknown rather than be converted into zero.
- Provider integrations must be replaceable.

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

### 4.1 A — Treat post-event price movement as event impact

**Advantages:** Simple and easy to communicate.

**Disadvantages:** Confuses temporal association with causality and ignores confounding factors.

**Risk:** Very High

### 4.2 B — Exclude market data from the product

**Advantages:** Avoids market-data licensing and alignment complexity.

**Disadvantages:** Removes useful context for market-facing economic analysis.

**Risk:** Medium

### 4.3 C — Separate market observations, impact assessments, and causal attribution

**Advantages:** Preserves observable data and analytical uncertainty.

**Disadvantages:** Requires provider adapters, instrument mapping, and event-window methodology.

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

Use provider-independent MarketDataAdapter contracts. Store MarketObservation separately from Event and Analysis records, with instrument, venue, timestamp, timezone, frequency, unit/currency, provider, quality, and licensing metadata. Economic impact analysis is a separate versioned assessment by channel, direction, magnitude, horizon, evidence status, and uncertainty. Describe a price move as an observed market reaction unless a documented causal methodology and supporting evidence justify a stronger attribution. Do not infer event causality solely from temporal proximity.

### 6.1 Decision Boundaries

- Define canonical instrument identifiers and alias mapping with venue and asset-class context.
- Normalize timestamps and trading calendars without discarding original provider timestamps.
- Record data frequency, units, currency, adjustment status, gaps, and stale-data flags.
- Define event-time windows and baseline periods as versioned methodology parameters, not universal constants.
- Store observed data independently from forecasts and analysis results.
- Link each impact assessment to exact market observations and other evidence.
- Respect provider licensing, retention, and redistribution restrictions.

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

- Define canonical instrument identifiers and alias mapping with venue and asset-class context.
- Normalize timestamps and trading calendars without discarding original provider timestamps.
- Record data frequency, units, currency, adjustment status, gaps, and stale-data flags.
- Define event-time windows and baseline periods as versioned methodology parameters, not universal constants.
- Store observed data independently from forecasts and analysis results.
- Link each impact assessment to exact market observations and other evidence.
- Respect provider licensing, retention, and redistribution restrictions.

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

- Define canonical instrument identifiers and alias mapping with venue and asset-class context.
- Normalize timestamps and trading calendars without discarding original provider timestamps.
- Record data frequency, units, currency, adjustment status, gaps, and stale-data flags.
- Define event-time windows and baseline periods as versioned methodology parameters, not universal constants.
- Store observed data independently from forecasts and analysis results.
- Link each impact assessment to exact market observations and other evidence.
- Respect provider licensing, retention, and redistribution restrictions.

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

- Every market observation is traceable to provider, instrument, timestamp, unit, and source terms.
- Time alignment can be reproduced from recorded timezone and calendar metadata.
- Missing/stale observations remain explicit and are not scored as zero.
- A temporal market reaction is not labeled causal without documented causal evidence.
- Potential impact, observed reaction, forecast probability, and impact magnitude are distinct fields/semantics.
- Impact analyses identify channel, direction, horizon, evidence status, uncertainty, and methodology version.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | Every market observation is traceable to provider, instrument, timestamp, unit, and source terms. | Architecture review and automated tests where applicable |
| AC-02 | Time alignment can be reproduced from recorded timezone and calendar metadata. | Architecture review and automated tests where applicable |
| AC-03 | Missing/stale observations remain explicit and are not scored as zero. | Architecture review and automated tests where applicable |
| AC-04 | A temporal market reaction is not labeled causal without documented causal evidence. | Architecture review and automated tests where applicable |
| AC-05 | Potential impact, observed reaction, forecast probability, and impact magnitude are distinct fields/semantics. | Architecture review and automated tests where applicable |
| AC-06 | Impact analyses identify channel, direction, horizon, evidence status, uncertainty, and methodology version. | Architecture review and automated tests where applicable |

Quantitative thresholds must be established using representative evaluation data or operational measurements. This ADR intentionally does not invent numerical targets.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- A new market-data provider or asset class is introduced.
- Coverage, latency, or licensing changes materially.
- The product proposes causal attribution or event-study features.
- Evaluation reveals systematic time-alignment or instrument-mapping errors.

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
