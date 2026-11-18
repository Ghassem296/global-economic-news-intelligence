# GENI-ADR-015 — Market Data Integration and Economic Impact Classification

**ADR ID:** GENI-ADR-015  
**Title:** Market Data Integration and Economic Impact Classification  
**Version:** 0.1  
**Status:** Proposed — Awaiting Project Owner Review  
**Priority:** P1  
**Created:** 2026-11-18  
**Last Updated:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approval:** No approval has been recorded.

## 1. Context and Problem Statement

The product may compare events with market observations and analyze effects across currencies, rates, commodities, equities, sectors, trade, and macroeconomic channels. Observed price changes do not by themselves prove event causality.

This is a proposed decision document. Its recommendation does not become an approved architectural constraint until the Project Owner explicitly accepts it.

## 2. Decision Question

How should market data be sourced and aligned with events, and how should potential economic effects be distinguished from observed reactions?

## 3. Requirements and Constraints

- Preserve provenance, auditability, and historical traceability.
- Keep domain decisions separate from candidate generation, processing state, and external side effects.
- Version policies and derived assessments that may change over time.
- Represent uncertainty and unavailable information explicitly.
- Keep infrastructure replaceable where the domain does not require a specific provider.
- Do not treat a recommendation, draft, or implementation progress as approval.

## 4. Alternatives Considered

A. Treat price movement after an event as its impact. B. Exclude market data. C. Separate licensed observations, impact analysis, and causal attribution with explicit uncertainty.

## 5. Recommended Decision

Use provider-independent market-data adapters with instrument, venue, timestamp, timezone, units, frequency, quality, and licensing metadata. Store observations separately from analytical assessments. Analyze impact by channel, direction, magnitude, horizon, evidence status, and uncertainty. Label market reactions as observed temporal associations unless defensible causal evidence supports stronger language.

This is the recommended direction for review, not a final accepted decision.

## 6. Rationale

C supports useful market context without overstating causality or mixing observations with forecasts.

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

Define instrument mapping, event windows, baselines, stale/missing data handling, calendars, source quality, impact channels, and independent analysis versions.

### 9.2 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`, where sequencing is affected
- `docs/adr/README.md`

### 9.3 Related ADRs

- `GENI-ADR-008`
- `GENI-ADR-011`
- `GENI-ADR-019`

Related Proposed ADRs are dependencies or context only; their presence does not imply approval.

## 10. Implementation Implications

Implementation must not assume this proposal is accepted. After approval, translate it into versioned interfaces, data constraints, workflow behavior, and implementation tasks. Any material deviation discovered during implementation must be brought to the decision owner and recorded.

## 11. Acceptance and Verification Criteria

Every observation has provenance and units; missing data remains unknown; time alignment is reproducible; observed reaction and forecast impact are distinct; temporal proximity alone never proves causality.

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
