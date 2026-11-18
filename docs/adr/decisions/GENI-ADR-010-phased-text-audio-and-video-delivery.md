# GENI-ADR-010 — Phased Text, Audio, and Video Delivery

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-010  
**Title:** Phased Text, Audio, and Video Delivery  
**Status:** Proposed  
**Version:** 1.0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

The product's initial value is structured text intelligence. Audio and video may improve accessibility and distribution, but introduce additional content-rights, production, quality, storage, accessibility, and delivery requirements. Treating all formats as initial-release requirements would increase scope and create dependencies before the text intelligence workflow is validated.

This ADR is a proposal for formal review; it does not approve a production implementation.

## 2. Decision Question

How should text, audio, and video capabilities be sequenced, and what architectural boundaries should keep media production independent from the initial text product?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Initial release delivers structured text reports.
- Audio and video are later, independently deployable output capabilities.
- Media must be generated from approved, versioned report content rather than raw unverified source content.
- Apply format-specific rights checks to narration, quotations, images, clips, music, and distribution.
- Preserve lineage from media artifacts to exact report and analysis versions.
- Support format-specific quality, accessibility, retention, correction, and delivery handling.

### 3.2 Technical Constraints
- Text is the initial product release.
- Text-analysis permission does not automatically authorize narration or video transformation.
- Media provider, codecs, visual asset licensing, and distribution targets remain undecided.
- Rights requirements from ADR-013 apply.

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

### 4.1 Alternative A — All formats in initial release

**Description:** Build text, audio, and video at launch.

**Advantages:**
- Broad launch capability.

**Disadvantages:**
- Large scope and multiple rights/quality dependencies.

**Risks:**
- Delays core intelligence and multiplies failure modes.

**Estimated Complexity:** High

### 4.2 Alternative B — Text only with no extension boundary

**Description:** Implement text and defer all media design.

**Advantages:**
- Smallest initial scope.

**Disadvantages:**
- Could require redesign of artifact lineage and rights controls later.

**Risks:**
- Future media may be coupled to report internals.

**Estimated Complexity:** Low initially

### 4.3 Alternative C — Text-first phased delivery

**Description:** Ship text first and introduce separate audio/video pipelines after measurable gates.

**Advantages:**
- Protects the core product and isolates media requirements.

**Disadvantages:**
- Requires future extension contracts and separate phase investment.

**Risks:**
- Later capability depends on rights/provider validation.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | All formats in initial release | Text only with no extension boundary | Text-first phased delivery |
|---|---|---|---|
| Initial release feasibility | Low | High | High |
| Core product focus | Low | High | High |
| Future extensibility | High | Low to Medium | High |
| Rights isolation | Medium | Medium | High if gated |
| Initial operating burden | High | Low | Low to Medium |

The requirements in Section 3 are the evaluation criteria. Unmeasured latency, quality, throughput, and costs are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Text-first phased delivery with isolated media pipelines.

The initial release should deliver structured text intelligence only. Audio and video should be introduced as separate product phases after report quality, provenance, publication, and rights controls are validated. Media production must consume approved immutable report versions and enforce permissions specific to the transformation and destination. A right to analyze text must not be interpreted as permission to narrate, visualize, quote, or redistribute it.

**Rationale:**
- Protects the initial product from premature multimedia complexity.
- Reuses validated event dossiers and report versions.
- Makes format-specific rights and quality controls explicit.

**Deferred Questions:**
- Audio provider/voice, language coverage, accessibility requirements.
- Video generation and rights for images, footage, and music.
- Media storage, streaming, retention, and distribution targets.
- Quality and cost thresholds for each media phase.

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
- Keeps core product focused.
- Allows future media without binding core report model to one format.
- Makes rights and correction dependencies explicit.

### 8.2 Negative Consequences
- Media capabilities are deliberately delayed.
- Later phases need separate infrastructure and quality work.

### 8.3 Technical Trade-Offs
Phasing reduces initial risk but does not guarantee future media viability. Each phase must demonstrate audience value, rights coverage, quality, accessibility, and acceptable cost.

### 8.4 Operational Consequences
Media workflows require their own queues, storage, provider monitoring, retention, and delivery recovery. Failure must not corrupt the source report.

### 8.5 Product and Business Consequences
Users receive dependable text intelligence first; audio/video remain optional future channels.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Premature scope expansion | Medium | High | Keep media outside initial release acceptance criteria. |
| Unauthorized transformation/distribution | Medium | Critical | Require format-specific permissions and policy checks. |
| Media/report version drift | Medium | High | Bind each artifact to immutable report version. |
| Unknown media economics | High | Medium | Run bounded pilot with measured cost and quality. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- ReportGenerator
- ReportVersionService
- Future MediaProductionWorkflow
- PublicationService
- ReportDelivery

### 9.2 Affected Data Models and Interfaces
- ReportVersion
- Future MediaArtifact
- PublicationRecord
- DeliveryRecord
- ContentRightsProfile

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-013 | Depends on | Controls content transformation, retention, and distribution rights. |
| GENI-ADR-004 | Related to | Publication quality gates also apply to media outputs. |
| GENI-ADR-014 | Related to | Review/correction may be required for generated media. |
| GENI-ADR-017 | Related to | Media production may materially affect model and provider costs. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Keep report content and provenance independent of media formats.
- Define future media artifact lineage and format-specific permission interfaces.
- Add audio only after text quality and rights gates are established.
- Add video only after visual asset rights, quality, and economics are evaluated.
- Propagate corrections/withdrawals to dependent media where policy requires.

### 10.2 Migration or Compatibility Requirements
Inspect the current implementation and data before designing any migration. This ADR does not claim that a migration has been executed. Any transition must preserve provenance and historical state.

### 10.3 Dependencies
- GENI-ADR-013 — Controls content transformation, retention, and distribution rights.
- GENI-ADR-004 — Publication quality gates also apply to media outputs.
- GENI-ADR-014 — Review/correction may be required for generated media.
- GENI-ADR-017 — Media production may materially affect model and provider costs.

### 10.4 Implementation Sequence
1. Verify text release operates without media services.
2. Verify each media artifact references exact report and analysis versions.
3. Verify rights restrictions block media generation or distribution as applicable.
4. Verify report correction identifies dependent media for review/replacement/withdrawal.
5. Evaluate narration fidelity, accessibility, and production cost before launch.

### 10.5 Verification Requirements
- Verify text release operates without media services.
- Verify each media artifact references exact report and analysis versions.
- Verify rights restrictions block media generation or distribution as applicable.
- Verify report correction identifies dependent media for review/replacement/withdrawal.
- Evaluate narration fidelity, accessibility, and production cost before launch.

Implementation verification remains deferred until the ADR is accepted and the capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Initial text product works without audio/video dependencies. | Release scope test |
| AC-02 | Media artifacts retain report-version and provenance lineage. | Persistence tests |
| AC-03 | Media rights are checked separately from text-analysis permission. | Rights-policy tests |
| AC-04 | Corrections and withdrawals identify dependent media artifacts. | Lifecycle tests |
| AC-05 | Each media phase has independent quality and exit criteria. | Stage-gate review |

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
| `docs/01-product-and-system-architecture.md` | Internal | Defines initial text scope and later product releases. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines report and delivery boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines report versions, rights, and artifact lineage. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines phased product capabilities. |
| `GENI-ADR-013` | Internal | Defines rights controls. |

External legal, provider, and measured performance evidence must be added where material during formal review.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |

**End of ADR**
