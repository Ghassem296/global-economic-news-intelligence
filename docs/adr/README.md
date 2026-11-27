# Architecture Decision Records (ADR) Registry

**Project:** Global Economic News Intelligence  
**Owner:** Project Owner  
**Document:** Architecture Decision Records Registry  
**Document ID:** GENI-ADR-REGISTRY-001  
**Version:** 1.35
**Status:** Draft — Under Documentation Review  
**Last Updated:** 2026-11-27

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
    ├── evidence/
    │   └── GENI-ADR-005-persistence-proof-of-concept-protocol.md
    └── decisions/
        ├── GENI-ADR-001-event-centric-intelligence-architecture.md
        ├── GENI-ADR-002-article-deduplication-and-event-matching.md
        ├── GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md
        ├── GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md
        ├── GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md
        ├── GENI-ADR-006-provider-independent-llm-execution-architecture.md
        ├── GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md
        ├── GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md
        ├── GENI-ADR-009-near-real-time-news-acquisition-strategy.md
        ├── GENI-ADR-010-phased-text-audio-and-video-delivery.md
        ├── GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md
        ├── GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md
        ├── GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md
        ├── GENI-ADR-014-human-review-corrections-and-withdrawals.md
        ├── GENI-ADR-015-market-data-integration-and-economic-impact-classification.md
        ├── GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md
        ├── GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md
        ├── GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md
        ├── GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md
        └── GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md
```

### 2.1 Directory Responsibilities

| File or Directory | Responsibility |
|---|---|
| `README.md` | ADR registry, status tracking, and registry-level guidance |
| `adr-template.md` | Standard template for creating individual ADRs |
| `decisions/` | Contains individual architectural decision records |

The `decisions/` directory contains the individual ADR documents published in the shared repository.

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
| Withdrawn | The proposal has been withdrawn before acceptance. |

A Proposed ADR must not be treated as an approved architectural constraint.

Only Accepted ADRs represent formally approved architectural decisions.

Acceptance and implementation are separate activities. An Accepted ADR does not imply that its implementation is complete.

The decision status recorded in the registry must match the status in the corresponding individual ADR.

## 4. Initial ADR Inventory

The project has identified twenty architectural decision topics.

The registry distinguishes between:

- The existence of a decision topic.
- The existence and availability of an individual ADR file.
- The current decision status.
- The implementation status of the decision.

These are separate properties and must not be confused.

### 4.1 Individual ADR Documents

The following twenty individual ADR documents are committed to the published main branch. All twenty have status Proposed; none is an approved architectural decision.

| ADR ID | Title | Document Availability | Decision Status | Repository Path |
|---|---|---|---|---|
| GENI-ADR-001 | Event-Centric Intelligence Architecture | Published | Proposed | `decisions/GENI-ADR-001-event-centric-intelligence-architecture.md` |
| GENI-ADR-002 | Article Deduplication and Event Matching Separation | Published | Proposed | `decisions/GENI-ADR-002-article-deduplication-and-event-matching.md` |
| GENI-ADR-003 | Economic Intelligence as the Primary Editorial Focus | Published | Proposed | `decisions/GENI-ADR-003-economic-intelligence-as-primary-editorial-focus.md` |
| GENI-ADR-004 | Publication Decisions, Quality Gates, and Automated Publishing Policy | Published | Proposed | `decisions/GENI-ADR-004-publication-decisions-quality-gates-and-automated-publishing-policy.md` |
| GENI-ADR-005 | Initial Persistence Technology and Migration Strategy | Published | Proposed | `decisions/GENI-ADR-005-initial-persistence-technology-and-migration-strategy.md` |
| GENI-ADR-006 | Provider-Independent LLM Execution Architecture | Published | Proposed | `decisions/GENI-ADR-006-provider-independent-llm-execution-architecture.md` |
| GENI-ADR-007 | Deterministic Workflows and Selective Agent Reasoning | Published | Proposed | `decisions/GENI-ADR-007-deterministic-workflows-and-selective-agent-reasoning.md` |
| GENI-ADR-008 | Evidence Provenance and Uncertainty Representation | Published | Proposed | `decisions/GENI-ADR-008-evidence-provenance-and-uncertainty-representation.md` |
| GENI-ADR-009 | Near-Real-Time News Acquisition Strategy | Published | Proposed | `decisions/GENI-ADR-009-near-real-time-news-acquisition-strategy.md` |
| GENI-ADR-010 | Phased Text, Audio, and Video Delivery | Published | Proposed | `decisions/GENI-ADR-010-phased-text-audio-and-video-delivery.md` |
| GENI-ADR-011 | Event Identity, Matching, Continuation, Merging, and Splitting | Published | Proposed | `decisions/GENI-ADR-011-event-identity-matching-continuation-merging-and-splitting.md` |
| GENI-ADR-012 | Semantic Retrieval, Similarity Calculation, and Embedding Storage | Published | Proposed | `decisions/GENI-ADR-012-semantic-retrieval-similarity-calculation-and-embedding-storage.md` |
| GENI-ADR-013 | News Content Access, Full-Text Retention, Licensing, and Republishing | Published | Proposed | `decisions/GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md` |
| GENI-ADR-014 | Human Review, Corrections, and Withdrawals | Published | Proposed | `decisions/GENI-ADR-014-human-review-corrections-and-withdrawals.md` |
| GENI-ADR-015 | Market Data Integration and Economic Impact Classification | Published | Proposed | `decisions/GENI-ADR-015-market-data-integration-and-economic-impact-classification.md` |
| GENI-ADR-016 | Persistence, Async Execution, Idempotency, and Recovery | Published | Proposed | `decisions/GENI-ADR-016-persistence-async-execution-idempotency-and-recovery.md` |
| GENI-ADR-017 | LLM Budgets, Usage Tracking, and Evaluation Strategy | Published | Proposed | `decisions/GENI-ADR-017-llm-budgets-usage-tracking-and-evaluation-strategy.md` |
| GENI-ADR-018 | Multilingual Source Processing, Translation, and Language Policy | Published | Proposed | `decisions/GENI-ADR-018-multilingual-source-processing-translation-and-language-policy.md` |
| GENI-ADR-019 | Event Importance, Economic Relevance, and Economic Impact Assessment Methodology | Published | Proposed | `decisions/GENI-ADR-019-event-importance-economic-relevance-and-economic-impact-assessment-methodology.md` |
| GENI-ADR-020 | Data Protection, Privacy Processing Authorization, and Data Subject Rights Architecture | Published | Proposed | `decisions/GENI-ADR-020-data-protection-privacy-processing-authorization-and-data-subject-rights.md` |

**Publication terminology:**

- **Published** means the document is committed to and available in the shared Git repository.
- **Not created** means no individual ADR document currently exists in the repository.
- **Proposed** means the architectural proposal has been documented but has not been formally approved.
- **Accepted** means the decision has been formally approved by the authorized decision owner.

Document availability and decision status are independent properties.

The publication of an ADR does not imply that its proposal has been accepted.

The existence of an ADR file does not imply that its implementation is complete.

### 4.2 Decision Topics Without Individual ADR Documents

All twenty registered decision topics currently have individual ADR files in published main branch. There are no remaining uncreated topics in the current registry.

Document publication does not imply approval. All twenty ADRs remain Proposed pending explicit Project Owner decisions.

### 4.3 Inventory Rules

- A decision topic may exist before its individual ADR is drafted.
- An ADR document must not be marked Published until it is committed and available in the shared repository.
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
- **ADR-004** defines publication decisions, publication outcomes, and automated quality gates.
- **ADR-014** defines the operational human review process, including corrections and withdrawals.
- **ADR-005** addresses initial persistence technology and migration strategy.
- **ADR-016** addresses execution reliability, idempotency, and recovery.
- **ADR-006** defines the provider-independent LLM execution boundary.
- **ADR-017** addresses LLM budgets, usage tracking, and evaluation.
- **ADR-019** defines the separate assessment semantics and methodology boundaries for event importance, economic relevance, and economic impact.
- **ADR-015** addresses market data integration and observed impact classification; it must not replace the broader assessment semantics defined by ADR-019.
- **ADR-013** addresses content access, retention, licensing, and republication constraints.
- **ADR-010** addresses the phased delivery of text, audio, and video.

The GENI-ADR-005 evidence directory contains the persistence proof-of-concept protocol. It is a test protocol, not an ADR, test result, benchmark, or approval; its status and evidence artifacts must remain distinct from the decision status of ADR-005.

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
5. **Publication:** The ADR document is committed to the shared repository with its accurate status.
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
| P0 | GENI-ADR-013 | Addresses content access, retention, licensing, and republication constraints. |
| P0 | GENI-ADR-020 | Establishes privacy processing authorization, personal-data lineage, processor governance and data-subject rights before production personal-data processing. |
| P1 | GENI-ADR-008 | Defines evidence provenance and uncertainty representation. |
| P1 | GENI-ADR-012 | Defines semantic retrieval and similarity calculation. |
| P1 | GENI-ADR-015 | Distinguishes observed market reactions from source-reported and AI-inferred impact. |
| P1 | GENI-ADR-009 | Defines acquisition expectations and source handling. |
| P1 | GENI-ADR-005 | Establishes the initial persistence technology and migration strategy. |
| P1 | GENI-ADR-016 | Defines async execution, idempotency, and recovery requirements. |
| P1 | GENI-ADR-017 | Establishes LLM budgets, usage tracking, and evaluation strategy. |
| P1 | GENI-ADR-007 | Defines deterministic workflows and selective use of agent reasoning. |
| P1 | GENI-ADR-006 | Required before provider-backed LLM execution; not a prerequisite for the deterministic fixture slice. |
| P1 | GENI-ADR-019 | Defines the separate Event Importance, Economic Relevance, and Economic Impact assessment boundaries required by core reporting. |
| P2 | GENI-ADR-018 | Defines multilingual processing, translation, and language policy. |
| P2 | GENI-ADR-003 | Formalizes economic-intelligence scope and editorial prioritization. |
| P2 | GENI-ADR-010 | Defines the evolution of text, audio, and video delivery. |

This priority order is a planning recommendation, not an approval sequence or a requirement to create all ADRs before any implementation.

Every registered ADR must appear exactly once in this priority table. Adding or renumbering an ADR requires updating the priority inventory in the same change.

Dependencies discovered during review may change the order.

A P0 decision should be resolved before implementing the product capability that depends on it.

Work that does not depend on an unresolved decision may proceed only when its assumptions and limitations are explicitly documented.

## 13. Current Registry State

At the time of this revision:

- The ADR governance document exists.
- The ADR template exists.
- The ADR registry exists.
- Twenty architectural decision topics are registered.
- All twenty individual ADR documents are committed to the published main branch.
- All twenty ADRs have Proposed status.
- No registered decision topic remains without an individual ADR document in this branch.
- No individual ADR is currently recorded as Accepted in this registry.
- No claim of implementation completion is implied by the existence or publication of an ADR.

The registry must be updated as ADR documents are revised, reviewed, accepted, rejected, superseded, or withdrawn.

The publication status must be verified against the shared repository. Decision status must be verified against the metadata of each individual ADR.

## 14. Final Governance Statement

This registry is an inventory and planning tool.

It does not independently approve architectural decisions, authorize implementation, or replace the Project Owner's decision authority.

The distinction between an identified decision topic, an ADR that has not yet been created, a published Proposed ADR, an Accepted ADR, and an implemented decision must be preserved throughout the project lifecycle.

The registry is the central reference for ADR inventory and status tracking. Individual ADR documents remain the authoritative records for their respective decision contexts, rationale, consequences, and approval history.

---

**End of Document**

**Revision Note (v1.19):** Records the PostgreSQL owner-selected target status for GENI-ADR-005 v1.5. The ADR remains Proposed pending qualification evidence and formal acceptance.

**Revision Note (v1.20):** Synchronizes the ADR inventory with GENI-ADR-005 v1.6. PostgreSQL remains the owner-selected target; qualification and formal acceptance remain pending.

**Revision Note (v1.21):** Records GENI-ADR-005-POC-001 v1.4 and clarifies the distinction between PostgreSQL target selection and production qualification.

**Revision Note (v1.22):** Records GENI-ADR-005 v1.7 and PoC-001 v1.5, which adds the owner-approved workload-profile template while keeping all workload values and thresholds explicitly unset.

**Revision Note (v1.23):** Synchronizes the ADR inventory after GENI-ADR-005 v1.8, PoC-001 v1.6, and GENI-ADR-016 v1.2 clarified the separation between isolated PoC-only candidate tooling and production approval. Both ADRs remain Proposed; no production database dependency or capability is authorized.

**Revision Note (v1.24):** Records the first successful partial PostgreSQL PoC run documented in PoC-001 v1.7. The run produced 16 passing test methods but does not qualify PostgreSQL or accept ADR-005/ADR-016; backup/restore, security review, full process-restart recovery, workload approval, and production acceptance remain outstanding.

**Revision Note (v1.25):** Records the follow-up PoC-001 v1.8 run with 18 passing test methods, including full-database logical backup/restore, a child-process restart/reconnect exercise, and a least-privilege role smoke test. The PoC remains experimental; concurrent-write backup, backup protection/retention, workload and performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.26):** Records PoC-001 v1.9 and the successful concurrent-write full-database backup/restore run, plus the third SQL migration. All 18 test methods pass; backup security/retention, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.27):** Updates GENI-ADR-005 to v1.9 to reference the reproducible 18-test partial PoC evidence. ADR-005 remains Proposed; PostgreSQL is not production-qualified and no production toolchain or migration is approved.

**Revision Note (v1.28):** Synchronizes GENI-ADR-005 v2.0 and PoC-001 v1.10 with the latest successful 18-test run, including experimental authenticated-backup protection and private file permissions. Production key management, retention, off-site protection, restore authorization, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.29):** Synchronizes GENI-ADR-005 v2.1 and PoC-001 v1.11 with the successful 19-test PostgreSQL run, which adds clean-instance restoration and verification of user-defined cluster roles and memberships. Full cluster/tablespace/configuration recovery, secret recovery, production key management, retention, restore authorization, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.30):** Synchronizes GENI-ADR-005 v2.2 and PoC-001 v1.12 with the successful 20-test run. POC-20 verifies a dedicated read-only `pg_read_all_data` backup identity can dump and restore synthetic database contents without write, superuser, CREATEDB, or CREATEROLE privileges. Production credential lifecycle, retention enforcement, restore authorization, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.31):** Synchronizes GENI-ADR-005 v2.3 and PoC-001 v1.13 with the successful 20-test rerun using distinct backup and restore identities. The restore identity owns only the isolated target database and cannot write to the source database. Production credential lifecycle, retention enforcement, restore authorization, off-site protection, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.32):** Synchronizes GENI-ADR-005 v2.4 and PoC-001 v1.14 with the successful 21-test PostgreSQL run. POC-21 adds a fail-closed retention planner that requires explicit policy, preserves the minimum verified-copy count, legal holds, and immutability windows, and produces deterministic candidates without deleting or scheduling backups. Production retention values/enforcement, credential lifecycle, off-site protection, restore authorization, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.33):** Synchronizes GENI-ADR-005 v2.5 and PoC-001 v1.15 with the successful 24-test rerun: 20 PostgreSQL integration methods and four standalone retention-policy unit tests. The new tests validate malformed/future-dated metadata, immutability expiry boundaries, and deterministic ordering. Production retention policy/enforcement, credential lifecycle, off-site protection, restore authorization, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.34):** Synchronizes GENI-ADR-005 v2.6 and PoC-001 v1.16 with the successful 25-test run. POC-22 verifies transactional rollback of partial DDL and migration-history updates after an injected migration failure. Production migration tooling, rollback/recovery procedures, retention enforcement, credential lifecycle, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.

**Revision Note (v1.35):** Synchronizes GENI-ADR-005 v2.7 and PoC-001 v1.17 with the successful 26-test run. POC-23 verifies migration reapplication is idempotent and preserves the original migration-history timestamps. Production migration tooling, rollback/recovery procedures, retention enforcement, credential lifecycle, full cluster recovery, workload/performance qualification, and formal ADR acceptance remain open.
