# Global Economic News Intelligence
# Architecture Decision Records (ADR) Governance

**Document ID:** GENI-GOV-005
**Version:** 1.2
**Status:** Draft — Under Architecture Review
**Document Type:** Architecture Decision Management and Governance
**Project:** Global Economic News Intelligence
**Last Updated:** 2026-11-17

---

## 1. Purpose

This document defines the governance process for identifying, evaluating, approving, recording, implementing, validating, and revising architectural decisions for Global Economic News Intelligence.

Architecture Decision Records (ADRs) preserve the reasoning behind significant product, architectural, technical, and operational decisions.

The objectives are to ensure that:

- Important decisions are explicit and traceable.
- Alternatives and trade-offs are evaluated before major commitments.
- Architectural assumptions and unresolved questions remain visible.
- Implementation follows approved architectural decisions.
- Related project documents remain consistent.
- Historical decisions remain available for future review.
- Changes do not silently invalidate previously accepted decisions.
- Decision approval, implementation, and verification are tracked separately.

An important architectural decision must not exist only in source code, informal conversation, or an undocumented implementation assumption.

## 2. Scope

This governance process applies to decisions with meaningful long-term consequences for the product, including:

- System architecture and major design principles.
- Component responsibilities and interfaces.
- Data models and persistence.
- News acquisition and source management.
- Article deduplication and event matching.
- Event identity, continuation, merging, and splitting.
- Evidence collection and analytical methodology.
- LLM execution and provider integration.
- Publication, review, and correction policies.
- Security, privacy, and content rights.
- Infrastructure, deployment, and operational reliability.
- Delivery channels and future product capabilities.
- Evaluation, observability, and quality assurance.

Minor implementation details do not require an ADR unless they introduce significant architectural, operational, security, cost, or maintenance consequences.

The generic Agent Template documents are reference materials. They are not automatically product requirements. Any decision to adopt a capability from those templates must be evaluated in the context of the product architecture and justified through the relevant design process.

## 3. Decision-Making Responsibilities

### 3.1 Product Owner

The Product Owner is responsible for:

- Approving or rejecting architectural decisions.
- Establishing product priorities and constraints.
- Resolving product-level trade-offs.
- Approving material changes to accepted decisions.
- Accepting implementation conditions where appropriate.

### 3.2 AI Architecture Assistant

The AI Architecture Assistant is responsible for:

- Analyzing architectural alternatives.
- Comparing advantages, disadvantages, risks, complexity, and costs.
- Recommending an option with a clear rationale.
- Identifying assumptions and missing information.
- Identifying affected documents, components, interfaces, and workflows.
- Drafting and maintaining ADR records.
- Checking consistency between accepted decisions and project documentation.
- Identifying implementation and validation implications.

The AI Architecture Assistant may recommend a decision but cannot independently approve it.

### 3.3 Technical Implementation

Implementation work must:

- Follow accepted architectural decisions.
- Identify conflicts between implementation requirements and accepted ADRs.
- Avoid treating proposed decisions as approved requirements.
- Report implementation constraints and newly discovered risks.
- Preserve traceability between implementation and architectural decisions.

### 3.4 Approval Authority

The following approval rules apply:

| Decision Area | Approval Authority |
|---|---|
| Product scope and priorities | Product Owner |
| Publication risk and editorial policy | Product Owner |
| Data rights and content retention policy | Product Owner, with appropriate legal review where needed |
| Major architecture direction | Product Owner |
| Technical implementation details within an accepted architecture | May be delegated if they do not conflict with accepted ADRs |
| Technical recommendation | AI Architecture Assistant may prepare; recommendation alone is not approval |

An ADR becomes `Accepted` only after the required approval has been explicitly recorded.

Silence, discussion, drafting assistance, implementation progress, or the existence of a recommendation does not constitute approval.

Where a decision has legal, regulatory, or contractual implications, technical approval does not replace appropriate professional review.

## 4. What Requires an ADR?

An ADR is required when a decision has a meaningful impact on one or more of the following:

- System architecture.
- Component boundaries and responsibilities.
- Data ownership and persistence.
- Event modeling and identity.
- Article deduplication and event matching.
- Event identity, continuation, merging, and splitting.
- LLM provider or execution strategy.
- News acquisition and source management.
- Semantic search and embedding storage.
- Evidence provenance and analytical methodology.
- Market data integration and impact classification.
- Publication and review policies.
- Security, privacy, and content rights.
- Infrastructure and deployment.
- Operational reliability and recovery.
- Cost management and resource allocation.
- Migration and compatibility strategy.
- Audio, video, and other major future capabilities.

An ADR should also be created when:

- An existing architectural assumption is found to be materially incorrect.
- Two project documents prescribe conflicting behavior.
- An implementation requires a significant departure from an accepted decision.
- A previously accepted decision must be replaced or materially revised.

## 5. ADR Lifecycle

Every architectural decision follows this lifecycle:

1. **Identify:** Recognize an architectural question requiring an explicit decision.
2. **Investigate:** Collect relevant technical, product, operational, and business information.
3. **Analyze:** Evaluate constraints, alternatives, risks, and trade-offs.
4. **Recommend:** Prepare a preferred option with supporting reasoning.
5. **Document:** Create or update the corresponding ADR.
6. **Review:** Check consistency with existing decisions and project documents.
7. **Approve:** Obtain explicit approval from the authorized decision-maker.
8. **Implement:** Translate the accepted decision into implementation work.
9. **Validate:** Confirm that implementation satisfies the decision.
10. **Revisit:** Reconsider the decision when requirements, assumptions, or constraints change.

A decision must not be treated as approved merely because it has been discussed, recommended, drafted, or partially implemented.

### 5.1 Decision Status and Implementation Status

ADR approval status and implementation progress are separate concepts.

The ADR status describes the decision itself.

Implementation progress must be tracked separately in the roadmap, project tasks, or implementation records.

For example, an ADR may be `Accepted` while its implementation remains `Not Started`, `In Progress`, or `Implemented`.

An implementation may also require additional verification before it can be considered compliant with an Accepted ADR.

## 6. ADR Status Definitions

The following statuses are used for individual ADRs:

| Status | Meaning |
|---|---|
| Proposed | A decision has been documented and is awaiting review or approval. |
| Accepted | The authorized decision-maker has explicitly approved the decision. |
| Rejected | The proposed decision has been explicitly rejected. |
| Superseded | A later accepted decision has replaced the decision. |
| Deprecated | The decision is no longer recommended for new implementation but has not necessarily been replaced. |
| Withdrawn | The proposal has been withdrawn before acceptance. |

A decision may be Accepted with explicit implementation conditions. Those conditions must be recorded in the ADR.

An ADR must not be marked Accepted without an explicit approval record.

## 7. ADR Identification and Organization

### 7.1 Governance Document Identity

This governance document uses:

`GENI-GOV-005`

This identifier is distinct from all ADR decision identifiers.

### 7.2 ADR Identification

Each architectural decision receives a unique identifier:

`GENI-ADR-NNN`

Where:

- `GENI` identifies the project.
- `ADR` identifies the document type.
- `NNN` is a sequential identifier.

An ADR identifier belongs to one decision only and must never be reused.

### 7.3 Individual ADR Files

Each drafted decision must have its own Markdown file under:

`docs/adr/decisions/`

Recommended naming convention:

`GENI-ADR-NNN-short-decision-title.md`

Examples:

- `GENI-ADR-001-event-centric-intelligence-architecture.md`
- `GENI-ADR-002-article-deduplication-and-event-matching.md`
- `GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md`

The ADR registry in `docs/adr/README.md` lists decision topics and links to their individual records.

A registry entry is not a substitute for an individual ADR document.

A file must only be represented as an existing document link after it has actually been created in the repository.

### 7.4 ADR Versioning

Each individual ADR maintains its own version number.

- **Minor:** Additional analysis, consequences, or implementation details without changing the approved decision.
- **Major:** Material revision to the decision or its consequences.

A material change to an Accepted decision must follow the approval process and must be recorded in its change history.

If a new decision replaces an existing Accepted decision, a new ADR should normally be created and the previous ADR marked `Superseded`.

### 7.5 Governance Document Versioning

This governance document also maintains its own version.

Changes to the governance process, approval responsibilities, lifecycle, or registry rules must be reflected in its version history.

A governance document revision does not automatically change the status of any individual ADR.

## 8. Standard ADR Template

Every individual ADR should follow the standard template defined in:

`docs/adr/adr-template.md`

The template includes the following sections.

### 8.1 Title and Metadata

Record:

- ADR identifier.
- Decision title.
- Version.
- Status.
- Creation date.
- Last updated date.
- Decision owner.
- Review participants, where applicable.

### 8.2 Context

Describe the problem, background, requirements, constraints, and circumstances that make the decision necessary.

### 8.3 Decision Drivers

Identify the most important factors influencing the decision.

### 8.4 Options Considered

Document the realistic alternatives considered.

### 8.5 Decision

State the selected option or proposed recommendation clearly.

### 8.6 Rationale

Explain why the selected option is preferred.

### 8.7 Consequences

Describe positive, negative, and neutral consequences.

### 8.8 Risks and Mitigations

Identify relevant risks and explain how they will be managed.

### 8.9 Implementation Implications

Identify affected components, interfaces, data entities, workflows, and implementation tasks.

### 8.10 Dependencies

Identify related decisions and unresolved dependencies.

### 8.11 Validation and Verification

Define how compliance with the decision will be verified.

### 8.12 References

Link to relevant project documents, technical sources, and related ADRs.

### 8.13 Approval Record

Record:

- Approval status.
- Approving authority.
- Approval date.
- Conditions of approval.
- Outstanding conditions.

If approval has not occurred, explicitly state that no approval has been recorded.

### 8.14 Change History

Record subsequent changes to the ADR and explain why they were necessary.

## 9. ADR Review Requirements

An ADR review must evaluate:

- Whether the problem is clearly defined.
- Whether the decision is consistent with product objectives.
- Whether realistic alternatives have been considered.
- Whether assumptions are explicit.
- Whether risks and trade-offs are sufficiently analyzed.
- Whether affected components and documents are identified.
- Whether implementation implications are understood.
- Whether the decision conflicts with another accepted ADR.
- Whether validation criteria are measurable.
- Whether approval authority is clear.

A review recommendation is not an approval decision.

## 10. ADR Registry

The authoritative registry of individual architectural decisions is:

`docs/adr/README.md`

The registry must:

- List all registered ADR identifiers.
- Provide the correct decision title.
- Show the current status of each ADR.
- Link to existing individual ADR files.
- Distinguish existing documents from planned or uncreated topics.
- Identify dependencies and relevant relationships where appropriate.

The registry must reflect the actual repository state.

### 10.1 Registry Accuracy

The following rules apply:

- The registry must reflect the actual status of each individual ADR.
- Every registered decision must have a unique identifier.
- Every drafted ADR must have an individual file under `docs/adr/decisions/` once it is added to the repository.
- A Proposed registry entry must not be interpreted as an approved design.
- New topics may be added when architectural questions emerge.
- Existing topics may be split into multiple decisions when they contain independent questions.
- Related decisions should reference one another.
- The registry must not mark an ADR Accepted unless its individual record contains an explicit approval record.
- A document link must not point to a file that does not exist in the repository.
- The registry must distinguish a drafted ADR from an ADR that has been committed to the repository.

### 10.2 Initial Decision Priorities

The following topics should receive early attention because they affect multiple product documents and implementation dependencies:

1. Event-Centric Intelligence Architecture.
2. Article Deduplication and Event Matching Separation.
3. Event Identity, Matching, Continuation, Merging, and Splitting.
4. Publication Decisions and Quality Gates.
5. Human Review, Corrections, and Withdrawals.
6. Provider-Independent LLM Execution.
7. News Content Access and Rights.
8. Evidence Provenance and Uncertainty.
9. Semantic Retrieval and Embedding Strategy.
10. Market Data and Economic Impact Classification.
11. Persistence and Recovery.
12. LLM Budgets and Evaluation.

Priority does not imply approval.

A P0 decision should be resolved before implementing the product capability that depends on it. Work that does not depend on an unresolved decision may continue only when its assumptions and limitations are explicitly documented.

Not every registered ADR must be accepted before implementation begins.

## 11. Cross-Document Consistency

Accepted ADRs must be reflected in all relevant project documents.

The primary governed documents are:

1. `README.md`
2. `docs/README.md`
3. `docs/01-product-and-system-architecture.md`
4. `docs/02-component-architecture-and-interfaces.md`
5. `docs/03-data-model-and-storage-design.md`
6. `docs/04-implementation-plan-and-roadmap.md`
7. `docs/05-architecture-decision-records.md`
8. `docs/adr/README.md`
9. `docs/adr/adr-template.md`
10. Individual ADR records under `docs/adr/decisions/`

The generic Agent Template reference documents are:

- `docs/references/agent-template/README.md`
- `docs/references/agent-template/agent-template-architecture.md`
- `docs/references/agent-template/agent-template-implementation-specification.md`

These documents provide reusable architectural and implementation guidance. They do not automatically define product requirements or override product-specific architecture decisions.

### 11.1 ADR-to-Document Synchronization

When an ADR is accepted:

1. Identify all affected project documents.
2. Determine which statements, requirements, interfaces, data entities, or roadmap items must change.
3. Update only the affected sections unless a broader revision is necessary.
4. Update document versions and revision metadata.
5. Update the ADR registry.
6. Verify links, identifiers, terminology, and cross-references.
7. Confirm that no remaining document contradicts the accepted decision.

The individual ADR records the reasoning behind the decision.

The relevant product, architecture, data model, or implementation document describes the resulting system design.

An ADR does not automatically modify other documents.

### 11.2 Conflict Resolution

If an ADR conflicts with an existing project document:

1. Identify and describe the conflict.
2. Identify the authoritative Accepted ADR, if one exists.
3. Determine which documents require revision.
4. Obtain approval if the change modifies an accepted decision.
5. Update affected documents.
6. Verify consistency across related documents.
7. Preserve historical decision and document history.

An Accepted ADR takes precedence over an older conflicting proposal, but affected documents must still be updated to remove ambiguity.

### 11.3 Unapproved Assumptions

Where no Accepted ADR exists, project documents must clearly distinguish:

- Confirmed requirements.
- Proposed architectural decisions.
- Unresolved assumptions.
- Temporary implementation choices.
- Deferred decisions.

Proposed decisions must not be presented as mandatory architecture.

## 12. Change Management

When a requirement or architectural decision changes:

1. Describe the requested change.
2. Explain the reason for the change.
3. Identify affected ADRs.
4. Identify affected project documents and components.
5. Evaluate compatibility, migration, and operational implications.
6. Determine whether an existing ADR can be amended or a new ADR is required.
7. Obtain the required approval.
8. Update the ADR and related documentation.
9. Update the registry.
10. Validate consistency and preserve historical records.

Accepted ADRs must not be silently rewritten to represent a different decision.

Significant changes to an accepted decision should normally be documented in a new ADR. The original ADR must remain available and be marked `Superseded` when appropriate.

Minor editorial corrections that do not change the decision may be made without creating a new ADR.

## 13. Architecture Review Gate

Before implementation begins for a major component, the following questions must be considered:

- Are the relevant architectural decisions documented?
- Are required decisions accepted?
- Are unresolved assumptions visible?
- Are dependencies on unresolved decisions understood?
- Is the component safe to implement independently while other decisions remain open?

If a critical decision remains unresolved, implementation of the affected capability should wait.

Independent work that does not depend on that decision may continue.

## 14. Governance Principles

The following principles govern architecture decisions throughout the project:

1. Important architectural decisions must be explicit.
2. Every decision must have a unique identifier.
3. Every ADR must preserve its reasoning and context.
4. Recommendations must be distinguished from approvals.
5. Proposed decisions must not be treated as accepted architecture.
6. Accepted decisions must be traceable to implementation.
7. Changes must preserve historical decision records.
8. Related documents must remain consistent.
9. Dependencies and unresolved questions must remain visible.
10. Decisions must account for operational, security, and cost implications.
11. Unknown information must not be represented as a confirmed value.
12. Proposed technology choices must not be treated as mandatory before approval.
13. Governance effort should be proportional to architectural risk and project scale.
14. Acceptance, implementation, and verification must be tracked as distinct activities.

## 15. Definition of Done

The ADR governance process is considered operational when:

- The governance document is available.
- The standard ADR template is available.
- The ADR registry is maintained.
- Individual decisions have unique identifiers.
- Approval records are explicit.
- Relevant implementation dependencies are tracked.
- Superseded decisions remain historically available.
- Architecture review is part of the development process.
- No implementation is represented as an approved architectural decision without the required approval.
- Registry links and document paths are verified against the repository.

## 16. Current Governance State

At the time of this document revision:

- The ADR governance document exists as a draft under architecture review.
- The ADR template exists.
- The ADR registry exists.
- Eighteen initial architectural decision topics have been identified.
- ADR-001 exists in the committed repository with status `Proposed`.
- ADR-002, ADR-006, ADR-008, ADR-011, and ADR-013 have been prepared as individual draft files in the local working tree but have not yet been committed to the repository.
- The remaining registered topics do not yet have individual ADR files in the current working tree.
- No Proposed ADR should be interpreted as an Accepted architectural decision.
- Existing architectural descriptions that depend on unresolved ADRs remain provisional where applicable.
- Implementation must not treat unresolved proposals as finalized architectural decisions.

The next steps are to complete the documentation review, synchronize the ADR registry with the working tree and committed repository state, and publish the approved documentation changes.

The governance process becomes effective for an individual decision only when the required approval is explicitly recorded.

---

**End of Document**

**Document ID:** GENI-GOV-005
**Version:** 1.2
**Status:** Draft — Under Architecture Review
**Last Updated:** 2026-11-17
