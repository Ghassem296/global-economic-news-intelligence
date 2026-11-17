# GENI-GOV-006 — Documentation Governance and Change Management

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-GOV-006  
**Version:** 1.0  
**Status:** Proposed — Pending Project Owner Approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-17  
**Language:** English

---

## 1. Purpose

This document defines the governance process for creating, maintaining, reviewing, approving, versioning, and changing project documentation.

Its primary objective is to ensure that project documentation remains accurate, consistent, traceable, and aligned with the actual system architecture and implementation.

Documentation is treated as a maintained engineering asset rather than a one-time planning deliverable.

This policy applies to all project documentation, including architecture specifications, data models, implementation plans, Architecture Decision Records (ADRs), technical guides, and operational documentation.

## 2. Governance Principles

The following principles govern documentation management:

1. **Single Source of Truth:** The project's GitHub repository is the authoritative location for approved documentation.
2. **Documentation-Code Alignment:** Documentation and implementation must remain consistent.
3. **Explicit Approval:** Proposed architectural decisions and official documentation changes require explicit approval.
4. **Traceability:** Significant changes must have an identifiable reason, author, review history, and approval record.
5. **Incremental Maintenance:** Documentation should be updated when relevant changes occur, not postponed until the entire project is rewritten.
6. **Historical Preservation:** Important architectural decisions and their history must remain traceable.
7. **Proportional Documentation:** Documentation effort should reflect the complexity, impact, and risk of a change.
8. **No Silent Decisions:** A proposal must not be treated as an approved architectural decision without explicit authorization.

## 3. Documentation Scope and Classification

Project documentation is classified into the following categories.

### 3.1 Product Documentation

Describes:

- Product objectives and scope
- Target users and use cases
- Functional capabilities
- Product constraints
- Non-functional requirements

### 3.2 Architecture Documentation

Describes:

- System architecture
- Component responsibilities
- Interfaces and dependencies
- Processing workflows
- Architectural boundaries

### 3.3 Data Documentation

Describes:

- Data entities and relationships
- Storage architecture
- Data lifecycle
- Data provenance
- Retention and integrity requirements

### 3.4 Governance Documentation

Defines:

- Architectural decision processes
- Documentation management
- Approval responsibilities
- Change management rules

### 3.5 Architecture Decision Records

ADRs document significant architectural decisions, including:

- The problem being addressed
- Considered alternatives
- The selected approach
- Decision rationale
- Consequences and trade-offs
- Approval status

### 3.6 Implementation and Operational Documentation

Describes:

- Development phases
- Implementation requirements
- Testing and evaluation
- Deployment and operational procedures
- Maintenance and recovery processes

## 4. Document Ownership and Responsibilities

Every controlled document must have an assigned owner.

The following responsibilities apply.

### 4.1 Project Owner

The Project Owner is the final authority for project documentation and architectural decisions.

Responsibilities:

- Approve or reject significant documentation changes.
- Accept or reject proposed ADRs.
- Approve changes to product scope and architectural direction.
- Resolve conflicts between competing proposals.
- Prioritize documentation work.
- Authorize official updates to the main documentation baseline.

### 4.2 Architecture Advisor

The Architecture Advisor supports the Project Owner through technical analysis and documentation maintenance.

Responsibilities:

- Prepare and revise documentation.
- Identify affected documents when a change is proposed.
- Analyze architectural consequences.
- Identify inconsistencies and missing decisions.
- Prepare ADRs and technical recommendations.
- Review implementation against approved architectural decisions.
- Maintain documentation consistency.

The Architecture Advisor may recommend decisions but cannot independently approve architectural changes.

### 4.3 Development Team

When development begins, the Development Team is responsible for:

- Reporting implementation changes that affect documentation.
- Identifying discrepancies between code and approved specifications.
- Updating implementation-level documentation.
- Providing technical evidence for proposed changes.
- Participating in documentation reviews.

## 5. Document Metadata Requirements

Every controlled document must include a metadata header.

Required fields:

| Field | Description |
|---|---|
| Document ID | Unique document identifier |
| Title | Official document title |
| Version | Document version |
| Status | Current approval and review status |
| Owner | Accountable document owner |
| Last Updated | Date of the latest substantive update |

Optional fields may include:

- Related Documents
- Supersedes
- Superseded By
- Review Date
- Approved By
- Approval Date

Document identifiers must remain stable throughout the document's lifecycle.

A title or content change does not automatically justify assigning a new Document ID.

## 6. Document Lifecycle and Status

Controlled documentation uses the following lifecycle statuses.

### 6.1 Proposed

A draft or recommendation awaiting review and approval.

It must not be treated as an approved project requirement or architectural decision.

### 6.2 Under Review

The document is undergoing technical or product review.

Changes may be requested before approval.

### 6.3 Accepted

The document has been explicitly approved by the Project Owner.

An Accepted document represents the current approved documentation baseline within its defined scope.

### 6.4 Rejected

The proposal has been reviewed and rejected.

The reason for rejection should be recorded.

### 6.5 Superseded

The document or decision has been replaced by a newer approved document or decision.

Historical content must remain available.

### 6.6 Retired

The document is no longer applicable and has not necessarily been replaced by another document.

Its retirement reason must be recorded.

Status transitions must be explicit and traceable.

## 7. Document Versioning Policy

Controlled documents use semantic-style versioning:

**MAJOR.MINOR**

### 7.1 Major Version

Increment the major version when:

- The document undergoes a substantial architectural restructuring.
- Its fundamental scope or conceptual model changes.
- Previously established assumptions or requirements are materially revised.
- The changes introduce significant incompatibility with the previous specification.

Example:

`1.0 → 2.0`

### 7.2 Minor Version

Increment the minor version when:

- Sections are added or removed without fundamentally changing the document's scope.
- Interfaces or data structures are extended compatibly.
- Clarifications materially improve the specification.
- New requirements or constraints are introduced within the existing scope.

Example:

`1.0 → 1.1`

### 7.3 Editorial Changes

Typos, formatting corrections, and minor wording improvements that do not change meaning do not require a version increment.

Such changes should still be visible in Git history.

### 7.4 Versioning Rules

- Versions must increase monotonically.
- A previous version must never be silently overwritten in the documentation history.
- Version numbers must not be used as substitutes for approval status.
- A new version does not automatically become Accepted.
- The document version and its Git commit history are separate records.

## 8. Documentation Change Management

Every significant documentation change must follow a controlled process.

### Step 1 — Change Identification

A change may originate from:

- A newly identified product requirement.
- An architectural review.
- An implementation discovery.
- A performance or reliability issue.
- A security or compliance requirement.
- A new external dependency.
- A previously approved decision that needs revision.

The reason for the proposed change must be documented.

### Step 2 — Impact Analysis

Before editing, identify:

- Directly affected documents.
- Related ADRs.
- Affected components and interfaces.
- Data model implications.
- Implementation and testing implications.
- Operational, security, and compliance implications.

The impact analysis must distinguish confirmed effects from possible future effects.

### Step 3 — Change Classification

Classify the change as one of the following:

**Editorial Change**

A correction that does not alter technical meaning.

**Clarification**

An explanation of an existing requirement or decision without changing its intended meaning.

**Specification Change**

A change to requirements, interfaces, data structures, workflows, or implementation specifications.

**Architectural Decision Change**

A change that introduces, replaces, or reverses a significant architectural decision.

**Implementation Deviation**

A difference between the approved specification and actual implementation that requires investigation.

### Step 4 — Document Revision

Prepare the complete revised document or a clearly scoped change proposal.

The revision must:

- Preserve unaffected content.
- Update affected sections consistently.
- Update cross-references.
- Identify unresolved questions.
- Avoid presenting unapproved proposals as established requirements.

### Step 5 — Review

The Architecture Advisor checks:

- Technical correctness.
- Internal consistency.
- Cross-document consistency.
- Alignment with approved ADRs.
- Missing dependencies.
- Unintended consequences.

The Project Owner reviews and decides whether to approve the change.

### Step 6 — Approval and Publication

After explicit approval:

- Update document status where appropriate.
- Update the version number when required.
- Record approval metadata.
- Merge the approved change into the main branch.
- Update the documentation registry.
- Review dependent documents.

## 9. Architecture Decision Record Governance

ADRs are governed independently from ordinary documentation revisions.

### 9.1 When an ADR Is Required

An ADR should be created when a decision:

- Has a significant effect on system architecture.
- Affects multiple components or system boundaries.
- Introduces a major technology or infrastructure dependency.
- Has meaningful alternatives and trade-offs.
- Creates substantial migration or maintenance costs.
- Affects security, privacy, reliability, or data integrity.
- Establishes a long-term architectural constraint.

Routine implementation details do not automatically require ADRs.

### 9.2 ADR Status

ADRs use the following decision statuses:

- Proposed
- Accepted
- Rejected
- Superseded
- Deprecated

An ADR in Proposed status is not an approved architectural constraint.

### 9.3 ADR Approval

Only the Project Owner can formally accept or reject an ADR under the current project governance model.

Technical recommendations and final decisions must remain distinguishable.

### 9.4 Changing an Accepted ADR

An Accepted ADR must not be silently rewritten to represent a different decision.

When a material decision changes:

1. Create a new ADR.
2. Reference the earlier ADR.
3. Explain why the previous decision is no longer appropriate.
4. Document the new alternatives and rationale.
5. Obtain explicit approval.
6. Mark the earlier ADR as Superseded after the replacement decision is accepted.

Minor editorial corrections that do not change the decision are permitted.

## 10. Cross-Document Consistency

Documents must be maintained as a coordinated specification set.

The following relationships must be reviewed:

| Change Area | Documents to Review |
|---|---|
| Product scope | Product Architecture, Implementation Plan |
| System boundaries | Product Architecture, Component Architecture |
| Component responsibilities | Component Architecture, Implementation Plan |
| Data entities and relationships | Data Model, Component Architecture |
| Storage technology | Data Model, Architecture Decisions, Implementation Plan |
| Processing workflow | Product Architecture, Component Architecture, Implementation Plan |
| AI execution architecture | Component Architecture, relevant ADRs, Implementation Plan |
| Evidence and provenance | Data Model, Product Architecture, relevant ADRs |
| Security and data retention | Architecture, Data Model, relevant ADRs, Operational Documentation |

This table is a starting point rather than an exhaustive dependency matrix.

Each change must be assessed according to its actual impact.

## 11. Documentation-Code Alignment

After implementation begins, approved specifications and actual implementation must be compared regularly.

Three situations must be distinguished.

### 11.1 Implementation Matches Documentation

No specification change is required.

### 11.2 Implementation Does Not Match Documentation

Determine whether:

- The implementation is incorrect.
- The documentation is incomplete.
- An intentional architectural change has occurred.
- An unresolved technical limitation exists.

The discrepancy must be recorded and resolved.

### 11.3 Implementation Reveals a Better Design

A discovered improvement must be evaluated before changing the approved architecture.

If it materially changes an architectural decision, the ADR process applies.

Implementation must not silently redefine the approved architecture.

## 12. GitHub Repository and Change Control

The GitHub repository is the authoritative documentation repository.

The following practices are recommended.

### 12.1 Main Branch

The `main` branch contains the approved documentation baseline and approved implementation changes.

Unreviewed architectural proposals must not be represented as accepted decisions.

### 12.2 Branches

Documentation changes should normally be prepared in a dedicated branch.

Example:

`docs/update-data-model`

### 12.3 Pull Requests

Pull Requests should include:

- Change summary.
- Reason for the change.
- Affected document IDs.
- Version changes, if applicable.
- Related ADRs.
- Impact analysis.
- Open questions.
- Required approvals.

### 12.4 Commit Messages

Use clear commit prefixes.

Examples:

- `docs: update component architecture`
- `docs: add proposed ADR for LLM execution`
- `docs: clarify evidence provenance requirements`
- `docs: align data model with accepted ADR`
- `docs: correct documentation references`

### 12.5 Approval Enforcement

The Project Owner must explicitly approve changes that alter the approved product scope or architecture.

Repository access permissions and branch protection should support this governance model when the project team grows.

## 13. Documentation Registry

A central registry must track all controlled documents.

The registry should contain:

| Field | Purpose |
|---|---|
| Document ID | Unique identity |
| Title | Document name |
| Path | Repository location |
| Version | Current version |
| Status | Current lifecycle status |
| Owner | Responsible person |
| Last Updated | Latest substantive revision |
| Related Documents | Dependencies and references |
| Approval Date | Date of formal acceptance, if applicable |

The registry should be maintained in `docs/README.md` or in a dedicated registry file if the documentation set becomes large.

The registry must reflect the actual repository state.

It must not claim that a document is Accepted when its status or approval evidence does not support that claim.

## 14. Documentation Review Schedule

Documentation review occurs through two complementary mechanisms.

### 14.1 Event-Driven Review

A review is required when:

- An architectural decision changes.
- A component is added, removed, or substantially redesigned.
- A data structure or interface changes.
- A significant security or compliance issue is identified.
- An implementation discrepancy is discovered.

### 14.2 Periodic Review

A documentation consistency review should occur every two weeks during active architecture and development work.

The review should focus on:

- Outdated assumptions.
- Unresolved decisions.
- Cross-document contradictions.
- Missing implementation updates.
- Broken references.
- Unnecessary or obsolete documentation.

A periodic review does not require rewriting every document.

## 15. Documentation Quality Requirements

Every controlled document should satisfy the following quality criteria:

- Clear purpose and scope.
- Consistent terminology.
- Traceable assumptions and decisions.
- Accurate references to other documents.
- Explicit unresolved questions.
- Clear distinction between proposals and approved requirements.
- No unsupported claims of implementation or approval.
- No unnecessary duplication of authoritative specifications.

Where information is duplicated across documents, one document should be designated as the authoritative source for that information.

Other documents should reference it rather than maintain competing versions.

## 16. Open Questions

The following governance decisions remain open and require future review:

1. Whether GitHub branch protection and mandatory Pull Request approvals should be enforced immediately or introduced when development contributors are added.
2. Whether a dedicated machine-readable documentation registry is necessary.
3. Whether automated link checking and metadata validation should be added to CI.
4. Whether a formal documentation review checklist should be introduced.
5. Whether documentation approval should be recorded through GitHub Pull Request approval, an explicit approval record, or both.

These questions do not prevent the adoption of the basic governance process.

## 17. Implementation Plan

The governance process should be introduced incrementally.

### Phase 1 — Establish the Baseline

- Approve this governance document.
- Confirm the document metadata conventions.
- Review existing document IDs and filenames.
- Establish a reliable documentation registry.
- Identify documents awaiting approval.

### Phase 2 — Align Existing Documentation

- Review existing architecture documents.
- Identify outdated references and inconsistent terminology.
- Align ADR references and statuses.
- Record unresolved architectural decisions.

### Phase 3 — Introduce Change Control

- Use dedicated documentation branches.
- Review significant changes through Pull Requests.
- Record approval and version changes.
- Keep the main branch as the approved baseline.

### Phase 4 — Automate Quality Checks

When justified by project size:

- Validate document metadata.
- Check internal Markdown links.
- Detect missing ADR references.
- Validate required document sections.
- Integrate documentation checks into CI.

## 18. Acceptance Criteria

This governance document may be considered ready for operational adoption when:

1. The Project Owner approves the document.
2. Document status and versioning rules are understood.
3. Responsibilities are explicitly assigned.
4. ADR approval and supersession rules are established.
5. The documentation registry reflects the actual repository.
6. The change management process is usable through GitHub.
7. Existing documentation is reviewed for consistency.
8. The process distinguishes proposals, approved decisions, and implementation status.

## 19. Final Decision

**Current Status:** Proposed

**Recommendation:** Adopt this document as the governing policy for project documentation and architectural change management.

**Final Approval:** Pending explicit Project Owner approval.

This document does not independently approve existing architecture proposals or ADRs. Each architectural decision must retain its own approval status and decision history.