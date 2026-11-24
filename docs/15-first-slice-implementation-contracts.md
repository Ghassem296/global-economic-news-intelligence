# GENI-IMPL-015 — First-Slice Implementation Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-IMPL-015  
**Version:** 2.0  
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

**Resolved provenance contract:** Document 03 §11.6 and this DTO now use the same required `actor_type`, `actor_reference`, and `authorization_reference` fields. Values originate from authenticated command/security context; repositories persist validated references and must not infer authorization from caller-supplied role strings. The security/audit layer must be able to resolve the authorization reference to actor, action, resource, scope, policy/version, timestamp and result. A missing, invalid, stale or unverifiable reference blocks the append. **Remaining implementation blocker:** the exact effective-decision/supersession query rule and concurrent-successor algorithm must be specified deterministically; timestamps or storage order must not be used as an implicit tie-breaker.

### 10.6 CreateProcessingRun

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `id` | `ID<ProcessingRun>` | Required or server-assigned | Stable logical run identity; assignment ownership must be fixed by implementation contract. | Document 03 §13.1 |
| `run_type` | `string/enum` | Required | Must identify the workflow kind; vocabulary is not closed in Document 03. | Document 03 §13.1 |
| `target_type` | `string/enum` | Required | Must pair with target_id and resolve to a supported target family. | Document 03 §13.1 |
| `target_id` | `ID<target>` | Required | Polymorphic reference; application validates existence and target_type agreement. | Document 03 §13.1 |
| `idempotency_key` | `string` | Required | Unique within canonical operation/target scope; exact format/length TBD. | Documents 03 §13.1, §13.2.2 |
| `input_fingerprint` | `Fingerprint` | Required | Same key + same fingerprint reuses logical operation; changed fingerprint conflicts. | Documents 03 §§13.1, 13.2.2 |

The initial status, started_at behavior, heartbeat/lease initialization, retry schedule, and whether the run ID is caller- or server-assigned are not fully specified. These must be decided before implementation; do not accept caller-supplied RUNNING/COMPLETED states without an explicit lifecycle contract.

### 10.7 TransitionProcessingRun

| Field | Type | Requiredness | Validation / invariant | Authority |
|---|---|---|---|---|
| `run_id` | `ID<ProcessingRun>` | Required | Exact durable run. | Document 03 §13.1 |
| `expected_version` | `Version` | Required | Compare-and-swap against current aggregate version. | Document 15 §§4.13, 7 |
| `new_status` | `ProcessingRunStatus` | Required | Must be one of the declared statuses; transition graph is not yet defined. | Document 03 §13.1 |
| `actor/worker_reference` | `ActorReference` | Required | Authenticated service/worker identity; concrete representation TBD. | Documents 15 §3.2, 03 §13.2.1 |
| `fencing_token` | `integer` | Conditional | Required for every worker state-changing write when durable leases are enabled; must equal current token. | Document 03 §13.2.1 |
| `occurred_at` | `Instant` | Required | Server-trusted transition time; clock authority/precision TBD. | Document 15 §4.13 |
| `reason/error_category` | `Optional<string/enum>` | Conditional | Required when transition represents failure/cancellation or other reasoned outcome; exact categories TBD. | Document 15 §4.13 |

ProcessingRun statuses declared by Document 03 are PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, PARTIALLY_COMPLETED. No permitted transition table, terminal-state rules, retry/reopen rules, or exact relationship between ProcessingRun and ProcessingStep statuses is defined. Therefore the DTO is not implementation-ready: the transition graph is an explicit blocker, not a license to permit every pair of statuses.

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
- GENI-ADR-004, 005, 006, 011, 013, 014, 016, 017, 019 and 020.\n- GENI-FOUNDATION-017 — Executable Foundation and Domain Lifecycle Contracts.

---

**Document ID:** GENI-IMPL-015  
**Version:** 2.0  
**Status:** Proposed — Pending Project Owner Approval  
**Last Updated:** 2026-11-24

**Revision Note (v2.0):** Replaced the unresolved lifecycle-question inventory with the normative lifecycle contracts in GENI-FOUNDATION-017. Added explicit remaining gates for field-level DTO schemas, persistence proofs, authorization, and supporting attempt/history records. The state-machine rules are executable and unit-tested; no ADR approval or external processing authorization is implied.

**End of Document**
