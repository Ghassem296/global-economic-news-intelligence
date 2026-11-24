# GENI-READY-016 — Implementation Readiness and Release Gates

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-READY-016  
**Version:** 1.0  
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-24  
**Baseline:** Published `main` snapshot reviewed on 2026-11-24

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

**Overall status: NOT READY for implementation of the complete first vertical slice.**

The repository is a documentation-led architecture baseline. It is not yet an executable GENI application.

The following distinctions are important:

- Documentation validation infrastructure exists: `.github/workflows/docs-validation.yml`, `scripts/validate_docs.py`, and `tests/test_validate_docs.py` are present.
- The existing CI validates documentation inventory/metadata and ADR inventory. It is not application CI and does not prove application behavior.
- No application package, runtime dependency manifest, persistence adapter, executable product workflow, or application test suite is present in the repository snapshot reviewed.
- The technology table in Document 04 is explicitly a candidate list. It does not constitute a selected stack.
- The 20 ADRs are published as proposals; none is Accepted in the registry snapshot.
- Document 15 deliberately leaves several lifecycle and DTO contracts open. Its explicit blockers must not be silently completed by implementers.

Therefore, the project is ready for controlled architecture/contract closure and documentation-only validation work. It is not ready for the first-slice application implementation or production processing.

## 3. What may proceed now

The following work can proceed without pretending that unresolved architecture has been approved:

1. Documentation maintenance, cross-document reconciliation, and automated documentation checks.
2. Review of ADR alternatives and recording of explicit decisions by the Project Owner.
3. Drafting and review of missing transition tables, DTO schemas, authorization matrices, and transaction proofs.
4. Technology proof-of-concepts that are isolated, disposable, and clearly labelled as experiments; they must not become hidden production commitments.
5. Fixture design and human-reviewed evaluation-dataset preparation, provided fixtures are synthetic or their use is authorized.
6. Application project scaffolding only after the language/runtime/package decisions and the minimum architecture boundary are explicitly approved.

The following must remain disabled until their gates pass: production source collection, full-text retention, external LLM transmission of source content, automatic event creation/matching, material review actions, publication execution, delivery dispatch, and processing of personal data beyond an approved test context.

## 4. First-slice decision scope

Do not require all 20 ADRs to be accepted before any work begins. Accept or explicitly defer decisions according to the capabilities actually included in the first slice.

### 4.1 Foundational decisions

The following decisions affect the architecture or invariants of the first slice and must be resolved before dependent application code treats their recommendations as policy:

- **GENI-ADR-001 and 002:** event-centric architecture and the separation of article deduplication from event matching.
- **GENI-ADR-005:** persistence technology and migration strategy, after the workload/backup/concurrency proof-of-concept.
- **GENI-ADR-006 and 007:** provider-independent LLM execution and deterministic workflow boundaries.
- **GENI-ADR-008:** evidence provenance and uncertainty representation.
- **GENI-ADR-011:** event identity and matching lifecycle.

### 4.2 Capability-dependent decisions

These decisions are required before enabling the corresponding capability:

| Decision | Required before |
|---|---|
| GENI-ADR-003 | Finalizing editorial scope and economic-intelligence prioritization |
| GENI-ADR-004 | Enabling publication eligibility policy or any publication operation |
| GENI-ADR-009 | Selecting and operating near-real-time acquisition mechanisms |
| GENI-ADR-012 | Enabling semantic retrieval or embedding persistence |
| GENI-ADR-013 | Accessing, transmitting, retaining, deriving from, or republishing real source content under the relevant rights rules |
| GENI-ADR-014 | Enabling material human-review actions, corrections, or withdrawals |
| GENI-ADR-015 | Integrating market data or describing market observations as measured |
| GENI-ADR-016 | Enabling durable asynchronous execution, leases, fencing, idempotency, and recovery |
| GENI-ADR-017 | Enabling governed LLM budgets, usage accounting, and evaluation policy |
| GENI-ADR-018 | Enabling multilingual processing or translation |
| GENI-ADR-019 | Enabling the governed importance/relevance/impact assessment methodology |
| GENI-ADR-020 | Processing personal data or enabling provider/region-specific privacy authorization |

An ADR may be deferred only when its capability is excluded and the implementation boundary enforces that exclusion. A deferred ADR must not be treated as implicitly accepted.

## 5. Blocking contract closure

Document 15 §10.9–10.10 is the authoritative inventory of unresolved first-slice lifecycle contracts. The following are implementation blockers, not optional polish:

### 5.1 Processing execution

Before ProcessingRun or ProcessingStep lifecycle code is implemented, approve:

- Initial states and complete allowed-transition matrices.
- Terminal, cancellation, retry, and partial-completion semantics.
- Closed ProcessingStep status vocabulary.
- Deterministic step-to-run aggregation rules.
- Recovery identity: resume the same run or create a linked successor.
- Completed-step output reuse and non-repeatable-step behavior.
- Cancellation/deadline races and external-side-effect reconciliation.
- Recoverable-run eligibility and deterministic query ordering.
- Append-only transition history and projection-rebuild requirements, if required by the chosen model.

Lease ownership and fencing do not substitute for processing state transitions.

### 5.2 Event matching

Before EventMatchCase or candidate lifecycle code is implemented, approve:

- Server-controlled initial case state and idempotent creation behavior.
- Complete case transition matrix and guards.
- Mapping from each EventMatchDecision outcome to case state.
- Review interaction, close/cancel behavior, and reopening semantics.
- Atomic write set for case status, effective decision, supersession, and ArticleEventLink changes.
- Closed candidate status vocabulary and interrupted-generation behavior.
- Candidate evaluation idempotency, fingerprint handling, and supersession-chain rules.

Candidate status or similarity scores must never substitute for the authoritative case-level decision.

### 5.3 Publication

Before publication decision or operation workflows are implemented, approve:

- Deterministic effective-decision selection for an exact immutable Report version.
- Concurrent successor prevention and predecessor validation.
- Complete actor/authorization provenance and field ownership.
- Decision-to-review/workflow mapping and caveat representation/enforcement.
- PublicationAttempt outcome-to-PublicationRecord transition matrix.
- Confirmed-failure retry policy, reconciliation-not-applied behavior, late results, and cancellation guards.
- Reconciliation requirements before another side-effecting attempt after an unknown outcome.

A PublicationDecision is not evidence that an external publication succeeded.

### 5.4 Review and delivery

Before ReviewService material actions or delivery dispatch are enabled, approve:

- ReviewRecord initial state and initial action.
- Complete ReviewAction validity and action-to-projection mapping.
- Terminal/cancellation rules, reopen-segment identity, ordering, concurrency, and authorization matrix.
- ReviewContextLink uniqueness, ordering, access control, and completion-race behavior.
- DeliveryRecord initial state and transition matrix.
- DeliveryAttempt outcome vocabulary and mapping.
- Dispatch-time authorization revalidation, retry, cancellation, and unknown-outcome reconciliation.

Document 02 explicitly limits the initial review target to ARTICLE_DEDUPLICATION, EVENT_MATCHING, and REPORT_VERSION; that target scope does not enable any material ReviewService action until the above requirements and GENI-ADR-014 are approved and tested.

## 6. Cross-document consistency rules

The following rules apply across Documents 01–15 and all ADRs:

1. **Technology candidates are not selections.** Document 04 §4.1 lists candidates. Python, uv, Pydantic, LiteLLM, SQLite/PostgreSQL, SQLAlchemy, Alembic, pytest, Ruff, and GitHub Actions must not be described as an approved application stack until the relevant decision is recorded.
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
| R1 — Technology baseline | Accepted ADR-005 and recorded language/runtime, package manager, database/driver, migration, async, transaction, and LLM adapter choices | Reproducible environment and documented rationale; database proof-of-concept passes |
| R2 — Contract baseline | Approved Document 15; complete DTO schemas and transition matrices for every enabled workflow | No enabled workflow depends on an unresolved state, field, authorization, or concurrency rule |
| R3 — Security, rights, and privacy | Threat-model controls, operation-specific rights decisions, privacy authorization boundaries, secret handling | Deny/unknown/expired/revoked/scope-mismatch cases fail closed; test-source permissions are documented |
| R4 — Executable foundation | Installable application package, pinned dependencies, validated configuration, logging, errors, CI, migrations | Clean setup succeeds; tests/lint/type checks run without paid production services |
| R5 — Domain and persistence verification | Contract tests, schema constraints, transaction tests, concurrency/idempotency/failure-injection tests | Required invariants are demonstrated, not merely documented |
| R6 — Vertical-slice verification | End-to-end fixture run and trace preserving provenance from ArticleRevision to Report and PublicationDecision | Reproducible run; no unauthorized side effect; all quality gates and budgets enforced |
| R7 — Operational release | Backup/restore, recovery, observability, incident and rollback procedures, deployment security | Operational acceptance criteria in Documents 13 and 04 are demonstrated |

Passing an earlier gate does not imply that a later gate has passed. A gate may be passed for a limited capability while other capabilities remain disabled.

## 8. CI and repository baseline clarification

The current repository has a documentation-only automation baseline:

- `.github/workflows/docs-validation.yml` runs on pushes to `main`, pull requests targeting `main`, and manual dispatch.
- It uses Python 3.12 to run `python -m unittest discover -s tests -v`.
- It runs `python scripts/validate_docs.py` to validate controlled document versions and the ADR inventory.

This is useful and must be preserved. It does **not** currently establish application CI, package installation, static typing, linting, migration validation, database integration tests, or end-to-end product behavior. Those checks belong in the application CI baseline after the application foundation is created.

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
9. Produce a PublicationDecision without performing an external publication.

The first slice must not silently expand to production crawling, full-text retention, semantic search, market data, translation, audio/video, user personalization, external publication, or delivery. Each is separately gated.

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
- GENI-ADR-001 through GENI-ADR-020, as applicable to the enabled capability.

---

**Document ID:** GENI-READY-016  
**Version:** 1.0  
**Status:** Proposed — Readiness assessment; not an architectural approval  
**Last Updated:** 2026-11-24

**End of Document**
