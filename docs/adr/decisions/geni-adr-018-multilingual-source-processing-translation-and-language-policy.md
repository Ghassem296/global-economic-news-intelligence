# GENI-ADR-018 — Multilingual Source Processing, Translation, and Language Policy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-018  
**Title:** Multilingual Source Processing, Translation, and Language Policy  
**Version:** 0.2  
**Status:** Proposed  
**Priority:** P2  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

International news sources publish in many languages. Translation can improve retrieval and reporting but can alter nuance, named entities, dates, quantities, negation, attribution, and quotations. The original source and its permitted content references must remain the provenance anchor. The initial report language is documented as English, but source language and output language are separate concerns.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision.

## 2. Decision Question

How should the platform detect source language, preserve original content, generate translations, and use multilingual material in analysis and reporting?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Preserve original source language and provenance.
- Treat translation as a derived artifact, not an authoritative replacement.
- Maintain exact alignment between translated statements and original source spans where feasible.
- Detect and represent uncertainty in language identification and translation quality.
- Keep output-language policy explicit and independently versioned.

### 3.2 Technical Constraints

- Domain contracts must not depend on a specific external provider unless explicitly approved.
- Derived artifacts must identify their exact input version and generation configuration.
- Historical provenance must remain available for review and correction.
- Unknown or unavailable information must remain explicit.

### 3.3 Business and Product Constraints

- The initial release remains focused on the core text intelligence workflow.
- Additional channels and languages must be introduced only when justified by product requirements.
- User-facing claims must reflect validated capability and actual source coverage.

### 3.4 Security and Privacy Constraints

- External source content is untrusted input.
- External processing must comply with applicable privacy and data-protection requirements.
- Provider credentials and sensitive content must not be exposed in logs.

### 3.5 Operational and Cost Constraints

- Processing concurrency, media generation, translation calls, and storage must be bounded.
- Provider failures must not corrupt authoritative report or source records.
- Cost and quality must be observable separately.

### 3.6 Legal and Content-Rights Constraints

- Access to source material does not imply permission to translate, store, transform, or republish it.
- Media and translation outputs may have additional provider/platform terms.
- Legal review may be required for jurisdiction-specific obligations.

### 3.7 Explicit Non-Goals

- This ADR does not select a specific TTS, video, or translation vendor.
- This ADR does not establish unmeasured language-quality or media-quality thresholds.
- This ADR does not authorize expansion beyond the approved product scope.

## 4. Alternatives Considered

### 4.1 A — Translate all content immediately and discard originals

**Advantages:** Simplifies downstream processing around one language.

**Disadvantages:** Destroys source fidelity and makes translation errors difficult to audit or correct.

**Risk:** Very High

### 4.2 B — Process every language independently with no translation

**Advantages:** Preserves source language and avoids translation errors.

**Disadvantages:** Limits cross-language retrieval, comparison, and reporting capabilities.

**Risk:** Medium

### 4.3 C — Preserve originals and create traceable optional translations

**Advantages:** Supports multilingual retrieval while retaining original evidence and reviewability.

**Disadvantages:** Requires translation lineage, quality checks, and language-aware evaluation.

**Risk:** Medium


## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured cost or output quality.

| Criterion | Alternative A | Alternative B | Alternative C |
|---|---|---|---|
| Initial scope control | Low | High | High |
| Provenance preservation | Low | High | High |
| Future extensibility | High but premature | Low | High |
| Operational complexity | High | Low | Medium |
| Quality and rights governance | Difficult to coordinate | Simple but limited | Explicit per derived artifact |

Alternative C is recommended because it separates the core intelligence model from channel-specific presentation while preserving future extensibility.

## 6. Recommended Decision

Preserve original source-language metadata and permitted content references as primary provenance. Language identification and translation are separate, versioned derived artifacts. Each translation records provider/model, version, source revision, source/target language, generation time, and quality metadata. Translation may support retrieval and analysis but must not replace original evidence. Important claims should retain original-language spans and, where feasible, be checked against the original for names, quantities, dates, negation, and quotations. Keep report output language as a separate product policy; English remains the initial proposed output language unless explicitly changed.

### 6.1 Decision Boundaries

- Define language detection result, confidence, method, and model version; permit UNKNOWN or mixed-language outcomes.
- Preserve original source text or permitted references according to content-rights policy.
- Define translation artifacts keyed to exact ArticleRevision and target language.
- Record translation provider/model/version, prompt/configuration, timestamps, and quality status.
- Preserve sentence/segment alignment to original source spans where technically feasible.
- Use multilingual entity aliases and transliteration carefully; do not merge entities solely on transliterated similarity.
- Build language-specific and cross-language evaluation datasets.
- Require original-source verification for high-impact quotations, quantities, dates, and disputed claims where possible.
- Separate source-language policy from report-language and user-interface localization policy.

### 6.2 Assumptions and Open Questions

- The initial output language and supported media formats remain product-level policy choices.
- Provider selection requires comparative quality, cost, rights, and operational review.
- Legal and platform-specific requirements must be validated before production use.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded; the recommendation is awaiting Project Owner review.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Preserves source/report lineage for derived outputs.
- Keeps the core event and report model independent of presentation technology.
- Allows channel or language expansion to be phased and evaluated.

### 8.2 Negative Consequences

- Requires separate artifact records and quality checks.
- Adds translation/media-specific storage and lifecycle management.
- Some capabilities remain deferred until demand and quality are demonstrated.

### 8.3 Technical Trade-Offs

The recommendation favors derived, versioned artifacts over a single mutable multi-format report. This increases traceability and storage requirements but prevents generated media from silently diverging from the authoritative report version.

### 8.4 Operational Consequences

Every enabled adapter needs monitoring, retries, cost controls, rights checks, and a correction/withdrawal procedure. Failures must be isolated from the core text pipeline.

### 8.5 Product and Business Consequences

New channels and languages may increase reach but must not weaken factual quality, accessibility, source attribution, or editorial control.

### 8.6 Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Media or translation diverges from corrected source report | Maintain exact lineage and trigger downstream review on report supersession. |
| Provider output introduces factual errors | Review transcripts/translations and retain source references. |
| Rights are assumed rather than verified | Apply source and output-specific rights checks before generation and publication. |
| Premature expansion increases cost | Use phased acceptance gates and task-level budgets. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- Define language detection result, confidence, method, and model version; permit UNKNOWN or mixed-language outcomes.
- Preserve original source text or permitted references according to content-rights policy.
- Define translation artifacts keyed to exact ArticleRevision and target language.
- Record translation provider/model/version, prompt/configuration, timestamps, and quality status.
- Preserve sentence/segment alignment to original source spans where technically feasible.
- Use multilingual entity aliases and transliteration carefully; do not merge entities solely on transliterated similarity.
- Build language-specific and cross-language evaluation datasets.
- Require original-source verification for high-impact quotations, quantities, dates, and disputed claims where possible.
- Separate source-language policy from report-language and user-interface localization policy.

### 9.2 Affected Data Models and Interfaces

If accepted, define derived artifact records, source/report lineage, provider metadata, output format, quality state, and supersession references. Keep them separate from Article, Event, Analysis, and Report authoritative records.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

- GENI-ADR-004 — Publication decisions and quality gates.
- GENI-ADR-013 — Content access, licensing, retention, and republication.
- GENI-ADR-014 — Human review, corrections, and withdrawals.
- GENI-ADR-017 — LLM budgets, usage tracking, and evaluation.

## 10. Implementation Implications

### 10.1 Required Implementation Work

- Define language detection result, confidence, method, and model version; permit UNKNOWN or mixed-language outcomes.
- Preserve original source text or permitted references according to content-rights policy.
- Define translation artifacts keyed to exact ArticleRevision and target language.
- Record translation provider/model/version, prompt/configuration, timestamps, and quality status.
- Preserve sentence/segment alignment to original source spans where technically feasible.
- Use multilingual entity aliases and transliteration carefully; do not merge entities solely on transliterated similarity.
- Build language-specific and cross-language evaluation datasets.
- Require original-source verification for high-impact quotations, quantities, dates, and disputed claims where possible.
- Separate source-language policy from report-language and user-interface localization policy.

### 10.2 Migration or Compatibility Requirements

No runtime or database migration is authorized by this proposal. If accepted, any existing content references or report records must be inspected before a migration is designed. Preserve existing source and report versions.

### 10.3 Dependencies

Implementation sequencing must follow the related ADRs and the product roadmap. Proposed related ADRs are not approved merely because they are referenced here.

### 10.4 Implementation Sequence

1. Obtain explicit Project Owner approval.
2. Validate product demand, rights, and provider capabilities.
3. Define artifact contracts and lineage.
4. Implement one bounded adapter as a pilot.
5. Evaluate quality, accessibility, cost, and operational behavior.
6. Expand only after acceptance criteria are met.

### 10.5 Verification Requirements

- Original language and detection provenance remain available for every ArticleRevision.
- A translation is traceable to an exact source revision and target language.
- Updating a translation does not overwrite the original source artifact.
- Important claims retain original-source references or explicitly disclose when alignment is unavailable.
- Unknown or mixed language is not forced into an incorrect language label.
- Translation quality and downstream extraction quality are evaluated separately by language.
- The report-language policy does not alter the source-language provenance.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | Original language and detection provenance remain available for every ArticleRevision. | Architecture review and automated tests where applicable |
| AC-02 | A translation is traceable to an exact source revision and target language. | Architecture review and automated tests where applicable |
| AC-03 | Updating a translation does not overwrite the original source artifact. | Architecture review and automated tests where applicable |
| AC-04 | Important claims retain original-source references or explicitly disclose when alignment is unavailable. | Architecture review and automated tests where applicable |
| AC-05 | Unknown or mixed language is not forced into an incorrect language label. | Architecture review and automated tests where applicable |
| AC-06 | Translation quality and downstream extraction quality are evaluated separately by language. | Architecture review and automated tests where applicable |
| AC-07 | The report-language policy does not alter the source-language provenance. | Architecture review and automated tests where applicable |

Quantitative quality and cost thresholds must be established through representative evaluation, not invented in this ADR.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- The product adds new target languages or markets.
- A translation provider/model changes materially.
- Evaluation shows language-specific extraction or translation failures.
- Legal or content-rights rules change for translation or external processing.

### 12.2 Review Schedule

**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions

Reconsider this proposal when product scope, provider capabilities, rights, or measured quality/cost materially change. A replacement of an accepted decision requires a new or explicitly superseding ADR.

## 13. References and Supporting Evidence

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/adr/README.md`
- Related decision records listed in the ADR Registry.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 0.1 | 2026-11-18 | Proposed | Initial proposal drafted | AI Architecture Assistant |
| 0.2 | 2026-11-18 | Proposed | Expanded alternatives, evaluation, implementation, risks, and verification criteria | AI Architecture Assistant |

**End of ADR**
