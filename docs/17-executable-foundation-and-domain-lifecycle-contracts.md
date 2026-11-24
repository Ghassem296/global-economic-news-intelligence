# GENI-FOUNDATION-017 — Executable Foundation and Domain Lifecycle Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-FOUNDATION-017  
**Version:** 1.0  
**Status:** Proposed — Executable baseline; architecture approval remains governed by ADRs  
**Owner:** Project Owner  
**Last Updated:** 2026-11-24

---

## 1. Purpose

This document records the first executable repository baseline and the normative lifecycle behavior implemented by the pure domain policy module. It closes selected ambiguities in Document 15 for implementation and test purposes. It does not accept any Proposed ADR, authorize external processing, or grant source-content rights.

The code is the executable expression of the lifecycle rules below. A change to a rule must update this document, the implementation, and its tests in the same change.

## 2. Runtime and package baseline

The initial development foundation uses:

- Python 3.12 and 3.13; Python 3.14 is not included in the supported range.
- A setuptools-based pyproject package.
- No runtime third-party dependencies in the domain foundation.
- pytest, Ruff, and mypy as development tools.
- GitHub Actions for application CI.

The supported runtime range and tools are implementation baseline choices for this foundation. They do not settle database, LLM provider, source acquisition, or deployment architecture. The runtime baseline should be revisited when security support windows or dependency requirements change.

## 3. Dependency boundaries

The initial package root is src/global_economic_news_intelligence.

- domain contains pure invariants and policies; it must not import infrastructure, transport, provider SDKs, or configuration.
- application will orchestrate domain policies and enforce authorization.
- infrastructure will implement persistence and external adapters behind contracts.
- tests/unit verifies pure behavior without external services.
- Integration and end-to-end tests must use controlled fixtures and must not access production sources by default.

The initial code creates only the package, CLI, and pure workflow lifecycle policies. Directories for future capabilities are created when an implemented use case requires them.

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

PublicationRecord and DeliveryRecord use the common external-operation lifecycle: PENDING, IN_PROGRESS, SUCCEEDED, FAILED, CANCELLED, RECONCILIATION_REQUIRED.

| Current operation state | Attempt | Immutable attempt outcome | Next operation state |
|---|---|---|---|
| IN_PROGRESS | EXECUTE | CONFIRMED_SUCCESS | SUCCEEDED |
| IN_PROGRESS | EXECUTE | CONFIRMED_FAILURE | FAILED |
| IN_PROGRESS | EXECUTE | OUTCOME_UNKNOWN | RECONCILIATION_REQUIRED |
| RECONCILIATION_REQUIRED | RECONCILE | RECONCILED_SUCCESS | SUCCEEDED |
| RECONCILIATION_REQUIRED | RECONCILE | RECONCILED_NOT_APPLIED | PENDING only if the exact same operation remains authorized and retry policy permits; otherwise FAILED |

Rules:

- An EXECUTE attempt is valid only for IN_PROGRESS.
- A RECONCILE attempt is valid only for RECONCILIATION_REQUIRED.
- No new side-effecting attempt is allowed while outcome is unknown.
- A confirmed failure is terminal for that operation; a new attempt requires an explicitly authorized successor operation or a provider contract that proves safe same-operation retry.
- Reconciled-not-applied is not automatically retryable; authorization and retry policy are rechecked.
- A late attempt result is retained as immutable evidence and may update the projection only if its attempt/operation version is still current; contradictory late results trigger reconciliation/incident handling, never overwrite a confirmed result.
- Cancellation is allowed before execution or after reconciliation proves no effect. An in-flight operation with unknown outcome must not be marked CANCELLED.

Delivery uses the same lifecycle but remains a separate aggregate and must revalidate recipient/destination authorization immediately before dispatch. A delivery failure never reverses confirmed publication.

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

The initial Python code implements pure transition and projection rules only. Persistence and command DTOs must additionally enforce:

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

The first executable baseline includes the Python package, pure lifecycle policy module, CLI, tests, Ruff, mypy, and application CI. It deliberately does not include a production persistence adapter, external source fetcher, LLM adapter, publication client, or delivery adapter. These remain gated by their corresponding ADRs and evidence in Document 16.

---

**End of Document**
