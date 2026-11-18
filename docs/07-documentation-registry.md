# GENI-GOV-007 — Documentation Registry

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-GOV-007  
**Version:** 1.31
**Status:** Proposed — Pending Project Owner Approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18  
**Registry Scope:** Published GitHub `main` branch snapshot  
**Language:** English

---

## 1. Purpose

This document provides the central inventory of controlled project documentation.

It identifies documentation files, their locations, document identifiers, versions, lifecycle statuses, publication states, and relationships.

The registry is intended to:

- Provide a reliable overview of all project documentation.
- Distinguish locally available files from committed and published files.
- Track document approval and review status.
- Identify missing, outdated, or inconsistent documentation.
- Support cross-document impact analysis.
- Track planned documentation that has not yet been created.
- Provide a starting point for periodic documentation reviews.
- Support controlled documentation maintenance as the project evolves.

This registry records documentation status. It does not independently approve any document or architectural decision.

## 2. Registry Authority and Scope

### 2.1 Repository Information

**Repository:** `Ghassem296/global-economic-news-intelligence`  
**Branch:** `main`  
**Documentation Root:** `docs/`

The GitHub repository is the authoritative location for published project documentation.

The registry must distinguish the following states.

| State | Definition |
|---|---|
| Planned | The document topic has been identified, but no document file is available |
| Locally Available | The file exists in the local Working Tree |
| Modified | A tracked file has local changes not yet committed |
| Untracked | A local file is not yet recorded in the current Git commit |
| Committed | The file is recorded in the relevant Git commit |
| Published | The file is available in the designated GitHub repository and branch |

### 2.2 Working Tree and Repository State

The following concepts must not be confused:

**Working Tree**

Files currently available in the local project directory, including modified and untracked files.

**HEAD**

Files recorded in the latest local Git commit on the inspected branch.

**Remote Branch**

Files recorded in the corresponding branch on GitHub.

**Published Documentation**

Files available in the designated GitHub repository and branch.

A file present in the Working Tree is not necessarily committed or published.

A locally modified file may have a published baseline while its latest changes remain unpublished.

A document may be published while its lifecycle status remains Proposed or Under Review.

### 2.3 Registry Snapshot

Every inventory snapshot must identify:

- Inspection date.
- Repository and branch.
- Local branch and commit, when available.
- Remote branch and commit, when available.
- Whether the Working Tree was inspected.
- Any limitations affecting the inventory.

Registry findings describe the inspected state only.

They must be refreshed before formal approval, major implementation milestones, or repository publication.

## 3. Document Status Definitions

Lifecycle status and repository publication status are separate attributes.

### 3.1 General Document Lifecycle

| Status | Meaning |
|---|---|
| Accepted | Explicitly approved by the Project Owner |
| Draft — Under Architecture Review | Draft undergoing architecture review |
| Draft — Under Documentation Review | Draft undergoing documentation review |
| Proposed | Proposal awaiting review or approval |
| Proposed — Pending Project Owner Approval | Document prepared and awaiting explicit Project Owner approval |
| Rejected | Proposal formally rejected |
| Superseded | Replaced by a newer approved document |
| Retired | No longer applicable |

### 3.2 ADR Decision Status

Individual ADRs use their own decision lifecycle.

| Status | Meaning |
|---|---|
| Proposed | Decision recommendation awaiting approval |
| Accepted | Decision formally approved |
| Rejected | Decision formally rejected |
| Superseded | Decision replaced by a later accepted ADR |
| Deprecated | Decision no longer recommended for new implementation |
| Withdrawn | Proposal withdrawn before acceptance |

The ADR governance document, `docs/05-architecture-decision-records.md`, defines the authoritative ADR lifecycle and transition rules.

### 3.3 Supporting Material Classification

The following are document classifications rather than approval statuses:

- Reference
- Template
- Index
- Registry

They identify the purpose of a file and do not imply formal architectural approval.

### 3.4 Status Accuracy

The status recorded in this registry must match the document's actual metadata and available approval evidence.

The following statements are not equivalent:

- A document exists.
- A document is committed.
- A document is published.
- A document is reviewed.
- A document is approved.
- A decision has been implemented.

Each must be tracked independently.

## 4. Core Documentation Inventory

The versions and lifecycle states below were read from the actual file headers in the published GitHub `main` branch during this registry refresh.

| Document ID | Title | Repository Path | Actual Version | Lifecycle Status | Publication State | Owner | Last Updated | Approval Reference |
|---|---|---|---:|---|---|---|---|---|
| GENI-ARCH-001 | Product and System Architecture | `docs/01-product-and-system-architecture.md` | 1.19 | Draft — Under Architecture Review | Published | Project Owner | 2026-11-18 | No approval recorded |
| GENI-ARCH-002 | Component Architecture and Interface Contracts | `docs/02-component-architecture-and-interfaces.md` | 1.37 | Draft — Under Architecture Review | Published | Project Owner | 2026-11-18 | No approval recorded |
| GENI-DATA-003 | Data Model and Storage Design | `docs/03-data-model-and-storage-design.md` | 1.26 | Draft — Under Architecture Review | Published | Project Owner | 2026-11-18 | No approval recorded |
| GENI-PLAN-004 | Implementation Plan and Development Roadmap | `docs/04-implementation-plan-and-roadmap.md` | 1.17 | Draft — Under Architecture Review | Published | Project Owner | 2026-11-18 | No approval recorded |
| GENI-GOV-005 | Architecture Decision Records Governance | `docs/05-architecture-decision-records.md` | 1.7 | Draft — Under Architecture Review | Published | Project Owner | 2026-11-18 | No approval recorded |

The version column is a repository snapshot. It must be refreshed whenever a listed document is revised. Publication in `main` does not constitute Project Owner approval.

## 5. Documentation Governance and Index Inventory

| Document ID | Document | Repository Path | Actual Version | Lifecycle Status | Publication State | Owner | Last Updated | Approval Reference |
|---|---|---|---:|---|---|---|---|---|
| GENI-GOV-006 | Documentation Governance and Change Management | `docs/06-documentation-governance-and-change-management.md` | 1.2 | Proposed — Pending Project Owner Approval | Published | Project Owner | 2026-11-17 | Pending Project Owner approval |
| GENI-GOV-007 | Documentation Registry | `docs/07-documentation-registry.md` | 1.31 | Proposed — Pending Project Owner Approval | Published | Project Owner | 2026-11-18 | Pending Project Owner approval |
| GENI-DOC-INDEX-001 | Documentation Index | `docs/README.md` | 1.10 | Draft — Under Documentation Review | Published | Project Owner | 2026-11-18 | Pending documentation review |
| GENI-ADR-REGISTRY-001 | ADR Registry | `docs/adr/README.md` | 1.13 | Draft — Under Documentation Review | Published | Project Owner | 2026-11-18 | Pending documentation review |
| N/A | ADR Template | `docs/adr/adr-template.md` | 1.2 | Template | Published | Project Owner | 2026-11-18 | Not applicable — supporting template |
| N/A | Repository README / Project Entry Point | `README.md` | N/A | Entry-point document | Published | Not stated in file metadata | Not stated | Not applicable |

The version, lifecycle, owner, date, and approval-reference values were checked against the published file metadata and available approval evidence. The ADR template is supporting material, not an architectural decision. The root `README.md` is included as the published repository entry point; it currently has no controlled Document ID, version, owner, last-updated date, or lifecycle metadata and is therefore classified separately.

## 6. Architecture Decision Records Inventory

The published `main` branch contains all nineteen individual ADR documents. The file paths and versions below were checked against the actual repository files. The date column records the latest proposal/revision date only; it is not an approval or acceptance date. Approval remains unrecorded for every Proposed ADR.

| ADR ID | Title | Repository Path | Actual Version | Decision Status | Publication State | Decision Owner | Proposal / Revision Date | Approval Reference |
|---|---|---|---:|---|---|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | `docs/adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` | 1.4 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | `docs/adr/decisions/GENI-ADR-002-article-deduplication-and-event-matching.md` | 1.6 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-003 | Economic Intelligence as the Primary Editorial Focus | `docs/adr/decisions/GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md` | 1.3 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-004 | Publication Decisions, Quality Gates, and Automated Publishing Policy | `docs/adr/decisions/GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md` | 1.2 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-005 | Initial Persistence Technology and Migration Strategy | `docs/adr/decisions/GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md` | 1.2 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | `docs/adr/decisions/GENI-ADR-006-provider-independent-llm-execution-architecture.md` | 1.3 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-007 | Deterministic Workflows and Selective Agent Reasoning | `docs/adr/decisions/GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md` | 1.2 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | `docs/adr/decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` | 1.6 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-009 | Near-Real-Time News Acquisition Strategy | `docs/adr/decisions/GENI-ADR-009-near-real-time-news-acquisition-strategy.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-010 | Phased Text, Audio, and Video Delivery | `docs/adr/decisions/GENI-ADR-010-phased-text-audio-and-video-delivery.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | `docs/adr/decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md` | 1.7 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-012 | Semantic Retrieval, Similarity Calculation, and Embedding Storage | `docs/adr/decisions/GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md` | 1.1 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | `docs/adr/decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` | 1.3 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-014 | Human Review, Corrections, and Withdrawals | `docs/adr/decisions/GENI-ADR-014-human-review-corrections-and-withdrawals.md` | 1.4 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-015 | Market Data Integration and Economic Impact Classification | `docs/adr/decisions/GENI-ADR-015-market-data-integration-and-economic-impact-classification.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-016 | Persistence, Async Execution, Idempotency, and Recovery | `docs/adr/decisions/GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-017 | LLM Budgets, Usage Tracking, and Evaluation Strategy | `docs/adr/decisions/GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md` | 1.1 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-018 | Multilingual Source Processing, Translation, and Language Policy | `docs/adr/decisions/GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |
| GENI-ADR-019 | Event Importance, Economic Relevance, and Economic Impact Assessment Methodology | `docs/adr/decisions/GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md` | 1.0 | Proposed | Published | Project Owner | 2026-11-18 | Not yet approved |

### 6.1 ADR Publication and Availability

- Individual ADR files in `main`: **19 of 19**.
- Registered ADR topics without an individual file: **0**.
- ADRs with status `Proposed`: **19**.
- ADRs with status `Accepted`: **0**.
- Publication and implementation completion are not implied by file availability.

Each decision status must match the metadata and approval record in its individual ADR. The Project Owner remains the approval authority under Document 05.

### 6.2 ADR Governance Rules

- Every ADR must have a unique identifier and a verified repository path.
- Proposed ADRs must not be treated as accepted decisions.
- Publication does not imply acceptance.
- Acceptance does not automatically imply implementation.
- Superseded and withdrawn decisions must remain traceable.
- ADR changes must be reflected in this registry and in the central documentation registry.
- Material changes to accepted decisions require the approval process defined in Document 05.

## 7. Reference Documentation Inventory

Reference materials provide supporting architectural or implementation context.

They are not automatically binding project specifications.

| Title | Repository Path | Classification | Publication State |
|---|---|---|---|
| Agent Template Reference Guide | `docs/references/agent-template/README.md` | Reference | Published |
| Agent Template Architecture | `docs/references/agent-template/agent-template-architecture.md` | Reference | Published |
| Agent Template Implementation Specification | `docs/references/agent-template/agent-template-implementation-specification.md` | Reference | Published |

Reference material may inform project design, but product-specific requirements and accepted decisions must be documented in the appropriate authoritative project documents.

## 8. Planned Documentation Topics

Planned documentation must be tracked separately from existing files.

A planned topic does not represent an existing document.

Potential future documents include:

### 8.1 Product and Domain Specifications

- Event Intelligence and Correlation Specification.
- News Sources, Content Acquisition, and Rights Policy.
- Economic Taxonomy Specification.
- Evidence and Claim Validation Specification.
- Reporting and Publication Specification.

### 8.2 Technical and Operational Specifications

- API Specification.
- Security and Threat Model.
- Deployment and Operations Guide.
- Testing and Evaluation Strategy.
- Observability and Monitoring Specification.
- Data Retention and Recovery Policy.

### 8.3 Future Intelligence Capabilities

- Audio Intelligence Architecture.
- Video Intelligence Architecture.
- Advanced Intelligence and Personalization Specification.

These topics are candidates for future documentation.

They must not be assigned final document identifiers or treated as approved deliverables until their scope and necessity have been reviewed.

The ADR registry separately tracks architectural decision topics. ADR topics must not be confused with planned technical specification documents.

## 9. Document Dependency Overview

The following relationships provide a high-level guide for change impact analysis.

| Primary Document | Main Dependencies and Related Documents |
|---|---|
| GENI-ARCH-001 | GENI-ARCH-002, GENI-DATA-003, GENI-PLAN-004, relevant ADRs |
| GENI-ARCH-002 | GENI-ARCH-001, GENI-DATA-003, relevant ADRs |
| GENI-DATA-003 | GENI-ARCH-001, GENI-ARCH-002, relevant data and evidence ADRs |
| GENI-PLAN-004 | Approved product and architecture specifications |
| GENI-GOV-005 | ADR Template, ADR Registry, individual ADRs |
| GENI-GOV-006 | Documentation Index, Documentation Registry, all controlled documents |
| GENI-GOV-007 | Documentation Index, Documentation Governance, ADR Registry, all controlled documents |
| Individual ADRs | All documents and components affected by the decision |

This is a high-level dependency guide, not a complete technical dependency graph.

Specific dependencies must be verified during each change impact analysis.

## 10. Registry Maintenance Rules

The registry must be maintained whenever the documentation set changes.

### 10.1 Adding a Document

When a new controlled document is prepared or published:

1. Assign or verify its Document ID.
2. Confirm its official title.
3. Confirm its repository path.
4. Record its version.
5. Record its actual lifecycle status.
6. Record its local availability.
7. Record its Git commit and publication state.
8. Identify related documents.
9. Add it to the appropriate registry section.
10. Update the documentation index.
11. Verify internal links.

### 10.2 Updating a Document

When an existing document changes:

1. Verify the updated version.
2. Verify the resulting lifecycle status.
3. Update the Last Updated date in the document itself.
4. Update the registry when tracked metadata changes.
5. Review dependent documents.
6. Distinguish local modifications from committed and published changes.
7. Verify that the document index remains accurate.

### 10.3 Renaming or Moving a Document

When a document is moved or renamed:

1. Preserve its Document ID unless a formal identity change is justified.
2. Update its registry path.
3. Update internal references and links.
4. Verify that no broken references remain.
5. Check the Git change history and publication state.
6. Update the documentation index.

### 10.4 Retiring or Superseding a Document

Do not remove historical records from the registry without explanation.

Record:

- The final lifecycle status.
- The reason for the change.
- The replacement document, if applicable.
- The date of the transition.
- Relevant approval information.

### 10.5 Repository Publication

Before publication:

1. Review the document content and metadata.
2. Verify its repository path.
3. Verify internal links and cross-references.
4. Confirm that its lifecycle status is accurate.
5. Review the complete Git diff.
6. Obtain the required Project Owner authorization.
7. Confirm that related registry and index updates are included.

After publication:

- Verify that the file exists in the intended GitHub branch.
- Update the publication state.
- Update the registry snapshot.
- Verify the published version and document metadata.

Publication must never be interpreted as automatic architectural or project approval.

## 11. Registry Review

The registry must be reviewed:

- Whenever a controlled document is added or removed.
- Whenever an ADR changes status.
- Whenever an approved architecture decision changes.
- Whenever a document is committed, published, renamed, or retired.
- During periodic documentation consistency reviews.
- Before starting a major implementation phase.
- Before a formal documentation baseline is approved.

A periodic review should verify that the registry matches:

1. The actual local documentation inventory.
2. The current local Git commit.
3. The current remote GitHub branch.
4. The metadata inside the actual document files.
5. The relevant approval records.

## 12. Current Documentation Findings

### 12.1 Snapshot Information

**Inspection Date:** 2026-11-18  
**Repository:** `Ghassem296/global-economic-news-intelligence`  
**Reference Branch:** `main`  
**Baseline Commit Inspected:** `4c1b7b6242ca407243551737e7e1ae06555bc97d`  
**Registry Refresh:** This inventory was checked against the published `main` branch at the baseline commit above, after the preceding architecture, ADR, and governance-metadata corrections, including the clarified semantic-retrieval approval gate, claim/evidence contract alignment, and the exhaustive repository write-ownership matrix. This registry revision is committed as the next change on `main`.

This refresh was performed against the published GitHub `main` branch after Pull Request #1 had been merged. The local Working Tree was not inspected; local-only changes are outside this registry snapshot.

### 12.2 Core Documents

The five primary product, architecture, data, planning, and ADR-governance documents are present in `main`. Their actual versions and lifecycle statuses are recorded in Section 4.

### 12.3 Governance Documents

Documents 06 and 07 are published in `main` but remain Proposed pending explicit Project Owner approval. Publication must not be treated as approval.

### 12.4 ADR Inventory

All nineteen individual ADR files are present in `main`. All nineteen are Proposed; none is recorded as Accepted. There are no uncreated individual ADR files among the nineteen registered topics.

### 12.5 Indexes and Reference Materials

The Documentation Index, ADR Registry, ADR Template, and three Agent Template reference documents are present in the repository. Their publication state is independent of their lifecycle or classification.

### 12.6 Snapshot Limitations

This is a repository-only snapshot. It does not establish local Working Tree state, formal document approval, implementation completion, CI success, or operational verification. Refresh the registry after material documentation changes and before formal baseline approval.

## 13. Acceptance Criteria

This registry may be considered ready for operational adoption when:

1. The Project Owner approves the registry.
2. All listed repository paths are verified.
3. Document identifiers, versions, and lifecycle statuses match the actual files.
4. Local file availability and committed repository availability are clearly distinguished.
5. Unpublished local files are clearly separated from published documents.
6. ADR statuses match the individual ADR files.
7. Cross-document references are reviewed.
8. The registry maintenance process is established.
9. The documentation index references this registry.
10. The inventory is checked again before publication.
11. The snapshot date and inspected repository state are recorded.
12. No document is incorrectly represented as approved, published, or implemented.

## 14. Final Decision

**Current Status:** Proposed — Pending Project Owner Approval

**Recommendation:** Adopt this document as the central documentation inventory for Global Economic News Intelligence.

**Final Approval:** Pending explicit Project Owner approval.

This registry is an inventory and tracking mechanism.

It does not replace individual documents, ADR governance, documentation change management, or the Project Owner's approval authority.

Every controlled document and architectural decision must retain its own lifecycle status, publication state, and approval history.

**End of Document**