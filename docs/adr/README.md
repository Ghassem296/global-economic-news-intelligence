# Architecture Decision Records (ADR) Registry

**Project:** Global Economic News Intelligence  
**Document:** Architecture Decision Records Registry  
**Document ID:** GENI-ADR-REGISTRY-001  
**Version:** 1.5  
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-17

---

## 1. Purpose

This directory contains the Architecture Decision Records (ADRs) for the Global Economic News Intelligence project.

ADRs document significant architectural and technical decisions, including:

- The context and problem that require a decision.
- The options and alternatives considered.
- The recommended or selected approach.
- The rationale behind the decision.
- Expected consequences, limitations, and trade-offs.
- Implementation, migration, and review implications.

This registry provides a central inventory of architectural decision topics and tracks the availability and status of their individual ADR documents.

It does not replace individual ADR documents, which contain the complete decision rationale, decision status, and approval history.

The registry distinguishes between document availability, decision status, and implementation status. These properties must be maintained independently.

## 2. Directory Structure

The ADR directory follows this structure:

```text
docs/
└── adr/
    ├── README.md
    ├── adr-template.md
    └── decisions/
        ├── GENI-ADR-001-event-centric-intelligence-architecture.md
        ├── GENI-ADR-002-article-deduplication-and-event-matching.md
        ├── GENI-ADR-006-provider-independent-llm-execution-architecture.md
        ├── GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md
        ├── GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md
        └── GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md
```

### 2.1 Directory Responsibilities

| File or Directory | Responsibility |
|---|---|
| `README.md` | ADR registry, status tracking, and registry-level guidance |
| `adr-template.md` | Standard template for creating individual ADRs |
| `decisions/` | Contains individual architectural decision records |

The `decisions/` directory contains the individual ADR documents currently prepared for the project.

New ADR files must be stored in this directory.

## 3. ADR Status Definitions

Every individual ADR must use one of the following statuses:

| Status | Meaning |
|---|---|
| Proposed | A decision has been documented but has not been formally approved. |
| Accepted | The decision has been formally approved. |
| Rejected | The proposal has been reviewed and explicitly declined. |
| Deprecated | The decision is no longer recommended or applicable. |
| Superseded | The decision has been replaced by a newer ADR. |

A Proposed ADR must not be treated as an approved architectural constraint.

Only Accepted ADRs represent formally approved architectural decisions.

Acceptance and implementation are separate activities. An Accepted ADR does not imply that its implementation is complete.

The decision status recorded in the registry must match the status in the corresponding individual ADR.

## 4. Initial ADR Inventory

The project has identified eighteen architectural decision topics.

The registry distinguishes between:

- The existence of a decision topic.
- The existence and availability of an individual ADR file.
- The current decision status.
- The implementation status of the decision.

These are separate properties and must not be confused.

### 4.1 Individual ADR Documents

The following individual ADR documents currently exist in the local project working directory.

| ADR ID | Title | Local Document Availability | Decision Status | Repository Path |
|---|---|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | Published | Proposed | `decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | Prepared locally; pending publication | Proposed | `decisions/GENI-ADR-002-article-deduplication-and-event-matching.md` |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | Prepared locally; pending publication | Proposed | `decisions/GENI-ADR-006-provider-independent-llm-execution-architecture.md` |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | Prepared locally; pending publication | Proposed | `decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | Prepared locally; pending publication | Proposed | `decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md` |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | Prepared locally; pending publication | Proposed | `decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` |

**Publication terminology:**

- Published means the document is committed to and available in the shared Git repository.
- Prepared locally means the document exists in the local working directory but has not yet been published to the shared repository.
- Not created means no individual ADR document currently exists.

The local documents listed as prepared must be reviewed, committed, and pushed before they are considered published.

The existence of an ADR file does not imply that its proposal has been accepted.

### 4.2 Remaining Decision Backlog

The following decision topics have been identified but do not yet have individual ADR documents in the current local project directory.

| ADR ID | Title | Priority | Document Availability |
|---|---|---|---|
| GENI-ADR-003 | Economic Intelligence as the Primary Editorial Focus | P2 | Not created |
| GENI-ADR-004 | Publication Decisions, Quality Gates, and Automated Publishing Policy | P0 | Not created |
| GENI-ADR-005 | Initial Persistence Technology and Migration Strategy | P1 | Not created |
| GENI-ADR-007 | Deterministic Workflows and Selective Agent Reasoning | P1 | Not created |
| GENI-ADR-009 | Near-Real-Time News Acquisition Strategy | P1 | Not created |
| GENI-ADR-010 | Phased Text, Audio, and Video Delivery | P2 | Not created |
| GENI-ADR-012 | Semantic Retrieval, Similarity Calculation, and Embedding Storage | P1 | Not created |
| GENI-ADR-014 | Publication Decisions, Human Review, Corrections, and Withdrawals | P0 | Not created |
| GENI-ADR-015 | Market Data Integration and Economic Impact Classification | P1 | Not created |
| GENI-ADR-016 | Persistence, Async Execution, Idempotency, and Recovery | P1 | Not created |
| GENI-ADR-017 | LLM Budgets, Usage Tracking, and Evaluation Strategy | P1 | Not created |
| GENI-ADR-018 | Multilingual Source Processing, Translation, and Language Policy | P2 | Not created |

### 4.3 Inventory Rules

- A decision topic may exist before its individual ADR is drafted.
- An ADR draft may exist locally without being published to the shared repository.
- A document must not be marked Published until its file is committed and available in the shared repository.
- The decision status must match the metadata of the individual ADR.
- Proposed topics must not be presented as approved architectural requirements.
- The registry must be updated when a document is created, published, or its decision status changes.
- Document availability must not be used as a substitute for decision status.
- Implementation progress must be tracked separately from ADR publication and approval.

## 5. ADR Priority Definitions

The priority labels represent suggested implementation-dependency urgency.

| Priority | Meaning |
|---|---|
| P0 | Resolve before implementing the product capabilities that depend on the decision. |
| P1 | Resolve before implementing the corresponding advanced or dependent capabilities. |
| P2 | Can generally be deferred until the relevant product phase. |

Priority does not indicate approval status.

A P0 ADR is not automatically more correct or more important as a business decision than a P1 or P2 ADR.

Priority indicates the urgency of resolving an architectural question relative to implementation dependencies.

## 6. Relationship Between Related ADRs

Some decision topics are closely related but address different architectural questions.

In particular:

- **ADR-001** establishes the event-centric intelligence model.
- **ADR-002** establishes the separation between article deduplication and event matching.
- **ADR-011** defines event identity and the rules for matching, continuing, merging, and splitting events.
- **ADR-012** addresses semantic retrieval and similarity calculation as technical capabilities supporting event intelligence.
- **ADR-008** defines evidence provenance and uncertainty representation.
- **ADR-004** defines publication outcomes and automated quality gates.
- **ADR-014** defines the operational review process, including human review, corrections, and withdrawals.
- **ADR-005** addresses initial persistence technology and migration strategy.
- **ADR-016** addresses execution reliability, idempotency, and recovery.
- **ADR-006** defines the provider-independent LLM execution boundary.
- **ADR-017** addresses LLM budgets, usage tracking, and evaluation.
- **ADR-013** addresses content access, retention, licensing, and republication constraints.
- **ADR-010** addresses the phased delivery of text, audio, and video.

Related ADRs should cross-reference one another where their decisions have dependencies or affect shared architectural boundaries.

They must not duplicate or contradict each other's scope.

A cross-reference does not automatically establish a formal dependency or imply approval of the referenced ADR.

Where a related ADR is still Proposed or has not yet been created, the relationship must be treated as a planning or coordination reference rather than an approved architectural constraint.

## 7. ADR Creation Rules

Every individual ADR must:

1. Use the standard structure defined in `adr-template.md`.
2. Have a unique and permanent ADR identifier.
3. Describe the problem and relevant architectural context.
4. Document meaningful alternatives.
5. Distinguish recommendations from final decisions.
6. Explain the decision rationale.
7. Identify positive and negative consequences.
8. Identify affected components, interfaces, and documents.
9. Describe implementation and migration implications where applicable.
10. Define the decision status.
11. Record the decision date and relevant reviewers.
12. Identify unresolved questions and assumptions.
13. Include references to related ADRs where appropriate.

### 7.1 File Naming Convention

Individual ADR files must use this naming convention:

`GENI-ADR-NNN-short-descriptive-title.md`

Examples:

- `GENI-ADR-001-event-centric-intelligence-architecture.md`
- `GENI-ADR-002-article-deduplication-and-event-matching.md`
- `GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md`
- `GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md`
- `GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md`

Files must be stored inside the `decisions/` directory.

The ADR identifier in the document metadata, filename, and registry must match exactly.

File names should use lowercase descriptive words separated by hyphens.

ADR identifiers are permanent. A rejected or superseded identifier must not be reused for an unrelated decision.

## 8. ADR Lifecycle

The expected ADR lifecycle is:

1. **Identification:** An architectural question or unresolved design choice is identified.
2. **Proposal:** An individual ADR is drafted using the standard template.
3. **Review:** Technical, product, security, operational, and other relevant implications are examined.
4. **Decision:** The proposal is accepted or rejected by the authorized decision owner.
5. **Publication:** The approved or reviewed ADR document is committed to the shared repository with its accurate status.
6. **Implementation:** Accepted decisions are reflected in implementation and relevant documentation.
7. **Verification:** Implementation is checked against the accepted decision.
8. **Maintenance:** The ADR is reviewed when significant assumptions or architectural conditions change.
9. **Supersession or Deprecation:** The ADR may be replaced or retired when its assumptions are no longer valid.

Not every Proposed ADR must necessarily be accepted. Some may be rejected, combined, or replaced after further analysis.

Publication, acceptance, and implementation are distinct lifecycle activities.

## 9. Relationship with Other Project Documents

ADRs complement the main project documentation.

| Document | Relationship to ADRs |
|---|---|
| `README.md` | Introduces the project and provides the main entry point. |
| `docs/README.md` | Defines the documentation structure and reading order. |
| `docs/01-product-and-system-architecture.md` | Describes the overall product and system architecture. |
| `docs/02-component-architecture-and-interfaces.md` | Defines system components and their contracts. |
| `docs/03-data-model-and-storage-design.md` | Describes domain entities, persistence, and storage design. |
| `docs/04-implementation-plan-and-roadmap.md` | Defines implementation stages, dependencies, and delivery priorities. |
| `docs/05-architecture-decision-records.md` | Defines ADR governance and decision-management rules. |
| `docs/06-documentation-governance-and-change-management.md` | Defines documentation maintenance, review, and change-management practices. |
| `docs/07-documentation-registry.md` | Provides the inventory and status of project documentation. |
| `docs/adr/adr-template.md` | Defines the standard ADR document structure. |

Generic Agent Template documents are maintained under `docs/references/agent-template/`.

They are reference material and do not automatically define product implementation requirements.

When an ADR is accepted and changes an architectural decision, all affected documents must be reviewed and updated.

The ADR records the reasoning behind the decision. The relevant architecture or specification document describes the resulting system design.

Documentation changes must preserve consistency between the ADR, architecture specifications, implementation roadmap, and documentation registry.

## 10. Change Management

The following rules apply to architectural changes:

- Accepted ADRs must not be silently rewritten to represent a different decision.
- Significant changes to an accepted decision should be documented in a new ADR.
- A new ADR may supersede an existing decision.
- The original ADR must remain available for historical traceability.
- Related architecture, data model, and implementation documents must be updated when necessary.
- The registry must reflect the latest status of every individual ADR.
- Minor editorial corrections that do not change the decision do not require a new ADR.
- Changes to a Proposed ADR may be made during review, provided its status remains accurate.
- Changes to document availability must be reflected in the registry.
- Changes to decision priority must be documented and justified where they affect implementation planning.

When an ADR is superseded, the original and replacement ADRs must cross-reference each other.

Historical decision records must be preserved. A status change must not erase the original decision history.

## 11. Review and Approval

Before an ADR is marked Accepted, reviewers should verify that:

- The problem is clearly defined.
- The proposed solution addresses the actual requirement.
- Alternatives have been considered fairly.
- The decision is consistent with the product architecture.
- Dependencies and trade-offs are understood.
- Security, reliability, cost, and operational implications have been considered.
- Legal and content-rights implications have been considered where relevant.
- Required changes to related documentation have been identified.
- The decision is sufficiently specific to guide implementation.
- The proposed approach is feasible within the project's technical and operational constraints.

The Project Owner is the final decision authority under the current project governance model.

Technical analysis and drafting assistance do not themselves constitute formal approval.

An ADR must not be marked Accepted without an explicit decision by the authorized decision owner.

## 12. Initial Priority for ADR Development

The following priorities are a suggested review order based on architectural risk and implementation dependencies.

| Priority | ADR | Reason |
|---|---|---|
| P0 | GENI-ADR-001 | Establishes the event-centric intelligence model. |
| P0 | GENI-ADR-002 | Separates article deduplication from event correlation. |
| P0 | GENI-ADR-011 | Defines event identity, continuation, merging, and splitting rules. |
| P0 | GENI-ADR-004 | Establishes publication outcomes and quality gates. |
| P0 | GENI-ADR-014 | Defines human review, corrections, and withdrawals. |
| P0 | GENI-ADR-006 | Establishes the shared provider-independent LLM execution boundary. |
| P0 | GENI-ADR-013 | Addresses content access, retention, licensing, and republication constraints. |
| P1 | GENI-ADR-008 | Defines evidence provenance and uncertainty representation. |
| P1 | GENI-ADR-012 | Defines semantic retrieval and similarity calculation. |
| P1 | GENI-ADR-015 | Distinguishes observed market reactions from source-reported and AI-inferred impact. |
| P1 | GENI-ADR-009 | Defines acquisition expectations and source handling. |
| P1 | GENI-ADR-005 | Establishes the initial persistence technology and migration strategy. |
| P1 | GENI-ADR-016 | Defines async execution, idempotency, and recovery requirements. |
| P1 | GENI-ADR-017 | Establishes LLM budgets, usage tracking, and evaluation strategy. |
| P1 | GENI-ADR-007 | Defines deterministic workflows and selective use of agent reasoning. |
| P2 | GENI-ADR-018 | Defines multilingual processing, translation, and language policy. |
| P2 | GENI-ADR-003 | Formalizes economic-intelligence scope and editorial prioritization. |
| P2 | GENI-ADR-010 | Defines the evolution of text, audio, and video delivery. |

This priority order is a planning recommendation, not an approval sequence or a requirement to create all ADRs before any implementation.

Dependencies discovered during review may change the order.

A P0 decision should be resolved before implementing the product capability that depends on it.

Work that does not depend on an unresolved decision may proceed only when its assumptions and limitations are explicitly documented.

## 13. Current Registry State

At the time of this revision:

- The ADR governance document exists.
- The ADR template exists.
- The ADR registry exists.
- Eighteen initial architectural decision topics have been identified.
- Six individual ADR documents currently exist in the local project working directory.
- `GENI-ADR-001` is published in the shared repository.
- `GENI-ADR-001` has Proposed status.
- `GENI-ADR-002`, `GENI-ADR-006`, `GENI-ADR-008`, `GENI-ADR-011`, and `GENI-ADR-013` are prepared locally and pending publication.
- All six existing individual ADRs have Proposed status.
- Twelve identified decision topics remain without individual ADR documents.
- No individual ADR is currently recorded as Accepted in this registry.
- No claim of implementation completion is implied by the existence or publication of an ADR.

The registry must be updated as additional ADR documents are created, published, reviewed, and approved.

The local document availability statements must be rechecked before committing this registry to the shared repository.

## 14. Final Governance Statement

This registry is an inventory and planning tool.

It does not independently approve architectural decisions, authorize implementation, or replace the Project Owner's decision authority.

The distinction between a decision topic, an unpublished draft, a locally prepared ADR, a published Proposed ADR, an Accepted ADR, and an implemented decision must be preserved throughout the project lifecycle.

The registry is the central reference for ADR inventory and status tracking. Individual ADR documents remain the authoritative records for their respective decision contexts, rationale, consequences, and approval history.

---

**End of Document**