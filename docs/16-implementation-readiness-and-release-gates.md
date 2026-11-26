# GENI-READY-016 — Implementation Readiness and Release Gates

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-READY-016  
**Version:** 4.1  
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-26  
**Baseline:** Published `main` snapshot reviewed on 2026-11-26

---

## 1. Purpose and authority

This document records the implementation-readiness assessment of the published repository and defines the evidence required to move from architecture review into implementation.

It is a coordination and readiness document. It does not approve an ADR, select a technology, grant a source license, authorize personal-data processing, or override Documents 01–15. Where a required decision remains Proposed or a contract remains explicitly unresolved, this document preserves that gate rather than inventing a default.

The authority order is:

1. An accepted ADR governs the architectural decision within its scope.
2. Approved product, architecture, data, security, privacy, and implementation specifications define the applicable requirements.
3. Document 15 defines the first-slice repository and application contract baseline, subject to its approval gates.
4. This document reports readiness and links the outstanding evidence; it cannot supersede those sources.

A published file, passing documentation check, or merged change is not by itself an approval of an architectural decision.

## 2. Assessment result

**Overall status: FOUNDATION IMPLEMENTED; NOT READY for the complete first vertical slice or production operation.**

The repository is no longer documentation-only. It now contains an installable Python package, a minimal CLI, pure domain lifecycle policies, unit tests, Ruff/mypy configuration, and a dedicated application CI workflow.

The initial executable foundation was originally checked on Python 3.12 and 3.13. That historical matrix has been superseded: the current project runtime policy is Python 3.15 only. Python 3.15 compatibility is now verified by the successful main-branch Application CI run 45465238823 (commit 80ad85993bbfaa5073df4123d7dcc1bf5d42a0fd), which completed Ruff, mypy, and pytest successfully.

- Python package metadata and supported runtime range (Python 3.15 only; `>=3.15,<3.16`).
- Pure lifecycle policies for ProcessingRun, ProcessingStep, EventMatchCase, EventMatchCandidate, publication/delivery external operations, and ReviewRecord actions.
- A CLI that reports package version and disabled capability boundaries, using validated settings and safe logging initialization.
- Unit tests for transition guards, aggregation, successor-decision linearity, review projection, external-outcome reconciliation, validated configuration, safe errors/logging, and domain dependency boundaries.
- Application CI for Python 3.15 only, running Ruff, mypy, and pytest; the current main-branch run passed (45465238823).
- Existing documentation CI and registry validation remain separate and are preserved.

The lifecycle rules are now specified in GENI-FOUNDATION-017 and cross-referenced by Documents 03 and 15. This closes the prior logical state-machine specification gap; it does not implement durable state persistence, attempt storage, or transaction enforcement.

The project package-management choice is now uv 0.13.9, pinned by `[tool.uv].required-version` in `pyproject.toml`; the setuptools build backend is pinned to 84.2.1. A committed `uv.lock` records the complete resolved development dependency graph with artifact hashes for the Python 3.15 target. Application CI verifies lock freshness with `uv lock --check`, installs with `uv sync --locked --extra dev`, and runs Ruff, mypy, and pytest without re-resolving dependencies. The lock was generated and its locked installation and quality checks were verified on CPython 3.15.2 using uv 0.13.9. This closes the current dependency-resolution reproducibility gap for the declared Python project environment. It does not establish artifact provenance for every upstream package, guarantee offline builds, or approve any database, LLM provider, source, or deployment architecture.

The following remain absent or incomplete:

- No selected physical database, driver, ORM, or migration mechanism; GENI-ADR-005 remains Proposed.
- No durable repositories, UnitOfWork, migrations, lease/idempotency persistence, or ProcessingStepAttempt adapter.
- Document 15 v4.0 now defines the first source and article-to-report command/query DTO tranches and a proposed command-to-permission crosswalk; Document 08 v1.9 now defines deny-by-default role boundaries and a minimum operation-permission catalogue. These are proposed logical baselines only. Final role-to-permission grants, policy administration, exact field bounds/canonicalization, and Project Owner approval remain incomplete.
- Validated environment/log-level configuration, safe error-envelope primitives, and allowlisted structured JSON logging now exist; centralized exception mapping, metrics, tracing, alerting, and operational telemetry remain incomplete.
- A pure, fail-closed content-rights persistence gate now exists for exact source/content scope and PERSISTENT_STORAGE assessments. Rights evidence verification, freshness policy, limited-retention deadlines, temporary-content lifecycle, persistence, revocation propagation, deletion, and operation-specific external-processing enforcement remain unimplemented.
- No source acquisition, rights adapter, LLM execution adapter, economic analysis workflow, report generator, publication client, or delivery client.
- No application integration, concurrency, crash-recovery, or end-to-end vertical-slice tests.
- All 20 ADRs remain Proposed in the current registry snapshot.

Therefore, the repository is ready for continued foundation and domain implementation. It is not yet ready to claim a complete first-slice implementation or to process production content.

## 3. What may proceed now

The following work can proceed without pretending that unresolved architecture has been approved:

1. Documentation maintenance, cross-document reconciliation, and automated documentation checks.
2. Review of ADR alternatives and recording of explicit decisions by the Project Owner.
3. Completion and review of remaining field-level DTO schemas, final role-to-permission assignments, persistence/transaction proofs, attempt/history records, and integration contracts. The initial deny-by-default authorization matrices and first-slice command crosswalk now exist in Documents 08 and 15, but they do not grant runtime permissions or complete the approval gate. The logical lifecycle tables for the implemented pure policies are already specified in GENI-FOUNDATION-017; their durable persistence and transactional enforcement remain outstanding.
4. Technology proof-of-concepts that are isolated, disposable, and clearly labelled as experiments; they must not become hidden production commitments.
5. Fixture design and human-reviewed evaluation-dataset preparation, provided fixtures are synthetic or their use is authorized.
6. The existing Python 3.15-only package and CLI are a bounded development foundation recorded in GENI-FOUNDATION-017, not an approval of the production application stack. Additional application capabilities that depend on unresolved technology or architecture decisions may proceed only after the relevant ADR and specification gates are satisfied.

The following must remain disabled until their gates pass: production source collection, full-text retention, external LLM transmission of source content, automatic event creation/matching, material review actions, publication execution, delivery dispatch, and processing of personal data beyond an approved test context.

## 4. First-slice decision scope

Do not require all 20 ADRs to be accepted before any work begins. Accept or explicitly defer decisions according to the capabilities actually included in the first slice.

### 4.1 Foundational decisions

The following decisions affect the architecture or invariants of the first slice and must be resolved before dependent application code treats their recommendations as policy:

- **GENI-ADR-001 and 002:** event-centric architecture and the separation of article deduplication from event matching.
- **GENI-ADR-005:** persistence technology and migration strategy, after the workload/backup/concurrency proof-of-concept.
- **GENI-ADR-007:** deterministic workflow boundaries. GENI-ADR-006 is capability-dependent because the first slice makes no provider or LLM call.
- **GENI-ADR-008:** evidence provenance and uncertainty representation.
- **GENI-ADR-011:** event identity and matching lifecycle.

### 4.2 Capability-dependent decisions

These decisions are required before enabling the corresponding capability:

| Decision | Required before |
|---|---|
| GENI-ADR-003 | Finalizing editorial scope and economic-intelligence prioritization |
| GENI-ADR-004 | Enabling publication eligibility policy, creating an authoritative PublicationDecision, or any publication operation |
| GENI-ADR-006 | Enabling provider-backed LLM execution or external LLM transmission; not required for deterministic fixture analysis |
| GENI-ADR-009 | Selecting and operating near-real-time acquisition mechanisms |
| GENI-ADR-012 | Enabling semantic retrieval or embedding persistence |
| GENI-ADR-013 | Accessing, transmitting, retaining, deriving from, or republishing real source content under the relevant rights rules |
| GENI-ADR-014 | Enabling material human-review actions, corrections, or withdrawals |
| GENI-ADR-015 | Integrating market data or describing market observations as measured |
| GENI-ADR-016 | Enabling durable asynchronous execution, leases, fencing, idempotency, and recovery |
| GENI-ADR-017 | Enabling governed LLM budgets, usage accounting, and evaluation policy |
| GENI-ADR-018 | Enabling cross-language analytical processing, multilingual model-based classification/matching, or translation; source-language identification and preservation remain baseline metadata requirements |
| GENI-ADR-019 | Enabling the governed importance/relevance/impact assessment methodology |
| GENI-ADR-020 | Processing personal data or enabling provider/region-specific privacy authorization |

An ADR may be deferred only when its capability is excluded and the implementation boundary enforces that exclusion. A deferred ADR must not be treated as implicitly accepted.

## 5. Remaining implementation blockers

The logical lifecycle contracts for the first-slice state machines are now specified and implemented as pure policies in GENI-FOUNDATION-017. The blockers below concern the persistence, authorization, integration, and operational enforcement of those rules.

### 5.1 Field-level DTO and command schemas

Document 15 §10.11–10.13 provides field-level DTO tranches for the core article-to-report flow, source configuration/identity and command-to-permission crosswalk. Section 10.14 defines separate structured-output baselines for Importance, Economic Relevance and Economic Impact; §10.15 defines ReportContent and ReportGenerationProvenance; §10.16 adds the pairwise article-deduplication repository, authorization and DTO contracts. These are proposed logical baselines only. Document 03 v1.52 now requires actor and immutable authorization references on both duplicate candidate and decision records, bound to their exact operation scope.
For every actual provider request, Document 15 v4.0 requires an LLMUsageRecord linked to the exact Analysis and/or ProcessingRun/ProcessingStep and carrying the applicable privacy-authorization decision, processing purpose, data category, region, transfer assessment, content-rights decision references, provider/model, prompt/schema versions, outcome and retry provenance. Document 08 v1.9 adds the independent `privacy.processing.authorize` permission bound to the exact purpose, operation, data category, payload/input fingerprint, provider/model and region. Privacy authorization must independently ALLOW that exact request, and source-content rights must separately cover the exact payload and use; missing, unknown, expired, revoked or mismatched references block egress.
Remaining work includes the explicit blockers in Document 15 §§10.10.1, 10.11.9, 10.12.5, 10.13.2, 10.14.5, 10.15.4 and 10.16.4: exact serialization/bounds/canonicalization, remaining query/report-family schemas, assessment vocabularies/scales/uncertainty calibration, template/input-manifest identity, duplicate-pair canonicalization and score/decision calibration, final grant assignments and policy-administration contracts. These documents remain Proposed and do not authorize execution.

### 5.2 Persistence and transaction implementation

Complete the PostgreSQL qualification in GENI-ADR-005-POC-001 using an approved workload profile and predeclared thresholds; retain raw results, failed runs, environment/configuration, commit SHA, migration and backup/restore evidence. PostgreSQL is the Project Owner-selected target, but the protocol is a test plan, not a test result or production authorization. GENI-ADR-005 must be formally Accepted, and all PostgreSQL qualification gates must pass, before production activation. Then implement:
- Database adapter, migrations, repository implementations, and UnitOfWork.
- Optimistic concurrency and unique constraints for idempotency and linear decision successors, including canonical DuplicateCandidate pairs and one linear DuplicateDecision chain per candidate.
- ProcessingStepAttempt, state-transition history, PublicationAttempt, and DeliveryAttempt persistence.
- Atomic write sets for decision pointer and ArticleEventLink reconciliation.
- Atomic EvidenceLocation, AnalysisInput/AnalysisEvidenceLink, and ReportEventLink/ReportEvidenceLink/ReportArticleLink/ReportAnalysisLink writes through the parent aggregate repositories; child link persistence must not commit independently.
- Atomic review action sequencing and projection updates.
- Durable leases, fencing, idempotency records, and recovery.
- Backup/restore and crash-recovery tests.

### 5.3 Security, source rights, and privacy

Implement and test fail-closed authorization at each operation boundary using the proposed deny-by-default baseline in Document 08 §5 and the first-slice crosswalk in Document 15 §10.13. Final role grants, identity/session lifecycle, policy decision point, grant administration, separation-of-duties exceptions and break-glass controls remain open. GENI-ADR-013 must govern real source-content access/retention/transmission; GENI-ADR-020 and Document 14 govern personal-data processing and provider/region authorization. Unknown, expired, revoked, or mismatched authorization must deny the operation.

### 5.4 LLM and analysis execution

Complete the bounded provider-independent execution contract, structured output validation, budgets, usage tracking, model/prompt/schema provenance, timeout classification, and retry behavior under ADRs 006, 007, and 017. Before any provider network egress, enforce the independent privacy-processing authorization and exact source-content-rights decision for the immutable payload/input fingerprint, purpose, operation, data category, provider/model and region; require an applicable transfer assessment and persist the resulting references in the LLMUsageRecord linked to the exact Analysis and/or ProcessingRun/ProcessingStep. Re-evaluate authorization for retries or any changed request context. Missing, unknown, expired, revoked, or mismatched authorization/rights references fail closed. Provider egress remains disabled until the applicable ADRs and approval gates pass. Model output remains a proposal and cannot directly mutate authoritative state.

### 5.5 Review, publication, and delivery

Lifecycle mechanics are specified, but material review actions, publication policy, and external operations remain disabled until ADR-004/014, reviewer authorization, publication target contracts, distribution authorization, and rights/privacy gates are satisfied. External unknown outcomes must be reconciled before retry.

### 5.6 End-to-end verification

Build a synthetic/authorized-fixture vertical slice from Source and ArticleRevision through deduplication, event matching, evidence, analysis, and Report version. Verify exact provenance, idempotency, concurrency, rollback, recovery, and absence of unauthorized external effects. PublicationDecision and publication eligibility are explicitly outside this slice until GENI-ADR-004 and dependent gates are accepted.

## 6. Cross-document consistency rules

The following rules apply across Documents 01–17 and all ADRs:

1. **Selected project tooling is distinct from unresolved architecture candidates.** Document 04 §4.1 records CPython 3.15, uv 0.13.9, setuptools 84.2.1, pytest, Ruff, and mypy as the bounded development toolchain. Pydantic, LiteLLM, SQLAlchemy, Alembic, exact PostgreSQL driver/version, source-acquisition mechanisms, and deployment choices remain candidates or pending decisions; they must not be treated as approved application architecture until their relevant ADR and evidence gates pass. PostgreSQL itself is the owner-selected target, subject to its qualification and production-activation gate.
2. **Language-neutral contracts remain language-neutral until approval.** Document 15's `ID<T>`, `Version`, `Instant`, `Fingerprint`, and DTO notation must not be silently translated into a concrete representation before the runtime/serialization decision.
3. **Domain decisions remain distinct from workflow state.** Candidate evaluation, case resolution, review tasks, publication eligibility, external publication attempts, and delivery attempts are separate concepts.
4. **Unknown is not failure, zero, denial, or absence.** Unknown external outcomes require reconciliation; unknown rights/authorization context fails closed.
5. **No LLM output directly performs a material domain transition.** LLM results are validated inputs to deterministic application/domain policies.
6. **Rights and privacy are operation-specific.** Permission to fetch does not imply permission to retain, embed, send to an LLM, derive, publish, or deliver.
7. **Provenance is version-bound.** Reports and assessments must retain exact input revisions, evidence references, methodology/prompt/model versions where applicable, and uncertainty.
8. **No production capability is enabled by documentation alone.** Each capability requires accepted decisions, implementation, tests, and operational evidence.

## 7. Readiness gates and evidence

A first-slice implementation may start only when all applicable gates below have evidence recorded in the repository.

| Gate | Required evidence | Pass condition |
|---|---|---|
| R0 — Product and architecture baseline | Scope statement, accepted foundational ADRs, reconciled architecture/data/component documents | No unresolved contradiction affecting the selected slice; deferred capabilities are explicitly disabled |
| R1 — Technology baseline | Accepted ADR-005 backed by completed PostgreSQL qualification in GENI-ADR-005-POC-001; approved workload profile and predeclared thresholds; raw correctness, concurrency, migration, backup/restore and recovery evidence; exact language/runtime, package manager, PostgreSQL version/driver, migration, async, transaction and connection-lifecycle choices | Every mandatory correctness and workload gate passes; reproducible evidence and operational feasibility are reviewed; selected engine and exact implementation choices are recorded in the Accepted ADR |
| R2 — Contract baseline | Approved Document 15; complete DTO schemas and transition matrices for every enabled workflow | No enabled workflow depends on an unresolved state, field, authorization, or concurrency rule |
| R3 — Security, rights, and privacy | Threat-model controls, operation-specific rights decisions, privacy authorization boundaries, secret handling | Deny/unknown/expired/revoked/scope-mismatch cases fail closed; test-source permissions are documented |
| R4 — Executable foundation | Installable application package, pinned dependencies, validated configuration, safe errors, structured logging, CI, migrations | Clean setup succeeds; tests/lint/type checks run without paid production services |
| R5 — Domain and persistence verification | Contract tests, schema constraints, transaction tests, concurrency/idempotency/failure-injection tests | Required invariants are demonstrated, not merely documented |
| R6 — Vertical-slice verification | End-to-end fixture run and trace preserving provenance from ArticleRevision through duplicate/event decisions, Evidence, Analysis, and Report | Reproducible run; no unauthorized side effect; all enabled-slice quality gates and budgets enforced |
| R7 — Operational release | Backup/restore, recovery, observability, incident and rollback procedures, deployment security | Operational acceptance criteria in Documents 13 and 04 are demonstrated |

Passing an earlier gate does not imply that a later gate has passed. A gate may be passed for a limited capability while other capabilities remain disabled.

## 8. CI and repository automation

The repository now has two independent CI workflows:

- Documentation validation: .github/workflows/docs-validation.yml runs documentation validator unit tests and checks controlled document versions and ADR inventory.
- Application CI: .github/workflows/ci.yml installs the package and development tools on Python 3.15 only, then runs Ruff, mypy, and pytest.

Passing application CI proves package quality checks and unit tests for the implemented foundation only. It does not prove database transactions, migrations, concurrency, provider contracts, source rights, LLM quality, or end-to-end product behavior. Those require separate integration and release evidence.

## 9. First-slice scope guard

The first executable vertical slice should remain deliberately narrow and fixture-driven until the relevant source and privacy decisions are accepted.

The slice should prove the core chain:

1. Persist an authorized test Source and Article/ArticleRevision.
2. Normalize and fingerprint the revision.
3. Evaluate duplicate candidates and record an explicit immutable decision.
4. Create/reuse an EventMatchCase and immutable candidate evaluations.
5. Record an explicit EventMatchDecision; apply ArticleEventLink only for the effective MATCH outcome.
6. Attach typed evidence with exact provenance and rights references.
7. Persist a versioned structured analysis with uncertainty.
8. Create an immutable Report version with provenance.
9. Stop at the immutable Report version and its provenance. Publication eligibility is outside this slice.

For `NEW_EVENT_CANDIDATE`, persist the proposal only; do not create an Event until the applicable policy and GENI-ADR-011 gate are approved. For `AMBIGUOUS` or `REVIEW_REQUIRED`, preserve the unresolved outcome and do not execute a material ReviewService action until GENI-ADR-014 and its contracts are approved. Analysis and Report in this slice use deterministic fixtures; no LLM or provider call is part of first-slice acceptance. Do not create or persist an authoritative `PublicationDecision`, evaluate publication eligibility, create a `PublicationRecord`/`PublicationAttempt`, or dispatch delivery; those capabilities remain disabled until GENI-ADR-004 and all dependent review, rights, authorization, and target contracts are accepted. The `PublicationDecisionRepository` contract in Document 15 is dormant in this slice.

The first slice must not silently expand to production crawling, full-text retention, semantic search, market data, cross-language analytical processing, translation, provider-backed LLM execution, publication eligibility, audio/video, user personalization, external publication, or delivery. Source-language identification and preservation of the original-language representation are metadata/provenance requirements, not a claim of multilingual analytical coverage. Each excluded capability is separately gated.

## 10. Correction policy and limitations

This assessment is based on the published repository snapshot identified above. It does not claim that local uncommitted work, external legal advice, provider agreements, or unlinked operational evidence do not exist.

If new evidence changes readiness, update this document and the affected source-of-truth documents together. Do not change an ADR status merely to make a readiness table appear complete. An ADR becomes Accepted only through the approval process defined in Documents 05 and the ADR registry.

---

## 11. Related documents

- README.md — repository status and entry point.
- Document 01 — Product and System Architecture.
- Document 02 — Component Architecture and Interface Contracts.
- Document 03 — Data Model and Storage Design.
- Document 04 — Implementation Plan and Development Roadmap.
- Document 05 — Architecture Decision Records Governance.
- Document 07 — Documentation Registry.
- Document 08 — Security Architecture and Threat Model.
- Document 09 — API and Integration Contracts.
- Document 12 — Testing and Evaluation Strategy.
- Document 13 — Deployment, Operations, and Observability.
- Document 14 — Data Protection and Privacy Specification.
- Document 15 — First-Slice Implementation Contracts.
- Document 17 — Executable Foundation and Domain Lifecycle Contracts.
- GENI-ADR-001 through GENI-ADR-020, as applicable to the enabled capability.

---

**Document ID:** GENI-READY-016  
**Version:** 4.1
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Last Updated:** 2026-11-26

**Revision Note (v2.8):** Tightened R1 and persistence blockers to require completed GENI-ADR-005-POC-001 evidence and formal ADR-005 acceptance before selecting a production database. Aligned the first-slice scope guard with Document 04 v1.31: new-event proposals remain proposals, ambiguous/review-required outcomes remain unresolved without material review actions, and Analysis/Report are fixture-driven with no LLM or external side effects. No ADR approval is implied.

**Revision Note (v3.0):** Recorded successful Python 3.15 main-branch Application CI verification and the then-open dependency reproducibility gap.

**Revision Note (v3.1):** Records uv 0.13.9 as the selected package manager, setuptools 84.2.1 as the pinned build backend, the committed Python 3.15 `uv.lock`, and successful locked dependency installation and quality checks. This resolves the package-resolution gap only; database selection, persistence proofs, contracts, security, rights, and vertical-slice gates remain open.

**Revision Note (v3.3):** Makes provider-independent LLM execution capability-dependent rather than a prerequisite for the deterministic first slice; removes authoritative PublicationDecision creation from that slice until ADR-004 is accepted; separates source-language metadata preservation from multilingual analysis/translation gated by ADR-018; and records the corresponding disabled capabilities. No ADR is accepted by this documentation change.

**Revision Note (v3.4):** Aligns the persistence readiness gate with the Project Owner-selected PostgreSQL target. PostgreSQL qualification and formal ADR-005 acceptance remain mandatory before production activation.

**Revision Note (v3.5):** At that revision, the source-aware mixed content-retention direction from GENI-ADR-013 Alternative C had been selected, while the ArticleRevision metadata-only fingerprint and exact content-hash semantics were still open. Document 15 v4.0 and Document 03 v1.52 now resolve the fingerprint/hash contract; source-specific rights and production authorization remain gated. ADR-013 remains Proposed.

**Revision Note (v3.7):** Records the versioned ArticleRevision semantic fingerprint and separate retained-content hash contract defined in Document 15 v4.0 / Document 03 v1.52. Metadata-only/unavailable revisions persist no content reference/hash/normalization version; current-revision-only comparison preserves append-only history when content later returns to an earlier state. Source-specific rights, production persistence and PostgreSQL qualification remain gated; ADR-013 remains Proposed.

**Revision Note (v3.8):** Aligns the readiness baseline with the ArticleRevision author snapshot added to Documents 03 v1.50 and 15 v3.8. Source-specific metadata allowlists, production rights enforcement, retention deletion, repositories, and PostgreSQL qualification remain gated.

**Revision Note (v3.9):** Records the application-layer ArticleRevision command envelope, which composes the common CommandMetadata with the revision payload without duplicating expected-version or authorization metadata. This remains a command contract; ArticleRevisionService, rights enforcement, repositories, and persistence are not implemented.

**Revision Note (v4.0):** Records the immutable ArticleRevisionRecord persistence result and technology-neutral ArticleRevisionRepository port. The Article projection repository, application service, rights adjudication, and concrete persistence adapters remain unimplemented.

**Revision Note (v4.1):** Aligns the rights-status model with Document 03 v1.52: Article.rights_status is a display/monitoring summary only, while every restricted operation requires a current RightsAssessment for its exact operation and content scope.

**End of Document**
