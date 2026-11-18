# GENI-ADR-010 — Phased Text, Audio, and Video Delivery

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-010  
**Title:** Phased Text, Audio, and Video Delivery  
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

The product's core value is evidence-based event intelligence and reports. Audio and video may broaden reach, but they introduce new content transformation, media storage, licensing, accessibility, localization, moderation, and distribution concerns. The initial product scope is text-first, and media must not bypass the same review, rights, correction, and publication controls.

This ADR is a proposal for formal review. It does not approve an implementation or override another decision.

## 2. Decision Question

How should text, audio, and video capabilities be sequenced and governed so that media remains a derived presentation of approved report content?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Protect the quality and stability of the core text intelligence workflow.
- Keep reports and analyses as authoritative sources rather than generated media.
- Preserve exact report-version lineage for each media artifact.
- Apply rights, review, correction, and withdrawal rules across all channels.
- Avoid premature media infrastructure and vendor lock-in.

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

### 4.1 A — Build text, audio, and video simultaneously

**Advantages:** Provides multi-channel capability early.

**Disadvantages:** Multiplies production, review, rights, storage, and operational complexity before the core product is validated.

**Risk:** High

### 4.2 B — Text-only permanently

**Advantages:** Keeps scope and operations minimal.

**Disadvantages:** Precludes future channel expansion even if product demand is demonstrated.

**Risk:** Low

### 4.3 C — Phased text-first delivery with downstream channel adapters

**Advantages:** Validates core intelligence first while preserving channel extensibility.

**Disadvantages:** Requires explicit artifact lineage and channel-specific quality controls.

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

Deliver text reports first. Treat audio and video as downstream, versioned presentation artifacts generated only from an eligible, approved report version. Add audio after text quality, publication, rights, and correction workflows are operationally reliable. Add video only after audio generation, media asset provenance, and channel review are validated. Every artifact must reference the exact source report version and generation configuration. A corrected or withdrawn report must trigger an explicit assessment of dependent media artifacts; they must not remain silently presented as current.

### 6.1 Decision Boundaries

- Keep media rendering outside Event Intelligence, Analysis, and ReportGenerator domain responsibilities.
- Define a channel adapter interface that consumes an immutable report version and returns a versioned media artifact.
- Record TTS/voice provider, model, voice, language, script/transcript, asset hashes, generation time, and output format.
- Preserve transcript and caption alignment for accessibility and review.
- Apply source-content rights and derived-output policy before generating media.
- Apply publication and delivery decisions independently for each channel.
- Maintain dependency links from media artifacts to report versions and supersession/withdrawal events.

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

- Keep media rendering outside Event Intelligence, Analysis, and ReportGenerator domain responsibilities.
- Define a channel adapter interface that consumes an immutable report version and returns a versioned media artifact.
- Record TTS/voice provider, model, voice, language, script/transcript, asset hashes, generation time, and output format.
- Preserve transcript and caption alignment for accessibility and review.
- Apply source-content rights and derived-output policy before generating media.
- Apply publication and delivery decisions independently for each channel.
- Maintain dependency links from media artifacts to report versions and supersession/withdrawal events.

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

- Keep media rendering outside Event Intelligence, Analysis, and ReportGenerator domain responsibilities.
- Define a channel adapter interface that consumes an immutable report version and returns a versioned media artifact.
- Record TTS/voice provider, model, voice, language, script/transcript, asset hashes, generation time, and output format.
- Preserve transcript and caption alignment for accessibility and review.
- Apply source-content rights and derived-output policy before generating media.
- Apply publication and delivery decisions independently for each channel.
- Maintain dependency links from media artifacts to report versions and supersession/withdrawal events.

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

- Initial release acceptance does not require audio or video.
- A media artifact references one exact report version and generation configuration.
- A corrected report causes dependent media to be marked for review, replacement, or withdrawal according to policy.
- Media publication cannot bypass report publication and content-rights requirements.
- Transcript/caption content can be inspected and reviewed before release where policy requires.
- Failure in a media adapter does not corrupt or block the core text report workflow.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification |
|---|---|---|
| AC-01 | Initial release acceptance does not require audio or video. | Architecture review and automated tests where applicable |
| AC-02 | A media artifact references one exact report version and generation configuration. | Architecture review and automated tests where applicable |
| AC-03 | A corrected report causes dependent media to be marked for review, replacement, or withdrawal according to policy. | Architecture review and automated tests where applicable |
| AC-04 | Media publication cannot bypass report publication and content-rights requirements. | Architecture review and automated tests where applicable |
| AC-05 | Transcript/caption content can be inspected and reviewed before release where policy requires. | Architecture review and automated tests where applicable |
| AC-06 | Failure in a media adapter does not corrupt or block the core text report workflow. | Architecture review and automated tests where applicable |

Quantitative quality and cost thresholds must be established through representative evaluation, not invented in this ADR.

## 12. Review and Reconsideration

### 12.1 Review Triggers

- Text reporting and review workflows meet their approved quality requirements.
- A documented product requirement justifies an audio or video channel.
- Rights or platform rules change for media content.
- Media generation cost or quality changes materially.

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
