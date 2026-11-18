# GENI-ADR-008 — Evidence Provenance and Uncertainty Representation

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-008  
**Title:** Evidence Provenance and Uncertainty Representation  
**Status:** Proposed  
**Version:** 1.2
**Date:** 2026-11-18
**Decision Owner:** Product Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence is designed to produce evidence-based economic intelligence from multiple international news sources, official publications, market observations, and other relevant information.

The system must extract claims, assess supporting information, identify contradictions, and generate analytical conclusions without confusing reported statements with independently established facts.

A single economic development may produce many different types of information:

- An official institution publishes a policy announcement.
- A news organization reports the announcement.
- Other publishers reproduce or summarize the same report.
- An analyst interprets the implications.
- Market data records a subsequent price movement.
- Another source publishes a conflicting account.
- Later information corrects an earlier statement.

These records do not have equivalent evidential value.

For example, ten articles repeating the same original report do not necessarily constitute ten independent confirmations.

Similarly:

- A source reporting that a central bank made a decision is not identical to the underlying official decision.
- A market price movement is an observed market fact, but its cause may remain uncertain.
- An analyst's interpretation is not the same as a directly observed fact.
- An AI-generated summary is not an independent source of evidence.
- A source's historical reliability does not guarantee that every statement it publishes is correct.

Without explicit provenance and uncertainty rules, the system may:

- Treat repeated reporting as independent corroboration.
- Confuse a source claim with a verified fact.
- Lose the original source behind syndicated content.
- Present conflicting evidence as if it did not exist.
- Assign unjustified confidence to incomplete information.
- Treat source reputation as proof of individual claims.
- Generate analytical conclusions that cannot be traced to supporting evidence.
- Fail to preserve corrections and changes in evidential status.
- Present uncertain economic causality as established fact.

The system therefore requires a consistent model for representing the origin, context, relationships, and assessment of evidence.

It must also represent uncertainty explicitly rather than reducing every evidential question to a single confidence score.

This ADR proposes the foundational architecture for evidence provenance, claim assessment, source independence, uncertainty representation, and analytical traceability.

## 2. Decision Question

How should Global Economic News Intelligence represent and evaluate information so that every important claim, evidence item, assessment, and analytical conclusion remains traceable to its origin and evidential status?

Specifically:

1. How should source claims be distinguished from evidence and verified facts?
2. How should evidence provenance be preserved across acquisition, extraction, analysis, and reporting?
3. How should independent corroboration be distinguished from syndicated or derivative reporting?
4. How should supporting, contradicting, qualifying, and inconclusive evidence be represented?
5. How should uncertainty be expressed without creating misleading confidence?
6. How should source reliability and claim-level assessment remain separate?
7. How should LLM-generated outputs reference evidence without becoming evidence themselves?
8. How should corrections, retractions, and changing evidence affect previous assessments and reports?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Every source claim must retain its source provenance.
- Every evidence item must have an identifiable origin or explicitly recorded origin limitation.
- Claims must be independently assessable.
- Evidence must support, contradict, qualify, or otherwise relate to claims through explicit relationships.
- The system must distinguish direct evidence from secondary reporting and analytical interpretation.
- The system must support multiple evidence items for one claim.
- The system must support evidence that relates to multiple claims.
- The system must preserve conflicting evidence.
- The system must represent insufficient or unavailable evidence.
- The system must distinguish source attribution from claim verification.
- The system must support evidence corrections, withdrawals, and supersession.
- Analytical conclusions must retain references to their supporting inputs.
- Reports must preserve references to relevant claims, evidence, and assessments.
- Historical assessments must remain traceable after new evidence arrives.
- The system must distinguish independent corroboration from repeated reporting.
- Evidence must be associated with relevant articles, events, sources, and observations where applicable.

### 3.2 Technical Constraints

- Provenance must be represented through explicit domain relationships.
- Core provenance information must not exist only in unstructured LLM-generated text.
- Evidence and assessment records must support versioning.
- The design must not depend on a particular LLM provider.
- The design must support structured outputs and schema validation.
- Evidence relationships must be queryable.
- Important provenance fields must be persistable using relational storage.
- Flexible metadata may use versioned JSON structures.
- Evidence references must remain stable when source content is reprocessed.
- The system must support multilingual evidence and source attribution.
- The system must distinguish missing information from negative evidence.
- Assessment methodology and version must be recorded.
- Historical report inputs must remain identifiable.

### 3.3 Business and Product Constraints

- The product must prioritize factual accuracy and transparent uncertainty.
- Economic intelligence must not present speculation as confirmed fact.
- Reports must distinguish reported developments from independently supported conclusions.
- Conflicting accounts must remain visible when materially relevant.
- The system must avoid exaggerating certainty merely to produce a complete narrative.
- Evidence quality must take precedence over the number of supporting articles.
- Important economic conclusions must be explainable to reviewers and readers.

### 3.4 Security and Privacy Constraints

- Retrieved source content must be treated as untrusted data.
- Article content must not be interpreted as instructions to LLM components.
- LLM-generated evidence references must be validated against persisted source records.
- Evidence extraction must not create unauthorized access to external systems.
- Sensitive information must not be unnecessarily reproduced in analytical outputs.
- Logs must not expose restricted source content or credentials.
- Access to original source material must respect applicable legal and contractual restrictions.

### 3.5 Operational and Cost Constraints

- Evidence extraction should be incremental.
- Reprocessing must not silently overwrite previous assessments.
- Evidence assessment must be observable and auditable.
- Expensive LLM calls should be bounded by budgets and deadlines.
- The system must support review of important unsupported or disputed claims.
- The initial implementation should avoid unnecessary specialized infrastructure.
- Evidence references must be sufficient to reconstruct the basis of a report without retaining prohibited source content.

### 3.6 Legal and Content-Rights Constraints

- Technical access to source content does not imply permission to store or republish it.
- Full-text retention must follow applicable licensing and source restrictions.
- Evidence spans and quotations must respect permitted use.
- The system should retain source URLs, identifiers, timestamps, and other permissible provenance metadata.
- Where full text cannot be retained, evidence must reference an authorized source location or a permitted derived representation.
- Deletion and withdrawal obligations must be respected.
- Derived analytical records must not be used to circumvent content restrictions.

### 3.7 Explicit Non-Goals

This ADR does not finalize:

- A universal numerical source reliability score.
- A universal numerical claim confidence threshold.
- A complete fact-checking methodology.
- The detailed LLM prompt or extraction strategy.
- The final evidence taxonomy for every economic domain.
- A legal determination of permissible quotation or retention.
- The complete report publication and review policy.
- The initial database technology.
- The exact market-data verification methodology.

These concerns require separate specifications, evaluation, or ADRs.

## 4. Alternatives Considered

### 4.1 Alternative A: Store Source Text and Generate Narrative Summaries

**Description:**

Retain available articles and generate summaries or analytical narratives using LLMs. Source references may be attached to the final summary, but individual claims and evidence relationships are not represented as structured domain records.

**Advantages:**

- Simple initial implementation.
- Low data-model complexity.
- Fast generation of readable summaries.
- Minimal explicit evidence-management infrastructure.

**Disadvantages:**

- Individual claims cannot be reliably traced to their supporting passages.
- Contradictory evidence is difficult to represent.
- Source attribution may become ambiguous.
- Repeated or syndicated reporting may be mistaken for corroboration.
- Historical evidence changes are difficult to reconstruct.
- Reviewers cannot reliably inspect the basis of important conclusions.

**Risks:**

- Unsupported statements in published reports.
- Hallucinated or incorrectly attributed information.
- Misleading certainty.
- Loss of evidential traceability.

**Estimated Complexity:** Low initially; High for reliable intelligence operations.

### 4.2 Alternative B: Attach Source References to Claims Without Explicit Evidence Relationships

**Description:**

Represent claims as structured records and attach article or source references to each claim. Do not separately model evidence items, evidence locations, or the relationship between evidence and claims.

**Advantages:**

- Better attribution than narrative-only summaries.
- Relatively simple data model.
- Supports basic claim-to-article traceability.
- Easier initial implementation than a complete evidence model.

**Disadvantages:**

- Cannot reliably identify the exact supporting or contradicting material.
- Does not adequately represent evidence spans.
- Cannot distinguish different evidence types.
- Makes conflicting evidence difficult to assess.
- Provides limited support for claim-level verification.
- Makes it difficult to explain why a source reference supports a particular conclusion.

**Risks:**

- Source attribution may be mistaken for evidential support.
- Reviewers may assume that every cited article supports the entire claim.
- Unsupported or weakly supported conclusions may pass unnoticed.

**Estimated Complexity:** Medium.

### 4.3 Alternative C: Structured Evidence Provenance and Versioned Claim Assessment

**Description:**

Represent claims, evidence items, evidence origins, evidence locations, claim-evidence relationships, source assessments, and claim assessments as separate domain concepts.

Every important claim retains references to its originating sources and relevant evidence.

Assessments are versioned and distinguish supporting, contradicting, qualifying, and insufficient evidence.

Source independence is evaluated separately from article count.

Analytical outputs retain references to their inputs and evidence.

**Advantages:**

- Strong claim-level traceability.
- Explicit distinction between source statements and evidence.
- Supports conflicting and incomplete evidence.
- Preserves corrections and historical assessments.
- Supports independent-source analysis.
- Enables explainable reporting and human review.
- Reduces the risk of unsupported conclusions.

**Disadvantages:**

- More complex domain model.
- Additional processing and persistence operations.
- Requires evidence taxonomy and assessment policies.
- May increase LLM and review costs.
- Requires explicit handling of unavailable source content.

**Risks:**

- Poor evidence classification can create misleading assessments.
- Incorrect source relationship classification can exaggerate corroboration.
- Inconsistent assessment policies may produce incomparable results.

**Estimated Complexity:** High.

### 4.4 Alternative D: Fully Human-Verified Evidence Before Any Analytical Use

**Description:**

Require a human reviewer to validate every evidence item and claim before it can be used in analytical processing.

**Advantages:**

- Human control over evidence acceptance.
- Potentially stronger review of critical claims.
- Explicit accountability for evidence decisions.

**Disadvantages:**

- High operational cost.
- Significant processing delays.
- Difficult to scale across international sources.
- Human reviewers may also make inconsistent judgments.
- Unsuitable for every low-risk or routine information item.

**Risks:**

- Review backlogs.
- Delayed intelligence delivery.
- Excessive dependence on manual operations.

**Estimated Complexity:** High operationally.

## 5. Evaluation and Comparison

| Evaluation Criterion | Alternative A | Alternative B | Alternative C | Alternative D |
|---|---|---|---|---|
| Claim Traceability | Low | Medium | High | High |
| Evidence-Level Provenance | Low | Low | High | High |
| Contradiction Handling | Low | Low | High | High |
| Source Independence | Low | Limited | High | High |
| Historical Assessment | Low | Limited | High | Medium to High |
| Automation Suitability | High | High | High | Low |
| Initial Complexity | Low | Medium | High | High |
| Operational Cost | Low initially | Medium | Medium to High | High |
| Explainability | Low | Medium | High | High |
| Support for Uncertainty | Low | Limited | High | High |

### 5.1 Evaluation Priorities

The most important criteria are:

1. Traceability from report statements to claims and evidence.
2. Preservation of source provenance.
3. Correct treatment of independent corroboration.
4. Explicit handling of contradictory information.
5. Separation of evidence assessment from AI-generated analysis.
6. Historical reproducibility of important assessments.
7. Suitability for automated processing with selective human review.

Narrative-only approaches are insufficient for the intended product.

A source reference attached to a claim is useful but does not fully explain which information supports or contradicts that claim.

A structured evidence model provides the necessary foundation for reliable intelligence.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Structured Evidence Provenance and Versioned Claim Assessment.

The system should use a structured evidence model in which claims, evidence, provenance, relationships, and assessments are represented separately.

### 6.1 Core Domain Distinctions

The following concepts must remain separate.

#### 6.1.1 Source

A Source represents the publisher, institution, data provider, or other origin from which information is acquired.

Examples:

- A central bank.
- A government department.
- A news publisher.
- An international organization.
- A market-data provider.

A Source may publish multiple articles or datasets.

Source identity does not automatically establish the independence of every publication attributed to it.

#### 6.1.2 Article

An Article represents a published information item.

It retains:

- Source identity.
- Publication metadata.
- Original URL or source reference.
- Language.
- Publication timestamp where available.
- Acquisition metadata.
- Content availability.
- Revision information where applicable.

An article may contain multiple claims and evidence items.

An article is not itself equivalent to a verified fact.

#### 6.1.3 Source Claim

A Source Claim represents a statement attributed to a source.

Examples:

- A central bank states that its policy rate will remain unchanged.
- A government announces a proposed fiscal package.
- A company reports a decline in quarterly revenue.
- A news publisher reports that a particular agreement has been reached.

A source claim must preserve its attribution.

The system must not silently transform an attributed statement into an independently verified fact.

#### 6.1.4 Evidence

Evidence represents information relevant to evaluating a claim.

Evidence may support, contradict, qualify, or provide context for a claim.

Examples:

- An official policy document.
- A statistical release.
- A direct quotation from an authorized institution.
- A documented transaction record.
- A market observation.
- A relevant article passage.
- An independently obtained dataset.
- A subsequent official correction.

Evidence must have an identifiable origin or an explicit provenance limitation.

#### 6.1.5 Evidence Location

An Evidence Location identifies where the relevant information can be found.

Examples:

- Article paragraph.
- Page number.
- Document section.
- Table and row.
- Timestamp in an audio or video source.
- External source URL and anchor.
- Structured dataset record.

The system should preserve the most precise permitted location available.

An evidence location must not imply that the full underlying content has been legally retained.

#### 6.1.6 Claim Assessment

A Claim Assessment represents an evaluation of the available evidence concerning a claim.

It must be separate from the original claim and its source.

An assessment should record:

- Assessment outcome.
- Supporting evidence references.
- Contradicting evidence references.
- Qualifying evidence references.
- Unresolved questions.
- Assessment methodology.
- Assessment version.
- Relevant timestamps.
- Reviewer or processing actor.
- Assessment limitations.

An assessment is a time-specific evaluation of available information, not an immutable declaration of truth.

#### 6.1.7 AI Analysis

AI Analysis represents an interpretation generated from claims, evidence, assessments, and other relevant inputs.

Examples include:

- Possible economic implications.
- Cross-source interpretation.
- Scenario analysis.
- Causal hypotheses.
- Forecasts.
- Risk assessments.

AI Analysis must not be treated as independent evidence.

An analytical statement must retain references to the claims and evidence on which it depends.

### 6.2 Provenance Chain

The system should preserve the following logical provenance chain:

1. Source.
2. Published article, official document, or structured observation.
3. Extracted source claim or evidence item.
4. Evidence location and relevant source context.
5. Claim-evidence relationship.
6. Claim assessment.
7. Analytical input and conclusion.
8. Report statement and published report version.

Each step must retain sufficient references to reconstruct the relevant information path.

The chain must not depend exclusively on generated narrative text.

### 6.3 Evidence Relationship Types

Evidence-to-claim relationships should use explicit types.

Proposed types:

| Relationship Type | Meaning |
|---|---|
| `SUPPORTS` | The evidence provides support for the claim. |
| `CONTRADICTS` | The evidence conflicts with the claim. |
| `QUALIFIES` | The evidence limits, narrows, or adds conditions to the claim. |
| `CONTEXTUALIZES` | The evidence provides relevant context without directly proving or disproving the claim. |
| `DERIVED_FROM` | The evidence or assertion is derived from another identifiable information item. |
| `NEUTRAL` | The evidence has been examined but does not materially support or contradict the claim. |
| `UNASSESSED` | The relationship has not yet been evaluated. |

A relationship must not be assigned merely because an article contains similar words.

The relationship must reflect the actual evidential relevance of the information.

### 6.4 Evidence Types

The initial evidence taxonomy should distinguish at least:

| Evidence Type | Description |
|---|---|
| `OFFICIAL_STATEMENT` | Statement issued by an authorized institution or representative. |
| `OFFICIAL_DOCUMENT` | Formal publication, regulation, decision, or institutional document. |
| `STATISTICAL_RELEASE` | Published statistical or economic data. |
| `PRIMARY_REPORTING` | Reporting based on direct access, observation, or clearly identified original reporting. |
| `SECONDARY_REPORTING` | Reporting based on another publication or an intermediary source. |
| `DIRECT_OBSERVATION` | A directly recorded observation or measurement. |
| `MARKET_OBSERVATION` | Observed market prices, yields, volumes, or other market data. |
| `EXPERT_INTERPRETATION` | Interpretation attributed to an identifiable expert. |
| `DOCUMENTARY_RECORD` | A verifiable record or document relevant to the claim. |
| `DERIVED_DATA` | Information calculated from identifiable underlying data. |
| `AI_GENERATED` | An AI-generated statement or extraction, not independent evidence. |
| `OTHER` | A documented evidence category not covered above. |

This taxonomy is a starting point. Additional domain-specific types may be introduced.

The evidence type must describe the nature of the information, not automatically assign its reliability.

### 6.5 Source Independence and Syndication

The system must distinguish source count from independent corroboration.

Multiple articles may originate from:

- The same original report.
- A news agency dispatch.
- A syndicated publication.
- A shared press release.
- A common official statement.
- A common dataset.
- Independent reporting by different publishers.

The number of articles alone must never be used as a measure of independent confirmation.

The system should maintain source relationship information where available.

Proposed source relationship types include:

- `ORIGINAL_REPORTING`
- `SYNDICATED_FROM`
- `REPRINTED_FROM`
- `DERIVED_FROM`
- `QUOTES`
- `SUMMARIZES`
- `CITES`
- `USES_COMMON_PRIMARY_SOURCE`
- `UNKNOWN_RELATIONSHIP`

When several publications derive their information from one original report, the system should preserve the shared origin.

A source relationship may be uncertain. The system must not invent an origin relationship merely because two articles use similar wording.

Where independence cannot be established, the system must record the limitation.

Independent corroboration requires evidence that the supporting information has sufficiently independent origins, not simply different publisher names.

### 6.6 Source Reliability Versus Claim Assessment

Source reliability and claim assessment must remain separate.

**Source Reliability** concerns the historical or contextual reliability of a source.

It may consider:

- Editorial standards.
- Correction practices.
- Transparency.
- Direct access to primary information.
- Historical accuracy.
- Subject-matter expertise.
- Known source limitations.

**Claim Assessment** concerns the evidential support for one particular claim.

A historically reliable source can publish an incorrect statement.

A source with limited historical reliability can occasionally provide accurate information supported by strong evidence.

Therefore:

- Source reliability must not automatically determine claim truth.
- Claim assessment must not automatically modify source reliability.
- Source reliability must be contextual and versioned where appropriate.
- A source-level score must not be interpreted as a probability that a particular claim is true.

### 6.7 Claim Assessment Outcomes

The system should use explicit assessment outcomes.

Proposed values:

| Outcome | Meaning |
|---|---|
| `SUPPORTED` | Available evidence provides sufficient support under the applicable assessment policy. |
| `PARTIALLY_SUPPORTED` | Some parts of the claim are supported, but others remain uncertain or unsupported. |
| `CONTRADICTED` | Available evidence materially conflicts with the claim. |
| `MIXED` | Material supporting and contradicting evidence both exist. |
| `UNVERIFIED` | The available evidence is insufficient to establish the claim. |
| `INCONCLUSIVE` | The available evidence has been examined but does not permit a reliable conclusion. |
| `SUPERSEDED` | A newer assessment or corrected claim has replaced this assessment for current use. |
| `WITHDRAWN` | The claim or assessment has been withdrawn under an explicit correction or review process. |

The outcome must be interpreted in context.

`SUPPORTED` does not mean absolute certainty.

`UNVERIFIED` does not mean false.

`CONTRADICTED` must identify the relevant conflicting evidence.

`MIXED` must preserve the distinction between the different supporting and contradicting items.

### 6.8 Uncertainty Representation

Uncertainty must not be reduced to one universal confidence score.

The system should distinguish several dimensions.

#### 6.8.1 Factual Uncertainty

How strongly is the underlying claim supported by available evidence?

#### 6.8.2 Source Uncertainty

How much is known about the origin, independence, and reliability of the information?

#### 6.8.3 Temporal Uncertainty

How precise are the relevant event time, observation time, publication time, or validity period?

#### 6.8.4 Attribution Uncertainty

How certain is the identification of the person, institution, or entity responsible for the statement or action?

#### 6.8.5 Measurement Uncertainty

How precise or reliable is the underlying numerical measurement or dataset?

#### 6.8.6 Causal Uncertainty

How strongly is a proposed cause-and-effect relationship supported?

A market movement observed after a policy announcement does not by itself establish that the announcement caused the movement.

#### 6.8.7 Analytical Uncertainty

How sensitive is an analytical conclusion to assumptions, incomplete information, or alternative interpretations?

These dimensions should be represented only where relevant.

Unknown uncertainty dimensions must remain unknown rather than being assigned artificial values.

### 6.9 Confidence and Probability Policy

The system may use confidence values for specific tasks, but each value must have documented semantics.

For every confidence measure, define:

- What is being assessed.
- The valid scale.
- Whether higher values indicate stronger confidence.
- The assessment method.
- The relevant model or policy version.
- Whether the value is calibrated.
- Whether it represents a probability or a heuristic score.
- The conditions under which values may be compared.

A heuristic score must not be described as a probability.

A model-generated confidence value must not automatically be treated as calibrated statistical confidence.

Where calibration has not been demonstrated, the system should prefer categorical outcomes and explicit uncertainty descriptions.

### 6.10 Evidence Quality and Relevance

Evidence quality and claim relevance are different concepts.

Evidence quality may consider:

- Directness.
- Source transparency.
- Originality.
- Independence.
- Temporal relevance.
- Methodological quality.
- Completeness.
- Known limitations.

Claim relevance concerns how directly the evidence relates to the specific claim.

A high-quality source may provide evidence that is only indirectly relevant to a particular claim.

A directly relevant source may still contain uncertain or disputed information.

The system should preserve these dimensions separately where the assessment process supports them.

### 6.11 Conflicting Evidence

The system must preserve material contradictions rather than silently selecting one source.

When evidence conflicts, the assessment should consider:

- Whether the sources refer to the same time period.
- Whether the claims use the same definitions.
- Whether the measurements use comparable methodologies.
- Whether the sources have independent origins.
- Whether one source has corrected or superseded an earlier statement.
- Whether the apparent contradiction can be explained by scope or timing differences.
- Whether the available information remains insufficient.

Conflicting evidence may result in a `MIXED` or `INCONCLUSIVE` assessment.

The system must not automatically resolve contradictions by selecting the source with the highest general reliability score.

### 6.12 Temporal Validity and Corrections

Evidence and assessments must preserve relevant time information.

Where applicable, distinguish:

- `published_at`: When a source published the information.
- `observed_at`: When the underlying observation occurred.
- `collected_at`: When the system acquired it.
- `valid_from`: When the represented information became applicable.
- `valid_until`: When the information ceased to apply, if known.
- `assessed_at`: When the assessment was performed.

A correction or retraction must create a traceable change.

Previous evidence and assessments must not be silently overwritten.

The system should distinguish:

- Corrected information.
- Retracted information.
- Superseded information.
- Disputed information.
- Information that has become outdated.
- Information whose validity period has ended.

A historical report must remain traceable to the information available when it was generated.

### 6.13 LLM and AI Output Restrictions

LLMs may assist with:

- Claim extraction.
- Evidence extraction.
- Evidence classification.
- Source relationship candidate generation.
- Claim-evidence relevance assessment.
- Contradiction detection.
- Uncertainty identification.
- Structured analytical synthesis.

However:

- LLM output is not an independent source of evidence.
- An LLM must not create fabricated source references.
- Every generated evidence reference must resolve to an existing source record or explicitly identified external reference.
- Extracted quotations must be validated against available source material.
- Structured outputs must pass schema and business-rule validation.
- Source content must be treated as untrusted input.
- LLM output must not directly modify authoritative assessment or publication state without the required validation and workflow controls.
- An analytical conclusion must not be presented as verified merely because an LLM generated it.

The system must preserve model, prompt, schema, and processing version metadata where relevant.

### 6.14 Evidence and Report Traceability

Important report statements should be traceable to:

- Their analytical input.
- Relevant claims.
- Supporting or contradicting evidence.
- Original source records.
- Relevant evidence locations where available.
- Claim assessment versions.
- Analysis methodology and version.

Reports should distinguish:

- Established or sufficiently supported information.
- Attributed statements.
- Unverified claims.
- Analytical interpretations.
- Forecasts and scenarios.
- Material uncertainties.

The report must not imply that all statements have equal evidential strength.

The absence of evidence must not be represented as evidence that an event or claim did not occur.

### 6.15 Recommendation Summary

The recommended architecture treats evidence provenance and uncertainty as first-class domain responsibilities.

The central rule is:

**Every important claim must be distinguishable from the evidence supporting it, and every assessment must preserve the origin, limitations, and uncertainty of that evidence.**

## 7. Final Decision

This ADR is currently **Proposed**.

**Selected Alternative:** Not yet formally selected.

**Decision Status:** Proposed

**Decision Owner:** Product Owner

**Approved By:** Not yet approved

**Approval Date:** N/A

**Decision Rationale:**

Alternative C is recommended because it provides structured, auditable provenance and allows the system to represent supporting, contradicting, incomplete, and uncertain information explicitly.

It separates source attribution, evidence relationships, claim assessment, and AI analysis.

This separation is necessary for reliable economic intelligence and transparent reporting.

The Product Owner must explicitly accept or reject this recommendation.

**Conditions or Restrictions:**

- LLM-generated output must not be treated as independent evidence.
- Repeated reporting must not automatically count as independent corroboration.
- Source reliability must remain separate from claim assessment.
- Missing information must not be converted into a negative finding.
- Uncalibrated scores must not be described as probabilities.
- Historical evidence and assessment records must remain traceable.
- The implementation must comply with content access and retention restrictions.

**Deferred Questions:**

- Detailed source reliability methodology.
- Final evidence taxonomy.
- Claim assessment calibration.
- Automated contradiction resolution policy.
- Domain-specific verification rules for economic data.
- Detailed retention periods for evidence content.
- Final review and escalation thresholds.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Improved traceability from reports to original sources.
- Explicit separation of claims, evidence, and analysis.
- Better handling of conflicting information.
- Reduced risk of false corroboration.
- More transparent uncertainty representation.
- Support for evidence-based human review.
- Historical reconstruction of important assessments.
- Better evaluation of analytical quality.
- Reduced dependence on narrative-only LLM output.

### 8.2 Negative Consequences

- More complex domain and persistence models.
- Additional extraction and assessment operations.
- Increased storage and processing requirements.
- More sophisticated provenance queries.
- Additional evaluation and testing requirements.
- Potentially slower report generation for claims requiring deeper assessment.
- Increased operational effort for corrections and disputed evidence.

### 8.3 Technical Trade-Offs

The architecture favors traceability and explicit evidence relationships over minimal data-model complexity.

It introduces additional records and relationships, but avoids relying on generated narratives as the only representation of evidential support.

The system may initially use simpler categorical assessments before introducing calibrated quantitative methods.

### 8.4 Operational Consequences

Operations must support:

- Inspection of evidence origins.
- Identification of syndicated and derivative reporting.
- Review of contradictory evidence.
- Correction and withdrawal handling.
- Assessment version history.
- Source relationship maintenance.
- Monitoring of unsupported claims.
- Evaluation of evidence extraction and assessment quality.

### 8.5 Product and Business Consequences

Reports can explain the basis and limitations of important conclusions.

However, the product must sometimes communicate that a claim remains unverified or that evidence is conflicting.

This may reduce the appearance of certainty in some reports, but improves the distinction between established information and unresolved questions.

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Syndicated articles counted as independent confirmation | Medium | High | Record source relationships and shared origins |
| LLM generates unsupported evidence references | Medium | High | Validate references against persisted source records |
| Source reputation mistaken for claim truth | Medium | High | Separate source assessment from claim assessment |
| Conflicting evidence silently discarded | Medium | High | Preserve explicit contradiction relationships |
| Uncalibrated confidence presented as probability | Medium | High | Document score semantics and prohibit unsupported probability language |
| Historical assessment overwritten | Medium | High | Version assessments and preserve audit history |
| Evidence content retained beyond permitted rights | Medium | High | Apply source-specific access and retention policies |
| Excessive review workload | Medium | Medium | Prioritize material claims and use risk-based review |
| False causal interpretation of market movements | Medium | High | Separate observation from causal analysis |
| Evidence extraction loses source context | Medium | High | Preserve evidence locations and contextual references |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- Source Management
- Source Relationship Management
- Article Processing
- Claim Extraction
- Evidence Extraction
- Evidence Management
- Claim Assessment
- Source Assessment
- Entity Resolution
- Event Intelligence
- Historical Context Service
- Analysis Pipeline
- Market Observation Processing
- Reporting Pipeline
- Review Service
- Evaluation and Observability

### 9.2 Affected Data Models and Interfaces

Proposed domain entities include:

- `Source`
- `SourceRelationship`
- `SourceAssessment`
- `Article`
- `ArticleRevision`
- `Claim`
- `ClaimObservation`
- `Evidence`
- `EvidenceLocation`
- `ClaimEvidenceLink`
- `ClaimAssessment` — immutable, versioned result for one Claim and a defined evidence set.
- `ClaimAssessmentEvidenceLink` — exact evidence considered by one assessment.
- `AssessmentHistory` — append-only lifecycle/audit actions for claim assessments.
- `Analysis`
- `AnalysisInput`
- `AnalysisEvidenceLink`
- `MarketObservation`
- `Report`
- `ReportEvidenceLink`
- `ReportArticleLink`
- `AssessmentHistory`

These are logical domain concepts. The final physical schema and repository boundaries must be defined in Documents 02 and 03. Claim.verification_status and Claim.confidence are current projections only; the authoritative assessment is an immutable ClaimAssessment. A new assessment must preserve the prior assessment, its exact evidence links, method/policy version, rationale, and supersession reference. AssessmentHistory records append-only lifecycle actions.

Proposed application operations include:

- `extract_claims`
- `extract_evidence`
- `register_evidence`
- `link_evidence_to_claim`
- `assess_claim`
- `assess_source`
- `identify_source_relationship`
- `detect_conflicting_evidence`
- `record_claim_correction`
- `supersede_claim_assessment`
- `resolve_evidence_provenance`
- `validate_analysis_references`

These are logical operations, not finalized implementation signatures.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-001 | Related to | Establishes the event-centric architecture and evidence-based event dossiers. |
| GENI-ADR-002 | Related to | Separates article deduplication from event matching and prevents duplicate reporting from being confused with independent evidence. |
| GENI-ADR-011 | Related to | Uses evidence and uncertainty when evaluating event identity and matching decisions. |
| GENI-ADR-006 | Related to | Defines the controlled LLM execution boundary used by extraction and assessment components. |
| GENI-ADR-013 | Related to | Defines content access, retention, licensing, and republication constraints. |
| GENI-ADR-014 | Related to | Defines human review, corrections, and withdrawals. |
| GENI-ADR-015 | Related to | Requires observed market information to be distinguished from reported and inferred economic impact. |
| GENI-ADR-017 | Related to | Defines LLM usage tracking and evaluation requirements. |
| GENI-ADR-018 | Related to | Requires translated evidence to retain original-language provenance and translation uncertainty. |
| GENI-ADR-019 | Depends on / Related to | Applies separate evidence, confidence, and uncertainty semantics to importance, economic relevance, and economic impact. |

## 10. Implementation Implications

### 10.1 Required Implementation Work

If accepted, implementation should include:

- Structured claim records.
- Structured evidence records.
- Evidence origin and provenance references.
- Evidence location references.
- Explicit claim-evidence relationships.
- Source relationship records.
- Source assessment records where justified.
- Versioned claim assessments.
- Explicit contradiction and qualification handling.
- Assessment methodology and version tracking.
- Analysis input references.
- Report-to-evidence traceability.
- Correction and withdrawal history.
- Evidence extraction and assessment evaluation datasets.
- Content retention controls.

### 10.2 Migration or Compatibility Requirements

If an existing implementation stores claims and evidence only in narrative form:

- Existing source references must be preserved.
- Historical report content must remain available subject to applicable rights.
- New structured evidence records must not be fabricated from unavailable source material.
- Unrecoverable provenance must be marked as incomplete.
- Existing assessments must not be retroactively presented as independently verified.
- Migration must preserve the distinction between generated summaries and source-originated statements.

### 10.3 Dependencies

- ADR-001: Event-centric architecture.
- ADR-002: Article deduplication and event matching separation.
- ADR-006: Shared LLM execution architecture.
- ADR-011: Event identity and lifecycle.
- ADR-013: Content access and rights.
- ADR-014: Human review and correction operations.
- ADR-017: Evaluation and LLM usage tracking.
- Data model and component contract updates.

### 10.4 Implementation Sequence

1. Define the Claim and Evidence domain contracts.
2. Define provenance and evidence location contracts.
3. Define the initial evidence taxonomy.
4. Implement source and article provenance persistence.
5. Implement structured claim extraction.
6. Implement evidence extraction and validation.
7. Implement claim-evidence relationships.
8. Implement source relationship and syndication tracking.
9. Implement versioned claim assessment.
10. Implement uncertainty and contradiction representation.
11. Integrate evidence references into analysis.
12. Integrate evidence traceability into reports.
13. Implement correction and withdrawal handling.
14. Add evaluation datasets and quality metrics.
15. Add operational review and observability.

### 10.5 Verification Requirements

Verification must demonstrate that:

- Every claim retains its source attribution.
- Evidence references resolve to valid source records or explicitly identified external references.
- Evidence locations are preserved where available.
- Supporting and contradicting evidence can coexist.
- Syndicated reporting is not automatically treated as independent corroboration.
- Source reliability does not automatically determine claim truth.
- LLM-generated statements are not treated as independent evidence.
- Unknown information remains distinct from negative evidence.
- Uncalibrated scores are not presented as probabilities.
- Assessments can be versioned and reconstructed.
- Corrections do not silently erase historical assessments.
- Reports retain references to their supporting evidence.
- Restricted content is handled according to applicable retention rules.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Claims and evidence are separate domain records. | Domain and schema tests |
| AC-02 | Every source claim has traceable source attribution. | Provenance tests |
| AC-03 | Evidence has an identifiable origin or an explicit provenance limitation. | Validation tests |
| AC-04 | Evidence locations can be represented independently of full-text storage. | Domain and repository tests |
| AC-05 | Evidence-to-claim relationships support support, contradiction, qualification, and contextualization. | Relationship tests |
| AC-06 | Multiple evidence items can support or contradict one claim. | Relationship tests |
| AC-07 | Source relationships can represent syndicated and derivative reporting. | Source relationship tests |
| AC-08 | Repeated articles from a shared origin are not automatically treated as independent confirmation. | Integration tests |
| AC-09 | Source reliability and claim assessment are stored separately. | Domain and schema tests |
| AC-10 | Claim assessment supports explicit uncertain and inconclusive outcomes. | Assessment tests |
| AC-11 | Missing evidence is not treated as evidence of absence. | Assessment policy tests |
| AC-12 | Conflicting evidence remains traceable. | Integration tests |
| AC-13 | Assessment methodology and version are recorded. | Audit-record tests |
| AC-14 | Historical assessments remain available after reassessment. | Versioning tests |
| AC-15 | Corrections and retractions create traceable history. | Correction workflow tests |
| AC-16 | LLM-generated references are validated against available source records. | Security and contract tests |
| AC-17 | AI-generated analysis is not treated as independent evidence. | Workflow and domain tests |
| AC-18 | Reports preserve references to claims and supporting evidence. | Reporting integration tests |
| AC-19 | Uncalibrated confidence scores are not represented as statistical probabilities. | Policy and output validation tests |
| AC-20 | Evidence retention follows the applicable content-rights policy. | Retention and compliance tests |
| AC-21 | Evidence and assessment records can be evaluated using representative test datasets. | Evaluation pipeline |

Implementation verification is deferred until this ADR is formally accepted and the relevant capabilities are implemented.

## 12. Review and Reconsideration

### 12.1 Review Triggers

This ADR should be reviewed when:

- New source types introduce materially different evidence requirements.
- Evidence extraction quality is insufficient.
- Source independence cannot be reliably assessed.
- Claim assessment outcomes prove too coarse for important use cases.
- New legal or licensing restrictions affect evidence retention.
- The system introduces advanced market data or statistical analysis.
- Confidence calibration becomes available.
- Material changes are made to analytical or publication policy.

### 12.2 Review Schedule

**Review Date:** Not scheduled

**Review Owner:** Product Owner

### 12.3 Reconsideration Conditions

The recommendation should be reconsidered if structured evidence management proves disproportionately complex for the product's actual reporting requirements.

Any alternative must still preserve claim attribution, evidence traceability, contradiction handling, uncertainty, and historical report provenance.

## 13. References and Supporting Evidence

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Establishes event-centric intelligence and evidence-based reporting requirements. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines claim extraction, evidence assessment, analysis, and reporting boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines the proposed Claim, Evidence, and Analysis domain concepts. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines implementation sequencing and evaluation requirements. |
| `docs/adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` | Internal ADR | Establishes the event-centric architectural foundation. |
| [GENI-ADR-011](GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md) | Related Proposed ADR | Defines event identity and the use of evidence in event matching; the ADR is published in this repository. |
| `GENI-ADR-013` | Related Proposed ADR | Addresses source content access, retention, and licensing constraints. |

The recommendation is based on the project's documented product and architecture requirements.

No empirical claim-verification accuracy, source-reliability calibration, or universal confidence threshold is asserted.

Such measurements must be established through representative datasets and evaluation procedures before quantitative assessment policies are finalized.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-16 | Proposed | Initial proposal covering evidence provenance, claim assessment, source independence, uncertainty, and analytical traceability. | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Clarified distinct assessment semantics and source/evidence provenance constraints. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Aligned ClaimAssessment, ClaimAssessmentEvidenceLink, AssessmentHistory, and Claim current-assessment projection with Documents 02 and 03. | AI Architecture Assistant |

---

**End of ADR**