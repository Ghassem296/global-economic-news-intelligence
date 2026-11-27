# GENI-READY-016 — Implementation Readiness and Release Gates

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-READY-016  
**Version:** 4.69  
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-27  
**Baseline:** Implementation/code snapshot reviewed through 2026-11-27 commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70`; ArticleRevision URL-validation hardening and unambiguous source-identity authorization resource serialization are included; Application CI, Documentation Validation, and PostgreSQL 18.7 PoC are verified on this exact commit

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

The initial executable foundation was originally checked on Python 3.12 and 3.13. That historical matrix has been superseded: the current project runtime policy is Python 3.15 only. On current main commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70`, Application CI run `45981896909` completed locked dependency installation, Ruff, mypy, and pytest with all 296 tests passing; Documentation Validation run `45981897073` passed all 23 validator tests and the repository-wide documentation checks; PostgreSQL 18.7 / Python 3.15 PoC run `45981896934` passed all 32 test methods (28 PostgreSQL integration methods and four standalone retention-policy unit tests; artifact `15189922078`). The PoC artifact for this exact commit confirms `successful: true`, zero failures, and zero skipped tests.

The current-code CI and PostgreSQL evidence above applies to the exact reviewed `main` commit. It verifies the shared structural HTTP(S) URL validator and its Source/ArticleRevision regression coverage as included in that commit. The PostgreSQL run remains an isolated correctness PoC, not production qualification or authorization.

- Python package metadata and supported runtime range (Python 3.15 only; `>=3.15,<3.16`).
- Pure lifecycle policies for ProcessingRun, ProcessingStep, EventMatchCase, EventMatchCandidate, publication/delivery external operations, and ReviewRecord actions.
- An executable ArticleRevisionService with technology-neutral ArticleRepository and ArticleRevisionRepository ports. It coordinates authorization, fail-closed rights checks, command idempotency, immutable revision append/reuse, and Article projection updates through one injected UnitOfWork; current tests are unit-level and do not qualify durable adapters or database concurrency.
- A CLI that reports package version and disabled capability boundaries, using validated settings and safe logging initialization.
- Unit tests for transition guards, aggregation, successor-decision linearity, review projection, external-outcome reconciliation, validated configuration, safe errors/logging, and domain dependency boundaries.
- Application CI for Python 3.15 only, running Ruff, mypy, and pytest; current `main` commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70` passed 296 tests, Ruff, and mypy (run `45981896909`).
- Existing documentation CI and registry validation remain separate and are preserved.

The lifecycle rules are now specified in GENI-FOUNDATION-017 and cross-referenced by Documents 03 and 15. This closes the prior logical state-machine specification gap; it does not implement durable state persistence, attempt storage, or transaction enforcement.

The project package-management choice is now uv 0.13.9, pinned by `[tool.uv].required-version` in `pyproject.toml`; the setuptools build backend is pinned to 84.2.1. A committed `uv.lock` records the complete resolved development dependency graph with artifact hashes for the Python 3.15 target. Application CI verifies lock freshness with `uv lock --check`, installs with `uv sync --locked --extra dev`, and runs Ruff, mypy, and pytest without re-resolving dependencies. The lock was generated and its locked installation and quality checks were verified on CPython 3.15.2 using uv 0.13.9. This closes the current dependency-resolution reproducibility gap for the declared Python project environment. It does not establish artifact provenance for every upstream package, guarantee offline builds, or approve any database, LLM provider, source, or deployment architecture.

The following remain absent or incomplete:

- PostgreSQL is the Project Owner-selected target relational engine. The latest isolated PoC-only run against PostgreSQL 18.7 with Psycopg 3.3.9 passed all 32 test methods (28 PostgreSQL integration methods and four standalone retention-policy unit tests) on commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70` (GitHub Actions run `45981896934`, evidence artifact `15189922078`). POC-29 verifies concurrent ArticleRevision append/current-pointer compare-and-swap: one writer commits and the stale writer's revision insert rolls back. POC-24 through POC-27 verify concurrent migration execution, same-Article current-revision integrity, decision-case/outcome constraints, and source-identity index integrity. POC-28 verifies an atomic synthetic legacy Article revision backfill candidate, including rollback on an invalid deferred pointer and commit of a valid same-Article revision/pointer pair. POC-29 verifies competing ArticleRevision appends against the same expected Article version; only one writer advances the current pointer and the losing transaction leaves no extra revision. This is partial PoC evidence, not production qualification or approval of the legacy backfill policy. Production KMS/HSM integration, key custody/rotation, retention enforcement, off-site/immutable protection, restore authorization, full cluster/tablespace/configuration/secret recovery, formal security review, approved workload values, and performance thresholds remain outstanding. GENI-ADR-005 remains Proposed.
- The ArticleRevisionService and technology-neutral ArticleRepository/ArticleRevisionRepository ports are implemented, but no durable repository or UnitOfWork adapter, transactional idempotency store, concrete authorization/rights adapter, production migrations, lease/fencing persistence, or ProcessingStepAttempt adapter exists.
- Document 15 v4.10 now defines the first source and article-to-report command/query DTO tranches, the proposed command-to-permission crosswalk, the PostgreSQL qualification gate, and unambiguous structured source-identity authorization resource references; Document 08 v1.9 now defines deny-by-default role boundaries and a minimum operation-permission catalogue. These are proposed logical baselines only. Final role-to-permission grants, policy administration, exact field bounds/canonicalization, and Project Owner approval remain incomplete.
- Validated environment/log-level configuration, safe error-envelope primitives, and allowlisted structured JSON logging now exist. Non-finite numeric metadata is omitted and strict JSON serialization is enforced; centralized exception mapping, metrics, tracing, alerting, and operational telemetry remain incomplete.
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
- **GENI-ADR-005:** production qualification and activation of the owner-selected PostgreSQL target, including exact version and migration strategy, after the workload/backup/concurrency proof-of-concept and formal ADR acceptance.
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

Document 15 §10.11–10.13 provides field-level DTO tranches for the core article-to-report flow, source configuration/identity and command-to-permission crosswalk. Section 10.14 defines separate structured-output baselines for Importance, Economic Relevance and Economic Impact; §10.15 defines ReportContent and ReportGenerationProvenance; §10.16 adds the pairwise article-deduplication repository, authorization and DTO contracts. These are proposed logical baselines only. Document 03 v1.54 requires actor and immutable authorization references on both duplicate candidate and decision records, bound to their exact operation scope; v1.54 also makes the Source configuration aggregate version explicit. Neither change approves the proposed contracts or enables production persistence.
For every actual provider request, Document 15 v4.10 requires an LLMUsageRecord linked to the exact Analysis and/or ProcessingRun/ProcessingStep and carrying the applicable privacy-authorization decision, processing purpose, data category, region, transfer assessment, content-rights decision references, provider/model, prompt/schema versions, outcome and retry provenance. Document 08 v1.9 adds the independent `privacy.processing.authorize` permission bound to the exact purpose, operation, data category, payload/input fingerprint, provider/model and region. Privacy authorization must independently ALLOW that exact request, and source-content rights must separately cover the exact payload and use; missing, unknown, expired, revoked or mismatched references block egress.
Remaining work includes the explicit blockers in Document 15 §§10.10.1, 10.11.9, 10.12.5, 10.13.2, 10.14.5, 10.15.4 and 10.16.4: exact serialization/bounds/canonicalization, remaining query/report-family schemas, assessment vocabularies/scales/uncertainty calibration, template/input-manifest identity, duplicate-pair canonicalization and score/decision calibration, final grant assignments and policy-administration contracts. These documents remain Proposed and do not authorize execution.

### 5.2 Persistence and transaction implementation

Continue the PostgreSQL qualification in GENI-ADR-005-POC-001 from the latest successful 32-test run (28 PostgreSQL integration methods plus four standalone retention-policy unit tests; GitHub Actions run `45981896934`, source commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70`, evidence artifact `15189922078`). POC-29 verifies concurrent ArticleRevision append/current-pointer compare-and-swap: one writer commits and the stale writer's revision insert rolls back. POC-24 through POC-28 cover concurrent migration execution, same-Article current-revision integrity, decision-case/outcome constraints, source-identity index integrity, and an atomic synthetic legacy-revision backfill candidate. These results remain partial PoC evidence, not production qualification or approval of a production backfill policy. Continue with production key custody/rotation, off-site/immutable backup storage, retention enforcement, restore authorization, tablespace/configuration and full cluster-global recovery, privacy-ledger reconciliation, monitoring, alerting, and operator procedures. Obtain an approved workload profile and predeclared thresholds before making capacity claims; retain raw results, failed runs, exact experimental versions/configuration, commit SHA, migration and backup/restore evidence. Correctness and operational-feasibility experiments may be recorded while numeric workload targets remain unset, but no capacity or final production-readiness claim is permitted. PostgreSQL is the Project Owner-selected target, but the protocol is a test plan, not a test result or production authorization. GENI-ADR-005 must be formally Accepted, and all applicable PostgreSQL qualification gates must pass, before production dependencies, production migrations, or production activation.

Then implement:
- Concrete database adapters, migrations, durable repository implementations, and UnitOfWork behind the existing application ports.
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

### 5.7 Review findings recorded on 2026-11-27

A full review of the published `main` snapshot at `8b486f3` produced the initial findings below. Their status is reconciled with the subsequent application and PostgreSQL PoC evidence: (1) rights-evaluation time is resolved at the application-contract level; a production Clock adapter and integration evidence remain open; (2) the isolated PoC migration runner correction is exercised by POC-24 in the successful 32-test run, but the runner remains experimental and is not an approved production migration tool; (3) the migration 004 schema-integrity corrections are exercised by POC-25 through POC-27, while the production legacy-revision backfill/non-null policy remains open; (4) the PostgreSQL PoC image and GitHub Actions are pinned, with routine supply-chain refresh retained as maintenance; (5) ArticleRevision identity and projection refresh are resolved at the application-service level, while concrete repository lookup and database race/integration tests remain open; and (6) the bounded Ruff/mypy scope is an intentional, documented validation-harness boundary, not an unresolved application-quality failure. PoC evidence does not remove production qualification gates.

1. **Rights-evaluation time:** Resolved in the reviewed application service: a validated Clock supplies one trusted evaluation instant for metadata and persistent-storage rights checks. The source-provided `observed_at` remains provenance only. A production Clock adapter and integration evidence remain open.
2. **PoC migration runner hardening:** Corrected in the isolated PoC runner. It acquires a schema-scoped transaction advisory lock before checking migration history and executes each SQL file whole. POC-24 now tests concurrent runners and PL/pgSQL bodies containing internal semicolons; execution evidence is pending. This remains an experimental runner, not an approved production migration tool.
3. **PoC schema integrity corrections verified.** Migration 004 adds `articles.current_revision_id` with a composite FK that prevents cross-Article revision pointers, adds/backfills `decision_cases` before constraining `decision_records.case_id`, adds a CHECK for the exercised `OPEN`/`MATCH`/`NO_MATCH` outcome vocabulary, and removes the redundant `articles_source_identity_idx`. POC-25 through POC-27 passed in the 30-test run. The pointer remains nullable for legacy rows; a production backfill/non-null policy is still open.
4. **Supply-chain pinning:** The PostgreSQL PoC service image is pinned to the linux/amd64 manifest digest `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3` for `postgres:18.7`, and that image was successfully used by the 30-test run. GitHub Actions are pinned to commit SHAs; continue scheduled Dependabot/manual refresh and review.
5. **Revision identity and projection refresh:** Resolved at the application-service level. The semantic fingerprint continues to exclude `original_url`, `external_id` and `canonical_url`; those fields are treated as mutable source-routing attributes. An unchanged semantic fingerprint now triggers an optimistic-concurrency projection refresh without appending a new ArticleRevision. The source identity key is the tuple `(source_id, canonical_source_identifier, normalization_version)`. Concrete repository lookup semantics and PostgreSQL race/integration tests remain open.
6. **Quality tooling scope — intentionally bounded.** Ruff covers the repository's Python files, while strict mypy is applied to the shipped application package. `scripts`, `tests`, and `tools/postgres_poc` are validation/development harnesses, not runtime product modules; they are not promoted into the strict application typing target. If any of these directories becomes shipped runtime code, strict typing and corresponding CI coverage become a pre-merge requirement. This is a documented scope decision, not an unresolved application-quality failure.

## 6. Cross-document consistency rules

The following rules apply across Documents 01–17 and all ADRs:

1. **Selected project tooling is distinct from unresolved architecture candidates.** Document 04 §4.1 records CPython 3.15, uv 0.13.9, setuptools 84.2.1, pytest, Ruff, and mypy as the bounded development toolchain. Pydantic, LiteLLM, SQLAlchemy, Alembic, exact PostgreSQL driver/version, source-acquisition mechanisms, and deployment choices remain candidates or pending decisions; they must not be treated as approved application architecture until their relevant ADR and evidence gates pass. A candidate may be pinned in an isolated PoC-only environment for reproducible testing without becoming a production selection. PostgreSQL itself is the owner-selected target, subject to its qualification and production-activation gate.
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
| R1 — Technology baseline | 32 PoC test methods passed on PostgreSQL 18.7/Psycopg 3.3.9/Python 3.15.2 (28 PostgreSQL integration methods plus four standalone retention-policy unit tests; GitHub Actions run `45981687620`, source commit `999617c06fc9c8047c6eb588adb5438e62b9af17`, evidence artifact `15189951455`). Coverage includes concurrent-write full-database logical backup/restore, four migrations, experimental encrypted/authenticated backup with private file permissions, user-defined cluster-role/membership restore into a clean instance, separate read-only backup and target-scoped restore identities, fail-closed retention planning (without deletion/enforcement), child-process restart/reconnect, least-privilege role smoke tests, failed-migration rollback (POC-22), migration reapplication idempotency (POC-23), concurrent whole-file migration execution (POC-24), Article current-revision same-aggregate FK (POC-25), decision-case/outcome constraints (POC-26), unique source-identity index verification (POC-27), and atomic synthetic legacy Article revision backfill with invalid-pointer rollback and valid same-Article pointer commit (POC-28), and concurrent ArticleRevision append/current-pointer compare-and-swap with rollback of the losing writer (POC-29). The PostgreSQL 18.7 linux/amd64 image is pinned to `sha256:32f5fdbf4d27ebe0d4552313126a593400f40b21bff207e43617b2305838bce3`. Remaining production credential/key management, owner-approved retention values/enforcement, off-site/restore controls, restore authorization/credential lifecycle, full cluster/tablespace recovery, approved workload profile and thresholds, formal ADR-005 acceptance and explicit production-toolchain selection remain open | All mandatory correctness, backup/security, recovery, and approved workload gates pass; reproducible evidence and operational feasibility are reviewed; production engine/tooling/configuration are explicitly recorded in the Accepted ADR. PoC-only candidates do not satisfy production selection by themselves |
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
- Application CI: .github/workflows/ci.yml installs the package and development tools on Python 3.15 only, then runs Ruff, mypy, and pytest. Ruff covers `src`, `tests`, `scripts` and `tools` with import-order checking enabled; mypy strict mode covers the application package only.

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
**Version:** 4.69
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Last Updated:** 2026-11-27

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

**Revision Note (v4.2):** Adds the pure, fail-closed content-rights persistence gate for exact source/content scope and PERSISTENT_STORAGE operation. This is not legal validation or complete rights management: assessment evidence verification, freshness, retention deadlines, temporary-content lifecycle, persistence, revocation propagation, deletion, and external-provider enforcement remain gated.

**Revision Note (v4.3):** Records that LIMITED_RETENTION now requires an explicit positive maximum duration in the pure domain contract; expiry scheduling and deletion execution remain unimplemented.

**Revision Note (v4.4):** Corrects the persistence readiness statement to distinguish the Project Owner-selected PostgreSQL target from its still-pending production qualification, exact implementation choices, and formal ADR-005 acceptance. Refreshes the Python 3.15 CI evidence to the successful run for the current inspected `main` commit. No production authorization or ADR acceptance is implied.

**End of Document**

**Revision Note (v4.5):** Synchronizes current Document 15 references to v4.2 and preserves older version references only in historical revision notes. Aligns readiness evidence with the PostgreSQL target qualification gate.

**Revision Note (v4.6):** Refreshes the inspected `main` baseline and Python 3.15 CI evidence to commit `b869cf9cf77dd1305ea1ae71aedb900df8caaafc` and successful Application CI run 45939259661 (211 tests passed). This verifies the code-quality baseline only; it does not establish product or production readiness.


**Revision Note (v4.7):** Refreshes the inspected main-branch baseline to `b2e8ac5` and records the latest successful Python 3.15 Application CI run 45939388122 and Documentation validation run 45939388133. No ADR status, first-slice approval, or production authorization is changed.

**Revision Note (v4.8):** Resolves the ADR-005 PoC/production-tooling sequencing deadlock by permitting isolated, pinned PoC-only candidate stacks while retaining formal ADR acceptance and all production dependency/migration/activation gates. Numeric workload and capacity thresholds remain owner-approved inputs.

**Revision Note (v4.9):** Records the first successful PostgreSQL 18.7/Psycopg 3.3.9 PoC run (16 test methods) and distinguishes its partial correctness evidence from full qualification. Backup/restore, security/backup-control review, full process restart, approved workload profile, performance thresholds, and production approval remain open.

**Revision Note (v4.10):** Records the follow-up PoC run with all 18 test methods passing, including full-database logical backup/restore, a child-process restart/reconnect exercise, and least-privilege role smoke testing. Concurrent-write backup, backup encryption/retention/restore permissions, formal security review, workload approval, performance thresholds, and production acceptance remain open.

**Revision Note (v4.11):** Records the follow-up PoC run with all 18 tests passing after adding a concurrent-write backup window and a third migration. The full-database backup restored successfully to an isolated database. Backup protection/retention, restore authorization, formal security review, workload approval, performance thresholds, and production acceptance remain open.

**Revision Note (v4.12):** Records the successful 18-test run with private backup-file permissions and an experimental authenticated-encryption envelope, including wrong-key and tamper detection. Operations Document 13 v1.2 now specifies backup/restore requirements and the evidence boundary. Production key custody/rotation, retention, off-site/immutable storage, restore authorization, cluster-global recovery, workload/performance approval, and formal ADR-005 acceptance remain open.

**Revision Note (v4.13):** Records the successful 19-test PostgreSQL PoC run, adding restoration of user-defined cluster roles and role membership into a clean PostgreSQL 18.7 instance. The test retains the destination bootstrap administrator and excludes role passwords; full cluster/tablespace/configuration recovery, production key custody, retention, off-site protection, restore authorization, workload/performance approval, and formal ADR-005 acceptance remain open.

**Revision Note (v4.14):** Records the successful 20-test PostgreSQL PoC run, adding a dedicated `pg_read_all_data` backup identity that can dump and restore synthetic database contents while lacking write, superuser, CREATEDB, and CREATEROLE privileges. Production credential custody/rotation, retention enforcement, restore-identity separation, off-site/immutable protection, full cluster recovery, workload/performance approval, and formal ADR-005 acceptance remain open.

**Revision Note (v4.15):** Refines POC-20 to use separate backup and restore identities. The backup identity is read-only; the restore identity owns only the isolated target database and cannot write to the source database. Production credential provisioning/rotation/revocation, retention enforcement, restore authorization, off-site/immutable protection, full cluster/tablespace recovery, workload/performance approval, and formal ADR-005 acceptance remain open.

**Revision Note (v4.16):** Records the successful 21-test PostgreSQL PoC run, adding a fail-closed retention planner with explicit policy inputs, minimum verified-copy protection, legal holds, immutability windows, and deterministic candidate ordering. The planner performs no deletion or scheduling and uses fixture values only; production retention policy/enforcement, credential lifecycle, off-site protection, restore authorization, full cluster recovery, workload/performance approval, and formal ADR-005 acceptance remain open.

**Revision Note (v4.17):** Records the successful 24-test rerun, comprising 20 PostgreSQL integration methods and four independent retention-policy unit tests. The additional tests cover malformed/future-dated metadata, immutability expiry boundaries, and deterministic ordering. The planner remains non-destructive; owner-approved production retention and enforcement remain open.

**Revision Note (v4.18):** Records 25 passing test methods, including POC-22's transactional failed-migration rollback check. A failure after partial DDL leaves neither the schema object nor an applied-migration history entry. Production migration tooling and rollback/recovery procedures remain unapproved.


**Revision Note (v4.19):** Updated the readiness assessment against the 2026-11-27 main-branch snapshot and recorded the 26-test PostgreSQL PoC evidence while preserving the distinction between partial PoC results and production qualification.

**Revision Note (v4.20):** Reconciles the readiness blockers and R1 technology gate with the latest 26-test PostgreSQL PoC evidence (22 integration methods plus four standalone retention-policy tests), including POC-22 migration rollback and POC-23 migration reapplication idempotency. The evidence remains partial; production key/credential custody, retention enforcement, off-site protection, restore authorization, full cluster/tablespace recovery, approved workload and performance thresholds, formal ADR-005 acceptance, and production toolchain selection remain open.


**Revision Note (v4.21):** Updates active Document 15 references to v4.3 after specifying and implementing the ArticleRevisionService application orchestration contract. This does not close Gate R2: the Document 15 baseline remains Proposed pending formal approval, and production authorization, rights, idempotency, PostgreSQL adapters, and integration/recovery evidence remain required.


**Revision Note (v4.22):** Updates active Document 15 references to v4.4 after making metadata-rights verification an explicit ArticleRevisionService precondition. Metadata access/preservation and full-text persistent storage remain distinct checks; production rights adapters and approved source-specific rules remain gated.


**Revision Note (v4.23):** Updates active Document 15 references to v4.5 after requiring at least one applicable rights-assessment reference for every persisted ArticleRevision. Missing rights evidence now fails closed before transaction startup; production rights adapters and source-specific policy approval remain required.

**Revision Note (v4.24):** Records the 2026-11-27 full-repository review findings (§5.1), the widened Ruff scope, and the Document 15 v4.6 / Document 17 v2.4 alignment. The readiness verdict is unchanged.

**Revision Note (v4.25):** Records that all GitHub Actions in the three workflows are pinned to commit SHAs; the PostgreSQL service image digest pin remains open (§5.1 item 4).


**Revision Note (v4.26):** Refreshes the readiness review after resolving the two ArticleRevisionService findings: rights are checked against a trusted application Clock, and non-semantic source URL/external-ID changes refresh the current Article projection without creating a content revision. The production Clock/repository adapters, transaction race tests, PostgreSQL qualification, and all formal ADR gates remain open.


**Revision Note (v4.27):** Aligns the ArticleRevision application contract with Document 15 v4.7 and records the stable source identity tuple plus projection-refresh behavior. The inspected implementation baseline includes trusted-clock rights evaluation and synthetic tests; production adapters, PostgreSQL concurrency evidence, and formal ADR gates remain open.


**Revision Note (v4.28):** Refreshes the inspected source/test baseline after adding explicit coverage for invalid Clock values and shared rights-evaluation timestamps. CI status for the refreshed commit must be confirmed from the workflow run; no production readiness or ADR status is changed.


**Revision Note (v4.29):** Records the PostgreSQL PoC migration-runner correction: migration history is checked only after acquiring a schema-scoped transaction advisory lock, and SQL files are executed whole rather than split on semicolons. POC-24 covers concurrent runners and PL/pgSQL statement bodies; its execution evidence remains pending. The PoC remains isolated and does not qualify a production migration tool.


**Revision Note (v4.30):** Adds PostgreSQL PoC migration 004 for Article current-revision integrity, decision-case referential integrity/backfill, constrained decision outcomes, and removal of a duplicate source-identity index. Adds POC-25 through POC-27, updates migration coverage to 001–004, and pins the PostgreSQL 18.7 linux/amd64 service image by manifest digest. The 26-test historical run remains unchanged; the new migration and tests require fresh PostgreSQL workflow evidence. Production ADR-005 and all operational gates remain open.


**Revision Note (v4.31):** Refreshes the inspected baseline to the published main commit containing PostgreSQL migration 004, POC-25–27, and the immutable image pin. The Documentation Registry's self-inventory version row and snapshot baseline were also corrected after CI exposed stale registry self-metadata. The PostgreSQL workflow result remains the authority for the new PoC evidence.


**Revision Note (v4.32):** Records the successful 30-test PostgreSQL PoC run (26 PostgreSQL integration methods plus four standalone retention-policy unit tests), including POC-24 through POC-27 and migration 004, with PostgreSQL 18.7 / Psycopg 3.3.9 / Python 3.15.2 and the immutable linux/amd64 image digest. Captures the raw evidence artifact and explicitly retains the nullable legacy current-revision pointer as an open production data-backfill/non-null gate. This is stronger PoC correctness evidence, not production qualification or ADR-005 acceptance.


**Revision Note (v4.33):** Synchronizes the R1 technology gate with the latest successful 30-test PostgreSQL PoC evidence (26 PostgreSQL integration methods plus four standalone retention-policy tests), the four-migration schema, POC-24–27, immutable PostgreSQL image digest, and machine-readable artifact. The test run demonstrates PoC correctness only; production security/operations, workload approval, non-null legacy Article revision backfill, formal ADR-005 acceptance, and production toolchain selection remain gated.


**Revision Note (v4.34):** Clarifies that strict mypy is intentionally scoped to the shipped application package; repository scripts, tests, and the isolated PostgreSQL PoC remain development/validation tooling. Their promotion into runtime product code requires strict typing before merge. Refreshes the reviewed baseline to the successful 30-test PoC and green CI snapshot; no production authorization or ADR status changes.


**Revision Note (v4.35):** Refreshes both the persistence narrative and R1 gate to the latest successful 30-test PostgreSQL PoC execution on commit `8e4d9dd7f2118e385b08bc3c6e94c7a332cbcd68` (run `45955663899`, evidence artifact `15178467250`). Application CI and Documentation validation also passed on the same commit. Production ADR-005 acceptance, operational/security gates, approved workload thresholds, and the legacy current-revision non-null/backfill policy remain open.


**Revision Note (v4.36):** Aligns the §5.2 persistence narrative with the same latest successful 30-test PostgreSQL PoC run and raw evidence artifact already recorded in R1. The run is on commit `8e4d9dd7f2118e385b08bc3c6e94c7a332cbcd68`; production qualification remains separate.


**Revision Note (v4.37):** Refreshes the reviewed main-branch baseline to `fe0975033b81227c95c75d6564897a9beafe70fc` and synchronizes the current persistence narrative and R1 evidence to the successful 30-test PostgreSQL PoC run `45955820635` and artifact `15178617050`. POC-24 through POC-27 are recorded. The PoC remains partial; ADR-005 acceptance, production security/operations, approved workload thresholds, and the legacy current-revision backfill/non-null policy remain open.


**Revision Note (v4.38):** Refreshes the reviewed baseline to `c712d3cc314eb6bfccfb8e2e00a073681ce04aed` and records the successful 31-test PostgreSQL PoC run `45957594663` / artifact `15179457157`. POC-28 adds synthetic evidence that legacy Article revision backfill can be performed atomically. The production backfill policy, non-null enforcement, formal ADR-005 acceptance, and production qualification remain open.


**Revision Note (v4.39):** Reconciles readiness with the executable ArticleRevisionService and its Article/ArticleRevision repository ports, while keeping durable adapters and database-level concurrency/recovery qualification open. Refreshes the inspected baseline to `78c1c8d3635b5fd02e82d4c151245ca6942275e6`, records the latest successful 31-test PostgreSQL PoC run `45957897197` / artifact `15179627092`, and confirms Application CI `45957896978` plus Documentation validation `45957897026` passed. No ADR acceptance, production rights authorization, or PostgreSQL production qualification is implied.


**Revision Note (v4.40):** Records the ArticleRevisionService fixes for stale expected-version acceptance on semantic no-op updates and source-observation time being used as Article creation time. Explicit Article updates now fail with `STALE_VERSION` unless the caller's expected aggregate version matches, and new Article projections use the trusted application Clock for `created_at`. The updated Application CI run `45959116807` passes 247 tests, Ruff, and mypy; Documentation validation `45959116802` passes; PostgreSQL PoC `45959116833` passes 31 test methods with artifact `15180485680`. No ADR acceptance, production rights authorization, or PostgreSQL production qualification is implied.


**Revision Note (v4.41):** Records ArticleRevisionService hardening for expected aggregate versions, trusted Article creation timestamps, current-revision ownership, and immutable projection metadata. The latest Application CI run `45959463469` passes 248 tests, Ruff, and mypy; Documentation validation `45959463453` passes; PostgreSQL PoC `45959463464` passes 31 test methods with artifact `15180470998`. No ADR acceptance, production rights authorization, or PostgreSQL production qualification is implied.


**Revision Note (v4.42):** Aligns active references with the then-current Document 15 contract and Document 03 v1.53. Records the initial immutable SourceRecord and read-only SourceRepository port from Document 17 v2.9. This is a configuration-record/read-only retrieval foundation only: source discovery, collection, configuration mutation, concrete persistence, health/reliability/relationship assessment, SSRF/egress enforcement, and production rights authorization remain unimplemented and gated. The overall readiness verdict and ADR/production gates are unchanged.


**Revision Note (v4.43):** Refreshes the inspected main baseline to `5cb1c67d6bdcea911b10c62da4e1e6f17f18eaf2` after the SourceRecord URL-type validation correction. Document 15 and Document 17 v2.9 remain the active source-contract references; source collection and production authorization remain gated.


**Revision Note (v4.44):** Aligns the active Document 15 references after documenting and testing stricter structural URL input validation for SourceRecord. The change does not alter source acquisition, SSRF/egress, rights, persistence, ADR acceptance, or production-readiness gates.


**Revision Note (v4.45):** Refreshes the inspected `main` baseline to `1317bd65cd4d0ce098234e5d36fcebe27df28ca9` and synchronizes the readiness evidence with Application CI run `45961222822` (275 tests, Ruff and mypy successful), Documentation Validation run `45961222872`, and PostgreSQL 18.7 / Python 3.15 PoC run `45961222866` (31 tests; evidence artifact `15180438438`). All three workflows succeeded. The PoC remains isolated and partial; GENI-ADR-005 remains Proposed, production qualification and all applicable authorization/rights/security/operational gates remain open, and the overall readiness verdict is unchanged.


**Revision Note (v4.46):** Refreshes the inspected `main` baseline to `7e124789d02a95992c28fb559a625155bbf43a96` and synchronizes the latest verified evidence: Application CI run `45961720499` (275 tests, Ruff and mypy successful), Documentation Validation run `45961720518`, and PostgreSQL 18.7 / Python 3.15 PoC run `45961720585` (31 tests; artifact `15180963314`, archive SHA-256 `438cfa4d5a698a454de53e1cf87503e16f055ea14941aee9642642f084546ac3`). All three workflows succeeded. The PoC remains isolated and partial; GENI-ADR-005 remains Proposed, production qualification and all applicable authorization/rights/security/operational gates remain open, and the overall readiness verdict is unchanged.


**Revision Note (v4.47):** Refreshes the inspected `main` baseline to `428e6b6d3ea142175373246bba209476c50cd5c6` and synchronizes the latest verified evidence: Application CI run `45961988981` (275 tests, Ruff and mypy successful), Documentation Validation run `45961988971`, and PostgreSQL 18.7 / Python 3.15 PoC run `45961988925` (31 tests; artifact `15180889132`, archive SHA-256 `c306b10267d9bd46988c5bf8cf15b2af0ddcb7add4bf191ab8edfbb98f7d9fe0`). All three workflows succeeded. The PoC remains isolated and partial; GENI-ADR-005 remains Proposed, production qualification and all applicable authorization/rights/security/operational gates remain open, and the overall readiness verdict is unchanged.


**Revision Note (v4.48):** Refreshes the inspected `main` baseline to `a1f7398cad7aec5e9279fd6b96815c503739e73a` and records successful verification of POC-29 on source commit `a9dd0d9ab82a875fff19b05d0b26fafad82a607d`: Application CI run `45962990531` (275 tests, Ruff and mypy successful), Documentation Validation run `45962990536`, and PostgreSQL 18.7 / Python 3.15 PoC run `45962990616` (32 tests; artifact `15181591814`, archive SHA-256 `b900d487ed456dc0dc8297731b17f0eab4f4df9c8fa28e4f7767a23436425987`). All three workflows succeeded. The new test verifies atomic concurrent ArticleRevision append/current-pointer compare-and-swap. The PoC remains isolated and partial; GENI-ADR-005 remains Proposed, production qualification and all applicable authorization/rights/security/operational gates remain open, and the overall readiness verdict is unchanged.


**Revision Note (v4.49):** Refreshes the inspected `main` baseline to `aaeb4de0c9c498c6e172ee878d2ee70875027104` and synchronizes evidence with the successful 275-test Application CI run `45963235364`, Documentation Validation run `45963235243`, and PostgreSQL 18.7 / Python 3.15 PoC run `45963235373` (32 tests; artifact `15182595241`, archive SHA-256 `5eac19ecfcb8c73cd40af1b54187f0eea28001371fd0e9bb11198df0eaf553b5`) on source commit `5c9e34af98a97326c22ac756f306225493f91e29`. POC-29 verifies one-winner concurrent ArticleRevision append/current-pointer compare-and-swap with rollback of the losing insert. The PoC remains isolated and partial; GENI-ADR-005 remains Proposed and production qualification, security/operations, workload thresholds, and formal acceptance remain open.


**Revision Note (v4.50):** Corrects the full source commit SHA recorded in the historical v4.48 evidence note for the POC-29 test commit. No test result, architecture decision, readiness gate, or approval status changes.


**Revision Note (v4.51):** Synchronizes the document footer version with the controlled header version after the v4.50 historical SHA correction. No readiness verdict or evidence status changes.


**Revision Note (v4.52):** Refreshes the inspected baseline to `b154650c9cda341c71c7e25fe0e8c7825c6edb06` and synchronizes the PostgreSQL evidence references to the 32-test POC-29 run `45963235373` / artifact `15182595241`. The PoC remains partial; production qualification and formal ADR-005 acceptance remain open.


**Revision Note (v4.53):** Corrects the paragraph boundary after the PostgreSQL qualification gate and completes the R1 evidence coverage through POC-29. No readiness verdict or approval status changes.

**Revision Note (v4.54):** Aligns the controlled footer version with the v4.54 header. No readiness verdict, test result, or approval status changes.

**Revision Note (v4.55):** Reconciles the 2026-11-27 review-finding summary with the recorded POC-24 through POC-29 evidence, distinguishes experimental PoC completion from production qualification, and corrects the duplicate subsection number. No ADR approval or production authorization is implied.


**Revision Note (v4.56):** Updates the active Document 03 cross-reference from v1.53 to v1.54 and records the Source configuration aggregate-version addition without implying approval of the proposed data model or production persistence. No readiness verdict or production authorization changes.

**Revision Note (v4.57):** Clarifies the implementation baseline and records the GitHub comparison showing documentation-only changes after the 275-test Application CI commit. The existing application test evidence remains applicable to current code; fresh documentation validation remains pending. No readiness verdict or production authorization changes.

**Revision Note (v4.58):** Records the shared ArticleRevision URL-validation hardening and regression tests, and corrects the CI evidence boundary: the 275-test result belongs to commit `5c9e34a` and does not verify the later code/test changes. Current-main Application CI and Documentation Validation results remain unverified. No readiness verdict or production authorization changes.

**Revision Note (v4.59):** Advances the reviewed code/test snapshot to `6afdfe7a876b93f0f31cc7cc5f14eaf12b5feedb` after extending URL validation to Unicode whitespace and control/format characters and adding regression cases. Current-main Application CI and Documentation Validation remain pending; no production authorization changes.

**Revision Note (v4.60):** Advances the inspected code/test snapshot to `bb7681854d197ccf5e916362b6b1b5cbd3a763eb` after a non-functional standard-library import-order cleanup in the shared URL validator. Current-main Application CI and Documentation Validation remain pending.

**Revision Note (v4.61):** Advances the reviewed code/test snapshot to `d511108cfdb48873ec8fe98e0fa403fba86db259` after correcting the new regression fixtures to contain actual Unicode whitespace, format-control, and newline characters rather than escaped backslash sequences. Current-main Application CI and Documentation Validation remain pending.

**Revision Note (v4.62):** Advances the reviewed code/test snapshot to `c75f6e7ed81e60c7330e739181a252723c098b59` after normalizing the regression fixtures to test a single literal backslash. Current-main Application CI and Documentation Validation remain pending.

**Revision Note (v4.63):** Clarifies that the current-main CI workflows are configured for push events, but their run results were not available for verification in this review. The 275-test result remains tied only to commit `5c9e34a`; no current-code CI success is claimed.

**Revision Note (v4.64):** Aligns the duplicated document-control version metadata and records verified current-main results: Application CI and the PostgreSQL 18.7 / Python 3.15 correctness PoC succeeded on commit `1dadc81137a54cbf80b923b1a2af8b72e7dc605a`; documentation validation exposed this metadata mismatch. No readiness verdict or production authorization changes.

**Revision Note (v4.65):** Refreshes the reviewed baseline to `20050089eb3b20f12478f4cd6fa8eadb193d59e6` and records verified current-main results: Application CI run `45980103489` passed 295 tests plus Ruff and mypy; Documentation Validation run `45980103595` passed 23 validator tests and repository-wide checks; PostgreSQL 18.7 / Python 3.15 PoC run `45980103424` passed 32 test methods (28 PostgreSQL integration methods and four standalone retention-policy unit tests; artifact `15187974876`). The PoC remains isolated and partial. GENI-ADR-005 remains Proposed; no production qualification, capability enablement, or authorization is implied.

**Revision Note (v4.66):** Synchronizes active references with Document 15 v4.10 and records the authorization-resource delimiter-collision hardening in ArticleRevisionService. Source-scoped authorization references now use a versioned fixed-order JSON tuple, with a regression test proving distinct identity tuples cannot collide. No readiness verdict, ADR approval, source-collection authorization, or production capability is implied.

**Revision Note (v4.67):** Refreshes the verified baseline to `999617c06fc9c8047c6eb588adb5438e62b9af17` after the source-identity authorization reference hardening. Application CI run `45981687648` passed 296 tests with Ruff and mypy; Documentation Validation run `45981687770` passed 23 validator tests and repository-wide checks; PostgreSQL 18.7 / Python 3.15 PoC run `45981687620` passed 32 test methods (artifact `15189951455`). The PostgreSQL result remains partial experimental evidence. GENI-ADR-005 remains Proposed and no production capability is authorized.

**Revision Note (v4.68):** Refreshes the inspected baseline to current `main` commit `1a02755f8356aa2263246c9c08ab13bfdd41bc70` and records the successful exact-commit reruns: Application CI `45981896909` (296 tests, Ruff and mypy), Documentation Validation `45981897073` (23 validator tests and repository-wide checks), and PostgreSQL 18.7 / Python 3.15 PoC `45981896934` (32 methods; artifact `15189922078`). The PoC remains partial correctness evidence; PostgreSQL production qualification, formal ADR-005 acceptance, and all production activation gates remain open.


**Revision Note (v4.69):** Records the structured-logging hardening that omits NaN and positive/negative infinity from allowlisted numeric metadata and enforces strict JSON serialization, with regression coverage. Application test coverage increases by one test; durable adapters, centralized telemetry, and production readiness remain unchanged.
