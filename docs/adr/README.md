# Architecture Decision Records (ADR) Registry

**Project:** Global Economic News Intelligence
**Document:** Architecture Decision Records Registry
**Document ID:** GENI-ADR-REGISTRY-001
**Version:** 1.3
**Status:** Active
**Last Updated:** 2026-11-16

---

## 1. Purpose

This directory contains the Architecture Decision Records (ADRs) for the Global Economic News Intelligence project.

ADRs document significant architectural and technical decisions, including:

- The context and problem that require a decision.
- The options and alternatives considered.
- The selected approach and its rationale.
- Expected consequences, limitations, and trade-offs.
- Implementation, migration, and review implications.

The purpose of this registry is to maintain a clear, traceable, and consistent record of architectural decisions throughout the project lifecycle.

This registry tracks decision topics and their current status. It does not replace the individual ADR documents, which contain the complete decision rationale.

## 2. Directory Structure

The ADR directory follows this structure:

```text
docs/
|-- adr/
|   |-- README.md
|   |-- adr-template.md
|   |-- decisions/
|       |-- (Created when the first individual ADR is drafted)
```

### 2.1 Directory Responsibilities

| File or Directory | Responsibility |
|---|---|
| `README.md` | ADR registry, status tracking, and registry-level guidance |
| `adr-template.md` | Standard template for creating individual ADRs |
| `decisions/` | Contains individual ADR documents |

The `decisions/` directory may be created when the first individual ADR is drafted. Until then, its absence does not indicate a documentation error.

## 3. ADR Status Definitions

Every individual ADR must use one of the following statuses:

| Status | Meaning |
|---|---|
| Proposed | A decision topic has been identified and documented, but no formal decision has been approved. |
| Accepted | The decision has been reviewed and formally approved. |
| Rejected | The proposal has been reviewed and explicitly declined. |
| Deprecated | The decision is no longer recommended or applicable. |
| Superseded | The decision has been replaced by a newer ADR. |

A Proposed ADR must not be treated as an approved architectural constraint.

Only Accepted ADRs represent formally approved architectural decisions.

The registry status must reflect the status recorded in the corresponding individual ADR. A registry entry must not be marked Accepted without an actual ADR document and a recorded approval.

## 4. Initial ADR Registry

The following 18 decision topics have been identified for formal review.

All entries are currently **Proposed**. Their presence in this registry does not mean that the corresponding decisions have been finalized, approved, or implemented.

| ADR ID | Title | Status | Document |
|---|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | Proposed | Not created |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | Proposed | Not created |
| GENI-ADR-003 | Economic Intelligence as the Primary Editorial Focus | Proposed | Not created |
| GENI-ADR-004 | Publication Decisions, Quality Gates, and Automated Publishing Policy | Proposed | Not created |
| GENI-ADR-005 | Initial Persistence Technology and Migration Strategy | Proposed | Not created |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | Proposed | Not created |
| GENI-ADR-007 | Deterministic Workflows and Selective Agent Reasoning | Proposed | Not created |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | Proposed | Not created |
| GENI-ADR-009 | Near-Real-Time News Acquisition Strategy | Proposed | Not created |
| GENI-ADR-010 | Phased Text, Audio, and Video Delivery | Proposed | Not created |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | Proposed | Not created |
| GENI-ADR-012 | Semantic Retrieval, Similarity Calculation, and Embedding Storage | Proposed | Not created |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | Proposed | Not created |
| GENI-ADR-014 | Publication Decisions, Human Review, Corrections, and Withdrawals | Proposed | Not created |
| GENI-ADR-015 | Market Data Integration and Economic Impact Classification | Proposed | Not created |
| GENI-ADR-016 | Persistence, Async Execution, Idempotency, and Recovery | Proposed | Not created |
| GENI-ADR-017 | LLM Budgets, Usage Tracking, and Evaluation Strategy | Proposed | Not created |
| GENI-ADR-018 | Multilingual Source Processing, Translation, and Language Policy | Proposed | Not created |

### 4.1 Important Clarifications

The registry is an architectural decision backlog, not a list of approved design specifications.

Before implementation, each decision must be examined against relevant requirements and project documentation, including:

- Product requirements and system architecture.
- Component architecture and interface contracts.
- Data model and storage design.
- Implementation plan and development roadmap.
- Security, reliability, and operational requirements.
- Content rights, licensing, and applicable legal constraints.
- Evaluation, quality, and publication requirements.

Where existing documents describe an approach that has not been formally approved, that approach must remain provisional until the relevant ADR is accepted.

A Proposed ADR may be revised, split, combined, rejected, or superseded as the architecture becomes clearer.

### 4.2 Relationship Between Related ADRs

Some decision topics are closely related but address different questions.

In particular:

- **ADR-002** establishes the architectural separation between article deduplication and event matching.
- **ADR-011** defines event identity and the rules for matching, continuing, merging, and splitting events.
- **ADR-012** addresses semantic retrieval and similarity calculation as technical capabilities supporting event intelligence.
- **ADR-004** defines publication decisions and automated quality gates.
- **ADR-014** defines the operational review process, including human review, corrections, and withdrawals.
- **ADR-005** addresses the initial persistence technology and migration strategy.
- **ADR-016** addresses execution reliability, idempotency, and recovery.

Related ADRs should cross-reference one another where their decisions have dependencies. They must not duplicate or contradict each other's scope.

## 5. ADR Creation Rules

Every individual ADR must:

1. Use the standard structure defined in `adr-template.md`.
2. Have a unique and permanent ADR identifier.
3. Describe the problem and relevant architectural context.
4. Document meaningful alternatives.
5. Explain the selected decision and its rationale.
6. Identify positive and negative consequences.
7. Identify affected components, interfaces, and documents.
8. Describe implementation and migration implications where applicable.
9. Define the decision status.
10. Record the decision date and relevant reviewers.
11. Identify unresolved questions and assumptions.
12. Include references to related ADRs where appropriate.

### 5.1 File Naming Convention

Individual ADR files must use this naming convention:

`GENI-ADR-NNN-short-descriptive-title.md`

Examples:

- `GENI-ADR-001-event-centric-intelligence-architecture.md`
- `GENI-ADR-002-article-deduplication-and-event-matching.md`
- `GENI-ADR-011-event-identity-and-lifecycle.md`

Files must be stored inside the `decisions/` directory.

An ADR must only appear as a document link in the registry after its corresponding file has actually been created.

The ADR identifier in the document metadata, filename, and registry must match exactly.

ADR identifiers are permanent. A rejected or superseded ADR identifier must not be reused for an unrelated decision.

## 6. ADR Lifecycle

The expected ADR lifecycle is:

1. **Identification:** An architectural question or unresolved design choice is identified.
2. **Proposal:** An individual ADR is drafted using the standard template.
3. **Review:** Technical, product, security, operational, and other relevant implications are examined.
4. **Decision:** The proposal is accepted or rejected by the authorized decision owner.
5. **Implementation:** Accepted decisions are reflected in implementation and relevant documentation.
6. **Verification:** Implementation is checked against the accepted decision.
7. **Maintenance:** The ADR is reviewed when significant assumptions or architectural conditions change.
8. **Supersession or Deprecation:** The ADR may be replaced or retired when its assumptions are no longer valid.

Not every Proposed ADR must necessarily be accepted. Some may be rejected, combined, or replaced after further analysis.

Acceptance and implementation are separate activities. An Accepted ADR does not imply that its implementation is complete.

## 7. Relationship with Other Project Documents

ADRs complement the main project documentation.

| Document | Relationship to ADRs |
|---|---|
| `docs/README.md` | Defines the documentation structure and reading order. |
| `01-product-and-system-architecture.md` | Describes the overall product and system architecture. |
| `02-component-architecture-and-interfaces.md` | Defines system components and their contracts. |
| `03-data-model-and-storage-design.md` | Describes domain entities, persistence, and storage design. |
| `04-implementation-plan-and-roadmap.md` | Defines implementation stages, dependencies, and delivery priorities. |
| `05-agent-template-architecture.md` | Describes the generic Agent architecture reference. |
| `06-agent-template-implementation-specification.md` | Defines the generic Agent implementation reference. |
| `07-architecture-decision-records.md` | Defines ADR governance and decision-management rules. |

The generic Agent Template documents are reference material. Their presence does not automatically make every generic Agent capability a requirement for this product. Product-specific adoption must be justified by the relevant architecture and ADRs.

When an ADR is accepted and changes an architectural decision, all affected documents must be reviewed and updated.

The ADR records the reasoning behind the decision. The relevant architecture or specification document describes the resulting system design.

## 8. Change Management

The following rules apply to architectural changes:

- Accepted ADRs must not be silently rewritten to represent a different decision.
- Significant changes to an accepted decision should be documented in a new ADR.
- A new ADR may supersede an existing decision.
- The original ADR must remain available for historical traceability.
- Related architecture, data model, and implementation documents must be updated when necessary.
- The registry must reflect the latest status of every individual ADR.
- Minor editorial corrections that do not change the decision do not require a new ADR.
- Changes to a Proposed ADR may be made during review, provided its status remains accurate.

When an ADR is superseded, the original and replacement ADRs must cross-reference each other.

## 9. Review and Approval

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

For a small development team, the review process should remain lightweight and proportional to the impact of the decision.

Decisions with significant consequences for data integrity, event identity, security, publication, content rights, or system architecture should receive more careful review.

The designated project decision owner is responsible for approving or rejecting an ADR. Drafting assistance or technical analysis does not itself constitute formal approval.

## 10. Initial Priority for ADR Development

The following priorities are a suggested review order based on architectural risk and implementation dependencies.

| Priority | ADR | Reason |
|---|---|---|
| P0 | GENI-ADR-001 | Establishes the event-centric intelligence model. |
| P0 | GENI-ADR-002 | Separates article deduplication from event correlation. |
| P0 | GENI-ADR-011 | Defines event identity, continuation, merging, and splitting rules. |
| P0 | GENI-ADR-004 | Establishes publication outcomes and quality gates. |
| P0 | GENI-ADR-014 | Defines human review, corrections, and withdrawals, including the operational meaning of HOLD_FOR_REVIEW. |
| P0 | GENI-ADR-006 | Establishes the shared provider-independent LLM execution boundary. |
| P0 | GENI-ADR-013 | Addresses content access, retention, licensing, and republication constraints. |
| P1 | GENI-ADR-008 | Defines evidence provenance and uncertainty representation. |
| P1 | GENI-ADR-012 | Defines semantic retrieval and similarity calculation for event intelligence. |
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

A P0 decision should be resolved before implementing the product capability that depends on it. Work that does not depend on an unresolved decision may proceed only when its assumptions and limitations are explicitly documented.

## 11. Governance Principles

The ADR process follows these principles:

1. Decisions must be explicit and traceable.
2. Proposed decisions must not be confused with accepted decisions.
3. Architectural choices must be supported by requirements and reasoning.
4. Alternatives and trade-offs must be documented.
5. Important decisions must remain historically traceable.
6. Documentation must not claim that an implementation exists when it does not.
7. Architectural governance should be proportional to project complexity.
8. ADRs should reduce ambiguity rather than create unnecessary bureaucracy.
9. Related ADRs and project documents must remain consistent.
10. Acceptance, implementation, and verification must be tracked as distinct activities.

## 12. Current State

At the time of this document revision:

- The ADR governance document exists.
- The ADR template exists.
- The ADR registry exists.
- Eighteen initial architectural decision topics have been identified.
- All eighteen topics remain Proposed.
- No individual ADR decision documents have been created yet.
- The `decisions/` directory is reserved for future ADR documents.
- No Proposed ADR should be interpreted as an Accepted architectural decision.
- Existing architectural descriptions that depend on unresolved ADRs remain provisional where applicable.

The next step is to draft and review the highest-priority individual ADRs, beginning with the foundational event model, event identity, publication policy, review process, LLM execution boundary, and content-rights constraints.

Implementation should not treat unresolved proposals as finalized architectural decisions.

---

**End of Document**