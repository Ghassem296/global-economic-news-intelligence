# Global Economic News Intelligence
## Documentation Index

**Project:** Global Economic News Intelligence  
**Owner:** Project Owner  
**Document ID:** GENI-DOC-INDEX-001  
**Version:** 1.26
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-19

---

# 1. Purpose

This directory contains the official product, architecture, data design, implementation planning, architectural decision, documentation governance, and technical reference documentation for the Global Economic News Intelligence project.

It provides a structured documentation baseline for:

- Product vision, objectives, and scope.
- System architecture and component responsibilities.
- Domain entities, relationships, and storage design.
- Implementation stages and development priorities.
- Architectural decision records and governance.
- Documentation governance and change management.
- Documentation inventory and lifecycle management.
- Reusable engineering and technical references.

This documentation supports consistent project planning, architecture review, implementation, and maintenance.

Documentation must be treated as a controlled project asset. Proposed designs and recommendations must not be interpreted as approved requirements unless their approval status explicitly confirms that.

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
|-- 06-documentation-governance-and-change-management.md
|-- 07-documentation-registry.md
|-- 08-security-architecture-and-threat-model.md
|-- 09-api-and-integration-contracts.md
|-- 10-source-credibility-and-independence.md
|-- 11-economic-taxonomy-specification.md
|-- 12-testing-and-evaluation-strategy.md
|-- 13-deployment-operations-and-observability.md
|-- 14-data-protection-and-privacy-specification.md
|-- 15-first-slice-implementation-contracts.md
|
|-- adr/
|   |-- README.md
|   |-- adr-template.md
|   |
|   +-- decisions/
|       |-- GENI-ADR-001-event-centric-intelligence-architecture.md
|       |-- GENI-ADR-002-article-deduplication-and-event-matching.md
|       |-- GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md
|       |-- GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md
|       |-- GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md
|       |-- GENI-ADR-006-provider-independent-llm-execution-architecture.md
|       |-- GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md
|       |-- GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md
|       |-- GENI-ADR-009-near-real-time-news-acquisition-strategy.md
|       |-- GENI-ADR-010-phased-text-audio-and-video-delivery.md
|       |-- GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md
|       |-- GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md
|       |-- GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md
|       |-- GENI-ADR-014-human-review-corrections-and-withdrawals.md
|       |-- GENI-ADR-015-market-data-integration-and-economic-impact-classification.md
|       |-- GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md
|       |-- GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md
|       |-- GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md
|       |-- GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md
|       +-- GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md
|
+-- references/
    |
    +-- agent-template/
        |-- README.md
        |-- agent-template-architecture.md
        +-- agent-template-implementation-specification.md
```

This structure represents the published documentation baseline in the shared repository.

New documents and directories must be reflected in this index and in the relevant documentation registry.

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

## 3.5 Architecture Decision Records Governance

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

## 3.6 Documentation Governance and Change Management

**File:** `06-documentation-governance-and-change-management.md`  
**Document ID:** `GENI-GOV-006`

**Purpose:**

Defines how project documentation is created, reviewed, approved, versioned, changed, and maintained.

It establishes documentation lifecycle rules, responsibilities, metadata requirements, change control, and cross-document consistency requirements.

**Consult this document when:**

- Creating a new project document.
- Updating an existing document.
- Changing document status or version.
- Reviewing documentation quality.
- Coordinating changes across multiple documents.
- Maintaining historical documentation records.

**Authority:** Primary documentation governance and change-management reference.

## 3.7 Documentation Registry

**File:** `07-documentation-registry.md`  
**Document ID:** `GENI-GOV-007`

**Purpose:**

Provides the central inventory of project documentation.

It records document identifiers, titles, file paths, versions, statuses, responsibilities, and relationships.

**Consult this document when:**

- Finding the authoritative document for a topic.
- Checking document publication and review status.
- Identifying missing documentation.
- Reviewing document dependencies.
- Verifying the current documentation inventory.

**Authority:** Primary documentation inventory and registry reference.

## 3.8 Security Architecture and Threat Model

**File:** 08-security-architecture-and-threat-model.md  
**Document ID:** GENI-SEC-008

Defines trust boundaries, threats, authorization, secure processing, incident handling, and security verification.

## 3.9 API and Integration Contracts

**File:** 09-api-and-integration-contracts.md  
**Document ID:** GENI-API-009

Defines workflow, repository, provider, and external API contract rules, including errors, retries, idempotency, concurrency, pagination, and contract testing.

## 3.10 Source Credibility and Independence

**File:** 10-source-credibility-and-independence.md  
**Document ID:** GENI-SRC-010

Defines source reliability context, source relationships, information-origin independence, evidence aggregation, and provenance.

## 3.11 Economic Taxonomy Specification

**File:** 11-economic-taxonomy-specification.md  
**Document ID:** GENI-TAX-011

Defines proposed topic identifiers, hierarchy, multi-label classification, unknown states, versioning, and governance.

## 3.12 Testing and Evaluation Strategy

**File:** 12-testing-and-evaluation-strategy.md  
**Document ID:** GENI-EVAL-012

Defines verification layers, dataset governance, metric definitions, AI evaluation provenance, regression gates, and release evidence.

## 3.13 Deployment, Operations, and Observability

**File:** 13-deployment-operations-and-observability.md  
**Document ID:** GENI-OPS-013

Defines environment separation, runtime responsibilities, deployment controls, observability, recovery, capacity, runbooks, and readiness gates.

## 3.14 Data Protection and Privacy Specification

**File:** `14-data-protection-and-privacy-specification.md`  
**Document ID:** `GENI-PRIV-014`

Defines the proposed data-protection and privacy requirements, including the data inventory, processing purposes, minimization, retention and deletion, data-subject rights, processor and model-provider governance, international transfers, privacy incidents, and impact assessments.

This is an engineering specification, not legal advice, a jurisdiction-specific compliance determination, or evidence that production processing is authorized.

**Consult this document when:**

- Introducing or changing personal-data processing.
- Sending data to an LLM or other external processor.
- Defining retention, deletion, or data-subject request workflows.
- Evaluating derived data, embeddings, exports, backups, or provider-held artifacts.
- Reviewing international transfers, privacy incidents, or production readiness.

**Authority:** Primary privacy and personal-data protection specification. Content-rights authorization remains a separate control.

## 3.15 First-Slice Implementation Contracts

**File:** `15-first-slice-implementation-contracts.md`  
**Document ID:** `GENI-IMPL-015`

Defines the proposed method-level repository contracts, field-level DTO schema tranche, state-machine inventory, transaction write sets, idempotency and concurrency requirements, and approval/testing gates for the first implementation slice. ProcessingRun and ProcessingStep lifecycle contracts, EventMatchCase transitions, EventMatchCandidate evaluation lifecycle, PublicationDecision effective-successor rules, PublicationAttempt outcome mapping, ReviewRecord lifecycle, and DeliveryRecord/DeliveryAttempt transitions remain explicitly blocked pending cross-document reconciliation and Project Owner approval. It does not approve a database, programming-language serialization, provider, content-rights policy, or any Proposed ADR.

**Consult this document when:**

- Defining the first-slice repository interfaces and application commands.
- Reviewing transaction boundaries and aggregate write ownership.
- Writing repository contract, rollback, stale-write, and idempotency tests.
- Checking whether an implementation is blocked by an unapproved ADR or authorization policy.

**Authority:** Proposed implementation-contract baseline subordinate to approved ADRs and the architecture/data-model documents. It must not be treated as accepted until explicitly approved.

## 3.16 Related Privacy Architecture Decision

[GENI-ADR-020 — Data Protection, Privacy Processing Authorization, and Data Subject Rights Architecture](adr/decisions/GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md) defines the proposed privacy execution model across application workflows, data lineage, provider boundaries, and deletion propagation. It is related to Documents 02, 03, 08, 09, 12, 13, and 14. The ADR remains Proposed pending explicit approval.

# 4. Architectural Decision Records

**Directory:** `adr/`

Architectural Decision Records document the reasoning behind significant architectural choices.

Each ADR should describe the problem, relevant context, alternatives, evaluation criteria, recommendation, consequences, and final decision status.

## 4.1 ADR Registry

**File:** `adr/README.md`

**Purpose:**

Provides the central index of architectural decision topics, identifiers, priorities, dependencies, and current statuses.

The registry distinguishes between:

- Published ADR documents.
- Proposed decisions.
- Accepted decisions.
- Rejected decisions.
- Deprecated or superseded decisions.
- Planned topics without individual ADR documents.

The ADR registry is the primary reference for ADR inventory and status.

The documentation index must not duplicate the full ADR inventory or independently maintain ADR statuses.

## 4.2 ADR Template

**File:** `adr/adr-template.md`

**Purpose:**

Defines the standard structure for individual ADRs.

It provides a consistent format for documenting:

- Context and problem statement.
- Decision drivers.
- Alternatives considered.
- Evaluation and recommendation.
- Decision status.
- Positive and negative consequences.
- Implementation implications.
- Related decisions and references.

## 4.3 Individual ADR Documents

Individual ADR records are maintained exclusively in the [ADR Registry](adr/README.md). Consult that registry for the authoritative ADR inventory, identifiers, titles, priorities, repository paths, and current decision statuses.

This index intentionally does not reproduce individual ADR rows or decision statuses. The existence or publication of an ADR does not imply formal acceptance or implementation.

### Important ADR Rules

- A Proposed ADR is not an approved architectural decision.
- A recommendation is not equivalent to a final decision.
- Publication does not imply acceptance.
- Acceptance does not imply implementation.
- Implementation status must be tracked separately.
- Superseded decisions must remain traceable.
- The ADR registry and individual ADR files must remain consistent.

# 5. Documentation Governance

Documentation governance defines how project documentation is created, reviewed, approved, versioned, and maintained.

The following governance documents are published:

## 5.1 Documentation Governance and Change Management

**File:** `06-documentation-governance-and-change-management.md`  
**Document ID:** `GENI-GOV-006`

This document defines document ownership, metadata, lifecycle, versioning, change control, review responsibilities, and cross-document consistency requirements.

**Repository Status:** Published.

## 5.2 Documentation Registry

**File:** `07-documentation-registry.md`  
**Document ID:** `GENI-GOV-007`

This document provides a structured inventory of project documentation, including document identifiers, file paths, versions, statuses, and relationships.

**Repository Status:** Published.

These documents are part of the current documentation baseline. Their publication does not mean that every governance process or document has received final project-owner approval.

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

# 7. Recommended Reading Order

New contributors should follow this reading sequence:

1. `01-product-and-system-architecture.md`
2. `02-component-architecture-and-interfaces.md`
3. `03-data-model-and-storage-design.md`
4. `04-implementation-plan-and-roadmap.md`
5. `05-architecture-decision-records.md`
6. `06-documentation-governance-and-change-management.md`
7. `07-documentation-registry.md`
8. `adr/README.md`
9. Relevant individual ADRs.
10. Technical references relevant to the assigned implementation task.

The reading order may be adjusted according to the task, but contributors should understand the product architecture and relevant accepted decisions before implementing major changes.

# 8. Documentation Authority and Source of Truth

Each document has a defined responsibility.

| Question | Primary Reference |
|---|---|
| What are we building? | Product and System Architecture |
| How is the system structured? | Component Architecture |
| How is information represented and stored? | Data Model and Storage Design |
| In what order should we build it? | Implementation Plan |
| How are architectural decisions governed? | Architecture Decision Records Governance |
| Why was an architectural decision made? | Relevant ADR |
| Which ADRs exist and what is their status? | ADR Registry |
| How should documentation changes be managed? | Documentation Governance |
| Which documents exist and what is their status? | Documentation Registry |
| Which generic engineering practices may be reused? | Technical References |

The shared GitHub repository contains the published project documentation baseline.

A draft prepared outside the repository does not become part of that baseline merely because it has been written or reviewed.

When documents conflict:

1. Identify and record the conflict.
2. Review relevant accepted ADRs.
3. Identify the affected architecture and implementation documents.
4. Determine whether an ADR change is required.
5. Prepare coordinated documentation updates.
6. Obtain the required approval.
7. Publish the approved changes.
8. Update the relevant registries.
9. Verify cross-document consistency.

Conflicts must not be silently resolved by choosing whichever document is more convenient.

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
- Update the documentation registry.
- Update affected internal references.
- Verify all relative links.
- Review cross-document consistency.

When an ADR is created or its status changes:

- Update the ADR itself.
- Update the ADR registry.
- Review affected product and architecture documents.

The documentation index, documentation registry, and ADR registry must not contain conflicting publication or status information.

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

# 12. Planned Future Documentation

Additional documentation may be introduced as the product develops.

## 12.1 Product and Domain Specifications

Potential documents include:

- Event Intelligence and Correlation Specification.
- News Sources, Content Acquisition, and Rights Policy.
- Further taxonomy extensions only where a distinct domain need remains beyond GENI-TAX-011.
- Evidence and Claim Validation Specification.
- Reporting and Publication Specification.

## 12.2 Technical and Operational Specifications

The API, security, source credibility, economic taxonomy, testing/evaluation, operations, and privacy topics are now tracked in Documents 08–14. Further detailed specifications should be created only for distinct requirements not covered by the existing authoritative documents.

## 12.3 Future Intelligence Capabilities

Potential documents include:

- Audio Intelligence Architecture.
- Video Intelligence Architecture.
- Advanced Intelligence and Personalization Specification.

A new document should be created only when it has a distinct responsibility and provides clear value.

Its scope, ownership, dependencies, and relationship with existing documents should be reviewed before creation.

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
- Documentation registry entries match the actual repository.
- Unresolved questions are explicitly documented.
- Obsolete or duplicated content has been identified.
- Cross-document changes have been reviewed together.

A documentation baseline should be approved only after these checks have been completed.

---

**End of Document**

**Document ID:** `GENI-DOC-INDEX-001`  
**Document:** `docs/README.md`  
**Version:** 1.26  
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-19
