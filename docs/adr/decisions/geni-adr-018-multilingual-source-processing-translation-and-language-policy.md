# GENI-ADR-018 — Multilingual Source Processing, Translation, and Language Policy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-018  
**Title:** Multilingual Source Processing, Translation, and Language Policy  
**Status:** Proposed  
**Version:** 1.0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

International economic news is published in multiple languages and scripts. Translation can change nuance, entity names, dates, units, quotation meaning, negation, and legal or policy terminology. The original source content and language must remain authoritative for provenance. The system needs a language policy that supports original-language processing where feasible, optional traceable translations, and language-specific evaluation without silently replacing the source.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

How should the system identify, preserve, translate, and use multilingual source content in processing, matching, analysis, and reporting?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Preserve original language, script, source references, and permitted source content.
- Record language identification result, method, confidence/quality, and uncertainty.
- Treat translation as a derived, versioned artifact linked to the exact source revision.
- Never replace original text with translated text as the only stored representation.
- Preserve names, numbers, dates, units, negation, quotation boundaries, and attribution where possible.
- Allow original-language analysis and cross-language retrieval when quality is demonstrated.
- Apply rights checks before external translation or processing.
- Evaluate supported languages separately and expose unsupported/low-quality cases.

### 3.2 Technical Constraints
- Language identification and translation quality vary by language, script, domain, and provider.
- Source rights for translation and external processing are governed by ADR-013.
- Cross-language retrieval is related to ADR-012.
- Initial supported-language set remains undecided.

### 3.3 Business and Product Constraints
- The initial product remains event-centric economic intelligence with text reports as its first release.
- The design must support incremental implementation and explicit evaluation.
- Proposals remain provisional until the decision owner records approval.

### 3.4 Security and Privacy Constraints
- Source content and model output are untrusted until validated.
- Only authorized application services and reviewers may change authoritative state.
- Secrets and unnecessary protected content must not appear in ordinary logs.

### 3.5 Operational and Cost Constraints
- Avoid unnecessary distributed infrastructure in the initial release.
- Measure cost and complexity against workload and reliability requirements.
- Failures, retries, recovery, and audit must be observable.

### 3.6 Legal and Content-Rights Constraints
- Access does not itself authorize retention, external processing, transformation, quotation, or republication.
- Source terms, licensing, privacy, and jurisdictional restrictions must be reviewed before production use.

### 3.7 Explicit Non-Goals
- This ADR does not invent unmeasured numerical thresholds or performance guarantees.
- This ADR does not approve a provider, database, or model merely by listing it as an alternative.
- This proposal does not supersede the ADR approval process.

## 4. Alternatives Considered

### 4.1 Alternative A — Translate all content to a pivot language

**Description:** Translate every source before classification and analysis, then de-emphasize the original.

**Advantages:**
- Simplifies downstream language handling.

**Disadvantages:**
- May lose nuance and provenance
- multiplies rights and cost.

**Risks:**
- Translation errors become invisible and hard to audit.

**Estimated Complexity:** Medium

### 4.2 Alternative B — Process each language independently

**Description:** Build separate processing pipelines for every language.

**Advantages:**
- Preserves linguistic fidelity.

**Disadvantages:**
- Large model/rule maintenance burden
- weak cross-language aggregation.

**Risks:**
- Coverage fragmentation and inconsistent results.

**Estimated Complexity:** High

### 4.3 Alternative C — Preserve originals with optional traceable translations

**Description:** Keep source language authoritative and create versioned translations only where justified and permitted.

**Advantages:**
- Traceable and incremental
- supports cross-language use without losing originals.

**Disadvantages:**
- Requires language metadata, translation lineage, and evaluation.

**Risks:**
- Quality may vary and require review.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Translate all content to a pivot language | Process each language independently | Preserve originals with optional traceable translations |
|---|---|---|---|
| Original-source fidelity | Low | High | High |
| Cross-language aggregation | High via pivot | Low to Medium | High where validated |
| Operational burden | Medium | High | Medium |
| Translation error visibility | Low | High | High |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Preserve original source content and create traceable optional translations.

The original source language and revision remain authoritative. Language identification is stored with method and uncertainty. Translation is an optional derived artifact linked to its source revision, translator/model/provider, configuration version, output language, and quality status. Downstream components must know whether they consume original text or a translation. Cross-language matching and analysis may use translations only after evaluation on representative domain-specific datasets. This ADR does not approve a translation provider or universal supported-language promise.

**Rationale:**
- Preserves source provenance and verification against original language.
- Allows incremental language coverage.
- Makes translation error and lineage visible.

**Deferred Questions:**
- Initial supported languages and scripts.
- Translation provider and local-versus-external processing policy.
- Domain-specific translation quality thresholds.
- Languages with limited evaluation data.
- Transliteration and entity-alias normalization policy.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The Project Owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review; Section 6 contains the recommendation.

**Conditions or Restrictions:**
- Maintain Proposed status until explicit approval is recorded.
- Do not treat deferred questions or example values as settled implementation details.
- Any temporary implementation assumption must be reversible and documented with a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Preserves original source integrity.
- Allows incremental multilingual capability.
- Improves traceability and cross-language evaluation.

### 8.2 Negative Consequences
- Adds translation artifacts and quality checks.
- Some languages may remain unsupported or require human review.

### 8.3 Technical Trade-Offs
Translation increases access but adds uncertainty. Original-language evidence remains authoritative; translated text must not silently become the canonical source.

### 8.4 Operational Consequences
Monitor language detection confidence, translation latency/cost, quality by language, provider errors, and rights denials.

### 8.5 Product and Business Consequences
The product can cover more sources without hiding language or translation limits behind fluent output.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Translation changes meaning | Medium | High | Preserve original, evaluate domain terminology, and review low-quality cases. |
| Entity/number corruption | Medium | High | Structured checks, normalization, and source-span traceability. |
| External rights violation | Medium | Critical | Check translation/external-processing permissions before transmission. |
| Uneven language coverage | High | Medium | Publish supported-language scope and track gaps. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- ArticleNormalizer
- LanguageIdentifier
- TranslationService
- EntityExtractor
- EventMatcher
- ClaimExtractor
- ReportGenerator

### 9.2 Affected Data Models and Interfaces
- ArticleRevision
- LanguageDetectionRecord
- TranslationArtifact
- EntityAlias
- ProcessingRun
- Analysis

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-002 | Related to | Defines duplicate detection and matching across article revisions. |
| GENI-ADR-006 | Related to | Defines provider-independent execution for translation tasks. |
| GENI-ADR-008 | Related to | Defines provenance and uncertainty for translated evidence. |
| GENI-ADR-012 | Related to | Defines semantic retrieval and cross-language embedding options. |
| GENI-ADR-013 | Depends on | Defines translation and external-processing rights. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Preserve source-language and script metadata on every article revision.
- Implement language identification with explicit unknown/ambiguous outcomes.
- Define translation artifact lineage and immutable version metadata.
- Separate original and translated text in component interfaces.
- Build language-specific and cross-language test sets.
- Evaluate numbers, units, names, negation, quotations, and policy terms.
- Gate unsupported languages or low-quality translations from material claims.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-002 — Defines duplicate detection and matching across article revisions.
- GENI-ADR-006 — Defines provider-independent execution for translation tasks.
- GENI-ADR-008 — Defines provenance and uncertainty for translated evidence.
- GENI-ADR-012 — Defines semantic retrieval and cross-language embedding options.
- GENI-ADR-013 — Defines translation and external-processing rights.

### 10.4 Implementation Sequence
1. Define language metadata and supported-language policy.
2. Preserve originals and implement language identification.
3. Define translation artifact schema and rights gate.
4. Build representative language-specific evaluation cases.
5. Introduce optional translation for selected languages.
6. Extend cross-language matching only after evaluation.

### 10.5 Verification Requirements
- Verify original content remains available subject to rights policy after translation.
- Test language detection on mixed-language, short, and noisy text.
- Test preservation of dates, units, values, names, negation, and attribution.
- Compare extraction from original and translation on reviewed cases.
- Verify external processing is blocked when source rights do not permit it.
- Verify translation changes create new artifacts without overwriting prior versions.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Original language and source revision remain authoritative. | Persistence tests |
| AC-02 | Translation artifacts are versioned and linked to source revisions. | Lineage tests |
| AC-03 | Language detection exposes unknown/ambiguous outcomes. | Component tests |
| AC-04 | Material analysis cannot silently rely on unvalidated translation. | Workflow policy tests |
| AC-05 | Supported-language quality is measured separately. | Evaluation report |
| AC-06 | Rights checks precede external translation. | Rights integration tests |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- New source languages materially expand product scope.
- Evaluation reveals systematic translation errors in economic terminology.
- Provider or rights restrictions change.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Defines language identification and international source processing. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines normalization and shared LLM execution. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines article revision and derived analysis provenance. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines multilingual capability roadmap. |
| `GENI-ADR-008` | Internal | Evidence provenance and uncertainty. |
| `GENI-ADR-013` | Internal | Content rights. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Date | Version | Status | Change |
|---|---|---|---|
| 2026-11-18 | 1.0 | Proposed | Expanded ADR proposal prepared for architecture review |

**End of ADR**
