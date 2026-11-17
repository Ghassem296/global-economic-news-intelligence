# GENI-GOV-007 — Documentation Registry

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-GOV-007  
**Version:** 1.1  
**Status:** Proposed — Pending Project Owner Approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-17  
**Registry Scope:** Documentation in the local working tree and the `main` branch  
**Language:** English

---

## 1. Purpose

This document provides the central inventory of project documentation.

It identifies controlled documentation files, their locations, document identifiers, versions, lifecycle statuses, publication states, and relationships.

The registry is intended to:

- Provide a reliable overview of project documentation.
- Distinguish locally available files from files recorded in the Git repository.
- Track document approval and review status.
- Identify missing, outdated, or inconsistent documentation.
- Support cross-document impact analysis.
- Provide a starting point for periodic documentation reviews.

This registry records documentation status. It does not independently approve any document or architectural decision.

## 2. Registry Authority and Scope

The GitHub repository is the authoritative source for published documentation.

**Repository:** `Ghassem296/global-economic-news-intelligence`  
**Branch:** `main`  
**Documentation Root:** `docs/`

This registry distinguishes two repository states:

- **Working Tree:** Files currently available in the local project directory, including modified and untracked files.
- **HEAD:** Files recorded in the latest local Git commit on the inspected branch.

A file present in the Working Tree is not necessarily present in HEAD or published to GitHub.

A modified tracked file is already part of the repository history, but its current local changes are not published until committed and pushed.

The registry must be updated whenever a controlled document is added, removed, renamed, materially revised, approved, rejected, or superseded.

A draft prepared outside the repository must not be listed as a repository file.

## 3. Status Definitions

The following lifecycle statuses are used in this registry.

| Status | Meaning |
|---|---|
| Accepted | Explicitly approved by the Project Owner |
| Draft — Under Architecture Review | Published draft awaiting architecture review |
| Draft — Under Documentation Review | Published draft awaiting documentation review |
| Proposed | Proposal awaiting approval |
| Proposed — Pending Project Owner Approval | Document prepared but awaiting explicit Project Owner approval |
| Reference | Supporting material, not an approved project specification |
| Superseded | Replaced by a later approved document |
| Retired | No longer applicable |

Lifecycle status and repository publication status are separate attributes.

For example, a document can be locally available, not yet committed, and still have the lifecycle status Proposed.

The status recorded here must match the document's actual metadata and approval evidence.

## 4. Core Documentation Inventory

The following documents constitute the main product, architecture, data, planning, and architecture-governance specifications.

| Document ID | Title | Repository Path | Version | Lifecycle Status |
|---|---|---|---|---|
| GENI-ARCH-001 | Product & System Architecture | `docs/01-product-and-system-architecture.md` | 1.1 | Draft — Under Architecture Review |
| GENI-ARCH-002 | Component Architecture & Interface Contracts | `docs/02-component-architecture-and-interfaces.md` | 1.1 | Draft — Under Architecture Review |
| GENI-DATA-003 | Data Model & Storage Design | `docs/03-data-model-and-storage-design.md` | 1.2 | Draft — Under Architecture Review |
| GENI-PLAN-004 | Implementation Plan & Development Roadmap | `docs/04-implementation-plan-and-roadmap.md` | 1.1 | Draft — Under Architecture Review |
| GENI-GOV-005 | Architecture Decision Records Governance | `docs/05-architecture-decision-records.md` | 1.2 | Draft — Under Architecture Review |

These identifiers, versions, and statuses were read from the actual document headers.

## 5. Documentation Governance and Index Files

| Document | Document ID | Repository Path | Version | Lifecycle Status |
|---|---|---|---|---|
| Documentation Governance and Change Management | GENI-GOV-006 | `docs/06-documentation-governance-and-change-management.md` | 1.0 | Proposed — Pending Project Owner Approval |
| Documentation Registry | GENI-GOV-007 | `docs/07-documentation-registry.md` | 1.1 | Proposed — Pending Project Owner Approval |
| Documentation Index | GENI-DOC-INDEX-001 | `docs/README.md` | 1.5 | Draft — Under Documentation Review |
| ADR Registry | GENI-ADR-REGISTRY-001 | `docs/adr/README.md` | 1.5 | Draft — Under Documentation Review |
| ADR Template | N/A | `docs/adr/adr-template.md` | 1.0 | Template |

The ADR Registry is an index for individual decision records. Its existence does not mean that all listed or proposed architectural decisions are accepted.

The ADR template is a reusable document template rather than an architectural decision.

Documents 06 and 07 are available in the local Working Tree but are not yet recorded in HEAD.

## 6. Architecture Decision Records Inventory

The following six individual ADR files are available in the local `docs/adr/decisions/` directory.

| ADR ID | Title | Repository Path | Version | Lifecycle Status | Local File | In HEAD |
|---|---|---|---|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | `docs/adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` | 1.0 | Proposed | Yes | Yes |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | `docs/adr/decisions/GENI-ADR-002-article-deduplication-and-event-matching.md` | 1.0 | Proposed | Yes | No |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | `docs/adr/decisions/GENI-ADR-006-provider-independent-llm-execution-architecture.md` | 1.0 | Proposed | Yes | No |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | `docs/adr/decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` | 1.0 | Proposed | Yes | No |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | `docs/adr/decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md` | 1.0 | Proposed | Yes | No |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | `docs/adr/decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` | 1.0 | Proposed | Yes | No |

### 6.1 Current ADR Status

Six individual ADR files are currently available in the local Working Tree.

Only `GENI-ADR-001` is recorded in the inspected HEAD commit.

The other five ADR files are locally prepared and await repository publication.

All six ADRs currently have the lifecycle status Proposed.

None of these statuses represents Project Owner approval.

An ADR must not be treated as an accepted architectural decision until explicit approval has been recorded.

## 7. Reference Documentation Inventory

Reference materials provide supporting architectural or implementation context.

They are not automatically binding project specifications.

The following reference files were identified in the documentation inventory:

| Title | Repository Path | Classification |
|---|---|---|
| Agent Template Reference Guide | `docs/references/agent-template/README.md` | Reference |
| Agent Template Architecture | `docs/references/agent-template/agent-template-architecture.md` | Reference |
| Agent Template Implementation Specification | `docs/references/agent-template/agent-template-implementation-specification.md` | Reference |

Reference material may inform project design, but project-specific requirements and accepted decisions must be documented in the appropriate authoritative project documents.

## 8. Locally Prepared Documents Pending Repository Publication

The following files are available in the local Working Tree but are not recorded in the inspected HEAD commit.

| Document ID | Title | Intended Repository Path | Version | Lifecycle Status |
|---|---|---|---|---|
| GENI-GOV-006 | Documentation Governance and Change Management | `docs/06-documentation-governance-and-change-management.md` | 1.0 | Proposed — Pending Project Owner Approval |
| GENI-GOV-007 | Documentation Registry | `docs/07-documentation-registry.md` | 1.1 | Proposed — Pending Project Owner Approval |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | `docs/adr/decisions/GENI-ADR-002-article-deduplication-and-event-matching.md` | 1.0 | Proposed |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | `docs/adr/decisions/GENI-ADR-006-provider-independent-llm-execution-architecture.md` | 1.0 | Proposed |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | `docs/adr/decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` | 1.0 | Proposed |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | `docs/adr/decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md` | 1.0 | Proposed |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | `docs/adr/decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` | 1.0 | Proposed |

These files exist locally; they must not be described as published repository documents until they have been committed and pushed.

Publication does not automatically imply approval. Each document retains its own lifecycle status and approval requirements.

## 9. Document Dependency Overview

The following relationships provide a high-level guide for impact analysis.

| Primary Document | Main Dependencies and Related Documents |
|---|---|
| GENI-ARCH-001 | GENI-ARCH-002, GENI-DATA-003, GENI-PLAN-004, relevant ADRs |
| GENI-ARCH-002 | GENI-ARCH-001, GENI-DATA-003, relevant ADRs |
| GENI-DATA-003 | GENI-ARCH-001, GENI-ARCH-002, relevant data and evidence ADRs |
| GENI-PLAN-004 | All approved product and architecture specifications |
| GENI-GOV-005 | ADR Template, ADR Registry, individual ADRs |
| GENI-GOV-006 | Documentation Index, Documentation Registry, all controlled documents |
| GENI-GOV-007 | Documentation Index, Documentation Governance, ADR Registry, all controlled documents |
| Individual ADRs | All documents and components affected by the decision |

This is a high-level dependency guide, not a complete technical dependency graph.

Specific dependencies must be verified during each change impact analysis.

## 10. Registry Maintenance Rules

The registry must be maintained under the following rules.

### 10.1 Adding a Document

When a new controlled document is prepared or published:

1. Assign or verify its Document ID.
2. Confirm its repository path.
3. Record its version.
4. Record its actual lifecycle status.
5. Record whether it exists locally and whether it is present in HEAD.
6. Identify related documents.
7. Add it to the appropriate registry section.
8. Update the relevant documentation index.

### 10.2 Updating a Document

When an existing document changes:

1. Verify the updated version.
2. Verify the resulting lifecycle status.
3. Update the Last Updated date in the document itself.
4. Update the registry when tracked metadata changes.
5. Review dependent documents.
6. Distinguish local modifications from committed and published changes.

### 10.3 Renaming or Moving a Document

When a document is moved or renamed:

1. Preserve its Document ID.
2. Update its registry path.
3. Update internal references and links.
4. Verify that no broken references remain.
5. Check the Git change history and publication state.

### 10.4 Retiring or Superseding a Document

Do not remove historical records from the registry without explanation.

Record the final status and the replacement document, if applicable.

### 10.5 Repository Publication

Before publication:

1. Review the document content and metadata.
2. Verify its repository path.
3. Verify internal links and cross-references.
4. Confirm that its lifecycle status is accurate.
5. Review the complete Git diff.
6. Obtain the required Project Owner authorization.

After publication, update the registry to reflect the committed repository state.

Publication must never be interpreted as automatic architectural or project approval.

## 11. Registry Review

The registry must be reviewed:

- Whenever a controlled document is added or removed.
- Whenever an ADR changes status.
- Whenever an approved architecture decision changes.
- Whenever a document is committed, published, renamed, or retired.
- During periodic documentation consistency reviews.
- Before starting a major implementation phase.

A periodic review should verify that the registry matches both the actual local documentation inventory and the repository's committed state.

## 12. Current Documentation Findings

Based on the local Working Tree and the inspected HEAD commit on 2026-11-17:

1. Five primary product, architecture, data, planning, and architecture-governance documents are present locally and represented in the repository.
2. `GENI-GOV-005` is currently at version 1.2 in the local Working Tree.
3. `GENI-GOV-006` and `GENI-GOV-007` are present locally but are not recorded in HEAD.
4. The Documentation Index is at version 1.5.
5. The ADR Registry is at version 1.5 in the local Working Tree.
6. The ADR template is present.
7. Six individual ADR files are present locally.
8. Only `GENI-ADR-001` is recorded in the inspected HEAD commit.
9. `GENI-ADR-002`, `GENI-ADR-006`, `GENI-ADR-008`, `GENI-ADR-011`, and `GENI-ADR-013` are locally prepared but not yet recorded in HEAD.
10. All six individual ADRs have the lifecycle status Proposed.
11. Three Agent Template reference documents are listed in the reference inventory.
12. This registry itself is locally prepared and is not yet recorded in HEAD.

These findings describe the inspected snapshot. They must be refreshed before any later approval or publication.

## 13. Acceptance Criteria

This registry may be considered ready for operational adoption when:

1. The Project Owner approves the registry.
2. All listed repository paths are verified.
3. Document identifiers, versions, and lifecycle statuses match the actual files.
4. Local file availability and committed repository availability are clearly distinguished.
5. Unpublished local files are clearly separated from documents recorded in HEAD.
6. Cross-document references are reviewed.
7. The registry maintenance process is established.
8. The documentation index references this registry.
9. The inventory is checked again before publication.

## 14. Final Decision

**Current Status:** Proposed — Pending Project Owner Approval

**Recommendation:** Adopt this document as the central documentation inventory for Global Economic News Intelligence.

**Final Approval:** Pending explicit Project Owner approval.

This registry is an inventory and tracking mechanism. It does not replace the individual documents, ADR governance, or the Project Owner's approval authority.