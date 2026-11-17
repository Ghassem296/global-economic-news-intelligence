# Global Economic News Intelligence
## Documentation Index

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-DOC-INDEX-001  
**Version:** 1.5  
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-17

---

# 1. Purpose

This directory contains the official product, architecture, data design, implementation planning, architectural decision, and technical reference documentation for the Global Economic News Intelligence project.

It provides a structured documentation baseline for:

- Product vision, objectives, and scope.
- System architecture and component responsibilities.
- Domain entities, relationships, and storage design.
- Implementation stages and development priorities.
- Architectural decision records and governance.
- Documentation governance and change management.
- Reusable engineering and technical references.

This documentation supports consistent project planning, architecture review, implementation, and maintenance.

Documentation must be treated as a controlled project asset. Proposed designs and recommendations must not be interpreted as approved requirements unless their approval status explicitly confirms that.

---

# 2. Documentation Structure

The documentation is organized into three main categories:

1. Core product and architecture documentation.
2. Architectural decision records.
3. Supporting technical references.

The current repository structure is:

```text
docs/
|
|-- README.md
|
|-- 01-product-and-system-architecture.md
|-- 02-component-architecture-and-interfaces.md
|-- 03-data-model-and-storage-design.md
|-- 04-implementation-plan-and-roadmap.md
|-- 05-architecture-decision-records.md
|
|-- adr/
|   |-- README.md
|   |-- adr-template.md
|   |
|   +-- decisions/
|       +-- GENI-ADR-001-event-centric-intelligence-architecture.md
|
+-- references/
    |
    +-- agent-template/
        |-- README.md
        |-- agent-template-architecture.md
        +-- agent-template-implementation-specification.md
```

Additional governance documents and individual ADRs are being prepared. They must be added to this structure only after review and approval for publication.

---

# 3. Core Product and Architecture Documentation

The following documents define the product-specific architecture and development baseline.

## 3.1 Product and System Architecture

**File:** `01-product-and-system-architecture.md`  
**Document ID:** `GENI-ARCH-001`

**Purpose:**

Defines the product vision, objectives, functional scope, high-level architecture, system boundaries, and fundamental design principles.

The architecture follows a workflow-first and event-centric intelligence approach rather than assuming that the product must be implemented as a general-purpose conversational Agent.

**Consult this document when:**

- Understanding the overall product.
- Changing product scope or objectives.
- Reviewing system boundaries.
- Evaluating a new high-level capability.
- Assessing whether a proposed architecture supports the product's objectives.

**Authority:** Primary product and system architecture reference.

## 3.2 Component Architecture and Interface Contracts

**File:** `02-component-architecture-and-interfaces.md`  
**Document ID:** `GENI-ARCH-002`

**Purpose:**

Defines the system's major components, responsibilities, dependencies, boundaries, and interface contracts.

It describes how the collection, normalization, event intelligence, analysis, reporting, and delivery capabilities interact.

**Consult this document when:**

- Designing or modifying a component.
- Changing component responsibilities.
- Defining service or module interfaces.
- Reviewing integration boundaries.
- Evaluating dependencies and execution flows.

**Authority:** Primary component and interface reference.

## 3.3 Data Model and Storage Design

**File:** `03-data-model-and-storage-design.md`  
**Document ID:** `GENI-DATA-003`

**Purpose:**

Defines the domain model, entities, relationships, persistence structures, data lifecycle, and storage design.

It establishes the conceptual distinction between sources, articles, events, claims, evidence, analysis, market observations, reports, and delivery records.

**Consult this document when:**

- Adding or modifying a domain entity.
- Changing Article and Event relationships.
- Modifying persistence structures.
- Designing data provenance.
- Changing data lifecycle, retention, or migration policies.

**Authority:** Primary data model and storage design reference.

Specific database technologies and unresolved storage decisions remain subject to their applicable ADRs.

## 3.4 Implementation Plan and Development Roadmap

**File:** `04-implementation-plan-and-roadmap.md`  
**Document ID:** `GENI-PLAN-004`

**Purpose:**

Defines the development stages, implementation sequence, dependencies, milestones, and acceptance criteria.

The roadmap should prioritize an early end-to-end product workflow and measurable evaluation rather than implementing infrastructure without a demonstrated product need.

**Consult this document when:**

- Planning development work.
- Determining implementation priorities.
- Reviewing stage dependencies.
- Evaluating milestone completion.
- Defining the next implementation increment.

**Authority:** Primary implementation planning reference.

## 3.5 Architecture Decision Governance

**File:** `05-architecture-decision-records.md`  
**Document ID:** `GENI-GOV-005`

**Purpose:**

Defines the governance principles and process for proposing, reviewing, accepting, rejecting, superseding, and maintaining architectural decisions.

It distinguishes recommendations, proposed decisions, and formally accepted decisions.

**Consult this document when:**

- Introducing a significant architectural change.
- Selecting a technology or integration strategy.
- Reviewing an existing architectural assumption.
- Creating or evaluating an ADR.
- Managing a change to an accepted architectural decision.

**Authority:** Primary architectural decision governance reference.

---

# 4. Architectural Decision Records

**Directory:** `adr/`

Architectural Decision Records document the reasoning behind significant architectural choices.

Each ADR should describe the problem, relevant context, alternatives, evaluation criteria, recommendation, consequences, and final decision status.

## 4.1 ADR Registry

**File:** `adr/README.md`

**Purpose:**

Provides the central index of ADR topics, identifiers, priorities, dependencies, and current statuses.

The registry must distinguish:

- Published ADRs.
- Proposed ADRs.
- Accepted ADRs.
- Rejected or superseded ADRs.
- Planned ADR topics that have not yet been drafted.

The registry must reflect the actual repository state and must not present unpublished drafts as existing repository files.

## 4.2 ADR Template

**File:** `adr/adr-template.md`

**Purpose:**

Defines the standard structure for individual ADRs.

It provides a consistent format for documenting context, alternatives, evaluation, recommendations, consequences, decision records, and implementation implications.

## 4.3 Individual ADRs

**Directory:** `adr/decisions/`

Individual architectural decisions are stored in this directory.

### Published ADR

**GENI-ADR-001 — Event-Centric Intelligence Architecture**

File:

`adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md`

This ADR proposes an event-centric intelligence architecture in which Articles and Events remain distinct domain entities connected through explicit relationships.

Its key architectural concerns include:

- Separation of Article and Event identities.
- Many-to-many Article–Event relationships.
- Event dossier construction.
- Uncertain event matching.
- Event history and traceability.
- Separation of evidence, claims, and analysis.

Its status must be checked in the ADR itself and the ADR registry before treating its recommendations as formally accepted decisions.

### Additional ADR Drafts

The following ADRs have been prepared as drafts but are not yet part of the published repository baseline:

- **GENI-ADR-002:** Article Deduplication and Event Matching.
- **GENI-ADR-008:** Evidence Provenance and Uncertainty Representation.

They must not be treated as published or accepted decisions until their publication and approval status has been formally updated.

Other planned architectural topics are tracked through the ADR planning process.

**Important ADR rules:**

- A Proposed ADR is not an approved architectural decision.
- A recommendation is not equivalent to a final decision.
- Accepted does not automatically mean implemented.
- Implementation status must be tracked separately.
- Superseded decisions must remain traceable.
- The registry and individual ADR files must remain consistent.

---

# 5. Documentation Governance

Documentation governance defines how project documentation is created, reviewed, approved, versioned, and maintained.

The following governance documents are planned:

## 5.1 Documentation Governance and Change Management

**Planned file:** `06-documentation-governance-and-change-management.md`  
**Document ID:** `GENI-GOV-006`

**Purpose:**

Defines document ownership, metadata, lifecycle, versioning, change control, review responsibilities, and cross-document consistency requirements.

**Status:** Draft prepared; pending project owner approval and publication.

## 5.2 Documentation Registry

**Planned file:** `07-documentation-registry.md`  
**Document ID:** `GENI-GOV-007`

**Purpose:**

Provides a structured inventory of project documentation, including document identifiers, file paths, versions, statuses, and relationships.

**Status:** Draft prepared; pending project owner approval and publication.

Until these documents are published, this README and the existing ADR registry remain part of the current documentation index.

---

# 6. Technical Reference Documentation

**Directory:** `references/`

This directory contains generic or reusable technical reference material.

Reference documents provide engineering guidance but do not automatically define product-specific implementation requirements.

## 6.1 Generic Agent Template

**Directory:** `references/agent-template/`

This directory contains documentation for a reusable generic Agent framework.

Files:

- `references/agent-template/README.md`
- `references/agent-template/agent-template-architecture.md`
- `references/agent-template/agent-template-implementation-specification.md`

These references describe generic Agent architecture, implementation patterns, and reusable engineering capabilities.

### Product-Specific Constraint

Global Economic News Intelligence follows a workflow-first architecture.

The existence of generic Agent reference material does not require the product to implement a complete conversational Agent runtime.

Potentially reusable capabilities include:

- Provider-independent LLM execution.
- Structured input and output validation.
- Token and cost budgeting.
- Execution deadlines and cancellation.
- Retry and fallback policies.
- Security and input validation.
- Observability and evaluation.

The following capabilities are not automatically required:

- Generic conversational memory.
- A general-purpose Agent execution loop.
- Generic MCP integration.
- Multi-agent coordination.
- Autonomous tool execution.

Each capability must be justified by a concrete product requirement and reviewed against the product architecture.

Product-specific architecture and formally accepted ADRs take precedence over generic reference material.

---

# 7. Recommended Reading Order

New contributors should follow this reading sequence:

1. `01-product-and-system-architecture.md`
2. `02-component-architecture-and-interfaces.md`
3. `03-data-model-and-storage-design.md`
4. `04-implementation-plan-and-roadmap.md`
5. `05-architecture-decision-records.md`
6. `adr/README.md`
7. Relevant individual ADRs.
8. Technical references relevant to the assigned implementation task.

Documentation governance documents should also be reviewed when they become approved and published.

The reading order may be adjusted according to the task, but contributors should understand the product architecture and relevant accepted decisions before implementing major changes.

---

# 8. Documentation Authority and Source of Truth

Each document has a defined responsibility.

| Question | Primary Reference |
|---|---|
| What are we building? | Product and System Architecture |
| How is the system structured? | Component Architecture |
| How is information represented and stored? | Data Model and Storage Design |
| In what order should we build it? | Implementation Plan |
| How are architectural decisions governed? | Architecture Decision Governance |
| Why was an architectural decision made? | Relevant ADR |
| Which ADRs exist and what is their status? | ADR Registry |
| How should documentation changes be managed? | Documentation Governance |
| Which generic engineering practices may be reused? | Technical References |

The GitHub repository's approved and published files constitute the project documentation baseline.

A draft prepared outside the repository does not become part of that baseline merely because it has been written or reviewed.

When documents conflict:

1. Identify and record the conflict.
2. Review relevant accepted ADRs.
3. Identify the affected architecture and implementation documents.
4. Determine whether an ADR change is required.
5. Prepare coordinated documentation updates.
6. Obtain the required approval.
7. Update the affected documents together.

Conflicts must not be silently resolved by choosing whichever document is more convenient.

---

# 9. Documentation Change Policy

Significant documentation changes must follow a controlled process.

The expected process is:

1. Identify the requested change.
2. Determine which documents are affected.
3. Review relevant ADRs and existing requirements.
4. Analyze cross-document dependencies.
5. Prepare the proposed changes.
6. Review technical and architectural consistency.
7. Obtain the required approval.
8. Publish the approved changes.
9. Update document versions, dates, and registry entries.
10. Verify links, paths, and cross-document references.

Major architectural changes should be evaluated through an ADR before implementation whenever practical.

Changes affecting multiple architecture documents should be reviewed together.

Documentation must not silently introduce unreviewed architectural decisions.

---

# 10. Documentation Maintenance Rules

The documentation set must remain consistent with the actual project state.

The following information must be maintained:

- Document identifiers and titles.
- File paths and naming conventions.
- Document versions and statuses.
- Last updated dates.
- Relationships and dependencies.
- Related ADRs.
- Approval and implementation status where applicable.

When a document is added, renamed, moved, or removed:

- Update this README.
- Update the documentation registry when published.
- Update affected internal references.
- Verify all relative links.
- Review cross-document consistency.

When an ADR is created or its status changes:

- Update the ADR itself.
- Update the ADR registry.
- Review affected product and architecture documents.

---

# 11. Documentation Rules

All official project documentation must follow these rules:

- Use English for official project documents.
- Use stable and descriptive file names.
- Assign a unique document identifier.
- Keep each document focused on its defined responsibility.
- Avoid unnecessary duplication.
- Reference related documents instead of copying entire sections.
- Separate generic references from product-specific requirements.
- Record significant architectural decisions in ADRs.
- Distinguish facts, requirements, proposals, recommendations, and unresolved questions.
- Do not treat Proposed decisions as approved requirements.
- Keep document versions and statuses accurate.
- Preserve consistency across architecture, data models, interfaces, and implementation plans.
- Do not claim that a document is published unless it exists in the repository.
- Do not claim that an architectural decision is accepted unless its status confirms approval.

---

# 12. Planned Future Documentation

Additional documentation may be introduced as the product develops.

## 12.1 Product and Domain Specifications

Potential documents include:

- Event Intelligence and Correlation Specification.
- News Sources, Content Acquisition, and Rights Policy.
- Economic Taxonomy Specification.
- Evidence and Claim Validation Specification.
- Reporting and Publication Specification.

## 12.2 Technical and Operational Specifications

Potential documents include:

- API Specification.
- Security and Threat Model.
- Deployment and Operations Guide.
- Testing and Evaluation Strategy.
- Observability and Monitoring Specification.
- Data Retention and Recovery Policy.

## 12.3 Future Intelligence Capabilities

Potential documents include:

- Audio Intelligence Architecture.
- Video Intelligence Architecture.
- Advanced Intelligence and Personalization Specification.

A new document should be created only when it has a distinct responsibility and provides clear value.

Its scope, ownership, dependencies, and relationship with existing documents should be reviewed before creation.

---

# 13. Documentation Review Checklist

Before considering a documentation baseline ready for implementation, verify that:

- All referenced published files exist.
- Planned documents are clearly identified as unpublished.
- Internal links and relative paths are valid.
- Document identifiers and filenames are consistent.
- Document responsibilities do not conflict.
- Data model entities match component responsibilities.
- Interface contracts match the architecture.
- Implementation stages reflect architectural dependencies.
- Proposed and accepted decisions are clearly distinguished.
- ADR registry statuses match the individual ADR files.
- Unresolved questions are explicitly documented.
- Obsolete or duplicated content has been identified.
- Cross-document changes have been reviewed together.

A documentation baseline should be approved only after these checks have been completed.

---

**End of Document**

**Document ID:** `GENI-DOC-INDEX-001`  
**Document:** `README.md`  
**Version:** 1.5  
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-17