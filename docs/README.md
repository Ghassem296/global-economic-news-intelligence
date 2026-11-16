# Global Economic News Intelligence
## Documentation Index

**Project:** Global Economic News Intelligence
**Document:** `README.md`
**Version:** 1.4
**Status:** Draft — Under Documentation Review
**Last Updated:** 2026-11-16

---

# 1. Purpose

This directory contains the official product, architecture, data design, implementation planning, architectural governance, and supporting reference documentation for the Global Economic News Intelligence project.

It serves as the central documentation index for:

- Product objectives and scope.
- System architecture and component responsibilities.
- Domain entities, data structures, and storage design.
- Implementation stages and development priorities.
- Architectural decision governance and individual ADRs.
- Reusable engineering and generic Agent framework references.

This documentation is the primary reference for project planning and implementation.

**Important:** Relevant documentation and accepted architectural decisions must be reviewed before implementing or changing major system components.

---

# 2. Documentation Structure

The current documentation structure is:

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

The numbered documents define the product-specific documentation set.

The `adr/` directory contains the ADR registry, standard template, and individual architectural decision records.

The `references/` directory contains generic or reusable technical reference material. These references do not automatically define product implementation requirements.

---

# 3. Core Product Documentation

## 3.1 Product & System Architecture

**File:** `01-product-and-system-architecture.md`

**Purpose:**

Defines the product vision, functional scope, high-level architecture, system boundaries, and major design principles.

**Consult this document when:**

- Understanding the overall product.
- Changing product scope.
- Reviewing major system responsibilities.
- Evaluating a new high-level capability.

**Document Authority:** Primary product and system architecture reference.

## 3.2 Component Architecture & Interface Contracts

**File:** `02-component-architecture-and-interfaces.md`

**Purpose:**

Defines system components, responsibilities, dependencies, boundaries, and interface contracts.

**Consult this document when:**

- Designing a new component.
- Changing component responsibilities.
- Modifying interfaces or dependencies.
- Reviewing integration boundaries.

**Document Authority:** Primary component and interface reference.

## 3.3 Data Model & Storage Design

**File:** `03-data-model-and-storage-design.md`

**Purpose:**

Defines domain entities, relationships, persistence structures, data lifecycle, and storage design proposals.

**Consult this document when:**

- Adding or modifying a domain entity.
- Changing Article or Event relationships.
- Modifying database structures.
- Changing data retention or migration policies.

**Document Authority:** Primary data model and persistence design reference.

Technology and schema choices remain subject to their applicable ADRs until formally accepted.

## 3.4 Implementation Plan & Development Roadmap

**File:** `04-implementation-plan-and-roadmap.md`

**Purpose:**

Defines implementation stages, development sequence, dependencies, milestones, and acceptance criteria.

**Consult this document when:**

- Planning development work.
- Determining implementation priorities.
- Reviewing stage completion.
- Evaluating development dependencies.

**Document Authority:** Primary development planning reference.

## 3.5 Architecture Decision Records — Governance

**File:** `05-architecture-decision-records.md`

**Purpose:**

Defines the governance process for creating, reviewing, accepting, rejecting, superseding, and maintaining architectural decisions.

**Consult this document when:**

- Introducing a major architectural change.
- Selecting a technology or integration strategy.
- Reviewing an existing architectural assumption.
- Creating or evaluating an ADR.
- Managing architectural decision changes.

**Document Authority:** Primary ADR governance reference.

---

# 4. Architectural Decision Records

**Directory:** `adr/`

This directory contains the ADR registry, standard template, and individual architectural decision records.

## 4.1 ADR Registry

**File:** `adr/README.md`

Maintains the list of architectural decision topics, their identifiers, priorities, relationships, and current statuses.

## 4.2 ADR Template

**File:** `adr/adr-template.md`

Defines the standard structure for documenting an architectural decision, including context, alternatives, evaluation, recommendation, consequences, and decision history.

## 4.3 Individual ADRs

**Directory:** `adr/decisions/`

Individual decision records are maintained in this directory.

Currently documented:

- [GENI-ADR-001 — Event-Centric Intelligence Architecture](adr/decisions/GENI-ADR-001-event-centric-intelligence-architecture.md)

**Important:**

- Proposed ADRs are not approved architectural decisions.
- Only formally accepted ADRs represent approved decisions.
- A recommendation is not equivalent to an accepted decision.
- The ADR registry must accurately reflect the current status of every ADR.

---

# 5. Reference Documentation

**Directory:** `references/`

This directory contains generic or reusable technical reference material that is separate from the product-specific architecture.

## 5.1 Generic Agent Template

**Directory:** `references/agent-template/`

Contains two documents describing a reusable generic Agent framework.

- [Agent Template — Architecture](references/agent-template/agent-template-architecture.md)
- [Agent Template — Implementation Specification](references/agent-template/agent-template-implementation-specification.md)
- [Agent Template — Reference Documentation Index](references/agent-template/README.md)

These documents describe generic Agent architecture and implementation practices.

**Product-specific constraint:**

Their presence does not require Global Economic News Intelligence to implement a complete conversational Agent runtime.

The product follows a workflow-first architecture. Only generic capabilities that provide clear product value should be adopted.

Potentially reusable capabilities include:

- Provider-independent LLM execution.
- Structured output validation.
- Token and cost budgeting.
- Execution deadlines and cancellation.
- Retry policies.
- Security and input validation.
- Observability and evaluation.

Generic conversational memory, a general-purpose Agent loop, generic MCP integration, and multi-agent coordination are not automatically required.

The product-specific architecture and accepted ADRs take precedence over generic reference material.

---

# 6. Recommended Reading Order

New contributors should read the documentation in this order:

1. Product & System Architecture.
2. Component Architecture & Interface Contracts.
3. Data Model & Storage Design.
4. Implementation Plan & Development Roadmap.
5. Architecture Decision Records — Governance.
6. Relevant individual ADRs from the ADR registry.
7. Generic Agent Template references when working on applicable reusable infrastructure.

The reading order may be adjusted according to the task.

---

# 7. Source of Truth and Document Authority

The documents have different responsibilities and authority boundaries.

| Question | Authoritative Reference |
|---|---|
| What are we building? | Product & System Architecture |
| How is the system structured? | Component Architecture |
| How is information represented and stored? | Data Model & Storage Design |
| In what order should we build it? | Implementation Plan |
| How are architectural decisions governed? | ADR Governance |
| Why was a particular architectural decision made? | Accepted ADRs |
| What generic Agent practices may be reused? | Agent Template references |

If documents conflict, do not silently choose one.

Identify the conflict, review relevant accepted ADRs, determine the intended design, and update affected documents through the change management process.

A proposed ADR does not override an accepted ADR or an approved architectural baseline.

Generic reference documents do not override product-specific architecture.

---

# 8. Documentation Change Policy

All significant documentation changes must follow a controlled process:

1. Identify the requested change.
2. Determine which documents are affected.
3. Review relevant architectural decisions.
4. Analyze cross-document dependencies.
5. Prepare proposed changes.
6. Obtain the required approval.
7. Update affected documents.
8. Update version numbers and change history.
9. Verify documentation consistency.

Major architectural changes should be evaluated through an ADR before implementation.

For changes affecting multiple architectural documents, all affected documents must be reviewed together.

Documentation changes must not silently introduce architectural decisions that have not been reviewed or approved.

---

# 9. Documentation Maintenance

The documentation must be maintained as a living project asset.

The following information should be kept current:

- Document titles and file paths.
- Document versions and statuses.
- Related ADRs.
- Dependencies between documents.
- Last updated dates.
- Ownership and approval information where applicable.

When a document is added, renamed, or removed, this README must be updated.

The ADR registry must also be updated whenever an individual ADR is created or its status changes.

---

# 10. Documentation Rules

- Use English for official project documentation.
- Use descriptive, stable file names.
- Keep documents focused on their defined responsibilities.
- Avoid unnecessary duplication across documents.
- Link related documents instead of copying entire sections.
- Keep generic reference material separate from product-specific architecture.
- Record important architectural decisions in ADRs.
- Update documentation before or alongside implementation.
- Do not treat proposed decisions as approved requirements.
- Keep document versions and statuses accurate.
- Preserve consistency between architecture, data model, component contracts, and implementation roadmap.
- Distinguish established requirements from proposals and unresolved questions.

---

# 11. Future Documentation

Additional documents may be introduced as the product evolves, including:

## 11.1 Core Product Specifications

- Event Intelligence and Correlation Specification.
- News Sources, Content Acquisition and Rights Policy.
- Economic Taxonomy Specification.
- Evidence and Claim Validation Specification.
- Reporting and Publication Specification.

## 11.2 Technical and Operational Specifications

- API Specification.
- Security and Threat Model.
- Deployment and Operations Guide.
- Testing and Evaluation Strategy.
- Observability and Monitoring Specification.
- Data Retention and Recovery Policy.

## 11.3 Future Intelligence Capabilities

- Audio Intelligence Architecture.
- Video Intelligence Architecture.
- Advanced Intelligence and Personalization Specification.

New documents should be created only when they provide a distinct and useful responsibility.

Their scope and relationship with existing documents should be reviewed before creation.

---

# 12. Documentation Review and Approval

Before documentation is considered ready for implementation, verify that:

- All referenced files exist.
- Internal links and file paths are valid.
- Document numbering and naming are consistent.
- Responsibilities do not conflict across documents.
- Data model entities match component responsibilities.
- Implementation stages reflect architectural dependencies.
- Proposed decisions are clearly distinguished from accepted decisions.
- Unresolved architectural questions are explicitly documented.
- No obsolete or duplicated content remains.

A documentation baseline should be approved only after these checks have been completed.

---

**End of Document**

**Document:** `README.md`
**Version:** 1.4
**Status:** Draft — Under Documentation Review