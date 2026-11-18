# GENI-ADR-012 — Semantic Retrieval, Similarity Calculation, and Embedding Storage

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-012  
**Title:** Semantic Retrieval, Similarity Calculation, and Embedding Storage  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Event matching and historical retrieval may require semantic discovery beyond exact identifiers and lexical overlap. Embeddings, similarity functions, and vector indexes may help retrieve candidates, but similarity is not identity proof. Selecting a model or dedicated vector database before measuring corpus size, retrieval quality, latency, update frequency, rights, and operational needs risks unnecessary infrastructure and false confidence.

This ADR is a proposal for formal review; it does not approve a production implementation.

## 2. Decision Question

How should semantic retrieval and embedding persistence support candidate discovery while preserving provenance, reproducibility, uncertainty, and database independence?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Keep candidate retrieval separate from final event-match decisions.
- Combine lexical, deterministic, entity, temporal, geographic, and semantic signals where useful.
- Version embedding model, preprocessing, dimensions, normalization, and index configuration.
- Preserve provenance and rights eligibility of every embedding input.
- Treat similarity as a ranking signal, not calibrated probability or association authorization.
- Support re-embedding, index rebuild, deletion, and fallback when providers are unavailable.

### 3.2 Technical Constraints
- A dedicated vector database is not mandatory by default.
- Relational domain records remain authoritative.
- External embedding providers are subject to ADR-006 and rights checks in ADR-013.
- Embedding model changes require evaluation and controlled reprocessing.

### 3.3 Business and Product Constraints
- The initial product remains text-based economic intelligence.
- The architecture must support incremental delivery and traceable evaluation.
- Proposed decisions remain provisional until explicitly approved.

### 3.4 Security and Privacy Constraints
- External source content and generated model output are untrusted until validated.
- Least-privilege access, secret protection, and explicit external permissions are mandatory.
- Operational logs must avoid unnecessary protected content.

### 3.5 Operational and Cost Constraints
- Avoid unnecessary distributed infrastructure in the initial release.
- Measure operational complexity and cost against expected workload.
- Timeouts, retries, recovery, and observability must be explicit.

### 3.6 Legal and Content-Rights Constraints
- Technical access does not imply permission to store, process externally, transform, quote, or republish source content.
- Source terms, licensing, privacy, and jurisdictional requirements must be reviewed before production use.

### 3.7 Explicit Non-Goals
- No unmeasured numerical threshold or performance guarantee is established by this proposal.
- No provider or infrastructure technology is mandatory solely because it appears as an alternative.
- This ADR does not replace the formal approval process.

## 4. Alternatives Considered

### 4.1 Alternative A — Lexical and rule-based retrieval only

**Description:** Use identifiers, keyword indexes, entity matching, and deterministic filters.

**Advantages:**
- Simple and explainable
- low infrastructure burden.

**Disadvantages:**
- May miss paraphrases, translations, and semantically equivalent reporting.

**Risks:**
- Candidate recall may be inadequate for varied news.

**Estimated Complexity:** Low to Medium

### 4.2 Alternative B — Embeddings in relational persistence

**Description:** Store versioned embedding artifacts in the selected relational engine or a supported extension.

**Advantages:**
- Fewer services
- easier provenance and lifecycle integration.

**Disadvantages:**
- Vector indexing and scale depend on engine features.

**Risks:**
- Latency or corpus limits may be reached.

**Estimated Complexity:** Medium

### 4.3 Alternative C — Dedicated vector retrieval service

**Description:** Use a specialized vector database/service while keeping relational records authoritative.

**Advantages:**
- Specialized indexing and scaling options.

**Disadvantages:**
- Adds service, backup, security, deletion, and consistency burden.

**Risks:**
- Premature infrastructure and index drift.

**Estimated Complexity:** High

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Lexical and rule-based retrieval only | Embeddings in relational persistence | Dedicated vector retrieval service |
|---|---|---|---|
| Initial simplicity | High | High to Medium | Low |
| Semantic potential | Low | High | High |
| Lifecycle integration | High | High | Requires integration |
| Scale flexibility | Medium | Engine dependent | High |
| Premature infrastructure risk | Low | Low to Medium | High |

The requirements in Section 3 are the evaluation criteria. Unmeasured latency, quality, throughput, and costs are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative B as a measured initial candidate, with an evidence-based escalation path to Alternative C.

Keep relational Event, Article, and decision records authoritative. Embeddings are derived, versioned retrieval artifacts. After this ADR is formally accepted, begin with lexical/deterministic retrieval and a separately measured embedding prototype stored using the simplest proven persistence option. Adopt dedicated vector infrastructure only when representative tests show that the selected relational approach cannot meet approved quality, latency, or scale objectives. Similarity may rank candidates; only a separate EventMatchDecision can authorize association.

**Rationale:**
- Avoids converting similarity into a domain decision.
- Enables staged infrastructure selection.
- Preserves provenance and lifecycle control for derived embeddings.

**Deferred Questions:**
- Embedding model/provider, dimensions, and preprocessing.
- Distance metric, normalization, and candidate cutoff.
- Index type and refresh/rebuild strategy.
- Vector service selection and operational requirements.
- Evaluation dataset and quality thresholds.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The Project Owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review; see Section 6 for the recommendation.

**Conditions or Restrictions:**
- Keep this ADR Proposed until explicit approval is recorded.
- Do not treat deferred questions as settled implementation details.
- Any interim implementation choice must be reversible, documented, and assigned a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Adds semantic candidate discovery without changing domain authority.
- Makes model and storage changes measurable.
- Avoids premature vector service dependencies.

### 8.2 Negative Consequences
- Requires derived-artifact lifecycle and rebuild operations.
- Initial prototype may have limited retrieval capacity.

### 8.3 Technical Trade-Offs
Use the simplest approach that meets measured retrieval requirements. Dedicated vector infrastructure is an optimization, not a domain requirement; candidate quality and identity-decision quality are evaluated separately.

### 8.4 Operational Consequences
Monitor embedding costs, index lag, retrieval latency/recall, failures, and rebuild status. Maintain fallback retrieval when embedding provider or index is unavailable.

### 8.5 Product and Business Consequences
Semantic retrieval may improve candidate discovery, but ambiguous cases remain unresolved rather than forced into a match.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Similarity mistaken for identity | Medium | Critical | Require separate EventMatchDecision. |
| Embedding model drift | Medium | High | Version model/preprocessing and maintain regression data. |
| Unauthorized content embedding | Medium | High | Run rights checks before external processing and persistence. |
| Unnecessary vector infrastructure | Medium | Medium | Use measured escalation criteria. |
| Index/relational divergence | Medium | High | Treat relational records as authoritative and reconcile indexes. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- EventMatcher
- EmbeddingService
- RetrievalAdapter
- WorkflowOrchestrator

### 9.2 Affected Data Models and Interfaces
- EmbeddingRecord
- EmbeddingModelVersion
- EmbeddingInputFingerprint
- EventMatchCandidate
- RetrievalRun

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-002 | Depends on / Related to | Defines article deduplication and event matching boundaries. |
| GENI-ADR-011 | Depends on / Related to | Defines event identity and final decisions. |
| GENI-ADR-006 | Related to | Controls provider-independent embedding execution if external. |
| GENI-ADR-013 | Depends on | Controls which source content may be embedded externally or retained. |
| GENI-ADR-016 | Related to | Provides reliable persistence and rebuild/recovery principles. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define an embedding artifact schema and deterministic input fingerprint.
- Record model, preprocessing, dimensions, timestamps, and rights eligibility.
- Create labeled cases for paraphrases, multilingual rewrites, and related-but-distinct events.
- Compare lexical baseline and embedding retrieval.
- Measure recall, candidate count, latency, cost, and index rebuild time.
- Keep candidate thresholding separate from final decision policy.

### 10.2 Migration or Compatibility Requirements
Inspect the current implementation and data before designing any migration. This ADR does not claim that a migration has been executed. Any transition must preserve provenance and historical state.

### 10.3 Dependencies
- GENI-ADR-002 — Defines article deduplication and event matching boundaries.
- GENI-ADR-011 — Defines event identity and final decisions.
- GENI-ADR-006 — Controls provider-independent embedding execution if external.
- GENI-ADR-013 — Controls which source content may be embedded externally or retained.
- GENI-ADR-016 — Provides reliable persistence and rebuild/recovery principles.

### 10.4 Implementation Sequence
1. Test that similar wording does not automatically merge distinct events.
2. Measure recall and precision at candidate cutoffs on labeled cases.
3. Verify similarity is not called probability without calibration.
4. Verify embedding artifacts identify model and input version.
5. Verify rights revocation/deletion propagates to dependent embeddings and indexes.

### 10.5 Verification Requirements
- Test that similar wording does not automatically merge distinct events.
- Measure recall and precision at candidate cutoffs on labeled cases.
- Verify similarity is not called probability without calibration.
- Verify embedding artifacts identify model and input version.
- Verify rights revocation/deletion propagates to dependent embeddings and indexes.

Implementation verification remains deferred until the ADR is accepted and the capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Candidate retrieval never creates an event association. | Workflow tests |
| AC-02 | Embeddings preserve model, input, and policy provenance. | Schema tests |
| AC-03 | Similarity semantics are documented and not treated as probability by default. | Contract tests |
| AC-04 | Retrieval is compared with a lexical baseline on labeled cases. | Evaluation report |
| AC-05 | Vector infrastructure requires measured evidence. | Architecture gate |
| AC-06 | Rebuild and deletion are traceable and rights-aware. | Lifecycle tests |

Quantitative thresholds require representative datasets, operational measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Before implementing the dependent capability.
- Material changes in product scope, legal constraints, provider capabilities, workload, or operational scale.
- Evaluation evidence shows that the recommendation does not meet requirements.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider this proposal when its assumptions are invalidated or measured evidence shows that it fails project requirements. Replacements must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

References are internal project documents used to establish documented context. They are not empirical benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines EventMatcher and workflow separation. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines candidate and provenance structures. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines semantic retrieval evaluation. |
| `GENI-ADR-002` | Internal | Defines matching boundary. |
| `GENI-ADR-011` | Internal | Defines event identity. |
| `GENI-ADR-013` | Internal | Defines content rights. |
| `GENI-ADR-016` | Internal | Defines reliable execution. |

External legal, provider, and measured performance evidence must be added where material during formal review.

## 14. Decision History

| Date | Version | Status | Change |
|---|---|---|---|
| 2026-11-18 | 1.0 | Proposed | Expanded ADR proposal prepared for architecture review |
| 2026-11-18 | 1.1 | Proposed | Clarified that the embedding prototype follows formal acceptance, consistent with the staged implementation roadmap. |

**End of ADR**
