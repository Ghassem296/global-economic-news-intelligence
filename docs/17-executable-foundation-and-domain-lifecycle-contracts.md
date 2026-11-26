# GENI-FOUNDATION-017 — Executable Foundation and Domain Lifecycle Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-FOUNDATION-017  
**Version:** 2.2  
**Status:** Proposed — Executable baseline; architecture approval remains governed by ADRs  
**Owner:** Project Owner  
**Last Updated:** 2026-11-26

---

## 1. Purpose

This document records the first executable repository baseline and the normative lifecycle behavior implemented by the pure domain policy module. It closes selected ambiguities in Document 15 for implementation and test purposes. It does not accept any Proposed ADR, authorize external processing, or grant source-content rights.

The code is the executable expression of the lifecycle rules below. A change to a rule must update this document, the implementation, and its tests in the same change.

## 2. Runtime and package baseline

The initial development foundation uses:

- Python 3.15 only, enforced by `pyproject.toml` (`requires-python = ">=3.15,<3.16"`), `.python-version`, and the Application CI matrix.
- A setuptools-based pyproject package with the build backend pinned to `setuptools==84.2.1`.
- uv 0.13.9 as the pinned project package manager, with the complete Python 3.15 dependency resolution committed in `uv.lock`.
- No runtime third-party dependencies in the domain foundation.
- Validated environment/log-level configuration, safe machine-classifiable errors, and allowlisted structured JSON logging.
- pytest, Ruff, and mypy as development tools.
- GitHub Actions for application CI.

The Python 3.15-only runtime range, uv 0.13.9 package manager, and setuptools 84.2.1 build backend are implementation baseline choices for this foundation. The committed lockfile is checked and installed in Application CI using locked mode; the main-branch workflow also runs Ruff, mypy, and pytest. Python 3.12 and 3.13 are not supported project runtimes. These choices do not settle database, LLM provider, source acquisition, or deployment architecture. The runtime baseline should be revisited when security support windows or dependency requirements change.

## 3. Dependency boundaries

The initial package root is src/global_economic_news_intelligence.

- domain contains pure invariants and policies; it must not import infrastructure, transport, provider SDKs, or configuration.
- application will orchestrate domain policies and enforce authorization.
- infrastructure will implement persistence and external adapters behind contracts.
- tests/unit verifies pure behavior without external services.
- Integration and end-to-end tests must use controlled fixtures and must not access production sources by default.

The initial code creates the package, CLI, validated configuration, safe error primitives, scalar-allowlisted structured logging, pure workflow lifecycle policies, and an automated test that prevents infrastructure/provider dependencies from entering the domain layer. Directories for future capabilities are created when an implemented use case requires them.

### 3.1 ArticleRevision payload contract

The pure domain package now includes `domain/article_revision_contracts.py` and its unit tests. The contract defines the revision-level `ContentAvailability` vocabulary (`available`, `partial`, `metadata-only`, `unavailable`), enforces that metadata-only/unavailable revisions persist no content reference/hash/content-normalization version, validates SHA-256 content hashes for retained full/partial content, and computes a separate versioned semantic `revision_fingerprint`. Fingerprint v1 uses a restricted JCS-safe JSON value set and a fixed semantic manifest; it excludes observation time, content storage location, change reason, and rights-assessment references. The fingerprint is intended for comparison with the current revision only, not for global historical uniqueness. The contract also snapshots the source-reported author and includes it in the fingerprint, validates source identity shape/version, absolute HTTP(S) URLs, millisecond-precision timezone-aware timestamps, unique immutable rights-assessment references, and deeply immutable JCS-safe metadata.

This is a payload/fingerprint contract only. It does not choose or execute production source-identity canonicalization, decide whether a rights assessment allows an operation, manage retention expiry/deletion or rights revocation, or persist an Article/ArticleRevision aggregate. The source adapter must provide the versioned source identity and only permission-filtered semantic metadata; the application/repository layer must compare the computed fingerprint with the current revision under optimistic concurrency. A null content hash is expected for metadata-only/unavailable revisions and is never used as an idempotency key.

### 3.2 ArticleRevision application command envelope

The application package now includes `application/article_revision_commands.py` and its unit tests. `PersistArticleRevisionCommand` composes the common `CommandMetadata` envelope with the typed `PersistArticleRevision` payload and an optional target Article ID. The expected aggregate version is carried only by `CommandMetadata`, never duplicated on the command. Create requests have no target Article ID or expected version; updates require both. The envelope keeps application authorization separate from source-content rights-assessment references.

This is an immutable command contract only. It does not implement ArticleRevisionService, idempotency storage, rights evaluation, repositories, UnitOfWork orchestration, or database persistence.

### 3.3 ArticleRevision persistence record and repository port

The domain package now includes the immutable `ArticleRevisionRecord`, which binds server-owned revision identity/number/timestamp to the immutable payload and verifies that the persisted fingerprint and schema version match the recomputed payload fingerprint. The application package includes the technology-neutral `ArticleRevisionRepository` Protocol. Its methods read by ID/current Article, match only the current fingerprint, and append through a caller-owned UnitOfWork; the repository must not commit that UnitOfWork.

The Protocol is an application port, not a PostgreSQL adapter. ArticleRepository, ArticleRevisionService, rights-decision evaluation, concurrency/transaction integration, and concrete persistence remain unimplemented and gated.

### 3.4 Content-rights assessment and persistence gate

The pure domain package now includes `domain/content_rights_contracts.py` and unit tests. It defines the operation vocabulary and assessment states from GENI-ADR-013, immutable source/content-scope-specific RightsAssessment records, versioned retention-mode contracts, and a fail-closed persistence decision. Persistent content is eligible only when an ALLOWED assessment matches the exact source, SHA-256 content-scope fingerprint, PERSISTENT_STORAGE operation, effective time window, and retention-policy version. Missing, mismatched, future, expired, denied, revoked, unknown, or review-required assessments result in metadata-only handling. NO_PERSISTENT_CONTENT and TEMPORARY_PROCESSING_ONLY never authorize persistent storage.

This is a bounded pure policy gate, not a legal determination or a complete rights-management subsystem. It does not verify license evidence, establish that an assessment is legally sufficient or freshly reviewed, calculate limited-retention deadlines, implement temporary buffers, persist assessments, evaluate other processing operations, propagate revocation, delete content, or authorize external LLM/provider egress. Those capabilities remain disabled and gated by the applicable ADRs and integration tests. The code must not be interpreted as production authorization.
 
## 4. ProcessingRun lifecycle

### 4.1 States

PENDING, RUNNING, PARTIALLY_COMPLETED, COMPLETED, FAILED, CANCELLED.

### 4.2 Allowed transitions

| From | To | Guard |
|---|---|---|
| PENDING | RUNNING | Server starts the run after validating its definition and authorization. |
| PENDING | CANCELLED | Authorized cancellation before execution starts. |
| RUNNING | PARTIALLY_COMPLETED | All currently attempted steps are terminal; at least one required step succeeded/skipped and at least one required step failed/blocked/cancelled. |
| RUNNING | COMPLETED | Every required step is SUCCEEDED or explicitly policy-approved SKIPPED. |
| RUNNING | FAILED | Run cannot progress and no required step succeeded; failure is classified and recorded. |
| RUNNING | CANCELLED | Cancellation is acknowledged and no external outcome remains unknown. |
| PARTIALLY_COMPLETED | RUNNING | Explicit recovery resumes the same run, reuses verified completed outputs, and creates a new attempt for retryable failed/blocked steps. |
| PARTIALLY_COMPLETED | CANCELLED | Authorized cancellation; unknown external outcomes must first be reconciled. |

COMPLETED, FAILED, and CANCELLED are terminal. Retrying a terminal run creates a successor run with a new run ID and a parent_run_id; it does not reopen or rewrite the prior run.

An expired lease alone never changes run state and never proves the prior worker stopped. Recovery requires fencing-token validation and idempotency checks.

### 4.3 Run status aggregation

The run projection is derived from the complete required step set:

1. If any step is PENDING, READY, or RUNNING, the run is RUNNING.
2. If every step is SUCCEEDED or policy-approved SKIPPED, the run is COMPLETED.
3. If all steps are terminal and at least one failed/blocked with at least one succeeded/skipped, the run is PARTIALLY_COMPLETED.
4. If all steps are terminal and at least one failed/blocked with no succeeded/skipped, the run is FAILED.
5. If all steps are CANCELLED, the run is CANCELLED.
6. If terminal outcomes mix cancellation and success/skip without failure, the run is PARTIALLY_COMPLETED.
7. An empty step set remains PENDING; an empty workflow must not be reported as completed.

The application must persist the step set version used to calculate the projection. A changing workflow definition cannot silently change the aggregation of an existing run.

## 5. ProcessingStep lifecycle

### 5.1 States

PENDING, READY, RUNNING, SUCCEEDED, FAILED, BLOCKED, SKIPPED, CANCELLED.

### 5.2 Allowed transitions

| From | To | Guard |
|---|---|---|
| PENDING | READY | All dependencies are satisfied and the step is eligible. |
| PENDING | BLOCKED | A required dependency or policy precondition prevents execution. |
| PENDING | SKIPPED | Explicit workflow policy marks an optional step unnecessary. |
| PENDING | CANCELLED | Run cancellation is accepted before step execution. |
| READY | RUNNING | Worker owns the current lease/fencing token and revalidates authorization. |
| READY | BLOCKED | A dependency or policy precondition became invalid before execution. |
| READY | SKIPPED | Explicit policy permits skip before execution. |
| READY | CANCELLED | Run cancellation is accepted before execution. |
| RUNNING | SUCCEEDED | Output is validated and committed with the successful attempt record. |
| RUNNING | FAILED | Attempt failed; classification and attempt evidence are persisted. |
| RUNNING | CANCELLED | Cancellation is confirmed safe; external unknown outcomes prohibit this transition. |
| FAILED | READY | Explicit retry policy authorizes a new attempt; prior attempt remains immutable. |
| BLOCKED | READY | Blocking dependencies/preconditions are now satisfied and revalidated. |

SUCCEEDED, SKIPPED, and CANCELLED are terminal for a logical step. A retry creates a new immutable ProcessingStepAttempt under the same logical step only when the operation is idempotent; otherwise create a successor logical step/run. FAILED is not automatically retryable.

A blocked step is not a failed attempt. Lease state is separate from step state.

## 6. EventMatchCase lifecycle

### 6.1 States and initial state

States: OPEN, PENDING_REVIEW, RESOLVED, CLOSED, CANCELLED. A newly created case starts in OPEN.

### 6.2 Decision-to-case projection

| Effective decision outcome | Case status | Association effect |
|---|---|---|
| MATCH | RESOLVED | Activate exactly one ArticleEventLink for the selected eligible candidate. |
| NO_MATCH | RESOLVED | No active link. |
| NEW_EVENT_CANDIDATE | OPEN | No event or link is created; authorized event creation and a successor MATCH decision are required. |
| AMBIGUOUS | OPEN | No active link; further evidence/evaluation may be added. |
| REVIEW_REQUIRED | PENDING_REVIEW | No active link; create/retain a scoped review task if review is authorized. |

A material review outcome is not itself a matching decision. The authorized workflow appends a successor EventMatchDecision; the case projection is then derived from that decision.

### 6.3 Case transitions

| From | To | Guard |
|---|---|---|
| OPEN | PENDING_REVIEW | Effective decision is REVIEW_REQUIRED or policy explicitly requires review. |
| OPEN | RESOLVED | Effective decision is MATCH or NO_MATCH. |
| OPEN | CLOSED | Authorized administrative closure; no pending external effect or active review. |
| OPEN | CANCELLED | Authorized cancellation before material resolution. |
| PENDING_REVIEW | OPEN | Review is cancelled/withdrawn without a material decision; review history is retained. |
| PENDING_REVIEW | RESOLVED | Authorized successor decision is MATCH or NO_MATCH. |
| PENDING_REVIEW | CANCELLED | Authorized cancellation; review task is also terminalized atomically. |
| RESOLVED | OPEN | Authorized successor decision supersedes the effective decision with NEW_EVENT_CANDIDATE or AMBIGUOUS. |
| RESOLVED | PENDING_REVIEW | Authorized successor decision is REVIEW_REQUIRED. |
| RESOLVED | CLOSED | Authorized administrative closure. |

CLOSED and CANCELLED are terminal. Reopening a closed/cancelled case requires a new case with explicit lineage; it never mutates the terminal case. Case status, effective decision pointer, decision supersession, and ArticleEventLink activation/deactivation commit in one transaction.

## 7. EventMatchCandidate lifecycle

States: GENERATED, EVALUATED, INELIGIBLE.

- Candidate creation persists the exact case, candidate Event version, policy version, and deterministic input fingerprint as GENERATED.
- Evaluation transitions GENERATED to exactly one of EVALUATED or INELIGIBLE.
- EVALUATED and INELIGIBLE are immutable terminal evaluation records.
- A changed input, candidate Event version, or policy creates a new candidate record with a supersedes_candidate_id referencing the prior evaluation for the same case and Event.
- Repeated identical input fingerprint converges to the same logical candidate record.
- Interrupted generation before candidate persistence creates no candidate; interrupted evaluation leaves GENERATED and can be resumed idempotently.
- Candidate status never expresses case-level acceptance, rejection, or supersession.

## 8. PublicationDecision and effective successor

PublicationDecision is immutable and scoped to one exact immutable Report version.

- The first decision has supersedes_decision_id = null.
- A successor must identify the current effective decision as its predecessor.
- Only one direct successor may reference a given predecessor for the same report version.
- The append operation locks/compares the report-version decision aggregate, validates the expected version and predecessor, appends the decision, and advances the effective pointer in one transaction.
- A stale or concurrent successor receives CONFLICT; it must reload the effective decision and obtain a new authorized decision rather than branch history.
- PUBLISH and PUBLISH_WITH_CAVEATS make the exact report version eligible for a separate publication operation; neither performs publication.
- PUBLISH_WITH_CAVEATS requires a non-empty, typed, validated caveat set that is rendered into the exact publication representation.
- HOLD_FOR_REVIEW blocks publication and requires an authorized review workflow.
- REJECT blocks publication. A later override requires a new authorized successor decision and explicit rationale.

## 9. PublicationRecord and PublicationAttempt

PublicationRecord and DeliveryRecord use the common external-operation lifecycle: PENDING, IN_PROGRESS, SUCCEEDED (publication), DELIVERED (delivery), FAILED, CANCELLED, RECONCILIATION_REQUIRED.

| Current operation state | Attempt | Immutable attempt outcome | Next operation state |
|---|---|---|---|
| IN_PROGRESS | EXECUTE | CONFIRMED_SUCCESS | SUCCEEDED for publication; DELIVERED for delivery |
| IN_PROGRESS | EXECUTE | CONFIRMED_FAILURE | FAILED |
| IN_PROGRESS | EXECUTE | OUTCOME_UNKNOWN | RECONCILIATION_REQUIRED |
| RECONCILIATION_REQUIRED | RECONCILE | RECONCILED_SUCCESS | SUCCEEDED for publication; DELIVERED for delivery |
| RECONCILIATION_REQUIRED | RECONCILE | RECONCILED_NOT_APPLIED | PENDING only if the exact same operation remains authorized and retry policy permits; otherwise FAILED |
| RECONCILIATION_REQUIRED | RECONCILE | RECONCILED_NOT_APPLIED + explicit cancellation authorization | CANCELLED; persist the reconciliation evidence and cancellation projection atomically |

Rules:

- An EXECUTE attempt is valid only for IN_PROGRESS.
- A RECONCILE attempt is valid only for RECONCILIATION_REQUIRED.
- No new side-effecting attempt is allowed while outcome is unknown.
- A confirmed failure is terminal for that operation; a new attempt requires an explicitly authorized successor operation or a provider contract that proves safe same-operation retry.
- Reconciled-not-applied is not automatically retryable; authorization and retry policy are rechecked.
- A late attempt result is retained as immutable evidence and may update the projection only if its attempt/operation version is still current; contradictory late results trigger reconciliation/incident handling, never overwrite a confirmed result.
- Cancellation before execution requires explicit authorization and transitions PENDING to CANCELLED. An IN_PROGRESS operation cannot transition directly to CANCELLED: it must first enter RECONCILIATION_REQUIRED. Cancellation from RECONCILIATION_REQUIRED requires explicit authorization plus durable reconciliation evidence that no external effect occurred; otherwise it remains blocked. The cancellation evidence and projection update must commit atomically. Terminal operations cannot be cancelled.

Delivery uses the same transition policy but remains a separate aggregate. The pure policy function accepts an explicit success_status: SUCCEEDED for publication and DELIVERED for delivery. A delivery must revalidate recipient/destination authorization immediately before dispatch. A delivery failure never reverses confirmed publication.

## 10. ReviewRecord and ReviewAction

Review states: PENDING, IN_PROGRESS, COMPLETED, CANCELLED.

- Creation appends CREATED and establishes PENDING atomically.
- STARTED transitions PENDING to IN_PROGRESS.
- COMPLETED transitions IN_PROGRESS to COMPLETED and requires an authorized reviewer outcome payload.
- CANCELLED transitions PENDING or IN_PROGRESS to CANCELLED with actor, authority and reason.
- ASSIGNED, REASSIGNED, PRIORITY_CHANGED, NOTE_ADDED, and ESCALATED append immutable actions without changing status; they require an active review and the corresponding permission.
- REOPENED is permitted only after COMPLETED or CANCELLED and creates a new ReviewRecord lifecycle segment with a new ID, predecessor_review_id, and a new CREATED action. It does not mutate the old record.
- Action sequence allocation, action append, projection update, and idempotency record commit atomically under expected-version concurrency control.
- Review completion never directly mutates EventMatchDecision or PublicationDecision. A separate authorized domain command appends the successor decision.

## 11. DTO and concurrency invariants added to executable baseline

The Python domain package implements pure transition/projection rules and typed payload contracts for duplicate evaluation/decisions, event matching, ProcessingRun commands, and ArticleRevision persistence input. It does not implement persistence. Repository and application boundaries must additionally enforce:

- Enum values serialize by their exact uppercase symbolic values.
- State-changing commands carry schema version, actor/service identity, authorization reference, correlation ID, idempotency key, and expected aggregate version where updating an existing aggregate.
- Server owns initial states, timestamps, IDs, aggregate versions, and effective pointers.
- Client/model-supplied status fields are rejected on create/update commands; transitions use dedicated domain commands.
- No command may set an arbitrary target state without passing the corresponding policy guard.
- All state transitions append an immutable history/attempt record in the same transaction as the current-state projection.
- Unknown external outcome blocks retry until reconciliation.
- A decision history is linear per aggregate; optimistic concurrency and a uniqueness constraint prevent multiple direct successors.
- Domain policy code must not import database, ORM, HTTP, provider SDK, or LLM libraries.

## 12. Implementation boundary

The first executable baseline includes the Python package, validated configuration, safe error primitives, allowlisted structured logging, pure lifecycle policy and typed payload-contract modules, CLI, tests (including domain dependency-boundary enforcement), Ruff, mypy, and application CI. It deliberately does not include a production persistence adapter, external source fetcher, LLM adapter, publication client, or delivery adapter. These remain gated by their corresponding ADRs and evidence in Document 16.

---

**Revision Note (v1.3):** Aligns the executable foundation's runtime statement with the current Python 3.15-only policy enforced by package metadata, `.python-version`, and Application CI. No other architecture or capability approval is implied.

**Revision Note (v1.4):** Adds the selected, pinned uv package manager, committed dependency lockfile, and exact setuptools build-backend version to the executable foundation baseline. No database, LLM, acquisition, publication, or deployment decision is implied.

**Revision Note (v1.5):** Aligns external-operation cancellation with the documented safe-cancellation rule: pending operations may be cancelled with authorization; in-flight operations must first be reconciled; only a proven no-effect outcome permits cancellation from reconciliation. The lifecycle implementation and tests enforce the same rule.

**Revision Note (v1.6):** Adds the source-aware ArticleRevision payload contract and its executable validation tests. The contract enforces revision-level content-availability/reference consistency while leaving source canonicalization, rights adjudication, metadata-only idempotency and persistence explicitly gated.

**Revision Note (v1.7):** Clarifies that the executable domain baseline includes typed payload contracts as well as pure lifecycle policies; it does not imply repository implementations, application authorization services, or persistence adapters.

**Revision Note (v1.8):** Adds the deterministic ArticleRevision fingerprint v1 contract and makes persisted content hashes unavailable to metadata-only/unavailable revisions. The contract remains a pure domain component and does not implement source rights enforcement, retention deletion, repositories, or PostgreSQL persistence.

**Revision Note (v1.9):** Adds the source-reported author as an immutable revision snapshot and a semantic fingerprint input. Source-specific metadata allowlists and rights decisions remain application-boundary responsibilities.

**Revision Note (v2.0):** Adds the typed application command envelope for ArticleRevision persistence and documents its separation from the common CommandMetadata and rights-assessment references. No service or persistence adapter is implied.

**Revision Note (v2.1):** Adds the immutable ArticleRevisionRecord and the technology-neutral ArticleRevisionRepository Protocol. The port does not select or implement a database adapter and must participate in the caller's UnitOfWork.

**Revision Note (v2.2):** Adds immutable, operation- and content-scope-specific RightsAssessment contracts and a fail-closed persistent-content eligibility gate aligned to GENI-ADR-013 Alternative C. This pure policy does not verify legal sufficiency, implement retention expiry/deletion, persist assessments, propagate revocation, or authorize external provider processing.

**Revision Note (v2.3):** Tightens the LIMITED_RETENTION contract to require an explicit positive maximum duration. Expiry scheduling, deadline calculation, and deletion execution remain outside this pure domain policy.

**End of Document**
