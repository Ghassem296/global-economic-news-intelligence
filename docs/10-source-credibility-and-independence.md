# GENI-SRC-010 — Source Credibility and Independence Specification

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-SRC-010  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

---

## 1. Purpose

Defines how GENI represents source credibility, relationships, and independence of reports used to assess claims. It operationalizes SourceAssessmentResult and evidence provenance in Documents 02/03 and GENI-ADR-008. It does not introduce a universal source score or treat reputation as claim verification.

## 2. Distinct Concepts

| Concept | Question | Not equivalent to |
|---|---|---|
| Source reliability | Dependability for a defined subject, period, and basis | Truth of a specific claim |
| Source independence | Independent information origin? | Number of articles/domains |
| Source health | Endpoint accessible and behaving? | Editorial credibility |
| Evidence relevance | Does evidence bear on this claim? | Source reputation |
| Claim assessment | What does evidence support/contradict/leave unresolved? | Source score |

Several articles may derive from one original report and count as one origin for corroboration. A reliable source can still be wrong in an individual report.

## 3. Source Identity and Relationships

Source identity represents publisher or identifiable information origin, not merely hostname. Preserve publisher, canonical source, domain/host, author where available, original publication time, acquisition time, and provider identifiers separately.

Typed, time-bounded relationship candidates include OWNED_BY, OPERATED_BY, SAME_EDITORIAL_GROUP, SYNDICATES_TO, SYNDICATED_FROM, REPUBLISHES, ATTRIBUTES_TO, CITES, AFFILIATED_WITH, and UNKNOWN_RELATIONSHIP. Preserve direction, validity interval, supporting evidence, assessment state, provenance, and version. Unknown relationship is not independence evidence.

## 4. Information-Origin Independence

Assess independence for a claim/event context, not globally for two brands. Consider explicit attribution; shared wording, unusual phrase overlap, identical errors and timing; common ownership/editorial control/syndication; original reporting versus summary; shared witnesses/documents/data releases/spokespeople; and whether the origin is identifiable.

Contextual outcomes should distinguish INDEPENDENT_ORIGIN, DEPENDENT_ORIGIN, PARTIALLY_INDEPENDENT, and INDEPENDENCE_UNKNOWN. They are not permanent publisher labels. Article/domain/language count must never directly equal independent confirmation count.

## 5. Reliability Profile

Potential dimensions: accuracy history for a defined subject/claim class; correction/retraction transparency; attribution quality; separation of reporting from opinion/promotional content; editorial accountability and ownership transparency; timeliness where relevant; and documented conflicts/limitations.

Each dimension needs definition, evidence basis, scope, observation period, assessor, and profile version. Missing data is UNKNOWN/not assessed, never zero or implicit negative. No global numeric weighting or probability-like score is approved. Any quantitative scale requires representative historical evidence, calibration, bias analysis, and explicit approval. Reliability never automatically upgrades a claim to verified.

## 6. Source Role and Evidence Aggregation

Source role is claim-dependent. An official institution may be primary for its own policy announcement but not an independent evaluator of consequences. Record role per evidence item (for example PRIMARY_ORIGIN, OFFICIAL_STATEMENT, ORIGINAL_REPORTING, SECONDARY_REPORTING, ANALYSIS_OR_COMMENTARY, DATA_PROVIDER, ROLE_UNKNOWN); roles do not determine truth.

Preserve every Article, ArticleRevision, Evidence record, and original attribution. Link syndicated/repeated reports to shared origins when supported. Do not discard dependent reports; they may add corrections/context. Assess independent origins at claim level and retain rationale. Distinguish corroboration from repetition, quotation, attribution, and shared-source reporting. Preserve contradictions. AI analysis is not an independent source. Missing provenance weakens corroboration but proves neither dependence nor independence.

## 7. Versioning and Provenance

SourceAssessmentResult remains typed and non-authoritative. Preserve source ID, source-metadata fingerprint, profile version, relevant relationship versions, method/version, timestamp, evidence references, and explicit unknowns. Capture exact result or stable fingerprint in ClaimAssessment input provenance. Later profile changes must not rewrite historical assessments; corrections create successor assessments with supersession lineage.

## 8. Review and Calibration

Prioritize high-impact claims, disputed relationships, uncertain origins, and profile changes affecting prior assessments. Reviewers record evidence and scope.

Before numeric scores/thresholds, create a reviewed dataset of syndication chains, shared ownership, primary documents, independent reporting, common-source repetition, and ambiguous cases. Evaluate precision/recall, false-independence and false-dependence rates, and performance by language, region, and source type. Thresholds derive from measured error costs, not intuition.

## 9. Acceptance Criteria

Ready for implementation when source identity/relationship semantics map to the data model; unknown states are explicit; provenance is reproducible; aggregation avoids double-counting dependent reports; and a representative evaluation set exists. Quantitative scoring remains disabled until calibrated and approved.

## 10. Related Documents

Documents 02, 03, and 12; GENI-ADR-008 and GENI-ADR-019.

---

**Document ID:** GENI-SRC-010  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**End of Document**
