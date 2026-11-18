# GENI-ADR-019 — Event Importance, Economic Relevance, and Economic Impact Assessment Methodology

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-019  
**Title:** Event Importance, Economic Relevance, and Economic Impact Assessment Methodology  
**Status:** Proposed  
**Version:** 1.0  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

The product must decide which events deserve attention, how economically connected they are, and what consequences they may have. These are different analytical questions. A single score can conflate editorial significance, economic transmission, and effect magnitude. Market reactions are measurements, not automatic proof of causality. Missing information must not be converted to zero or neutral impact. The architecture represents these outputs as separate versioned Analysis types, but methodology boundaries and evaluation rules require a formal decision.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

How should event importance, economic relevance, and economic impact be assessed independently while preserving evidence, uncertainty, methodology versions, and comparability limits?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Define separate constructs and output schemas for Event Importance, Economic Relevance, and Economic Impact.
- Store each as a distinct immutable, versioned Analysis result.
- Importance expresses overall significance/attention priority, not impact magnitude.
- Economic relevance describes the nature/strength of connection and plausible transmission pathways, not realized effect.
- Economic impact is channel-based and records direction, magnitude/range where supported, affected entities, horizon, evidence status, and uncertainty.
- Keep assessment confidence, forecast probability, effect magnitude, and importance distinct.
- Preserve unknown, unavailable, not-established, not-applicable, and conflicting evidence states.
- Define numeric scales and calibration only when independently specified and evaluated.
- Keep observed market reaction separate from event-causality attribution.

### 3.2 Technical Constraints
- The distinctions are reflected in docs 01-03, but this ADR remains Proposed until approved.
- No numeric range, threshold, weight, or global composite formula is approved.
- Market observation/provider semantics are addressed by ADR-015.
- Evidence provenance and uncertainty are addressed by ADR-008.

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

### 4.1 Alternative A — One composite event score

**Description:** Combine importance, relevance, and impact into a single weighted number.

**Advantages:**
- Simple ranking and presentation.

**Disadvantages:**
- Destroys construct distinctions and hides missingness/uncertainty.

**Risks:**
- Events may rank highly for the wrong reason
- weights are arbitrary.

**Estimated Complexity:** Low initially; high analytical risk

### 4.2 Alternative B — Two partially combined assessments

**Description:** Keep importance separate but combine relevance and impact.

**Advantages:**
- Some distinction retained
- fewer outputs.

**Disadvantages:**
- A plausible pathway is confused with consequence magnitude or certainty.

**Risks:**
- High relevance may be read as high impact.

**Estimated Complexity:** Medium

### 4.3 Alternative C — Three independent versioned assessments

**Description:** Use distinct schemas and methodologies, with any downstream prioritization separately governed.

**Advantages:**
- Preserves meaning and provenance
- supports independent evaluation.

**Disadvantages:**
- More complex reporting and evaluation.

**Risks:**
- Users may request composite scores before calibration exists.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | One composite event score | Two partially combined assessments | Three independent versioned assessments |
|---|---|---|---|
| Semantic clarity | Low | Medium | High |
| Uncertainty representation | Low | Medium | High |
| Independent evaluation | Low | Medium | High |
| Simple ranking | High | Medium | Requires separate policy |
| Risk of false economic/causal inference | High | Medium | Lower when enforced |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Three independent versioned assessments, with downstream prioritization treated as a separate policy.

Represent Event Importance, Economic Relevance, and Economic Impact as distinct immutable Analysis outputs with separate analysis types, schemas, methodology versions, and evaluation datasets. Importance describes overall significance and monitoring/editorial priority. Economic relevance describes direct, indirect, or contextual links and plausible transmission pathways. Economic impact describes realized or potential effects by channel, direction, magnitude/range where supported, affected entities, time horizon, evidence status, and uncertainty. Numeric values are optional and must not be introduced until construct, scale, direction, calibration, and validation are defined. Any cross-assessment ranking or composite is a separate decision.

**Rationale:**
- Prevents conflating significance, economic connection, and consequences.
- Makes unknown and insufficient evidence explicit.
- Supports independent evaluation and methodology change.

**Deferred Questions:**
- Exact dimensions and rubrics for each assessment.
- Whether numeric scores are required.
- Calibration and reference datasets.
- Downstream prioritization/ranking policy.
- How assessment outputs affect publication gates, if at all.

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
- Clear analytical semantics.
- Independent evaluation and controlled evolution.
- Better disclosure of evidence gaps and causal uncertainty.

### 8.2 Negative Consequences
- More complex assessment schemas and reporting.
- No immediate single-score ranking without a separate policy.

### 8.3 Technical Trade-Offs
Prioritize validity and traceability over a simplistic universal score. Any aggregate ranking must preserve inputs and rationale and demonstrate that it does not erase differences across channels or evidence states.

### 8.4 Operational Consequences
Track version adoption, unknown rates, inter-reviewer agreement, calibration, and regression by event class and language. Preserve historical results immutably.

### 8.5 Product and Business Consequences
Reports explain why an event matters, how it relates to the economy, and which consequences are supported, instead of compressing all three into an ambiguous score.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Construct conflation reappears | Medium | High | Use distinct types and labels; cross-document consistency tests. |
| Arbitrary numeric scales | Medium | High | Require construct definition and calibration before numeric deployment. |
| Missing data treated as zero | Medium | High | Use explicit unknown states and null semantics. |
| Model confidence misread as probability | Medium | High | Separate schema fields and explanatory policy. |
| Market movement misread as causal impact | Medium | Critical | Require separate causal assessment and uncertainty. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- ImportanceRanker
- EconomicRelevanceAssessor
- ImpactAnalyzer
- EvidenceAnalyzer
- ReportGenerator
- Evaluation pipeline

### 9.2 Affected Data Models and Interfaces
- Analysis types IMPORTANCE_ASSESSMENT, ECONOMIC_RELEVANCE_ASSESSMENT, ECONOMIC_IMPACT_ASSESSMENT
- Analysis schema/methodology versions
- Evidence and AnalysisInput relationships
- MarketObservation for observed reactions

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md
- docs/adr/README.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-008 | Depends on / Related to | Defines evidence provenance, confidence, and uncertainty distinctions. |
| GENI-ADR-015 | Related to | Defines market observations and reaction measurement. |
| GENI-ADR-001 | Related to | Establishes event-centric aggregation. |
| GENI-ADR-003 | Related to | Defines the economic intelligence editorial focus. |
| GENI-ADR-017 | Related to | Defines LLM evaluation and usage telemetry. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define a construct statement and structured schema for each assessment.
- Record methodology, policy, schema, model, and prompt versions independently.
- Create reference datasets where importance, relevance, and impact diverge.
- Define unknown, not-established, contradictory, and not-applicable states.
- Evaluate each assessment independently and inspect subgroup performance.
- Treat composite ranking as a separate policy with approval and evaluation gates.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-008 — Defines evidence provenance, confidence, and uncertainty distinctions.
- GENI-ADR-015 — Defines market observations and reaction measurement.
- GENI-ADR-001 — Establishes event-centric aggregation.
- GENI-ADR-003 — Defines the economic intelligence editorial focus.
- GENI-ADR-017 — Defines LLM evaluation and usage telemetry.

### 10.4 Implementation Sequence
1. Approve the distinct construct definitions.
2. Define initial schemas and unknown states.
3. Build reviewed datasets for each assessment.
4. Implement independent assessment workflows and persistence.
5. Evaluate by event class, language, and evidence state.
6. Specify composite prioritization only if a demonstrated requirement remains.

### 10.5 Verification Requirements
- Test a high-importance but economically unrelated event.
- Test a highly relevant event with unknown impact.
- Test an event with mixed effects across sectors or horizons.
- Verify model confidence is not reported as forecast probability.
- Verify market movement does not prove causality.
- Verify methodology changes create new Analysis versions.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Three constructs and schemas are independently defined. | Architecture/schema review |
| AC-02 | Analysis records preserve methodology/schema versions and evidence references. | Persistence tests |
| AC-03 | Unknown/not-established are distinct from zero, neutral, and low values. | Contract tests |
| AC-04 | Impact supports multiple channel-level results without forced aggregation. | Domain tests |
| AC-05 | Confidence, forecast probability, magnitude, and importance remain distinct. | Schema/evaluation tests |
| AC-06 | Each assessment has a reviewed evaluation dataset. | Evaluation report |
| AC-07 | Any composite prioritization is separately specified and approved. | Architecture review |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Evaluation identifies systematic construct confusion or calibration failure.
- Product requires an aggregate ranking or new assessment dimensions.
- Market-data or evidence methodology changes materially.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Defines three assessment questions and analysis flow. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines separate assessment components. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines separate Analysis types and score/confidence semantics. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines economic analysis and evaluation. |
| `GENI-ADR-008` | Internal | Evidence provenance and uncertainty. |
| `GENI-ADR-015` | Internal | Market data and observed reactions. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |

**End of ADR**
