# Global Economic News Intelligence
# Architecture Decision Records (ADR) Governance

**Document ID:** GENI-GOV-005
**Version:** 1.1
**Status:** Draft — Under Architecture Review
**Document Type:** Architecture Decision Management and Governance
**Project:** Global Economic News Intelligence
**Last Updated:** 2026-11-16

---

## 1. Purpose

This document defines the governance process for identifying, evaluating, approving, recording, implementing, and revising architectural decisions for Global Economic News Intelligence.

Architecture Decision Records (ADRs) preserve the reasoning behind important technical and product architecture decisions.

The objectives are to ensure that:

- Important architectural decisions are explicit and traceable.
- Recommendations are distinguished from approved decisions.
- Alternatives and trade-offs are evaluated before major commitments.
- Architectural assumptions and unresolved questions remain visible.
- Implementation follows approved architectural decisions.
- Related documents remain consistent.
- Historical decisions remain available for future review.
- Changes do not silently invalidate previously approved decisions.

An important architectural decision must not exist only in source code, informal conversation, or an undocumented implementation assumption.

This document defines the governance process. It does not itself approve the architectural decisions listed in the ADR registry.

## 2. Governance Scope

This governance process applies to decisions with meaningful long-term consequences for:

- Product direction and scope.
- System architecture.
- Component responsibilities and interfaces.
- Data models and persistence.
- News acquisition and source management.
- Article deduplication and event correlation.
- Evidence collection and analytical methodology.
- LLM execution and provider integration.
- Publication, review, and correction policies.
- Security, privacy, and content rights.
- Infrastructure, deployment, and operational reliability.
- Delivery channels and future product capabilities.

Minor implementation details do not require an ADR unless they introduce significant architectural, operational, security, or maintenance consequences.

The two generic Agent Template documents are foundational framework references. They are not automatically product requirements. Any decision to adopt a capability from those templates into the product must be evaluated in the context of the product architecture.

## 3. Decision-Making Responsibilities

Architectural decisions follow a collaborative process with explicit approval authority.

### 3.1 AI Architecture Assistant

The AI Architecture Assistant is responsible for:

- Identifying architectural questions and unresolved decisions.
- Explaining why a decision matters.
- Researching technical alternatives when necessary.
- Comparing advantages, disadvantages, risks, complexity, and costs.
- Recommending an option with a clear rationale.
- Identifying assumptions and missing information.
- Identifying affected documents, components, and interfaces.
- Drafting and maintaining ADR records.
- Checking consistency between accepted decisions and project documentation.
- Identifying implementation and validation implications.
- Highlighting decisions that should be revisited when their assumptions change.

The assistant may recommend a technical option but must not present an unapproved recommendation as an accepted project decision.

### 3.2 Product Owner

The Product Owner is responsible for:

- Defining product objectives and priorities.
- Clarifying business requirements and constraints.
- Confirming acceptable trade-offs.
- Approving decisions affecting product direction, scope, budget, or operational expectations.
- Approving major architectural commitments.
- Resolving conflicts between competing product priorities.
- Authorizing material changes to previously accepted decisions.

The Product Owner does not need to independently solve every technical question. Technical analysis and recommendations may be prepared by the AI Architecture Assistant.

### 3.3 Approval Authority

The following approval rules apply:

| Decision Type | Approval Requirement |
|---|---|
| Product direction and scope | Product Owner |
| Budget and operational commitments | Product Owner |
| Publication risk and editorial policy | Product Owner |
| Data rights and content retention policy | Product Owner, with appropriate legal review where needed |
| Major architecture direction | Product Owner |
| Technical implementation details within an accepted architecture | May be delegated, provided they do not conflict with accepted ADRs |
| Technical recommendation | AI Architecture Assistant may prepare; recommendation alone is not approval |

An ADR becomes `Accepted` only after the required approval has been explicitly recorded.

Silence, discussion, implementation progress, or the existence of a recommendation does not constitute approval.

Where a decision has legal, regulatory, or contractual implications, technical approval does not replace the need for appropriate professional review.

## 4. What Requires an ADR?

An ADR is required when a decision has a meaningful impact on one or more of the following:

- Overall system architecture.
- Technology or infrastructure selection.
- Data model or persistence strategy.
- Workflow and execution architecture.
- LLM provider or execution strategy.
- News acquisition and source management.
- Article deduplication and event matching.
- Event identity, merging, and splitting.
- Semantic search and embedding storage.
- Evidence provenance and analytical methodology.
- Market data integration and impact classification.
- Publication, review, and correction policies.
- Content licensing, retention, and republication.
- Security and privacy.
- Reliability, recovery, and idempotency.
- Scalability and operational costs.
- API contracts and component boundaries.
- Migration and compatibility strategy.
- Audio, video, and other major future capabilities.

An ADR should also be created when an existing assumption is found to be materially incorrect or when two project documents prescribe conflicting behavior.

## 5. ADR Lifecycle

Every architectural decision follows this lifecycle:

1. **Identify:** Recognize an unresolved architectural question.
2. **Analyze:** Examine requirements, constraints, assumptions, and alternatives.
3. **Recommend:** Present a preferred option and its rationale.
4. **Review:** Examine implications, risks, and unresolved concerns.
5. **Approve or Reject:** Obtain the required decision authority.
6. **Record:** Create or update the individual ADR.
7. **Synchronize:** Update affected project documents.
8. **Implement:** Apply the approved decision.
9. **Validate:** Confirm that implementation satisfies the decision.
10. **Revisit:** Reconsider the decision when requirements, assumptions, or constraints change.

A decision must not be treated as approved merely because it has been discussed, recommended, or partially implemented.

### 5.1 Decision States and Implementation States

ADR approval status and implementation progress are separate concepts.

The ADR status describes the decision itself.

Implementation progress may be tracked separately in the roadmap, project tasks, or implementation records.

For example, an ADR may be `Accepted` while its implementation remains planned or in progress.

## 6. ADR Status Definitions

Each ADR must have exactly one current status.

| Status | Meaning |
|---|---|
| Proposed | Under investigation or review; not approved |
| Accepted | Explicitly approved and currently valid |
| Rejected | Evaluated but not selected |
| Deprecated | No longer recommended for new implementation |
| Superseded | Replaced by another ADR |

Additional rules:

- A Proposed ADR must not be treated as an implementation mandate.
- An Accepted ADR must include an approval record.
- A Rejected ADR must preserve the reason for rejection.
- A Deprecated ADR remains historically available.
- A Superseded ADR must reference the ADR that replaces it.
- ADR identifiers must never be reused.
- Status changes must be recorded in the ADR change history.

A decision may be Accepted with explicit implementation conditions. Those conditions must be documented and must not contradict the approved decision.

## 7. ADR Identification, Files, and Versioning

### 7.1 Governance Document Identity

The governance document uses:

`GENI-GOV-007`

This identifier is distinct from all ADR decision identifiers.

### 7.2 Decision Identifiers

Each individual decision receives a unique identifier using:

`GENI-ADR-NNN`

Examples:

- `GENI-ADR-001`
- `GENI-ADR-002`
- `GENI-ADR-003`

An ADR identifier belongs to one decision only and must never be reused.

### 7.3 Individual ADR Files

Each actual decision must have its own Markdown file under:

`docs/adr/decisions/`

Recommended naming convention:

`GENI-ADR-NNN-short-decision-title.md`

For example:

`GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md`

The ADR registry in `docs/adr/README.md` lists decision topics and links to their individual records.

A registry entry is not a substitute for an individual ADR document.

### 7.4 ADR Versioning

Each individual ADR maintains its own version number.

- **Patch:** Editorial corrections or clarification that do not change the decision.
- **Minor:** Additional analysis, consequences, or implementation details without changing the approved decision.
- **Major:** Material revision to the decision or its consequences.

A material change to an Accepted decision must follow the approval process and must be recorded in its change history. If the new decision replaces the old one, a new ADR should normally be created and the previous ADR marked `Superseded`.

## 8. Standard ADR Template

Every individual decision must use the project ADR template at:

`docs/adr/adr-template.md`

The template must include the following sections.

### 8.1 Metadata

- ADR ID.
- Decision title.
- Project.
- Status.
- Version.
- Date.
- Decision owner.
- Prepared by.
- Related ADRs.

### 8.2 Context and Problem

Describe the problem, requirement, or architectural question.

Explain:

- Why is this decision necessary?
- What problem are we trying to solve?
- What constraints exist?
- What assumptions are currently being made?
- What happens if no decision is made?

### 8.3 Decision Question

State the question that must be answered in a clear and unambiguous form.

### 8.4 Requirements and Constraints

List relevant requirements, including:

- Functional requirements.
- Performance requirements.
- Reliability requirements.
- Security and privacy requirements.
- Cost constraints.
- Operational constraints.
- Legal or licensing constraints where applicable.
- Future compatibility requirements.

### 8.5 Alternatives Considered

Document realistic alternatives.

For each alternative, evaluate:

- Benefits.
- Disadvantages.
- Complexity.
- Initial and ongoing costs.
- Risks.
- Operational requirements.
- Long-term implications.
- Reversibility.

### 8.6 Recommended Option

Identify the recommended solution.

Explain why it is preferred over the alternatives and identify any assumptions that must hold for the recommendation to remain valid.

### 8.7 Final Decision

Record the actual approved decision.

Clearly distinguish:

- The initial recommendation.
- The final approved decision.
- Any conditions attached to approval.

If the ADR remains Proposed, the final decision section must explicitly state that no approval has been recorded.

### 8.8 Consequences and Trade-offs

Describe:

- Positive consequences.
- Negative consequences.
- Technical debt introduced.
- Operational responsibilities.
- Future limitations.
- Expected maintenance requirements.

### 8.9 Risk Assessment

Evaluate relevant risks:

- Technical risk.
- Security risk.
- Data integrity risk.
- Reliability risk.
- Cost risk.
- Vendor dependency.
- Legal or licensing risk.
- Migration risk.

### 8.10 Impacted Documents and Components

Identify every document, component, interface, data entity, or workflow affected by the decision.

### 8.11 Implementation Implications

Describe required implementation work, including:

- Required changes.
- Migration requirements.
- Compatibility considerations.
- Dependencies.
- Rollback or recovery considerations.
- Monitoring and operational requirements.

### 8.12 Validation and Acceptance Criteria

Define how the decision will be validated.

Acceptance criteria must be measurable or objectively verifiable wherever possible.

### 8.13 Approval Record

Record:

- Approved by.
- Approval date.
- Approval status.
- Conditions of approval.
- Outstanding conditions.

### 8.14 Change History

Record subsequent changes to the ADR and explain why they were necessary.

## 9. Decision Evaluation Framework

The AI Architecture Assistant should evaluate alternatives using criteria appropriate to the decision.

Typical criteria include:

| Criterion | Evaluation Question |
|---|---|
| Product Fit | Does it support the product's objectives? |
| Reliability | Can it operate consistently and recover from failures? |
| Scalability | Can it support expected future growth? |
| Complexity | How difficult is it to implement and maintain? |
| Cost | What are the initial and ongoing costs? |
| Security | Does it introduce security or privacy risks? |
| Data Integrity | Does it preserve correctness, provenance, and consistency? |
| Flexibility | Can it accommodate future changes? |
| Maintainability | Can the system be understood and maintained? |
| Portability | Does it create unnecessary vendor dependency? |
| Reversibility | How difficult would it be to change later? |
| Observability | Can its behavior and failures be inspected? |

Not every criterion has equal importance.

The assistant must explain which criteria materially influence each recommendation rather than relying on an unexplained numerical score.

Where quantitative comparisons are used, their assumptions, sources, and limitations must be stated.

## 10. Decision Categories

The ADR register should cover the following categories:

1. Product and Scope Decisions.
2. System Architecture Decisions.
3. Workflow and Execution Decisions.
4. Data Model and Storage Decisions.
5. News Acquisition and Content Rights Decisions.
6. Article Deduplication and Event Intelligence Decisions.
7. LLM and AI Provider Decisions.
8. Evidence and Analytical Decisions.
9. Market Data and Economic Impact Decisions.
10. Publication, Review, and Correction Decisions.
11. Security and Privacy Decisions.
12. Infrastructure, Deployment, and Recovery Decisions.
13. Monitoring and Operational Decisions.
14. Multilingual Processing Decisions.
15. Future Audio, Video, and Advanced Intelligence Decisions.

## 11. Initial ADR Register

The following register identifies architectural decisions that require analysis and review.

**All entries below are Proposed. None is approved by this governance document.**

The registry is a planning and tracking mechanism. Each decision must be developed into an individual ADR before it can be considered for approval.

| Proposed ID | Decision Topic | Initial Status |
|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | Proposed |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | Proposed |
| GENI-ADR-003 | Economic Intelligence as the Primary Editorial Focus | Proposed |
| GENI-ADR-004 | Automated Publication and Quality-Gate Policy | Proposed |
| GENI-ADR-005 | Initial Persistence Technology and Migration Strategy | Proposed |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | Proposed |
| GENI-ADR-007 | Deterministic Workflows and Selective Agent Reasoning | Proposed |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | Proposed |
| GENI-ADR-009 | Near-Real-Time News Acquisition Strategy | Proposed |
| GENI-ADR-010 | Phased Text, Audio, and Video Delivery | Proposed |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | Proposed |
| GENI-ADR-012 | Semantic Retrieval, Similarity Calculation, and Embedding Storage | Proposed |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | Proposed |
| GENI-ADR-014 | Publication Decisions, Human Review, Corrections, and Withdrawals | Proposed |
| GENI-ADR-015 | Market Data Integration and Economic Impact Classification | Proposed |
| GENI-ADR-016 | Persistence, Async Execution, Idempotency, and Recovery | Proposed |
| GENI-ADR-017 | LLM Budgets, Usage Tracking, and Evaluation Strategy | Proposed |
| GENI-ADR-018 | Multilingual Source Processing, Translation, and Language Policy | Proposed |

### 11.1 Registry Maintenance Rules

- The registry must reflect the actual status of each individual ADR.
- Every registered decision must have a unique identifier.
- Every completed ADR must have an individual file under `docs/adr/decisions/`.
- A Proposed registry entry must not be interpreted as an approved design.
- New topics may be added when architectural questions emerge.
- Existing topics may be split into multiple decisions when they contain independent questions.
- Related decisions should reference one another.
- The registry must not mark an ADR Accepted unless its individual record contains an explicit approval record.

### 11.2 Initial Decision Priorities

The following topics should receive early attention because they affect multiple product documents and implementation dependencies:

1. Workflow-First Architecture and Selective LLM Reasoning.
2. Event Identity, Matching, Continuation, Merging, and Splitting.
3. News Acquisition, Full-Text Access, and Content Rights.
4. Publication, Review, and Correction Policy.
5. Semantic Matching and Embedding Strategy.
6. Market Data and Impact Classification.
7. Persistence and Recovery Strategy.
8. LLM Budgets and Evaluation.

Priority does not imply approval.

## 12. Cross-Document Consistency

Accepted ADRs must be reflected in all relevant project documents.

The primary governed documents are:

1. `docs/01-product-and-system-architecture.md`
2. `docs/02-component-architecture-and-interfaces.md`
3. `docs/03-data-model-and-storage-design.md`
4. `docs/04-implementation-plan-and-roadmap.md`
5. `docs/07-architecture-decision-records.md`
6. `docs/adr/README.md`
7. `docs/adr/adr-template.md`
8. Individual ADR records under `docs/adr/decisions/`

The two generic Agent Template documents remain foundational references:

- `docs/05-agent-template-architecture.md`
- `docs/06-agent-template-implementation-specification.md`

They do not automatically override product-specific architecture decisions.

### 12.1 Conflict Resolution

If an ADR conflicts with an existing project document:

1. Identify and describe the conflict.
2. Identify the authoritative accepted decision, if one exists.
3. Determine which documents require revision.
4. Obtain approval if the change modifies an accepted decision.
5. Update affected documents.
6. Verify consistency across related documents.
7. Preserve historical decision and document history.

An ADR does not automatically modify other documents.

### 12.2 Unapproved Assumptions

Where no Accepted ADR exists, project documents must clearly distinguish:

- Current proposal.
- Working assumption.
- Unresolved question.
- Approved decision.

For example, SQLite, a particular embedding storage approach, full-text retention, and market data provider selection must not be described as finalized architectural decisions until their corresponding ADRs are accepted.

## 13. Change Management

When a requirement or architectural decision changes:

1. Describe the requested change.
2. Explain the reason for the change.
3. Identify affected ADRs.
4. Identify affected documents, components, and data entities.
5. Evaluate technical and product implications.
6. Prepare a revised recommendation.
7. Obtain the required approval.
8. Update the relevant ADR or create a replacement ADR.
9. Update affected project documents.
10. Review implementation and migration implications.
11. Validate the revised architecture.
12. Preserve the historical record.

A change must not silently invalidate an Accepted decision.

If an accepted decision is replaced, its ADR must be marked `Superseded` and reference the replacement decision.

## 14. Architecture Review Gate

Before implementation begins for a major component, the following questions must be answered:

- Are the relevant architectural decisions identified?
- Have meaningful alternatives been considered?
- Are unresolved assumptions visible?
- Have required decisions been approved?
- Are related documents consistent?
- Are risks and trade-offs understood?
- Are implementation and validation criteria clear?
- Are dependencies on unresolved decisions understood?
- Is the component safe to implement independently while other decisions remain open?

If a critical decision remains unresolved, implementation of the affected component should wait.

Independent work that does not depend on that decision may continue.

The review gate should be proportional to the project's size and risk. It must provide traceability without introducing unnecessary administrative overhead.

## 15. Core Governance Principles

The following principles govern architecture decisions throughout the project:

1. No important architectural decision should exist only in code.
2. Recommendations and approved decisions must be clearly distinguished.
3. Technical alternatives must be evaluated before major commitments.
4. Product Owner approval is required for product-level trade-offs.
5. Every Accepted decision must have a documented rationale and approval record.
6. Decisions must be revisited when their assumptions change.
7. Historical decisions must remain traceable.
8. Architecture documents must remain consistent with Accepted ADRs.
9. Implementation must not silently introduce a conflicting architectural decision.
10. Reversible decisions should be treated differently from expensive, difficult-to-reverse commitments.
11. Unknown information must not be represented as a confirmed value.
12. Proposed technology choices must not be treated as mandatory before approval.
13. Governance effort should be proportional to architectural risk and project scale.

## 16. Definition of Done

The ADR governance process is considered operational when:

- A standard ADR template is available.
- The governance document has an identifier distinct from ADR decision identifiers.
- Every major architectural decision has a unique identifier.
- Proposed and Accepted decisions are clearly distinguished.
- Approval responsibility is defined.
- Individual ADR records can be maintained independently.
- The ADR registry reflects the actual state of individual records.
- Related documents are updated after approval.
- Changes are traceable.
- Superseded decisions remain historically available.
- Architecture review is part of the development process.
- No implementation is represented as an approved architectural decision without the required approval.

## 17. Current Governance State

At the time of this document version:

- This governance document is a draft under architecture review.
- The initial ADR register contains proposed decision topics.
- The registry does not constitute approval of those topics.
- Individual ADR records must be created and reviewed before decisions can be accepted.
- Product-specific architecture and implementation documents must continue to identify unresolved assumptions.
- No technology or architecture choice should be considered approved solely because it appears in a draft document or roadmap.

The governance process becomes effective for a decision only when the required approval is explicitly recorded.

---

**End of Document**

**Document ID:** GENI-GOV-005
**Version:** 1.1
**Status:** Draft — Under Architecture Review