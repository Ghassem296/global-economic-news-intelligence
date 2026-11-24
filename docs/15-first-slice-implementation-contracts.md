# GENI-IMPL-015 — First-Slice Implementation Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-IMPL-015  
**Version:** 2.4  
**Status:** Proposed — Pending Project Owner Approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-24

---

## 1. Purpose

This document converts the first-slice repository inventory in Document 02, Section 6.1, and the contract-readiness requirements in GENI-API-009 into a reviewable, method-level baseline.

It is a proposed implementation specification, not an ADR and not an approval of any technology, policy, provider, source license, or business rule. It does not authorize production processing. The Project Owner must approve this contract baseline and all applicable ADRs before dependent implementation begins.

The notation is language- and database-neutral. Identifiers are opaque domain identifiers; concrete representations (UUID, integer, string, etc.) are selected by the implementation only after the applicable technology decision. No SQL, ORM, transport framework, database engine, queue, or public API is selected here.

## 2. Scope and explicit exclusions

The first-slice repository set is:

- SourceRepository
- ArticleRepository
- ArticleRevisionRepository
- EventRepository
- EventMatchCaseRepository
- EventMatchCandidateRepository
- EventMatchDecisionRepository
- ArticleEventLinkRepository
- EvidenceRepository
- AnalysisRepository
- ReportRepository
- PublicationDecisionRepository
- ProcessingRunRepository
- ReviewRepository
- ReviewContextLinkRepository

The contracts below define the minimum operations and invariants for those repositories. Related repositories for report provenance links, publication operations/attempts, rights assessments, content access, collection checkpoints, processing steps, idempotency records, and execution leases must be specified before their respective capabilities are implemented. Review persistence is included in the target first-slice repository baseline because `REPORT_VERSION` is part of the target review scope; however, inclusion does not enable review execution. ReviewService material actions remain disabled until the review DTO schemas, lifecycle/projection rules, authorization policy, and GENI-ADR-014 approval pass Gate A and the corresponding integration tests pass Gate C.

The baseline excludes:
- production source acquisition or full-text retention until GENI-ADR-013 is accepted and source-specific operation rights are approved;
- external LLM transmission until content-rights and privacy-processing authorization are independently satisfied;
- automatic Event creation until the EventCreationPolicy and authorization owner are approved;
- automatic event matching decisions until GENI-ADR-011 and the matching policy are approved;
- publication execution until publication policy, review authority, rights, and target capabilities are approved;
- semantic retrieval, embeddings, market-data integration, translation, audio, and video unless their respective ADRs and stages are approved.

Fixture-driven contract and integration tests may be developed without representing fixtures as licensed production sources.

## 3. Shared contract conventions

### 3.1 Type and nullability notation

- `ID<T>` is an opaque identifier for entity type `T`.
- `Version` is an opaque, monotonically comparable aggregate version used for optimistic concurrency.
- `Instant` is a timezone-aware timestamp.
- `Fingerprint` is a deterministic digest of the canonical logical inputs and relevant policy/version identifiers.
- `ActorType` is a security-owned actor category; its allowed vocabulary is defined by the approved identity contract and is not selected by this document.
- `ActorReference` is an opaque reference to an authenticated human or service identity resolvable by the security layer.
- `AuthorizationReference` is an immutable opaque reference to the authorization/audit context for a state-changing action, resolvable by the security/audit layer.
- `Optional<T>` means the value may be absent; it is not interchangeable with an unknown, denied, or empty value.
- `Page<T>` contains an ordered item list and an optional continuation cursor.
- `Result<T>` is either a successful value or a typed failure; a failure must never be represented as a successful empty result.

The concrete serialization and identifier encodings remain implementation choices.

### 3.2 Common command metadata

Every state-changing application command carries:
- `command_id`;
- `schema_version`;
- authenticated `actor` or service identity;
- immutable `authorization_reference` for operations that require an authorization decision;
- `correlation_id` and optional `causation_id`;
- `idempotency_key` with a documented operation scope;
- `expected_aggregate_version` when updating an existing aggregate;
- deadline/cancellation context where execution can outlive the caller.

A repository method receives only the metadata needed for its persistence responsibility. Authorization decisions are made by the application/domain boundary and their immutable references are persisted with the resulting state change; a repository must not infer authorization from caller-supplied role strings.

### 3.3 Common failures

Repository/application contracts use the error vocabulary in GENI-API-009:
`VALIDATION_ERROR`, `AUTHENTICATION_REQUIRED`, `AUTHORIZATION_DENIED`, `NOT_FOUND`, `CONFLICT`, `DEPENDENCY_UNAVAILABLE`, `TIMEOUT_OUTCOME_UNKNOWN`, `RIGHTS_NOT_ALLOWED`, and `INTERNAL_ERROR`.

Repository-specific failures additionally distinguish:
- `DUPLICATE_IDENTITY`: a uniqueness key already identifies another logical record;
- `STALE_VERSION`: expected aggregate version is no longer current;
- `INVARIANT_VIOLATION`: a proposed write violates a domain invariant;
- `IDEMPOTENCY_KEY_REUSE_CONFLICT`: the same scoped key was supplied with a different request fingerprint.

Only transient infrastructure failures are candidates for bounded retry. Validation, authorization, stale-version, invariant, and fingerprint-conflict failures are not retried unchanged.

### 3.4 Transaction boundary

All methods that mutate one or more related aggregates participate in an application-managed UnitOfWork (or equivalent). The UnitOfWork contract is:

- `begin() -> UnitOfWork`
- `commit() -> CommitResult`
- `rollback() -> void`

A UnitOfWork is single-use. A successful commit makes all participating local writes visible atomically; a failed commit leaves no partial local state. Repositories do not open hidden independent transactions. External side effects never occur inside a database transaction: persist durable intent first, perform the external call, then persist the confirmed or unknown outcome in a new transaction.

This logical contract does not select a transaction library or isolation level. The implementation must prove that its chosen isolation/locking strategy enforces the stated invariants.

## 4. Repository method contracts

The signatures below are logical signatures. Request and result structures named here must be implemented as typed immutable contract objects in the chosen language. The names identify the required contract types, but this baseline does not yet define every field, nullability rule, validation constraint, and serialized representation for every command/query DTO. Those field-level schemas are a remaining Gate A deliverable and must be completed and reviewed before the corresponding method is implemented; do not infer fields from method names.

### 4.1 SourceRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(source_id: ID<Source>) -> Optional<Source>` | Returns the configured source identity and configuration. Does not imply that content retrieval, retention, external processing, or distribution is authorized. |
| `list_collection_enabled` | `list_collection_enabled(query: SourceCollectionQuery) -> Page<Source>` | Stable ordering with a deterministic tie-breaker; bounded page size; only sources enabled for collection are returned. No secret values are returned. |
| `save_configuration` | `save_configuration(command: UpdateSourceConfiguration, expected_version: Version, uow: UnitOfWork) -> Source` | Updates source configuration under optimistic concurrency. Source identity remains stable. Configuration changes do not silently rewrite collection history or rights decisions. |

`SourceCollectionQuery` defines optional source-type, language, geographic-scope and status filters, bounded `limit`, and optional cursor. The exact maximum page size is an operational configuration decision, not a value fixed by this document.

### 4.2 ArticleRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(article_id: ID<Article>) -> Optional<Article>` | Returns the current Article projection, including its current revision reference. |
| `find_by_source_identity` | `find_by_source_identity(source_id: ID<Source>, external_identity: SourceArticleIdentity) -> Optional<Article>` | Resolves an Article using the source-scoped canonical external identity. A URL alone is not assumed globally unique. |
| `save_projection` | `save_projection(article: Article, expected_version: Optional<Version>, uow: UnitOfWork) -> Article` | Used only by ArticleRevisionService in the same UnitOfWork as revision creation/reuse. The projection must point to the latest valid persisted revision. |

`SourceArticleIdentity` contains the source-scoped canonical identifier selected by normalization and may include a canonical URL as a secondary lookup signal. Identity normalization rules must be deterministic and versioned; collision handling returns `CONFLICT`, never silent merge.

### 4.3 ArticleRevisionRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(revision_id: ID<ArticleRevision>) -> Optional<ArticleRevision>` | Returns an immutable revision. |
| `get_current_for_article` | `get_current_for_article(article_id: ID<Article>) -> Optional<ArticleRevision>` | Resolves the exact revision referenced by the Article projection. |
| `find_by_content_identity` | `find_by_content_identity(article_id: ID<Article>, content_hash: Fingerprint, normalization_version: Version) -> Optional<ArticleRevision>` | Finds an unchanged normalized content revision for the same Article. Hash equality across different normalization versions is not assumed equivalent. |
| `append_revision` | `append_revision(revision: ArticleRevision, expected_article_version: Optional<Version>, uow: UnitOfWork) -> ArticleRevision` | Appends a new immutable revision and updates the Article projection in the same UnitOfWork through ArticleRevisionService. Enforces unique `(article_id, revision_number)`; repeated identical content returns/reuses the existing logical revision rather than creating a duplicate. |

The write command must include the exact content reference permitted for the operation, content hash, normalization version, observed time, language, change reason, and applicable rights-assessment reference(s). A hash is not permission to retain the underlying content. Unknown or insufficient rights block restricted content operations.

### 4.4 EventRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(event_id: ID<Event>) -> Optional<Event>` | Returns the current Event projection and version. |
| `find_candidates` | `find_candidates(query: EventCandidateQuery) -> Page<Event>` | Returns candidate Events only; retrieval is not an identity decision. Filters and ordering must be deterministic and bounded. |
| `append_authorized_event` | `append_authorized_event(command: CreateAuthorizedEvent, uow: UnitOfWork) -> Event` | Available only after the applicable EventCreationPolicy and authorization contracts are approved. Requires stable preassigned Event ID, current effective NEW_EVENT_CANDIDATE decision, policy version, actor/authorization reference, and idempotency identity. Creates Event and initial EventHistory atomically. Same logical retry returns the same Event; a conflicting fingerprint fails. |

This repository must not expose an unrestricted create operation to generic workflows. Until the creation gate is approved, the method is unavailable to production application flows.

### 4.5 EventMatchCaseRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(case_id: ID<EventMatchCase>) -> Optional<EventMatchCase>` | Returns case state, effective decision pointer and aggregate version. |
| `find_by_development_identity` | `find_by_development_identity(article_revision_id: ID<ArticleRevision>, development_key: Fingerprint) -> Optional<EventMatchCase>` | Enforces reuse for the same immutable revision and deterministic development scope. |
| `append_case` | `append_case(command: CreateEventMatchCase, uow: UnitOfWork) -> EventMatchCase` | Creates a case for one independently identified development in one exact ArticleRevision. Unique by revision and development key. Repeated identical command is idempotent. |
| `set_effective_decision` | `set_effective_decision(case_id: ID<EventMatchCase>, decision_id: ID<EventMatchDecision>, expected_version: Version, uow: UnitOfWork) -> EventMatchCase` | Updates the current pointer only when the decision belongs to this case and is the authorized successor to the prior effective decision. Participates in the same transaction as decision append and association reconciliation. |

### 4.6 EventMatchCandidateRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(candidate_id: ID<EventMatchCandidate>) -> Optional<EventMatchCandidate>` | Returns one immutable candidate evaluation. |
| `list_for_case` | `list_for_case(case_id: ID<EventMatchCase>, query: CandidateListQuery) -> Page<EventMatchCandidate>` | Returns only candidates scoped to the case, in stable order. |
| `append_evaluation` | `append_evaluation(candidate: EventMatchCandidate, uow: UnitOfWork) -> EventMatchCandidate` | Appends immutable candidate evidence. Idempotency is scoped by case, candidate Event, policy version and input fingerprint. A candidate evaluation never authorizes an ArticleEventLink. |

Candidate scores are not decision confidence. Semantic similarity may be absent; no missing score is replaced with zero.

### 4.7 EventMatchDecisionRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(decision_id: ID<EventMatchDecision>) -> Optional<EventMatchDecision>` | Returns an immutable decision. |
| `get_effective_for_case` | `get_effective_for_case(case_id: ID<EventMatchCase>) -> Optional<EventMatchDecision>` | Resolves the decision referenced by the case's effective pointer. |
| `append_decision` | `append_decision(decision: EventMatchDecision, expected_case_version: Version, uow: UnitOfWork) -> EventMatchDecision` | Appends a decision and preserves supersession history. MATCH must select exactly one eligible candidate from the same case. Non-MATCH outcomes cannot authorize an active association. Decision append, case pointer update and link reconciliation are one atomic local transaction. |

The repository does not calculate match scores or decide outcomes. Those belong to the approved matching policy and Event Resolution Workflow. Policy version, decision actor/method and rationale are mandatory provenance.

### 4.8 ArticleEventLinkRepository

| Method | Signature | Contract |
|---|---|---|
| `get_active_for_case` | `get_active_for_case(case_id: ID<EventMatchCase>) -> Optional<ArticleEventLink>` | Returns at most one active link for the case. |
| `activate_for_match` | `activate_for_match(command: ActivateArticleEventLink, uow: UnitOfWork) -> ArticleEventLink` | Requires the effective MATCH decision, exact case, exact ArticleRevision and Event selected by that decision. Enforces one active link per case. |
| `deactivate_for_successor` | `deactivate_for_successor(command: DeactivateArticleEventLink, uow: UnitOfWork) -> ArticleEventLink` | Preserves the old link and records the successor decision that authorized deactivation. Must be atomic with effective-decision pointer update. |

No method may create or activate a link from a candidate score, NEW_EVENT_CANDIDATE, NO_MATCH, AMBIGUOUS, or REVIEW_REQUIRED outcome.

### 4.9 EvidenceRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(evidence_id: ID<Evidence>) -> Optional<Evidence>` | Returns evidence metadata and permitted provenance/location references. |
| `append_evidence` | `append_evidence(evidence: Evidence, uow: UnitOfWork) -> Evidence` | Persists evidence identity, origin, source attribution, verification state and permitted location references. Evidence does not by itself prove a claim. Source-derived content is subject to operation-specific rights and retention controls. |
| `list_for_subject` | `list_for_subject(subject: EvidenceSubject, query: EvidenceListQuery) -> Page<Evidence>` | Returns bounded, stable, access-controlled evidence references for an ArticleRevision, Event, Claim or Analysis as supported by the model. |

### 4.10 AnalysisRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(analysis_id: ID<Analysis>) -> Optional<Analysis>` | Returns immutable analysis output and version metadata. |
| `append_analysis` | `append_analysis(command: AppendAnalysis, uow: UnitOfWork) -> Analysis` | Persists one versioned analysis with exact input/evidence references, result-schema version, methodology version, model/prompt provenance where used, and explicit unknown/uncertainty semantics. |
| `list_for_event` | `list_for_event(event_id: ID<Event>, analysis_type: AnalysisType, query: AnalysisListQuery) -> Page<Analysis>` | Returns only the requested analysis type; importance, economic relevance and economic impact remain distinct types. |

The write command must reject missing required provenance and must not collapse unknown, not-established, zero, and false into one value.

### 4.11 ReportRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(report_id: ID<Report>) -> Optional<Report>` | Returns the exact immutable report version. |
| `get_latest_for_subject` | `get_latest_for_subject(subject: ReportSubject) -> Optional<Report>` | Returns the latest version for the requested subject without mutating historical versions. |
| `append_report_version` | `append_report_version(command: AppendReportVersion, uow: UnitOfWork) -> Report` | Appends an immutable report version with exact event/article-revision/analysis/evidence provenance. Report content and all required provenance links commit atomically. Generation alone does not publish or deliver the report. |

The report command includes a deterministic input fingerprint, template/version, generation provenance, and explicit content representation. Repeating the same logical generation request must not create uncontrolled duplicate versions.

### 4.12 PublicationDecisionRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(decision_id: ID<PublicationDecision>) -> Optional<PublicationDecision>` | Returns an immutable eligibility decision. |
| `get_effective_for_report` | `get_effective_for_report(report_id: ID<Report>) -> Optional<PublicationDecision>` | Returns the effective decision for the exact report version, not merely a mutable report family. |
| `append_decision` | `append_decision(command: AppendPublicationDecision, uow: UnitOfWork) -> PublicationDecision` | Persists an immutable decision, policy version, reasons, caveats, actor/provenance and supersession link. A material review outcome must result in a successor decision. This method never calls an external publication target. |

A decision for one report version does not authorize publication of a different version. Publication eligibility and recipient-distribution authorization remain separate.

### 4.13 ProcessingRunRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(run_id: ID<ProcessingRun>) -> Optional<ProcessingRun>` | Returns durable run state and version. |
| `create_run` | `create_run(command: CreateProcessingRun, uow: UnitOfWork) -> ProcessingRun` | Creates one logical run using a stable run/idempotency identity and explicit target/run type. Repeated same-fingerprint command returns the same logical run. |
| `transition_run` | `transition_run(command: TransitionProcessingRun, expected_version: Version, uow: UnitOfWork) -> ProcessingRun` | Applies only an allowed transition, with actor, time, reason/error category and optimistic concurrency. Exact allowed states/transitions must be imported from the approved processing state machine; this contract does not invent them. |
| `find_recoverable` | `find_recoverable(query: RecoverableRunQuery) -> Page<ProcessingRun>` | Returns bounded candidates for recovery only. It does not grant worker ownership; lease acquisition and fencing-token validation are separate required controls under GENI-ADR-016. |

A run status timestamp is not proof of lease ownership. No worker may commit a state change without validating its current fencing token when durable leases are enabled.

### 4.14 ReviewRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(review_record_id: ID<ReviewRecord>) -> Optional<ReviewRecord>` | Returns the current review-task projection and aggregate version; it does not authorize an action or imply that the lifecycle is implementation-ready. |
| `create_task` | `create_task(command: CreateReviewTask, uow: UnitOfWork) -> ReviewRecord` | Creates one typed review task for an exact supported subject and decision reference. The initial status and required `CREATED` action must be assigned by the approved lifecycle policy; this method is blocked until that policy and DTO schema are approved. |
| `append_action` | `append_action(command: AppendReviewAction, expected_version: Version, uow: UnitOfWork) -> ReviewAction` | Appends one immutable action with atomically allocated per-task sequence and idempotency enforcement. Updating the ReviewRecord projection in the same UnitOfWork is permitted only under the approved action-to-projection mapping; no mapping is inferred here. |
| `list_actions` | `list_actions(review_record_id: ID<ReviewRecord>, query: ReviewActionListQuery) -> Page<ReviewAction>` | Returns immutable actions in sequence order with bounded pagination; it does not reconstruct a projection using unapproved transition rules. |

`ReviewRepository` owns persistence of ReviewRecord and ReviewAction only. ReviewService validates actor authority and the approved lifecycle policy; a review action never directly mutates the authoritative domain decision or performs publication, delivery, rights, or event-identity side effects.

### 4.15 ReviewContextLinkRepository

| Method | Signature | Contract |
|---|---|---|
| `add_context_links` | `add_context_links(review_record_id: ID<ReviewRecord>, links: NonEmptyList<ReviewContextLinkInput>, uow: UnitOfWork) -> List<ReviewContextLink>` | Adds exact typed context references for an existing review task. The application validates reference existence, subject association, reviewer access, and task mutability. All links in the command are persisted atomically. |
| `list_for_review` | `list_for_review(review_record_id: ID<ReviewRecord>) -> List<ReviewContextLink>` | Returns the task's immutable context references in deterministic order. It must not dereference or copy restricted source content. |

Context links are immutable once the review is completed. Corrections require a successor task or an append-only action consistent with the approved review policy. Field-level DTO schemas, ordering, uniqueness, and completion-race behavior remain Gate A decisions.

## 5. Cross-repository transaction map

The following local write sets are indivisible. They must be implemented through one UnitOfWork or an equivalent proven consistency mechanism:

| Operation | Atomic local write set |
|---|---|
| Persist a material article revision | ArticleRevision insert + Article current-projection update + associated processing/idempotency state required by the operation |
| Create an Event | Event insert + initial EventHistory + authorized creation/idempotency provenance |
| Record an event-match decision | EventMatchDecision append + EventMatchCase effective pointer + required ArticleEventLink activation/deactivation |
| Persist evidence-backed analysis | Analysis append + exact AnalysisInput and AnalysisEvidenceLink set |
| Persist report version | Report version + all required report-to-event/article-revision/analysis/evidence links |
| Record publication eligibility | PublicationDecision append + supersession/effective-decision projection, if one is used |
| Create review task | ReviewRecord insert + initial `CREATED` ReviewAction + initial projection, once the approved initial-state/action mapping exists |
| Append review action | ReviewAction append + sequence/idempotency claim + ReviewRecord projection update, once the approved action-to-projection mapping exists |
| Attach review context | All ReviewContextLink inserts for one command, after subject/access validation |

The external publication call is explicitly outside the transaction. Its logical PublicationRecord and durable intent must exist before the call; attempt result and reconciliation state are committed afterward. Delivery follows the equivalent durable-intent pattern.

## 6. Required application commands and orchestration boundaries

Repositories are not called directly by transport handlers or LLM-generated tool code. Application workflows own orchestration and authorization.

| Application operation | Required inputs | Required result |
|---|---|---|
| `PersistArticleRevision` | Source ID, source-scoped article identity, normalized revision content/reference, content fingerprint, normalization version, observed time, rights decision references, idempotency metadata | Article ID, exact revision ID, created/reused indicator, resulting Article version |
| `ResolveEventDevelopment` | Exact ArticleRevision ID, stable development key, scope description, matching policy version, candidate retrieval/evaluation inputs, execution metadata | EventMatchCase ID, immutable candidate IDs, immutable decision ID or explicit unresolved outcome |
| `ApplyEventMatchDecision` | Case ID, decision ID, expected case version, authorization context where required | Effective decision ID and resulting active-link state |
| `RecordEvidence` | Evidence source/origin, exact subject references, permitted location references, rights provenance, idempotency metadata | Evidence ID and provenance result |
| `PersistAnalysis` | Analysis type, exact inputs/evidence IDs, schema/methodology/prompt/model versions as applicable, result and uncertainty representation | Immutable Analysis ID |
| `CreateReportVersion` | Exact source revisions, event/analysis/evidence references, template version, generation provenance, deterministic fingerprint | Immutable Report version ID and provenance completeness result |
| `DecidePublicationEligibility` | Exact Report version, policy version, evidence/rights/security context, reviewer decision references where applicable | Immutable PublicationDecision ID and permitted next action |
| `CreateReviewTask` | One canonical review family, exact subject and related decision references, reason, priority-policy version, actor/authorization context, idempotency metadata | ReviewRecord ID; execution remains blocked until approved initial-state and DTO contracts exist |
| `AppendReviewAction` | ReviewRecord ID, action type, actor/authorization context, expected version, idempotency metadata, action-specific fields | Immutable ReviewAction ID and resulting projection only under an approved transition contract |
| `AttachReviewContext` | ReviewRecord ID and exact typed context references with reviewer-access context | Immutable ReviewContextLink IDs; no source content is copied |

These command names identify logical boundaries; they do not authorize a workflow whose governing ADR or policy is still Proposed. The application must fail closed when required authorization or policy references are missing, stale, revoked, or out of scope.

## 7. State-transition and concurrency requirements

1. Every mutable aggregate update supplies an expected version or equivalent compare-and-swap condition.
2. Immutable records are appended; corrections create successors and preserve supersession links.
3. A decision pointer is a projection, not the authoritative historical record.
4. EventMatchDecision and ArticleEventLink changes are atomic; only the effective MATCH decision can authorize one active link per case.
5. PublicationDecision is not PublicationRecord; eligibility does not execute an external side effect.
6. A ProcessingRun is not a worker lease. A stale worker must be fenced from committing after lease ownership changes.
7. Unknown external outcomes are not failures and are not blindly retried; reconcile first.
8. A duplicate idempotency key with a different request fingerprint is a conflict.
9. Empty, unknown, denied, not-established and zero values remain semantically distinct.
10. No repository method silently performs a domain decision, calls an LLM, accesses the network, or triggers an external side effect.

## 8. Implementation and approval gates

### Gate A — Contract approval

Before implementation of these contracts:
- Project Owner reviews and approves this document.
- The relevant ADRs are explicitly accepted or the affected capability is isolated behind a disabled boundary.
- For any ReviewService capability: approve the `CreateReviewTask`, `AppendReviewAction`, and `ReviewActionListQuery` schemas; define the initial ReviewRecord state, complete status transition graph, action-to-projection mapping, terminal/cancellation semantics, reopen-segment identity, concurrency/sequence behavior, and authorization matrix; accept GENI-ADR-014. Until all are complete, ReviewRepository and ReviewContextLinkRepository may be contract-tested as persistence interfaces only, but no material review workflow may be enabled.
- Document 02 ownership and transaction crosswalk remains consistent with these method contracts.
- Document 03 schema constraints can enforce the listed uniqueness and referential invariants.
- Security, content-rights and privacy authorization requirements are mapped to each operation.

### Gate B — Technology proof and implementation selection

Before persistence adapters are selected:
- GENI-ADR-005 is accepted after the documented workload/backup/concurrency proof-of-concept.
- Database engine, driver, migration tool, async strategy, transaction isolation/locking and supported runtime versions are recorded.
- GENI-ADR-016 is accepted before durable lease, fencing, idempotency and recovery behavior is treated as approved implementation policy.

### Gate C — Executable verification

Before a first-slice milestone is declared complete:
- Every repository contract has schema/type tests and contract tests.
- Atomic write sets have rollback and failure-injection tests.
- Optimistic concurrency has stale-write tests.
- Idempotency has same-fingerprint replay and different-fingerprint conflict tests.
- Event matching has case-scoped candidate/decision/link invariant tests.
- Review tests cover task creation, exact typed subjects, append-only action ordering, idempotency, projection rebuild, authorization, concurrency, context-link access, and all approved transitions; tests must not encode provisional transitions.
- Publication decision tests prove no external publication side effect occurs.
- Rights/privacy denial, unknown, expiry, revocation and scope-mismatch tests fail closed.
- Processing recovery tests prove stale workers cannot commit.
- End-to-end fixture tests preserve exact ArticleRevision, Evidence, Analysis and Report provenance.
- CI results and commit SHA are recorded; documentation alone is not evidence of passing tests.

## 9. Unresolved items intentionally not decided here

The following remain open and must not be guessed by implementers:

- Concrete programming-language types, ID encoding and serialization.
- Database engine, schema dialect, driver, ORM/query layer and migration tool.
- Transaction isolation level, lock strategy and numeric concurrency targets.
- EventCreationPolicy values, authorization owner and review requirements.
- Event matching thresholds, scoring calibration and policy version semantics.
- Source-specific rights profiles, retention periods and permitted content operations.
- Privacy lawful-basis/jurisdiction rules, provider/region allowlists and transfer decisions.
- Publication quality thresholds, reviewer roles and target-specific replacement/withdrawal capabilities.
- Review priority scale/SLA, task initial-state rule, action-to-status projection, reopened task-segment identity, terminal-state and cancellation rules, and reviewer role/separation-of-duties matrix.
- Numeric retry counts, timeouts, page-size maxima, lease durations and recovery objectives.
- External API or transport framework.

These are explicit dependencies, not missing values to be filled with arbitrary defaults.

## 10. Field-level DTO schema tranche (v1.2)

### 10.1 Authority and schema notation

This section records only fields explicitly supported by Documents 02/03 and the existing method contracts. It is a logical field catalogue, not a wire-format schema. It does not select UUID/string encodings, JSON property names, database columns, enum serialization, maximum lengths, or transport validation rules.

- **Required** means the domain model or operation contract requires the value for the stated operation.
- **Conditional** means required only for the stated outcome/type.
- **Nullable** means the model explicitly permits absence.
- **TBD** means the source documents do not establish a safe field contract; implementation is blocked until resolved.
- Common command metadata in §3.2 applies to state-changing commands. The metadata is not duplicated in each table.
- A repository DTO must not accept client-supplied values for fields that are server-owned projections, such as effective pointers or current statuses.

### 10.2 CreateEventMatchCase

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `article_revision_id` | `ID<ArticleRevision>` | Required | Must resolve to the exact immutable revision; case scope cannot drift to another revision. | Document 03 §7.1 |
| `development_key` | `Fingerprint` | Required | Deterministic and stable within the exact ArticleRevision; identifies one development, not a random run. Unique with ArticleRevision. | Document 03 §7.1 |
| `scope_description` | `string` | Required | Describes the independently identified development. Exact length/normalization constraints TBD. | Document 03 §7.1 |
| `metadata` | `JSON/object` | Optional | Must not duplicate authoritative fields or contain secrets/restricted source content by default. Schema TBD. | Document 03 §7.1 |

Server-owned fields: case ID, initial case status, effective-decision pointer, created/closed timestamps, and aggregate version. The exact initial case status and who may create/reopen/cancel a case are not defined as a complete command contract.

### 10.3 EventMatchCandidate evaluation record

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `id` | `ID<EventMatchCandidate>` | Required | Stable immutable record identity. | Document 03 §7.2 |
| `case_id` | `ID<EventMatchCase>` | Required | Must resolve to the exact case. | Document 03 §7.2 |
| `candidate_event_id` | `ID<Event>` | Required | Candidate Event must be eligible in this case. | Document 03 §7.2 |
| `lexical_similarity` | `number/null` | Nullable | Null when not evaluated; scale/direction/version semantics must be defined by matching policy. | Document 03 §7.2 |
| `semantic_similarity` | `number/null` | Nullable | Must remain null when semantic retrieval is disabled/not evaluated. | Document 03 §7.2 |
| `entity_overlap_score` | `number/null` | Nullable | Null when not evaluated; no implicit zero. | Document 03 §7.2 |
| `temporal_compatibility_score` | `number/null` | Nullable | Null when not evaluated; no implicit zero. | Document 03 §7.2 |
| `geographic_compatibility_score` | `number/null` | Nullable | Null when not evaluated; no implicit zero. | Document 03 §7.2 |
| `overall_score` | `number/null` | Nullable | Null when not evaluated; not a decision confidence. | Document 03 §7.2 |
| `matching_method` | `string/enum` | Required | Vocabulary and allowed methods require matching-policy approval. | Document 03 §7.2 |
| `matching_policy_version` | `Version` | Required | Must identify the exact policy/configuration used. | Document 03 §7.2 |
| `candidate_input_fingerprint` | `Fingerprint` | Required | Covers revision/development scope, candidate Event version and evaluation inputs/configuration. | Document 03 §7.2 |
| `supersedes_candidate_id` | `Optional<ID<EventMatchCandidate>>` | Nullable | If present, same case and same candidate Event; no cross-case supersession. | Document 03 §7.2 |
| `candidate_status` | `enum` | Required | Candidate-processing status only; never ACCEPTED/REJECTED/SUPERSEDED. | Document 03 §7.2 |
| `evaluation_reason` | `string` | Required | Explains eligibility/ineligibility/evaluation; exact length TBD. | Document 03 §7.2 |
| `evaluated_at` | `Instant` | Required | Timestamp of evaluation. | Document 03 §7.2 |
| `created_at` | `Instant` | Required | Immutable creation timestamp. | Document 03 §7.2 |
| `metadata` | `JSON/object` | Optional | Versioned extension only; schema TBD. | Document 03 §7.2 |

The allowed candidate processing vocabulary is only exemplified as `GENERATED`, `EVALUATED`, and `INELIGIBLE`; the authoritative complete enum and transition rules are not explicitly closed. Do not treat this illustrative list as a final exhaustive enum until approved.

### 10.4 EventMatchDecision

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `id` | `ID<EventMatchDecision>` | Required | Immutable decision identity. | Document 03 §7.3 |
| `case_id` | `ID<EventMatchCase>` | Required | Must identify exactly one case. | Document 03 §7.3 |
| `outcome` | `enum` | Required | One of MATCH, NEW_EVENT_CANDIDATE, NO_MATCH, AMBIGUOUS, REVIEW_REQUIRED. | Document 03 §7.3 |
| `selected_candidate_id` | `Optional<ID<EventMatchCandidate>>` | Conditional | Required exactly for MATCH; candidate must be eligible and belong to same case. | Document 03 §7.3 |
| `proposed_event_reference` | `Optional<ID<Event>>` | Conditional | Required for NEW_EVENT_CANDIDATE; stable preassigned identifier; does not itself create Event/link. | Document 03 §7.3 |
| `decision_method` | `string/enum` | Required | Method vocabulary and authorization semantics TBD under matching policy. | Document 03 §7.3 |
| `decision_confidence` | `number/null` | Optional | Distinct from candidate similarity; semantics/calibration must be explicit. | Document 03 §7.3 |
| `decision_rationale` | `string` | Required | Must explain outcome; exact length/format TBD. | Document 03 §7.3 |
| `matching_policy_version` | `Version` | Required | Exact policy version used. | Document 03 §7.3 |
| `decided_by_type` | `string/enum` | Required | Actor category; vocabulary and authorization mapping TBD. | Document 03 §7.3 |
| `decided_by_reference` | `string/reference` | Required | Must resolve to authenticated actor/service identity; representation TBD. | Document 03 §7.3 |
| `authorization_reference` | `AuthorizationReference` | Required | Immutable reference from trusted security/application context; must resolve to the exact action, case/resource, actor, scope, policy/version, timestamp, and result. | Documents 03 §7.3, 08 §5 |
| `supersedes_decision_id` | `Optional<ID<EventMatchDecision>>` | Nullable | If present, same case and must be prior effective decision; one direct successor constraint applies. | Document 03 §§7.3–7.4 |
| `created_at` | `Instant` | Required | Immutable decision timestamp. | Document 03 §7.3 |
| `metadata` | `JSON/object` | Optional | Must not override typed authoritative fields. | Document 03 §7.3 |

Outcome-specific constraints:
- MATCH: exactly one selected candidate; proposed_event_reference absent.
- NEW_EVENT_CANDIDATE: proposed_event_reference required; selected_candidate_id absent.
- NO_MATCH, AMBIGUOUS, REVIEW_REQUIRED: neither candidate selection nor event creation authorization is implied.
- A review action is not a decision. A material review outcome creates a successor decision.
- The case effective pointer and all affected ArticleEventLink changes are one atomic write set.

### 10.5 AppendPublicationDecision

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `id` | `ID<PublicationDecision>` | Required | Immutable decision identity. | Document 03 §11.6 |
| `report_id` | `ID<Report>` | Required | Exact immutable report version, never a report family/current alias. | Documents 03 §11.6, 15 §4.12 |
| `decision` | `enum` | Required | PUBLISH, PUBLISH_WITH_CAVEATS, HOLD_FOR_REVIEW, REJECT. | Document 03 §11.6 |
| `reason_codes` | `list<string/enum>` | Required | Controlled vocabulary is TBD; must be stable and auditable. | Document 03 §11.6 |
| `explanation` | `string` | Required | Rationale for the decision; exact constraints TBD. | Document 03 §11.6 |
| `caveats` | `Optional<list/string>` | Nullable | Required in meaningful form for PUBLISH_WITH_CAVEATS; exact representation TBD. | Document 03 §11.6 |
| `policy_version` | `Version` | Required | Exact publication policy version. | Document 03 §11.6 |
| `actor_type` | `ActorType` | Required | Authenticated actor category from trusted command context; allowed values are governed by the security identity contract, not caller-supplied role text. | Documents 03 §11.6, 08 §5 |
| `actor_reference` | `ActorReference` | Required | Authenticated human or service identity; must resolve through the security layer. | Documents 03 §11.6, 08 §5 |
| `authorization_reference` | `AuthorizationReference` | Required | Immutable authorization/audit reference for the exact decision action; must be resolvable and valid at decision time. | Documents 03 §11.6, 08 §5 |
| `decided_at` | `Instant` | Required | Immutable decision time. | Document 03 §11.6 |
| `supersedes_decision_id` | `Optional<ID<PublicationDecision>>` | Nullable | If present, must belong to the same exact report version and be the effective predecessor. | Document 03 §11.6 |
| `metadata` | `JSON/object` | Optional | Typed decision fields remain authoritative. | Document 03 §11.6 |

**Resolved provenance contract:** Document 03 §11.6 and this DTO now use the same required `actor_type`, `actor_reference`, and `authorization_reference` fields. Values originate from authenticated command/security context; repositories persist validated references and must not infer authorization from caller-supplied role strings. The security/audit layer must be able to resolve the authorization reference to actor, action, resource, scope, policy/version, timestamp and result. A missing, invalid, stale or unverifiable reference blocks the append. **Effective-successor contract:** the first decision has no predecessor; each successor names the current effective decision for the exact report version. Only one direct successor may reference a predecessor. Append validates expected aggregate version and predecessor, then persists the decision and effective pointer atomically. A stale/concurrent append returns CONFLICT. See GENI-FOUNDATION-017 §8.

### 10.6 CreateProcessingRun

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `id` | `ID<ProcessingRun>` | Required or server-assigned | Stable logical run identity; assignment ownership must be fixed by implementation contract. | Document 03 §13.1 |
| `run_type` | `string/enum` | Required | Must identify the workflow kind; vocabulary is not closed in Document 03. | Document 03 §13.1 |
| `target_type` | `string/enum` | Required | Must pair with target_id and resolve to a supported target family. | Document 03 §13.1 |
| `target_id` | `ID<target>` | Required | Polymorphic reference; application validates existence and target_type agreement. | Document 03 §13.1 |
| `idempotency_key` | `string` | Required | Unique within canonical operation/target scope; exact format/length TBD. | Documents 03 §13.1, §13.2.2 |
| `input_fingerprint` | `Fingerprint` | Required | Same key + same fingerprint reuses logical operation; changed fingerprint conflicts. | Documents 03 §§13.1, 13.2.2 |

Server assigns the run ID and initial PENDING status. started_at remains null until the first valid transition to RUNNING; lease and heartbeat fields are initialized only when a worker lease is acquired. Retry scheduling is represented separately from lifecycle status. Terminal-run retry creates a successor run with parent_run_id; PARTIALLY_COMPLETED recovery resumes the same run under explicit recovery authorization. See GENI-FOUNDATION-017 §4.

### 10.7 TransitionProcessingRun

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `run_id` | `ID<ProcessingRun>` | Required | Exact durable run. | Document 03 §13.1 |
| `expected_version` | `Version` | Required | Compare-and-swap against current aggregate version. | Document 15 §§4.13, 7 |
| `new_status` | `ProcessingRunStatus` | Required | Must be one of the declared statuses and an allowed transition under GENI-FOUNDATION-017 §4; arbitrary status assignment is rejected. | Document 03 §13.1 |
| `actor/worker_reference` | `ActorReference` | Required | Authenticated service/worker identity; concrete representation TBD. | Documents 15 §3.2, 03 §13.2.1 |
| `fencing_token` | `integer` | Conditional | Required for every worker state-changing write when durable leases are enabled; must equal current token. | Document 03 §13.2.1 |
| `occurred_at` | `Instant` | Required | Server-trusted transition time; clock authority/precision TBD. | Document 15 §4.13 |
| `reason/error_category` | `Optional<string/enum>` | Conditional | Required when transition represents failure/cancellation or other reasoned outcome; exact categories TBD. | Document 15 §4.13 |

ProcessingRun transitions, terminal states, recovery identity, and step aggregation are defined in GENI-FOUNDATION-017 §4. This DTO must invoke that policy; it must not accept a caller-supplied arbitrary target status.

### 10.8 RecoverableRunQuery and shared query DTOs

| DTO | Fields established by source | Still unresolved |
|---|---|---|
| `RecoverableRunQuery` | Bounded page limit and optional cursor are required by the generic Page/query contract; optional filters may scope run type/target/status only if approved. | Exact filters, eligible statuses, ordering, lease-expiry cutoff, consistency semantics and max page size. |
| `CandidateListQuery` | Bounded limit, optional cursor, stable ordering. | Sort keys, filter set, maximum page size and cursor encoding. |
| `SourceCollectionQuery` | Optional source-type, language, geographic-scope and status filters; bounded limit; optional cursor. | Exact enum vocabularies, default/max page size, ordering and cursor format. |
| `EventCandidateQuery` | Candidate retrieval must be bounded, deterministic and stably ordered. | Filter fields, eligibility rules, tie-breakers and page bounds. |
| `AnalysisListQuery` | Query is scoped by event_id and analysis_type in repository signature. | Additional filters, sort order and page contract details. |

### 10.9 Explicit state-machine inventory

The state-machine gaps identified in version 1.9 have been closed at the logical policy level by GENI-FOUNDATION-017. That document is the normative, executable lifecycle contract for the initial implementation foundation. The Python policies and unit tests implement its transition guards and projection rules.

| Aggregate / concept | Closed lifecycle contract | Remaining implementation boundary |
|---|---|---|
| ProcessingRun | States, transitions, terminal states, recovery identity, and run aggregation are defined in GENI-FOUNDATION-017 §§4.1–4.3. | Durable history, fencing, attempts, and transactional persistence. |
| ProcessingStep | Closed status vocabulary, transitions, retry/block guards, and terminal semantics are defined in GENI-FOUNDATION-017 §5. | ProcessingStepAttempt persistence and run/step transaction implementation. |
| EventMatchCase | Initial state, decision-to-case projection, transitions, reopening, and terminal states are defined in GENI-FOUNDATION-017 §6. | Atomic persistence with effective decision and ArticleEventLink reconciliation. |
| EventMatchCandidate | GENERATED → EVALUATED/INELIGIBLE and immutable successor behavior are defined in GENI-FOUNDATION-017 §7. | Candidate persistence, uniqueness, and concurrent idempotency. |
| EventMatchDecision | Immutable outcome and linear successor semantics are defined in Documents 03/15 and GENI-FOUNDATION-017 §8. | Database uniqueness, authorization, and transaction proof. |
| PublicationDecision | Exact-report-version scope, linear effective successor, and outcome effects are defined in GENI-FOUNDATION-017 §8. | Caveat DTO, authorization, uniqueness, and persistence concurrency. |
| PublicationRecord / PublicationAttempt | EXECUTE/RECONCILE outcome mapping and unknown-outcome behavior are defined in GENI-FOUNDATION-017 §9. | Provider-specific reconciliation and durable attempt persistence. |
| DeliveryRecord / DeliveryAttempt | Same external-operation state model as publication, with recipient authorization revalidation, is defined in GENI-FOUNDATION-017 §9. | Destination-specific idempotency and reconciliation contract. |
| ReviewRecord / ReviewAction | Initial action, status projection, action guards, and successor-segment reopening are defined in GENI-FOUNDATION-017 §10. | Reviewer identity/authorization and persistence sequencing. |
| ExecutionLease / IdempotencyRecord | Ownership, fencing, and scoped replay semantics remain defined in Document 03 §13.2. | Concrete database atomicity, expiry policy, and operational tuning. |

A lifecycle being specified and unit-tested does not imply that its persistence adapter, authorization policy, or external capability is enabled.

### 10.10 Remaining contract blockers

The lifecycle transition tables previously listed as open questions are no longer open at the logical policy level. The following work remains mandatory before dependent persistence or external workflows are enabled.

#### 10.10.1 Field-level command and query schemas

For each first-slice DTO, define a versioned schema with:
- Exact field name, type, requiredness, and null semantics.
- String length, numeric range, enum vocabulary, canonicalization, and timezone rules.
- Server-owned versus caller-owned fields.
- Actor and authorization context requirements.
- Idempotency scope and request fingerprint inputs.
- Expected aggregate version and conflict behavior.
- Validation and typed failure outcomes.
- Data classification and permitted logging behavior.

The DTOs required for the first persistence slice include SourceCollectionQuery, UpdateSourceConfiguration, SourceArticleIdentity, article/revision append commands, EventCandidateQuery, CreateEventMatchCase, candidate evaluation, EventMatchDecision append, ArticleEventLink activation/deactivation, Evidence append, Analysis append, Report version append, and PublicationDecision append. Query DTOs must also define stable ordering, maximum page size, and cursor consistency.

#### 10.10.2 Persistence and transaction proof

Before selecting or enabling the physical database, complete GENI-ADR-005 proof-of-concept and record:
- Engine and supported version.
- Driver and synchronous/asynchronous access strategy.
- Migration tool and clean-install/upgrade behavior.
- Transaction isolation/locking and optimistic concurrency behavior.
- Unique constraints for idempotency and linear decision successors.
- Concurrent writer measurements under the expected deployment topology.
- Backup/restore and crash-recovery evidence.

For each multi-aggregate transition, identify the exact write set and prove atomicity. External effects must use durable intent and attempt records; they must never be included in a long-running database transaction.

#### 10.10.3 Authorization, policy, and capability gates

The following are separate from lifecycle mechanics and remain governed by their ADRs:
- GENI-ADR-004 publication eligibility and publication policy.
- GENI-ADR-005 persistence selection.
- GENI-ADR-006 provider-independent LLM execution.
- GENI-ADR-011 event identity and matching policy.
- GENI-ADR-013 source-specific rights and content use.
- GENI-ADR-014 reviewer identity, authority, and material review actions.
- GENI-ADR-016 durable async execution, leases, idempotency, and recovery.
- GENI-ADR-017 LLM budget and evaluation policy.
- GENI-ADR-019 economic assessment methodology.
- GENI-ADR-020 privacy processing authorization.

No transition table grants authority. Every material command still requires server-side authorization and immutable provenance.

#### 10.10.4 Persistence-specific records still required

Before implementing the corresponding capability, add explicit contracts for:
- ProcessingStepAttempt and append-only run/step transition history.
- PublicationRecord and PublicationAttempt.
- DeliveryRecord and DeliveryAttempt.
- ExecutionLease and IdempotencyRecord adapters.
- Report provenance links and content-rights references.
- Review lifecycle segment identity and immutable action sequencing.
- Event identity operation reconciliation and affected-record lineage.

These records must not be collapsed into generic status fields or hidden inside an unrelated aggregate.


### 10.11 Core article-to-report command and query schemas (tranche v1.3)

This tranche makes the operation payloads explicit for the core article-to-report path. It supplements, and does not replace, the entity field catalogues in §§10.2–10.7. It is still a logical schema: concrete serialization, identifier encoding, string bounds, numeric precision, enum closure, and transport representation remain unselected.

#### 10.11.1 PersistArticleRevision

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `source_id` | `ID<Source>` | Required | Must resolve to the configured Source. |
| `source_article_identity.canonical_source_identifier` | `string` | Required | Stable canonical identity scoped to this Source; normalization is deterministic and versioned. |
| `source_article_identity.canonical_url` | `string/null` | Optional | Secondary lookup signal only; it does not replace source-scoped identity. |
| `original_url` | `string` | Required | Must pass URL validation; preserve separately from canonical_url. |
| `external_id` | `string/null` | Optional | Source-provided identifier; uniqueness is source-scoped and applies only when meaningful. |
| `normalized_title` | `string` | Required | The title stored on the immutable revision and current Article projection. |
| `content_reference` | `reference/null` | Conditional | Required when content is retained or referenced; absent only with an explicit metadata-only/unavailable content state. Must point only to content permitted for this operation. |
| `content_hash` | `Fingerprint` | Required | Computed from the declared normalized representation; a hash does not grant content-retention rights. |
| `content_normalization_version` | `Version` | Required | Identifies the exact normalization rules used for the hash and any offsets. |
| `summary` | `string/null` | Optional | May contain only source material or derived text permitted by the applicable rights decision. |
| `language` | `string/null` | Optional | Declared or detected language; exact language-tag format remains a serialization decision. |
| `published_at` | `Instant/null` | Optional | Source publication time; unknown remains null. |
| `observed_at` | `Instant` | Required | Trusted observation time for this revision. |
| `change_reason` | `string/enum` | Required | Explains why this revision is appended; controlled vocabulary and free-text bounds remain open. |
| `rights_assessment_references` | `List<ID<RightsAssessment>>` | Conditional | Required for every source-derived content operation that is governed by a rights assessment; each reference must cover the exact operation and content scope. |
| `metadata` | `object` | Optional | Versioned, non-secret extension; must not duplicate authoritative typed fields. |

Server-owned values include Article ID when first created, ArticleRevision ID, revision number, current_revision_id, rights_status projection, created/updated timestamps, and resulting aggregate version. The application must atomically append/reuse the immutable ArticleRevision and update the Article current projection. Same Article + same content hash + same normalization version reuses the existing logical revision; a different normalization version is not presumed equivalent.

#### 10.11.2 EvaluateEventMatchCandidate

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `case_id` | `ID<EventMatchCase>` | Required | Case must belong to the exact ArticleRevision/development scope being evaluated. |
| `candidate_event_id` | `ID<Event>` | Required | Candidate Event must be eligible under the applicable matching policy. |
| `matching_method` | `string/enum` | Required | Method vocabulary is policy-governed and is not closed by this document. |
| `matching_policy_version` | `Version` | Required | Exact matching policy/configuration version. |
| `candidate_input_fingerprint` | `Fingerprint` | Required | Covers ArticleRevision, development scope, candidate Event version, and evaluation inputs/configuration. |
| `lexical_similarity` | `number/null` | Nullable | Null when not evaluated; scale and precision require policy definition. |
| `semantic_similarity` | `number/null` | Nullable | Must remain null when semantic retrieval is disabled or not evaluated. |
| `entity_overlap_score` | `number/null` | Nullable | Null when not evaluated; never default to zero. |
| `temporal_compatibility_score` | `number/null` | Nullable | Null when not evaluated; never default to zero. |
| `geographic_compatibility_score` | `number/null` | Nullable | Null when not evaluated; never default to zero. |
| `overall_score` | `number/null` | Nullable | Null when not evaluated; not a decision confidence. |
| `evaluation_reason` | `string` | Required | Safe explanation of eligibility/evaluation; exact length bound remains open. |

The candidate record ID, candidate processing status, evaluated_at, and created_at are server-owned. The idempotency scope is the exact case, candidate Event, matching-policy version, and candidate-input fingerprint. A repeated identical evaluation resolves to the same logical evaluation; changed inputs or policy create a successor immutable evaluation. Candidate evaluation never creates an EventMatchDecision or ArticleEventLink.

#### 10.11.3 AppendEventMatchDecision

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `case_id` | `ID<EventMatchCase>` | Required | Exact case being resolved. |
| `outcome` | `string/enum` | Required | MATCH, NEW_EVENT_CANDIDATE, NO_MATCH, AMBIGUOUS, or REVIEW_REQUIRED. |
| `selected_candidate_id` | `ID<EventMatchCandidate>/null` | Conditional | Required exactly for MATCH; candidate must belong to this case and be eligible. |
| `proposed_event_reference` | `ID<Event>/null` | Conditional | Required exactly for NEW_EVENT_CANDIDATE; stable preassigned ID, not an instruction to create an Event. |
| `decision_method` | `string/enum` | Required | Method vocabulary and permitted actor/policy combinations remain governed by the matching policy. |
| `decision_confidence` | `number/null` | Optional | Null unless the method defines semantics; never copy candidate similarity into this field. |
| `decision_rationale` | `string` | Required | Explains the outcome and material evidence/limitations; exact length/format remain open. |
| `matching_policy_version` | `Version` | Required | Exact policy version used. |
| `supersedes_decision_id` | `ID<EventMatchDecision>/null` | Conditional | Absent for the first decision; otherwise must identify the current effective predecessor in the same case. |

The decision ID, trusted actor identity, authorization reference, decision timestamp, effective-decision pointer, and aggregate version are server/application-owned. Actor identity and authorization are taken from authenticated command/security context, never caller-supplied role text. The authorization reference must resolve to the exact decision action, case/resource, actor/service, scope, policy/version, timestamp, and result; missing, stale, revoked, or unverifiable references fail closed. The append, effective-pointer update, case projection, and any ArticleEventLink reconciliation form one atomic local write set. A stale predecessor/version or competing successor returns CONFLICT.

#### 10.11.4 ActivateArticleEventLink and DeactivateArticleEventLink

**ActivateArticleEventLink**

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `case_id` | `ID<EventMatchCase>` | Required | Exact case whose effective decision is being applied. |
| `event_match_decision_id` | `ID<EventMatchDecision>` | Required | Must be the current effective MATCH decision for the same case. |
| `expected_case_version` | `Version` | Required | Compare-and-swap guard for the case and decision/link write set. |
| `relationship_type` | `string/enum` | Required | Must use an allowed ArticleEventLink relationship type; final enum governance remains open. |
| `association_confidence` | `number/null` | Explicit null or calibrated value; persistence nullability must be reconciled with Document 03 | Never copy candidate similarity into this field; a non-null value requires documented calibration semantics. |
| `association_method` | `string/enum` | Required | Derived from the effective decision and matching policy; callers must not override it. Allowed values remain policy-governed. |

ArticleRevision ID, Event ID, matching-policy version, link ID, associated_at, and active state are derived from the exact case, selected candidate, and effective decision or assigned by the application. They must not be independently supplied in a way that can contradict those references.

**DeactivateArticleEventLink**

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `case_id` | `ID<EventMatchCase>` | Required | Exact case owning the active link. |
| `link_id` | `ID<ArticleEventLink>` | Required | Must identify the active link for this case. |
| `successor_decision_id` | `ID<EventMatchDecision>` | Required | Must be the authorized successor decision in the same case and supersede the link's authorizing decision. |
| `expected_case_version` | `Version` | Required | Compare-and-swap guard for the atomic decision/link update. |

The application assigns deactivated_at. The prior link is preserved; the command cannot delete or repoint it. Both operations require the application authorization boundary and must commit with the effective-decision pointer update in one UnitOfWork.

#### 10.11.5 AppendEvidence

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `origin_type` | `string/enum` | Required | Determines which origin reference is required; the complete vocabulary remains open. |
| `source_id` | `ID<Source>/null` | Conditional | Required when origin_type identifies a configured Source. |
| `article_id` | `ID<Article>/null` | Conditional | Optional current-article navigation reference; must agree with article_revision_id when both are present. |
| `article_revision_id` | `ID<ArticleRevision>/null` | Conditional | Required for article-revision-origin evidence. |
| `source_document_reference` | `reference/null` | Conditional | Required for a non-article source document when no ArticleRevision identifies the origin. |
| `evidence_text` | `string` | Required by the current entity model | Must contain only the exact quotation/extract/derived text permitted for this operation; metadata-only rights do not authorize text storage. |
| `evidence_type` | `string/enum` | Required | Uses the documented illustrative types; final exhaustive enum remains open. |
| `observed_at` | `Instant` | Required | Time the evidence was observed or obtained; source-event time must not be substituted without provenance. |
| `content_location` | `EvidenceLocation/null` | Optional | Exact page/section/paragraph/offset/locator when available; never fabricate a location. |
| `language` | `string/null` | Optional | Language of the evidence text, if known. |
| `content_fingerprint` | `Fingerprint/null` | Optional | Fingerprint of the exact permitted representation; null when not available. |
| `rights_assessment_references` | `List<ID<RightsAssessment>>` | Conditional | Required whenever source-derived evidence storage or use is governed by rights assessment; scope must cover the exact evidence operation. |

Evidence ID and created_at are server-owned. An origin must be resolvable or explicitly recorded as unavailable under a separately approved representation. Because the current Evidence entity requires evidence_text, this command cannot be used for metadata-only evidence when text storage is not authorized; a separate metadata-only evidence representation remains unresolved. Evidence creation does not itself verify a claim or establish independent corroboration.

#### 10.11.6 AppendAnalysis

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `event_id` | `ID<Event>` | Required for event-scoped analysis | Must resolve to the exact Event version used by the analysis input manifest. |
| `analysis_type` | `AnalysisType` | Required | Importance, economic relevance, and economic impact are separate types and schemas. |
| `version` | `Version` | Server-assigned | Allocated under the event/type uniqueness rule; callers cannot overwrite an existing result. |
| `content` | `string/object` | Required | Human-readable or structured analysis representation; representation must be identified by schema/version. |
| `structured_output` | `object` | Required | Must validate against the exact result-schema version for analysis_type. |
| `confidence` | `number/null` | Nullable | Semantics must be defined by the analysis methodology; not forecast probability unless separately calibrated. |
| `status` | `string/enum` | Server/workflow-owned | Must follow the applicable processing policy; caller cannot mark an unvalidated result completed. |
| `model_provider` | `string/null` | Conditional | Required when a model provider was used; otherwise null. |
| `model_id` | `string/null` | Conditional | Required when a model was used; provider/model must be permitted by the applicable authorization decision. |
| `prompt_version` | `Version/null` | Conditional | Required when a prompt was used; otherwise null. |
| `schema_version` | `Version` | Required | Exact structured-output schema version. |
| `analysis_policy_version` | `Version` | Required | Exact methodology/policy version, distinct from model and prompt versions. |
| `input_fingerprint` | `Fingerprint` | Required | Covers exact immutable inputs, evidence set, and relevant processing versions. |
| `evidence_references` | `List<ID<Evidence>>` | Required | Exact evidence set considered; an empty set must be explicit and cannot be represented as successful evidential support. |
| `input_references` | `List<typed AnalysisInput references>` | Required | Typed references and versions for every non-evidence input consumed. |

Analysis ID, created_at, completed_at, and the next version are server-owned. Provider/model/prompt fields are provenance, not authorization; model-assisted processing remains disabled unless the exact provider, purpose, data category, region, privacy decision, and source-rights scope are authorized. A successful result is immutable; corrections or re-analysis create a successor record.

#### 10.11.7 AppendReportVersion

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `event_id` | `ID<Event>/null` | Conditional | Required for an event-specific report; null only when report_scope explicitly describes a non-event report. |
| `report_type` | `string/enum` | Required | Uses the documented report types; final exhaustive vocabulary remains open. |
| `report_scope` | `string/typed scope` | Required | Must identify the exact subject/scope; polymorphic scope representation remains to be standardized. |
| `title` | `string` | Required | Report title for this immutable version. |
| `content` | `string/object` | Required | Explicit content representation; source-derived content must comply with rights and distribution constraints. |
| `content_format` | `string/enum` | Required | Declares the representation; allowed formats and limits remain open. |
| `language` | `string` | Required | Language of this report version. |
| `template_version` | `Version` | Required | Exact template or generation-layout version. |
| `input_fingerprint` | `Fingerprint` | Required | Deterministic fingerprint of the exact generation inputs and versions. |
| `generation_provenance` | `object` | Required | Must identify the generation workflow/version and applicable model/prompt/schema provenance; schema remains to be closed. |
| `article_revision_references` | `List<ID<ArticleRevision>>` | Required | Exact article revisions used; never resolve through a mutable current Article pointer at read time. |
| `event_references` | `List<ID<Event>>` | Required | Exact Event references used, consistent with report_scope. |
| `analysis_references` | `List<ID<Analysis>>` | Required | Exact immutable analyses used. |
| `evidence_references` | `List<ID<Evidence>>` | Required | Exact evidence references supporting the report. |
| `rights_assessment_references` | `List<ID<RightsAssessment>>` | Conditional | Complete applicable set for source-derived content and any operation-specific use. |

Report ID, version, generation_status, generated_at, created_at, and supersedes_report_id are server-owned. Report content and all provenance links must commit atomically. Report generation does not create a PublicationDecision, authorize recipient distribution, or execute publication/delivery.

#### 10.11.8 Shared query and pagination contract

Every collection query returns a bounded page with stable ordering and a deterministic tie-breaker. The logical page request contains:

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| `limit` | `integer` | Required or defaulted by service | Positive and bounded; default and maximum values are operational configuration, not invented here. |
| `cursor` | `opaque string/null` | Optional | Must be bound to the query/filter/sort context; exact encoding and consistency semantics remain open. |
| `sort` | `typed sort specification` | Service-defined | Only explicitly supported sort keys; stable tie-breaker is mandatory. |
| `filters` | `typed query-specific fields` | Optional | Unknown filters are rejected rather than ignored. |

Query-specific fields established by the current contracts:

- `SourceCollectionQuery`: optional source type, language, geographic scope, and status filters; bounded limit; optional cursor.
- `EventCandidateQuery`: candidate retrieval must be deterministic, bounded, and stably ordered. Filter fields, eligibility criteria, and tie-breakers remain unresolved.
- `CandidateListQuery`: case-scoped results, stable ordering, bounded limit, optional cursor. Sort keys and filters remain unresolved.
- `AnalysisListQuery`: exact event and analysis_type scope from the repository signature; any additional filters and sort keys remain unresolved.
- `EvidenceListQuery`: exact subject scope and access-controlled evidence references; filter and sort vocabulary remains unresolved.

A cursor from one query/filter/sort context must not be reusable against another. Revoked access must be re-evaluated on each page; a previously issued cursor does not preserve authorization.

#### 10.11.9 Remaining field-level blockers after this tranche

This tranche does not claim that Gate A is complete. The following remain unresolved and must be closed before their corresponding operations are implemented or enabled:

- `UpdateSourceConfiguration`: writable configuration fields, source-type enum, URL-change validation, configuration versioning, and audit payload.
- `SourceArticleIdentity`: exact canonical identifier grammar and collision/redirect rules.
- Article projection creation/update DTO: explicit ownership and field mapping between Article and ArticleRevision, including metadata-only content availability.
- `EventCandidateQuery`, `CandidateListQuery`, `AnalysisListQuery`, and `EvidenceListQuery`: complete filters, sort vocabulary, cursor consistency, and default/maximum page size.
- Evidence origin-type mapping and the complete EvidenceType vocabulary.
- Analysis structured-output schemas for each enabled analysis_type; the generic Analysis record is not a substitute for those schemas.
- Report scope/type/content-format vocabularies, generation_provenance schema, and exact report-family/version allocation rules.
- Exact string lengths, numeric precision/ranges, timestamp precision, canonical serialization, and identifier encodings across all DTOs.
- Persistence-specific attempt/history/lease/idempotency records listed in §10.10.4.

No unresolved item above may be filled with an arbitrary default. A capability remains blocked until its own contract and governing ADR/authorization gates are satisfied.


### 10.12 Source registry and collection query contracts (tranche v1.4)

This tranche closes the source-configuration and source-identity payload catalogue to the extent supported by Documents 02, 03, 08, and the existing repository signatures. It does not authorize source discovery or collection. Source operations remain subject to operation-specific content-rights decisions and the applicable security controls.

#### 10.12.1 UpdateSourceConfiguration

The command is scoped to one existing Source and participates in optimistic concurrency through the repository method's expected_version. The command is a change set, not permission to replace the Source identity.

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| source_id | ID<Source> | Required | Must identify an existing Source; identity is immutable. |
| changes.name | string | Optional change | If supplied, must be non-empty after normalization; exact length and normalization remain open. |
| changes.source_type | string/enum | Optional change | Must select a supported source adapter type. RSS, API, web, and official dataset are examples, not a closed enum. |
| changes.base_url | URL | Optional change | Must pass URL validation and the Document 08 SSRF/redirect policy; DNS and redirect destinations require revalidation at use time. |
| changes.language | string/null | Optional change | Null clears the declared primary language; language-tag format remains to be selected. |
| changes.country_code | string/null | Optional change | Null clears the declared country; country-code format remains to be selected. |
| changes.ownership_group | string/null | Optional change | Null means unknown/unrecorded, not proof of independent ownership. |
| changes.syndication_group | string/null | Optional change | Null means unknown/unrecorded; do not infer a group from domain similarity alone. |
| changes.collection_config | object | Optional change | Non-secret, source-type-specific configuration only; schema must be validated by the selected adapter. Credentials and secret values are prohibited. |
| changes.is_active | boolean | Optional change | Enables/disables collection eligibility only; it does not grant content-access or retention rights. |
| expected_version | Version | Required | Compare-and-swap guard; stale updates return CONFLICT. |

The command must contain at least one actual change. Omitted fields mean unchanged; explicit null is accepted only for fields declared nullable. The exact serialized patch representation and distinction between omitted and explicit null must be fixed before implementation. The application/server owns Source ID, created_at, updated_at, resulting version, and audit provenance.

**Excluded from this generic command:** reliability_profile and reliability_profile_version. Source reliability is an assessed attribute with its own evidence and version semantics; it must not be silently overwritten as ordinary collection configuration. A dedicated reliability-profile update/evaluation contract remains to be specified.

Changing is_active does not rewrite collection history or rights assessments. Changing base_url or source_type must not silently transfer existing rights decisions to the new endpoint or adapter. Re-evaluate applicable access permissions before the next source operation. No credential, token, cookie, or secret may be included in collection_config, command errors, or ordinary logs.

#### 10.12.2 SourceCollectionQuery

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| source_type | string/enum or list | Optional filter | Only supported source types; exact scalar/list semantics remain open. |
| language | string or list | Optional filter | Matches declared source language; unknown language is not treated as a match. |
| geographic_scope | string/typed scope | Optional filter | Scope vocabulary and whether it maps to country_code or a broader coverage model remain open. |
| status | string/enum | Optional filter | Must map to an explicitly defined source lifecycle/collection state; it must not be silently interpreted as a rights decision. |
| limit | integer | Required or service-defaulted | Positive and bounded; default and maximum are deployment settings not specified here. |
| cursor | opaque string/null | Optional | Bound to the exact filter and sort context; encoding and consistency model remain open. |

The query returns only collection-enabled Sources for the list_collection_enabled operation, uses stable ordering with a deterministic tie-breaker, and never returns secret values. A cursor cannot be reused with different filters or sort order. Authorization to view Source configuration is checked independently of collection eligibility. Access to a Source record does not authorize any NewsCollector operation.

#### 10.12.3 SourceArticleIdentity

| Field | Type | Requiredness | Validation / ownership |
|---|---|---|---|
| canonical_source_identifier | string | Required | Stable identity within one Source, produced by deterministic, versioned source-specific normalization. |
| canonical_url | URL/null | Optional | Secondary lookup signal only; not globally unique and not a substitute for source-scoped identity. |
| normalization_version | Version | Required | Identifies the exact identity-normalization rules used. |

The enclosing repository call supplies source_id; the identity must never be compared across different Sources as though globally unique. The original article URL and source-provided external_id remain separately preserved on Article. The algorithm for selecting the canonical source identifier, precedence between external_id and other source-specific identifiers, redirect handling, URL canonicalization, collision resolution, and migration between normalization versions remain explicit open decisions. A collision returns CONFLICT; it never silently merges Articles.

#### 10.12.4 Article projection ownership and revision boundary

The Article record is a current projection, not a second independently editable copy of revision content.

| Article field group | Contract ownership |
|---|---|
| id, source_id, source-scoped identity | Stable identity; assigned/validated by the application and never silently changed by a revision update. |
| external_id, url, canonical_url | Source identity and URL references; preserve original and canonical forms separately. |
| title, content, summary, language, content_hash | Current projection derived from the latest valid ArticleRevision; content remains subject to exact rights and retention permissions. |
| current_revision_id | Server-owned pointer updated atomically with ArticleRevision append/reuse. |
| collected_at, last_seen_at | Server-owned observation projections; first successful collection and latest observation are distinct. |
| content_availability | Explicit state; the documented examples are available, partial, metadata-only, and unavailable. Missing content is never represented as an empty successful article. |
| rights_status | Summary projection only; never a substitute for operation-specific RightsAssessment records. |
| author, published_at, metadata | Present on Article in Document 03, but not all are represented on ArticleRevision. Their historical snapshot/update semantics remain unresolved; do not claim they are revision-stable until reconciled. |
| created_at, updated_at | Server-owned timestamps. |

ArticleRevision creation/reuse and Article projection update remain one UnitOfWork. A repeated unchanged normalized revision must not create a new revision; the same hash under a different normalization version is not presumed equivalent. The projection may expose only content permitted for the current operation and retention state. A later rights revocation or content restriction must not be bypassed by reading the Article projection or an old cache.

#### 10.12.5 Remaining source-contract blockers

The following remain open and block the corresponding implementation detail:

- Exact patch wire representation, omitted-versus-null serialization, and field-level string/URL bounds for UpdateSourceConfiguration.
- Supported source_type vocabulary and source-adapter configuration schemas.
- Dedicated Source reliability-profile update/evaluation contract, evidence requirements, and version/supersession rules.
- Geographic-scope vocabulary and its relationship to Source.country_code and source coverage.
- SourceArticleIdentity canonicalization algorithm, external_id precedence, redirect handling, collision remediation, and normalization-version migration.
- Historical snapshot semantics for Article.author, Article.published_at, and source metadata that are currently present on Article but absent from ArticleRevision.
- Cursor encoding, default/max page sizes, stable sort keys, and page consistency under concurrent source configuration changes.
- Secret-reference management, if source adapters require credentials; this contract intentionally prohibits secret values and does not select a secret manager.

These gaps must remain explicit. They must not be filled by silently choosing a provider, URL policy, identity algorithm, page-size limit, or credential mechanism.

## 11. Related documents

- Document 02 — Component Architecture and Interface Contracts.
- Document 03 — Data Model and Storage Design.
- Document 04 — Implementation Plan and Development Roadmap.
- Document 05 — Architecture Decision Records Governance.
- Document 08 — Security Architecture and Threat Model.
- Document 09 — API and Integration Contracts.
- Document 12 — Testing and Evaluation Strategy.
- Document 13 — Deployment, Operations, and Observability.
- Document 14 — Data Protection and Privacy Specification.
- GENI-ADR-004, 005, 006, 011, 013, 014, 016, 017, 019 and 020.
- GENI-FOUNDATION-017 — Executable Foundation and Domain Lifecycle Contracts.

---

**Document ID:** GENI-IMPL-015  
**Version:** 2.4  
**Status:** Proposed — Pending Project Owner Approval  
**Last Updated:** 2026-11-24

**Revision Note (v2.4):** Added source configuration, source collection query, source-scoped article identity, and Article projection ownership contracts. Distinguished assessed reliability metadata from routine source configuration and recorded unresolved identity, pagination, secret-reference, and ArticleRevision snapshot boundaries. This does not authorize source collection or complete Gate A.

**End of Document**
