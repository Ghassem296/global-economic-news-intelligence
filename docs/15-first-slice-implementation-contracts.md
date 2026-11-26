# GENI-IMPL-015 — First-Slice Implementation Contracts

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-IMPL-015  
**Version:** 3.8  
**Status:** Proposed — Pending Project Owner Approval  
**Owner:** Project Owner  
**Last Updated:** 2026-11-26

---

## 1. Purpose

This document converts the first-slice repository inventory in Document 02, Section 6.1, and the contract-readiness requirements in GENI-API-009 into a reviewable, method-level baseline.

It is a proposed implementation specification, not an ADR and not an approval of any technology, policy, provider, source license, or business rule. It does not authorize production processing. The Project Owner must approve this contract baseline and all applicable ADRs before dependent implementation begins.

The notation is language- and database-neutral. Identifiers are opaque domain identifiers; concrete representations (UUID, integer, string, etc.) are selected by the implementation only after the applicable technology decision. No SQL, ORM, transport framework, database engine, queue, or public API is selected here.

## 2. Scope and explicit exclusions

The following is the repository-contract inventory for the first slice and adjacent gated capabilities; listing a repository here does not enable its capability. The currently scoped deterministic fixture slice uses SourceRepository for fixture reads, ArticleRepository, ArticleRevisionRepository, DuplicateCandidateRepository, DuplicateDecisionRepository, EventRepository for pre-seeded fixtures only, EventMatchCaseRepository, EventMatchCandidateRepository, EventMatchDecisionRepository, ArticleEventLinkRepository, EvidenceRepository, AnalysisRepository, ReportRepository, and ProcessingRunRepository where run tracking is required.

The following contracts are retained for later gated capabilities and are dormant in the first executable slice: PublicationDecisionRepository, ReviewRepository, and ReviewContextLinkRepository. In particular, the first slice does not create or persist an authoritative PublicationDecision, evaluate publication eligibility, create PublicationRecord/PublicationAttempt, or dispatch delivery. Review repositories may be contract-tested, but no material ReviewService action is enabled.

The complete repository-contract inventory is:

- SourceRepository
- ArticleRepository
- ArticleRevisionRepository
- DuplicateCandidateRepository
- DuplicateDecisionRepository
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

The contracts below define the minimum operations and invariants for those repositories. The first-slice aggregate repositories also own the related link records defined in Documents 02/03: EvidenceRepository owns EvidenceLocation writes; AnalysisRepository owns AnalysisInput and AnalysisEvidenceLink writes; and ReportRepository owns ReportEventLink, ReportEvidenceLink, ReportArticleLink and ReportAnalysisLink writes. These child records must be persisted and queried through the parent aggregate contract and the same UnitOfWork; they are not independent application-level transaction owners. Infrastructure may use private child adapters only when the aggregate repository preserves the atomic boundary. Separate repositories for publication operations/attempts, rights assessments, content access, collection checkpoints, processing steps, idempotency records and execution leases must be specified before their respective capabilities are implemented. Review persistence is included in the target first-slice repository baseline because `REPORT_VERSION` is part of the target review scope; however, inclusion does not enable review execution. ReviewService material actions remain disabled until the review DTO schemas, lifecycle/projection rules, authorization policy, and GENI-ADR-014 approval pass Gate A and the corresponding integration tests pass Gate C.

The first executable fixture slice additionally excludes:
- source collection, source-configuration updates, and collection checkpoints; SourceRepository is read-only against synthetic or otherwise authorized fixtures;
- production SourceArticleIdentity canonicalization; fixture identity is explicitly test-scoped and does not establish a production identity algorithm;
- authoritative PublicationDecision creation and publication-eligibility evaluation until GENI-ADR-004 and dependent contracts are accepted;
- material review actions until GENI-ADR-014 and all review contracts/authorization gates are accepted;
- provider-backed LLM execution and external provider egress until GENI-ADR-006/017/020 and exact rights/privacy gates are accepted;
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

Every state-changing application command is protected by default and carries:
- `command_id`;
- `schema_version`;
- authenticated `actor` or service identity;
- required immutable `authorization_reference` from trusted security/application context;
- `correlation_id` and optional `causation_id`;
- `idempotency_key` with a documented operation scope;
- `expected_aggregate_version` when updating an existing aggregate;
- deadline/cancellation context where execution can outlive the caller.

No state-changing command is exempt merely because it is internal, automated, invoked by an administrator, or initiated by an LLM/tool. The authorization reference binds the exact actor/service, action, resource, scope, applicable policy/version, evaluation time and outcome; it is not a role string or caller assertion. Rights assessments and privacy-processing decisions are separate domain gates and their references must also be carried where applicable; a general execution authorization cannot substitute for them. A repository method receives only the metadata needed for its persistence responsibility. Authorization decisions are made by the application/domain boundary and their immutable references are persisted with the resulting state change; a repository must not infer authorization from caller-supplied role strings.

### 3.3 Common failures

The first-slice repository and domain contracts use the applicable subset of the error vocabulary in GENI-API-009:
`VALIDATION_ERROR`, `AUTHENTICATION_REQUIRED`, `AUTHORIZATION_DENIED`, `NOT_FOUND`, `CONFLICT`, `DEPENDENCY_UNAVAILABLE`, `TIMEOUT_OUTCOME_UNKNOWN`, `RIGHTS_NOT_ALLOWED`, and `INTERNAL_ERROR`.

Provider/transport boundaries may additionally return `RATE_LIMITED` and `BUDGET_EXCEEDED` as defined by GENI-API-009. These are valid boundary-level outcomes, but they are not repository-specific persistence failures and must retain their API-level retry/budget semantics.

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
| `find_current_by_revision_fingerprint` | `find_current_by_revision_fingerprint(article_id: ID<Article>, revision_fingerprint: Fingerprint, schema_version: Version) -> Optional<ArticleRevision>` | Matches only the current revision of the same Article. It must not search all historical revisions or impose global uniqueness on fingerprints. |
| `append_revision` | `append_revision(revision: ArticleRevision, expected_article_version: Optional<Version>, uow: UnitOfWork) -> ArticleRevision` | Appends a new immutable revision and updates the Article projection in the same UnitOfWork through ArticleRevisionService. Enforces unique `(article_id, revision_number)`; repeated identical content returns/reuses the existing logical revision rather than creating a duplicate. |

The write command carries the exact permitted content reference (only for persistently retained content), content hash and content-normalization version (only for `available`/`partial` content), observed time, language, change reason, and applicable immutable rights-assessment reference(s). A content hash is not permission to retain the underlying content. Unknown, expired, revoked, unverifiable, or insufficient rights block the restricted operation.

#### ArticleRevision identity and idempotency contract

Two different digests serve different purposes and must never be conflated:

- `content_hash`: SHA-256 of the exact UTF-8 bytes of the normalized content representation that is persistently retained. It is present only for `available` and `partial` revisions whose persistent-storage permission is current and verified. It is null for `metadata-only` and `unavailable`. The digest is lowercase 64-character hexadecimal; the associated `content_normalization_version` is mandatory and identifies the exact transformation used before hashing.
- `revision_fingerprint`: SHA-256 of a versioned semantic revision manifest. It supports idempotency when content is not retained and is computed for every revision. It is not a content digest, cross-article identifier, permission, or authorization token. Persist both the digest and `revision_fingerprint_schema_version` so the comparison is reproducible.

Fingerprint v1 is SHA-256 over UTF-8 RFC 8785 JSON Canonicalization Scheme (JCS) serialization of an object containing exactly:
1. `schema_version` = `article-revision-fingerprint-v1`;
2. `source_id`;
3. `canonical_source_identifier` and `source_identity_normalization_version`;
4. `normalized_title`, `summary`, `author`, `language`, and `published_at`;
5. `content_availability`;
6. `content_hash` and `content_normalization_version` (both null for metadata-only/unavailable revisions);
7. `metadata`, containing only source/article metadata permitted for retention and normalized by the source adapter.

For this fingerprint schema, `published_at` is UTC RFC 3339 with exactly millisecond precision and a trailing `Z`. Metadata is restricted to valid Unicode strings, booleans, null, safe integers in the IEEE-754 interoperable range, arrays, and objects; floating-point values are rejected. Object keys follow JCS UTF-16 code-unit ordering. Unicode strings are preserved exactly and are not normalized during canonicalization. The source adapter must exclude volatile observation/transport fields from `metadata`; such operational data belongs in collection records, not the semantic revision manifest.

The fingerprint deliberately excludes `content_reference` (storage relocation is not a content change), `original_url` and `external_id` (source-scoped canonical identity is authoritative), `observed_at`, `change_reason`, and rights-assessment references (observation, audit reason, and rights decisions do not change the semantic article revision). The canonical source identity and its normalization version remain included.

Idempotency compares the incoming fingerprint only with the Article's current revision. A match reuses the current revision and creates no new revision. A non-match appends a new revision under the Article's expected version. Do not impose a unique constraint across all historical fingerprints: if an article changes from A to B and later returns to A, the return is a new chronological revision even though its fingerprint equals the earlier A revision. The unique revision constraint remains `(article_id, revision_number)`.

The domain contract implements this deterministic fingerprint for the restricted JCS-safe value set. The application/repository layer must persist and verify the computed value; the storage adapter must not invent a second serialization or hashing scheme. The metadata-only fingerprint contains only permitted metadata; it does not justify retaining otherwise restricted content or derivatives.

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
| `append_evidence` | `append_evidence(evidence: Evidence, uow: UnitOfWork) -> Evidence` | Persists evidence identity, origin, source attribution, verification state and all permitted EvidenceLocation records atomically in the same UnitOfWork. Evidence does not by itself prove a claim. Source-derived content is subject to operation-specific rights and retention controls. |
| `list_for_subject` | `list_for_subject(subject: EvidenceSubject, query: EvidenceListQuery) -> Page<Evidence>` | Returns bounded, stable, access-controlled evidence references for an ArticleRevision, Event, Claim or Analysis as supported by the model. |

### 4.10 AnalysisRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(analysis_id: ID<Analysis>) -> Optional<Analysis>` | Returns immutable analysis output and version metadata. |
| `append_analysis` | `append_analysis(command: AppendAnalysis, uow: UnitOfWork) -> Analysis` | Persists one versioned Analysis together with its exact AnalysisInput and AnalysisEvidenceLink records in the same UnitOfWork, plus result-schema version, methodology version, model/prompt provenance where used, and explicit unknown/uncertainty semantics. |
| `list_for_event` | `list_for_event(event_id: ID<Event>, analysis_type: AnalysisType, query: AnalysisListQuery) -> Page<Analysis>` | Returns only the requested analysis type; importance, economic relevance and economic impact remain distinct types. |

The write command must reject missing required provenance and must not collapse unknown, not-established, zero, and false into one value.

### 4.11 ReportRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(report_id: ID<Report>) -> Optional<Report>` | Returns the exact immutable report version. |
| `get_latest_for_subject` | `get_latest_for_subject(subject: ReportSubject) -> Optional<Report>` | Returns the latest version for the requested subject without mutating historical versions. |
| `append_report_version` | `append_report_version(command: AppendReportVersion, uow: UnitOfWork) -> Report` | Appends an immutable report version with exact event/article-revision/analysis/evidence provenance. Report content, immutable content manifest, and all ReportEventLink, ReportEvidenceLink, ReportArticleLink and ReportAnalysisLink records commit atomically through ReportRepository. Generation alone does not publish or deliver the report. |

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

### 4.16 DuplicateCandidateRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(candidate_id: ID<DuplicateCandidate>) -> Optional<DuplicateCandidate>` | Returns one immutable pairwise candidate evaluation and its exact ArticleRevision references. |
| `find_by_identity` | `find_by_identity(article_revision_id_a: ID<ArticleRevision>, article_revision_id_b: ID<ArticleRevision>, matching_method: DuplicateMatchingMethod, matching_policy_version: Version, input_fingerprint: Fingerprint) -> Optional<DuplicateCandidate>` | Resolves the candidate using the approved canonical revision-pair ordering. Reverse-order input must resolve to the same logical pair. |
| `append_candidate` | `append_candidate(command: AppendDuplicateCandidate, uow: UnitOfWork) -> DuplicateCandidate` | Appends immutable candidate evidence with actor and authorization provenance. Enforces distinct revisions, Article/revision ownership, canonical pair ordering and idempotency for the same pair/method/policy/input fingerprint. A changed input or policy creates a new candidate evaluation. |

The repository does not decide whether the pair is duplicate, merge or delete Articles, or create an event association. Similarity scores remain nullable and are not probabilities unless separately calibrated.

### 4.17 DuplicateDecisionRepository

| Method | Signature | Contract |
|---|---|---|
| `get_by_id` | `get_by_id(decision_id: ID<DuplicateDecision>) -> Optional<DuplicateDecision>` | Returns one immutable decision and its supersession reference. |
| `get_effective_for_candidate` | `get_effective_for_candidate(candidate_id: ID<DuplicateCandidate>) -> Optional<DuplicateDecision>` | Resolves the unique terminal decision in the candidate's linear supersession chain. No decision means no effective outcome. |
| `append_decision` | `append_decision(command: AppendDuplicateDecision, expected_effective_decision_id: Optional<ID<DuplicateDecision>>, uow: UnitOfWork) -> DuplicateDecision` | Appends an immutable decision with authorization provenance only when the expected predecessor equals the current effective decision. The first decision requires no predecessor; a successor must reference the current effective decision for the same candidate. Enforces one initial decision and at most one direct successor per decision. Stale or competing writes return CONFLICT. |

The effective decision is the unique terminal node of the immutable supersession chain; it is not a mutable flag on a DuplicateDecision. An optional materialized lookup value is only a rebuildable projection and cannot replace the authoritative chain. A duplicate decision never deletes, merges, or rewrites either Article or ArticleRevision and never creates an ArticleEventLink.

## 5. Cross-repository transaction map

The following local write sets are indivisible. They must be implemented through one UnitOfWork or an equivalent proven consistency mechanism:

| Operation | Atomic local write set |
|---|---|
| Persist a material article revision | ArticleRevision insert + Article current-projection update + associated processing/idempotency state required by the operation |
| Append a duplicate candidate | Immutable DuplicateCandidate insert + scoped idempotency result; no Article or ArticleRevision is merged or deleted |
| Append a duplicate decision | Immutable DuplicateDecision insert + linear supersession constraint/idempotency result; effective outcome resolves from the unique terminal decision in the chain |
| Create an Event | Event insert + initial EventHistory + authorized creation/idempotency provenance |
| Record an event-match decision | EventMatchDecision append + EventMatchCase effective pointer + required ArticleEventLink activation/deactivation |
| Persist evidence-backed analysis | Analysis append + exact AnalysisInput and AnalysisEvidenceLink set, all owned by AnalysisRepository and committed atomically |
| Persist report version | Report version + immutable content manifest + all ReportEventLink, ReportArticleLink, ReportAnalysisLink and ReportEvidenceLink rows, committed atomically by ReportRepository |
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
| `EvaluateArticleDuplicate` | Two exact ArticleRevision IDs and owning Article IDs, approved duplicate method/policy version, exact comparison inputs and fingerprint, similarity signals where available | Immutable DuplicateCandidate ID; candidate evaluation only, never an authoritative duplicate decision |
| `ApplyDuplicateDecision` | DuplicateCandidate ID, one allowed outcome, rationale, decision method/policy version, actor/authorization context, expected effective predecessor and idempotency metadata | Immutable DuplicateDecision ID and effective outcome for that exact pair; no Article merge/deletion and no event decision |
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
- GENI-ADR-005 is formally Accepted only after the GENI-ADR-005-POC-001 protocol is executed with an approved workload profile, predeclared thresholds, all mandatory correctness/failure gates, reproducible raw evidence, and a reviewed engine recommendation. The protocol itself is not evidence of a passing PoC.
- Database engine, exact version, driver, migration tool, async strategy, transaction isolation/locking, connection lifecycle, deployment topology, and backup/restore procedure are recorded in the Accepted ADR and synchronized implementation baseline.
- GENI-ADR-016 is accepted before durable lease, fencing, idempotency and recovery behavior is treated as approved implementation policy.

### Gate C — Executable verification

Before a first-slice milestone is declared complete:
- Every repository contract has schema/type tests and contract tests.
- Atomic write sets have rollback and failure-injection tests.
- Optimistic concurrency has stale-write tests.
- Idempotency has same-fingerprint replay and different-fingerprint conflict tests.
- Event matching has case-scoped candidate/decision/link invariant tests.
- Review lifecycle tests are required only before a later ReviewService capability is enabled; they must cover task creation, exact typed subjects, append-only action ordering, idempotency, projection rebuild, authorization, concurrency, context-link access, and all approved transitions, and must not encode provisional transitions.
- The first slice creates no PublicationDecision and invokes no publication or delivery operation; tests must prove those boundaries remain disabled.
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

For the deterministic fixture slice, complete only the DTOs exercised by its enabled operations: fixture-backed Source/Article references and article/revision append commands; pairwise DuplicateCandidate evaluation and DuplicateDecision append; EventCandidateQuery (if candidate retrieval is performed), CreateEventMatchCase, event candidate evaluation, EventMatchDecision append, ArticleEventLink activation/deactivation; Evidence append; deterministic fixture Analysis append; Report version append; and ProcessingRun commands/queries if run tracking is included. Each enabled query must define stable ordering, bounded page size, and cursor consistency. The following are not first-slice DTO requirements and remain deferred: SourceCollectionQuery, UpdateSourceConfiguration, production SourceArticleIdentity canonicalization, PublicationDecision append, material ReviewService commands, and provider-specific request/usage DTOs. A test-scoped fixture identity or deterministic fixture payload must not be promoted to a production canonicalization, analysis methodology, or report-format decision.

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
- GENI-ADR-002 article-deduplication/event-matching separation and pairwise duplicate-decision semantics.
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
| `source_article_identity.normalization_version` | `Version` | Required | Exact version of the source-identity canonicalization rules used to produce the canonical identifier. It is distinct from content normalization. |
| `source_article_identity.canonical_url` | `string/null` | Optional | Secondary lookup signal only; it does not replace source-scoped identity. |
| `original_url` | `string` | Required | Must pass URL validation; preserve separately from canonical_url. |
| `external_id` | `string/null` | Optional | Source-provided identifier; uniqueness is source-scoped and applies only when meaningful. |
| `normalized_title` | `string` | Required | The title stored on the immutable revision and current Article projection. |
| `content_availability` | `string/enum` | Required | Exactly one of `available`, `partial`, `metadata-only`, or `unavailable`; describes this exact revision, not merely the source's general capability. |
| `content_reference` | `reference/null` | Conditional | Required for `available` or `partial`; must be null for `metadata-only` or `unavailable`. It may point only to the exact content representation permitted for the relevant operation. |
| `content_hash` | `Fingerprint/null` | Required for `available`/`partial`; null for `metadata-only`/`unavailable` | Lowercase 64-hex SHA-256 of the exact UTF-8 bytes of the persistently retained normalized representation. It does not grant retrieval, processing, or retention rights. |
| `content_normalization_version` | `Version` | Required when a content representation is normalized or hashed | Identifies the exact normalization rules used for the hash and any offsets; must not be fabricated when no content representation exists. |
| `revision_fingerprint` | `Fingerprint` | Server-computed, required | SHA-256 of the versioned semantic revision manifest; separate from `content_hash`. | 
| `revision_fingerprint_schema_version` | `Version` | Server-computed, required | Identifies the exact manifest and canonicalization rules; v1 is `article-revision-fingerprint-v1`. |
| `summary` | `string/null` | Optional | May contain only source material or derived text permitted by the applicable rights decision; included in the semantic revision fingerprint. |
| `author` | `string/null` | Optional | Source-reported author snapshot; included in the semantic revision fingerprint and retained only when permitted. |
| `language` | `string/null` | Optional | Declared or detected language; exact language-tag format remains a serialization decision. |
| `published_at` | `Instant/null` | Optional | Source publication time; unknown remains null. |
| `observed_at` | `Instant` | Required | Trusted observation time for this revision. |
| `change_reason` | `string/enum` | Required | Explains why this revision is appended; controlled vocabulary and free-text bounds remain open. |
| `rights_assessment_references` | `List<ID<RightsAssessment>>` | Conditional | Required for every source-derived content operation that is governed by a rights assessment; each reference must cover the exact operation and content scope. |
| `metadata` | `object` | Optional | Versioned, non-secret extension; must not duplicate authoritative typed fields. |

Server-owned values include Article ID when first created, ArticleRevision ID, revision number, current_revision_id, rights_status and content_availability projections, created/updated timestamps, and resulting aggregate version. The application must atomically append/reuse the immutable ArticleRevision and update the Article current projection. The Article content_availability projection must equal the current revision's state.

ArticleRevision idempotency is defined by the semantic `revision_fingerprint` and its schema version, not by `content_hash`. Compare the incoming fingerprint only with the current revision for the same Article. An equal fingerprint reuses the current revision; a different fingerprint appends a new revision. Do not enforce uniqueness across all historical fingerprints: a return from A to B and later back to A is a new chronological revision. The fingerprint manifest and exclusions are specified in §4.3 and are implemented by the pure domain payload contract.

The selected content-retention direction is source-aware and operation-specific: persist full or partial text only when the applicable persistent-storage permission is current and verified; otherwise retain only permitted metadata or mark the revision unavailable. A retrieval or analysis permission does not imply persistent storage, external LLM transmission, quotation, or republication permission. Missing, unknown, expired, revoked, or unverifiable rights fail closed for the affected operation.

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

Analysis ID, created_at, completed_at, and the next version are server-owned. Provider/model/prompt fields are provenance, not authorization. Every actual provider request must produce an LLMUsageRecord linked to the exact Analysis and/or ProcessingRun/ProcessingStep, with the applicable `privacy_authorization_decision_id`, `processing_purpose_id`, `data_category`, `processing_region`, `transfer_assessment_id`, `content_rights_decision_refs`, provider/model, prompt/schema versions, outcome and retry provenance required by Document 03 §13.5. The PrivacyAuthorizationDecision must independently ALLOW the exact purpose, operation, data category, provider/model and region; source-content rights must separately cover the exact payload and use. Missing, unknown, expired, revoked or mismatched references block egress. A successful result is immutable; corrections or re-analysis create a successor record.

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

The command must contain at least one actual change. Omitted fields mean unchanged; explicit null is accepted only for fields declared nullable. The exact serialized patch representation and distinction between omitted and explicit null must be fixed before implementation. The expected_version argument is supplied separately as required by the repository signature in §4.1; it is the compare-and-swap guard and is not duplicated inside the command payload. The application/server owns Source ID, created_at, updated_at, resulting version, and audit provenance.

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
| author, published_at, metadata | Historical snapshots on ArticleRevision; the Article projection derives these values from its current revision. Metadata contains only permitted, normalized semantic source fields; volatile collection/transport data belongs in separate collection records. |
| created_at, updated_at | Server-owned timestamps. |

ArticleRevision creation/reuse and Article projection update remain one UnitOfWork. A repeated unchanged normalized revision must not create a new revision; the same hash under a different normalization version is not presumed equivalent. The projection may expose only content permitted for the current operation and retention state. A later rights revocation or content restriction must not be bypassed by reading the Article projection or an old cache.

#### 10.12.5 Remaining source-contract blockers

The following remain open and block the corresponding implementation detail:

- Exact patch wire representation, omitted-versus-null serialization, and field-level string/URL bounds for UpdateSourceConfiguration.
- Supported source_type vocabulary and source-adapter configuration schemas.
- Dedicated Source reliability-profile update/evaluation contract, evidence requirements, and version/supersession rules.
- Geographic-scope vocabulary and its relationship to Source.country_code and source coverage.
- SourceArticleIdentity canonicalization algorithm, external_id precedence, redirect handling, collision remediation, and normalization-version migration.
- Source-specific metadata field allowlists and canonicalization profile; the core ArticleRevision author/summary/language/published_at snapshot fields and fingerprint inclusion are now defined.
- Cursor encoding, default/max page sizes, stable sort keys, and page consistency under concurrent source configuration changes.
- Secret-reference management, if source adapters require credentials; this contract intentionally prohibits secret values and does not select a secret manager.

These gaps must remain explicit. They must not be filled by silently choosing a provider, URL policy, identity algorithm, page-size limit, or credential mechanism.


### 10.13 Authorization crosswalk for first-slice operations (tranche v1.5)

This section maps the first-slice application commands and queries to the proposed permission identifiers in Document 08 §5.2. It is a contract crosswalk, not a grant of permissions, a completed role assignment, or acceptance of the governing ADRs. All state-changing commands require the common `authorization_reference` in §3.2. The operation-specific permissions below must be evaluated against the exact resource and scope. Rights and privacy decisions remain separate, additional gates.

| Application command/query | Minimum permission identifier(s) | Exact authorization binding | Additional independent gate / restriction |
|---|---|---|---|
| Read Source configuration / `SourceCollectionQuery` | `source.config.read` | Exact Source or bounded result set and requested fields | Never expose secrets; collection eligibility is not content-access authorization |
| `UpdateSourceConfiguration` | `source.config.update` | Exact Source, changed field set and expected version | Re-evaluate rights after source type or endpoint change; secret values prohibited |
| Source discovery / collection execution | `source.collect` | Exact Source, adapter, endpoint and collection purpose | Current source-specific access/collection rights; SSRF/egress controls; no blanket permission from `is_active` |
| `PersistArticleRevision` | `article.revision.append` and the applicable `source.collect` grant | Exact Source, source-scoped Article identity, revision fingerprint and content-availability state | Every retained/processed content field must be covered by the exact current rights/retention assessment; metadata-only permission cannot authorize content storage |
| `EvaluateArticleDuplicate` | `article.duplicate.evaluate` plus applicable article metadata/content read permission | Exact pair of ArticleRevision records, owning Articles, comparison method/policy version and input fingerprint | Current content-rights authorization for every content operation and derived candidate storage; candidate evaluation cannot decide, merge, or delete |
| `ApplyDuplicateDecision` | `article.duplicate.decide` | Exact DuplicateCandidate, outcome, effective predecessor and candidate scope | Approved duplicate-decision policy and immutable authorization reference; pairwise decisions are not transitive and cannot alter EventMatchDecision/ArticleEventLink |
| `ResolveEventDevelopment` | `event.match.case.create` and `event.match.evaluate` | Exact ArticleRevision, development scope, matching-policy version and candidate set | Candidate evaluation is not an authoritative decision and cannot create an Event or ArticleEventLink |
| `ApplyEventMatchDecision` | `event.match.decide` | Exact case, decision, predecessor, selected candidate and expected case version | Approved matching policy and immutable authorization reference; Event creation separately requires `event.create` and EventCreationPolicy |
| `RecordEvidence` | `evidence.append` | Exact evidence origin, subject, stored representation and content location | Rights/retention decision must cover the exact quotation, extract or derived text being stored |
| `PersistAnalysis` | `analysis.append`; plus `privacy.processing.authorize` for provider requests | Exact immutable input manifest, evidence set, analysis type and methodology version; exact purpose/category/provider/model/region for egress | Provider execution additionally requires an immutable ALLOW PrivacyAuthorizationDecision, applicable transfer assessment, source-content rights for the exact payload/use, and LLMUsageRecord provenance under Document 03 §13.5 |
| `CreateReportVersion` | `report.generate` | Exact report aggregate, input revisions, evidence/analysis references, template and fingerprint | Provenance and content-rights checks; report generation does not authorize publication or delivery |
| `DecidePublicationEligibility` | `publication.decide` | Exact immutable report version and publication scope | Approved publication policy, required review references and current rights/security context; decision is not a dispatch command |
| `CreateReviewTask` | `review.task.create` | Exact review family, typed subject, assignment and reviewer-visible context | Approved trigger/priority policy; authorize access to every linked context item |
| `AppendReviewAction` | `review.action` | Exact assigned ReviewRecord, action, actor and expected version | Approved transition graph, assignment and separation-of-duties rules; review action cannot bypass the authoritative domain command |
| `AttachReviewContext` | `review.context.attach` | Exact ReviewRecord and every typed context reference | Independently authorize access to each referenced object; no content copy or scope expansion |
| Start/transition a `ProcessingRun` | `processing.run.start` / `processing.run.transition` | Exact run, workflow, step, transition and aggregate version | Approved state machine, idempotency and transaction contract |
| Recover/resume a `ProcessingRun` | `processing.run.recover` | Exact run/step, lease owner, fencing generation and recovery reason | Explicit operational grant and append-only recovery audit; recovery cannot rewrite completed domain history |

The permission reference above is a minimum requirement, not an exhaustive authorization context. If a command performs multiple protected actions, each action must be authorized independently; authorization for the outer workflow does not implicitly authorize a nested Event creation, content read, provider request, publication, or delivery.

For read queries not listed individually, the application must authorize the requested resource and fields before returning data. A query cursor never carries or preserves authorization: every page re-evaluates the caller's current access. Sensitive read decisions are audited according to Document 08 §5.3 without logging restricted payloads.

The following remain deliberately outside this first-slice command crosswalk and must not be inferred from `publication.decide`: `distribution.authorize` and `delivery.dispatch`. They require the separate immutable DistributionAuthorizationDecision, complete RightsAssessment link set, exact content-scope manifest/fingerprint and immediate pre-dispatch revalidation specified in Document 02. A PublicationDecision, subscription, report-generation permission or general service identity is insufficient.

#### 10.13.1 Authorization denial and audit behavior

- Missing authentication returns `AUTHENTICATION_REQUIRED`; authenticated but ungranted, out-of-scope or policy-denied operations return `AUTHORIZATION_DENIED`.
- Missing, expired, revoked, stale, mismatched or unverifiable rights decisions return the rights-specific denial defined by GENI-API-009; they must not be converted into a generic successful metadata-only operation.
- A privacy authorization failure blocks provider egress even if execution permission and content rights are otherwise allowed.
- Denial and REQUIRES_REVIEW outcomes are auditable, but denied commands do not append domain records, advance aggregate versions, create links, or trigger external side effects.
- Re-evaluate authorization on retries, changed payloads, changed resource versions, changed provider/region, and immediately before irreversible external side effects.
- Authorization failures are not retried unchanged. A new grant or policy decision requires a new authorized command attempt and idempotency handling consistent with the original operation.

#### 10.13.2 Approval and implementation blockers

The crosswalk does not complete Gate A. The final role-to-permission assignments, grant administration, identity/session lifecycle, policy decision point, break-glass rules, separation-of-duties exceptions, and exact permission schema remain open in Document 08 §9. Review workflow remains blocked by GENI-ADR-014 and its unresolved state/assignment contracts. Source collection and content operations remain blocked by applicable rights/retention approvals and GENI-ADR-013. Provider-backed analysis remains blocked by GENI-ADR-006/017/020 and the exact rights/privacy decisions. No ADR is accepted by this revision.


### 10.14 Structured output contracts for the three core economic assessments (tranche v1.6)

This section defines a language-neutral logical field baseline for the three separate event assessments already required by Documents 02 and 03. It does not approve assessment methodology, scoring scales, calibration, or production execution. GENI-ADR-019 and the Project Owner approval gates remain applicable.

All three outputs are stored as distinct immutable `Analysis` records with separate `analysis_type`, `schema_version`, `analysis_policy_version`, input fingerprint, exact evidence/input references, and uncertainty representation. They must never be collapsed into one composite score or stored as interchangeable Event fields.

#### 10.14.1 ImportanceAssessmentOutput

Applies only to `IMPORTANCE_ASSESSMENT`.

| Field | Logical type | Requiredness | Contract |
|---|---|---|---|
| `dimensions_considered` | `List<ImportanceDimensionResult>` | Required; may be explicitly empty only when no dimension could be assessed | Records the dimensions actually considered. Dimension vocabulary and per-dimension scales remain methodology-governed. |
| `qualitative_rank` | `string/null` | Conditional | Required when the approved methodology produces a qualitative rank; value must belong to that versioned scale. |
| `numeric_score` | `number/null` | Conditional | Null unless the approved methodology defines a numeric scale, range, direction and interpretation. Never invent a default score. |
| `rationale` | `string` | Required | Explains the importance result and material factors; cannot merely repeat a rank. |
| `evidence_references` | `List<ID<Evidence>>` | Required | Exact supporting and, where applicable, contradicting evidence; empty means no evidence was available, not successful support. |
| `uncertainty` | `UncertaintyRepresentation` | Required | Must identify material uncertainty and limitations; exact schema and calibration remain governed by Document 03 §9.4 and GENI-ADR-008. |

Importance measures significance/attention priority. It must not encode economic relevance, effect magnitude, market direction, or forecast probability. The numeric score and qualitative rank are not both mandatory; the selected representation must be consistent with the exact methodology version.

#### 10.14.2 EconomicRelevanceAssessmentOutput

Applies only to `ECONOMIC_RELEVANCE_ASSESSMENT`.

| Field | Logical type | Requiredness | Contract |
|---|---|---|---|
| `relevance_classification` | `enum` | Required | Proposed values: `DIRECT`, `INDIRECT`, `CONTEXTUAL`, `NO_MATERIAL_LINK_ESTABLISHED`, `UNKNOWN`. Unknown must not be converted to no relevance. |
| `transmission_pathways` | `List<TransmissionPathway>` | Required; empty is valid only with an explicit no-pathway/unknown rationale | Identifies direct, indirect or contextual pathways and explains the economic connection. |
| `affected_entities` | `List<TypedEntityReference>` | Required; may be empty when unknown | Identifies supported countries, institutions, sectors, industries, commodities, markets or other affected entities. |
| `affected_geographies` | `List<GeographicReference>` | Required; may be empty when unknown | Records supported geographic scope; do not infer a geography from an unrelated entity label. |
| `rationale` | `string` | Required | Explains why the classification and pathways are supported or remain unknown. |
| `supporting_evidence_references` | `List<ID<Evidence>>` | Required | Exact evidence supporting the relevance assessment. |
| `uncertainty` | `UncertaintyRepresentation` | Required | Preserves missing information, competing interpretations and limitations. |

The classification is descriptive, not a numeric magnitude. The result must not estimate the size, direction or certainty of economic consequences and must not reuse an ImportanceAssessment result as a substitute.

#### 10.14.3 EconomicImpactAssessmentOutput

Applies only to `ECONOMIC_IMPACT_ASSESSMENT`.

| Field | Logical type | Requiredness | Contract |
|---|---|---|---|
| `channel_impacts` | `List<ChannelImpact>` | Required; empty only when no impact channel is established or assessable | One record per distinct transmission channel; never merge unlike channels into a single aggregate. |
| `channel` | `string/typed channel reference` | Required within each ChannelImpact | Uses a versioned channel vocabulary; final vocabulary remains methodology-governed. |
| `affected_entities_or_geographies` | `List<TypedEntityOrGeographyReference>` | Required within each ChannelImpact; may be empty only when unknown | Identifies the supported affected entity/geography for this channel. |
| `transmission_mechanism` | `string` | Required within each ChannelImpact | Describes how the event may or did produce the effect; causal attribution must not be implied without evidence. |
| `direction` | `enum` | Required within each ChannelImpact | `POSITIVE`, `NEGATIVE`, `MIXED`, `NEUTRAL`, or `UNCLEAR`; direction is not magnitude. |
| `magnitude_or_range` | `number/range/null` | Conditional | Only when defensible and supported; preserve units, basis and range semantics. Unsupported magnitude is null, never zero or fabricated precision. |
| `time_horizon` | `typed period/null` | Conditional | Required when the assessment can defensibly identify a horizon; exact period encoding remains open. |
| `duration` | `typed period/null` | Conditional | Distinct from time_horizon; null when unknown or not established. |
| `evidence_status` | `enum` | Required within each ChannelImpact | `OBSERVED_ECONOMIC_EFFECT`, `SOURCE_REPORTED_EFFECT`, `INFERRED_POTENTIAL_EFFECT`, or `UNKNOWN`. |
| `evidence_references` | `List<ID<Evidence>>` | Required within each ChannelImpact | Exact evidence supporting or qualifying this channel-level effect. |
| `uncertainty` | `UncertaintyRepresentation` | Required within each ChannelImpact | Captures uncertainty, limitations, counterevidence and missing data for this channel. |

A channel-level impact may describe realized or potential consequences. `OBSERVED_ECONOMIC_EFFECT` requires an identified economic/market observation; `SOURCE_REPORTED_EFFECT` is not independently verified merely because it is reported; `INFERRED_POTENTIAL_EFFECT` is an analytical inference; `UNKNOWN` means insufficient information. Market reaction is a separate assessment/evidence category and does not prove economic causality.

#### 10.14.4 Shared assessment invariants

- `IMPORTANCE_ASSESSMENT`, `ECONOMIC_RELEVANCE_ASSESSMENT`, and `ECONOMIC_IMPACT_ASSESSMENT` are separate immutable Analysis records and separate structured-output schemas.
- Each output is validated against its exact `schema_version`; methodology changes increment `analysis_policy_version` independently of schema, model and prompt versions.
- Every material conclusion must be traceable to exact evidence/input references and an explicit uncertainty representation. Missing evidence is not represented as a successful supported conclusion.
- The Analysis `confidence` field remains distinct from qualitative rank, numeric importance score, relevance classification, impact direction/magnitude and forecast probability.
- Forecast probability is not part of these baseline schemas. It may be added only through a separately defined and calibrated forecasting contract.
- A correction or re-analysis creates a successor immutable Analysis version; it never overwrites a completed result.
- An LLM may propose structured fields only. Application validation, rights/privacy authorization and the approved methodology govern acceptance and persistence.

#### 10.14.5 Explicitly unresolved schema details

The following details remain open and block a production schema or methodology release: complete importance-dimension vocabulary and scales; transmission-pathway and channel taxonomies; canonical typed entity/geography reference forms; numeric precision, units and range representation; period/time-horizon encoding; uncertainty object structure and calibration; treatment of conflicting evidence; minimum evidence sufficiency rules; and version migration/compatibility rules. These must be closed through the relevant controlled specification and GENI-ADR-008/019 approval process. No arbitrary defaults are introduced by this tranche.


### 10.15 Report content and generation-provenance contracts (tranche v1.7)

This section makes the semantic structure of a report version and its generation provenance explicit, using the responsibilities in Document 02 §§4.20 and 7.6 and the Report/ReportLink entities in Document 03 §11. It does not select a serialization format, template engine, or publication target.

#### 10.15.1 ReportContent

A report version must distinguish the kinds of statements it contains. A single untyped text blob is insufficient as the only representation of material conclusions.

| Field | Logical type | Requiredness | Contract |
|---|---|---|---|
| `sections` | `List<ReportSection>` | Required | Ordered sections for this immutable report version; an empty list is not a successfully generated substantive report. |
| `section_reference` | `string` | Required within each section | Stable unique reference within this report version; used by ReportEvidenceLink and ReportAnalysisLink. |
| `heading` | `string` | Required within each section | Human-readable section heading; exact length/format bounds remain open. |
| `blocks` | `List<ReportContentBlock>` | Required within each section | Ordered content units; each block has an explicit semantic type. |
| `block_type` | `enum` | Required within each block | Proposed values: `OBSERVED_FACT`, `SOURCE_ATTRIBUTED_CLAIM`, `ANALYTICAL_INTERPRETATION`, `FORECAST_OR_SCENARIO`, `LIMITATION_OR_UNCERTAINTY`. |
| `content` | `string/object` | Required within each block | Content in the declared versioned format; source-derived text remains subject to exact rights and retention scope. |
| `article_revision_references` | `List<ID<ArticleRevision>>` | Conditional | Exact source revisions supporting or supplying the block; never resolve a mutable current Article projection. |
| `evidence_references` | `List<ID<Evidence>>` | Conditional | Exact evidence supporting or qualifying the block. |
| `analysis_references` | `List<ID<Analysis>>` | Conditional | Exact immutable analytical results used by the block. |
| `uncertainty_or_limitation_reference` | `typed reference/null` | Conditional | Required where a material conclusion is qualified by a separately represented uncertainty/limitation; exact reference schema remains open. |

A source-attributed claim must retain enough attribution and evidence provenance to distinguish what a source reported from what GENI independently observed or inferred. An analytical interpretation must not be presented as an observed fact. A forecast/scenario block is permitted only when its separate methodology and calibration requirements are satisfied; this section does not authorize forecast probabilities. Unsupported precision, invented citations, and source quotations outside the exact allowed rights scope are prohibited.

The outer AppendReportVersion DTO's article, event, analysis, evidence and rights references must be the complete version-level provenance set. Section-level references must be subsets of those exact version-level references; they cannot silently add new inputs. The ReportEventLink, ReportArticleLink, ReportAnalysisLink and ReportEvidenceLink records must agree with the immutable content manifest and section references.

#### 10.15.2 ReportGenerationProvenance

The `generation_provenance` object in AppendReportVersion must identify how this exact report version was produced. Its minimum logical fields are:

| Field | Logical type | Requiredness | Contract |
|---|---|---|---|
| `generator_component` | `string/enum` | Required | Identifies the generating component; the current logical owner is `ReportGenerator`. |
| `generator_version` | `Version` | Required | Exact generator implementation/version identifier. |
| `workflow_version` | `Version` | Required | Exact reporting workflow contract/version used. |
| `template_reference` | `string/reference` | Required | Stable identity of the template used; display name alone is insufficient. |
| `template_version` | `Version` | Required | Must equal the outer AppendReportVersion template_version. |
| `content_schema_version` | `Version` | Required | Exact schema for ReportContent and its block types. |
| `input_fingerprint` | `Fingerprint` | Required | Must equal the outer input_fingerprint and cover the exact immutable input manifest and all generation-relevant versions. |
| `generation_run_reference` | `ID<ProcessingRun>/null` | Conditional | Required when generation is executed under a persisted ProcessingRun; otherwise null with an explicit execution mode. |
| `model_usage_references` | `List<ID<LLMUsageRecord>>` | Conditional | Exact usage records when a model was used to generate or transform report content; empty when no model was used. |

The generation-provenance object is evidence of how the report was produced, not authorization. It cannot replace the common command authorization reference, content-rights assessments, privacy-processing decisions, or publication/distribution decisions. Provider/model/prompt/region details must resolve through the referenced LLMUsageRecord when applicable; secrets and raw credentials are never included.

#### 10.15.3 Report identity, lineage and state invariants

- `report_type` is limited to the documented proposed families: `INITIAL_EVENT_REPORT`, `EVENT_UPDATE`, `EVENT_CLOSURE_REPORT`, and `PERIODIC_SUMMARY`; adding a type requires a controlled schema/version change.
- `report_scope` is mandatory and authoritative. `event_id` is nullable and may identify a primary event only where the report type/scope supports it. For multi-event reports, ReportEventLink is authoritative.
- `version` is server-assigned and unique under the Report aggregate's versioning rule. A material correction creates a successor version; no generated or published version is overwritten.
- `generation_status` is server/workflow-owned and limited to the documented states `DRAFT`, `GENERATED`, `FAILED`, and `SUPERSEDED`, subject to the approved transition contract.
- Publication state is not stored on Report. PublicationDecision is an immutable eligibility decision; PublicationRecord is the history of external publication operations. Neither is inferred from generation_status.
- Report generation does not authorize external publication, recipient distribution, or delivery dispatch. Those require the separate publication/distribution/delivery authorization contracts and immediate pre-side-effect validation.
- All version-level links, the immutable content manifest, input fingerprint and Report version must commit atomically. A failed write must not leave orphaned report links or a partially updated effective-version projection.

#### 10.15.4 Remaining report-contract blockers

The following remain open and must be resolved before production report generation: exact ReportContent serialization and content_format vocabulary; section/block schema and stable section-reference grammar; source-attribution representation; template identity and immutable template storage; canonical input-manifest serialization and fingerprint algorithm; version-allocation and supersession concurrency contract; generation-run and LLMUsageRecord reference lifecycle; and report-family-specific content/required-section rules. No HTML/Markdown/JSON format, template engine, or provider is selected by this tranche.

### 10.16 Article duplicate candidate and decision contracts (tranche v1.8)

This tranche closes the missing first-slice repository and logical DTO boundary for article deduplication, using GENI-ADR-002, Document 02 §§4.4/4.4.1, Document 03 §§5.8–5.9 and §16, and Document 08 §5.2. It does not approve a matching algorithm, score scale, threshold, physical schema, or human-review workflow. GENI-ADR-002 remains Proposed and its approval gate applies before production duplicate decisions are enabled.

#### 10.16.1 AppendDuplicateCandidate

| Field | Logical type | Requiredness | Validation / invariant |
|---|---|---|---|
| `article_id_a` | `ID<Article>` | Required | Must own `article_revision_id_a`. |
| `article_revision_id_a` | `ID<ArticleRevision>` | Required | Exact immutable revision in the canonical pair. |
| `article_id_b` | `ID<Article>` | Required | Must own `article_revision_id_b`. |
| `article_revision_id_b` | `ID<ArticleRevision>` | Required | Exact immutable revision; must differ from revision A. |
| `similarity_score` | `number/null` | Nullable | Null when no score was evaluated; scale, direction and interpretation are method/policy-specific. Never coerce missing to zero or call it a probability without calibration. |
| `matching_method` | `DuplicateMatchingMethod` | Required | Exact candidate-generation/evaluation method; vocabulary remains policy-governed. |
| `matching_policy_version` | `Version` | Required | Exact policy/configuration version used. |
| `input_fingerprint` | `Fingerprint` | Required | Deterministic fingerprint of the canonical exact revision pair and all comparison-relevant inputs/configuration. Canonical serialization remains open. |
| `evaluated_at` | `Instant` | Required | Server-trusted evaluation time. |
| `actor_reference` | `ActorReference` | Required | Authenticated service/human identity from trusted command context. |
| `authorization_reference` | `AuthorizationReference` | Required | Immutable ALLOW reference for the exact `article.duplicate.evaluate` action, canonical revision pair, scope, policy/version and input fingerprint. |
| `metadata` | `JSON/object` | Optional | Versioned extension only; cannot override typed fields or contain secrets/restricted content by default. |

Candidate ID and creation metadata are server-owned. The revision pair must be canonicalized so reverse-order requests resolve to the same logical candidate. The exact canonical ordering rule must be deterministic and versioned; it must not depend on an unapproved identifier encoding. Repeated evaluation with the same canonical pair, method/policy version and input fingerprint is idempotent. Changed inputs or policy create a new immutable candidate.

Candidate generation failure, timeout, insufficient content or unavailable signals must not create a negative DuplicateDecision. A null similarity score is not a zero score. Candidate similarity is not EventMatch confidence.

#### 10.16.2 AppendDuplicateDecision

| Field | Logical type | Requiredness | Validation / invariant |
|---|---|---|---|
| `duplicate_candidate_id` | `ID<DuplicateCandidate>` | Required | Exact immutable pairwise candidate. |
| `outcome` | `enum` | Required | Exactly `CONFIRMED_DUPLICATE`, `NOT_DUPLICATE`, or `REVIEW_REQUIRED`. |
| `decision_reason` | `string` | Required | Explains the outcome; exact length and controlled reason-code vocabulary remain open. |
| `decision_method` | `string/enum` | Required | Method that produced/authorized the decision; vocabulary remains policy-governed. |
| `decision_policy_version` | `Version` | Required | Exact decision policy version. |
| `decision_confidence` | `number/null` | Nullable | Null when not assessed; semantics and calibration must be explicit and distinct from candidate similarity. |
| `actor_reference` | `ActorReference` | Required | Authenticated actor/service identity from trusted command context. |
| `authorization_reference` | `AuthorizationReference` | Required | Immutable ALLOW reference for the exact `article.duplicate.decide` action, candidate, outcome, effective predecessor and policy/version. |
| `decided_at` | `Instant` | Required | Server-trusted immutable decision time. |
| `supersedes_decision_id` | `Optional<ID<DuplicateDecision>>` | Nullable | Null only for the first decision; otherwise must identify the current effective decision for the same candidate. |
| `metadata` | `JSON/object` | Optional | Versioned extension only; cannot override typed decision fields. |

The common command metadata in §3.2 also applies, including immutable `authorization_reference`, schema version, correlation/causation, scoped idempotency key and request fingerprint. The repository receives `expected_effective_decision_id` separately as the compare-and-swap predecessor. The first decision is accepted only when no prior decision exists; a successor must name the current terminal decision. Enforce one root decision per candidate and at most one direct successor per decision. A stale or competing append returns CONFLICT. The effective decision is the unique terminal decision in the linear chain, not a mutable flag on an immutable decision.

A correction creates a successor decision and preserves the previous decision. Only an effective `CONFIRMED_DUPLICATE` establishes a confirmed pairwise duplicate relationship. `REVIEW_REQUIRED` preserves uncertainty and does not enable a material review action unless GENI-ADR-014 and its contracts are accepted. Duplicate decisions do not merge/delete Articles or ArticleRevisions, do not modify source identity, and do not create or modify EventMatchDecision or ArticleEventLink.

#### 10.16.3 Pairwise and group semantics

- Duplicate decisions are pairwise and scoped to the exact two ArticleRevision records.
- Pairwise duplicate decisions are not transitive: A–B and B–C do not establish A–C.
- A connected component may be exposed only as a non-authoritative candidate/review cluster.
- Exact-duplicate grouping is permitted only when the same documented normalization/fingerprint rule yields the same exact-content identity.
- A near-duplicate group is authoritative only when every member pair has an effective `CONFIRMED_DUPLICATE` decision (complete-link), or when a separately versioned and approved group-decision contract is introduced by a future ADR.
- Missing, conflicting, or superseded pairwise decisions prevent automatic promotion to an authoritative group.
- Group reconstruction must be deterministic and retain the exact pairwise decisions, candidate inputs and policy versions used.
- Duplicate identity decisions remain separate from event identity and independent-source corroboration.

#### 10.16.4 Remaining duplicate-contract blockers

The following remain open and block production implementation of the corresponding detail: canonical revision-pair ordering rule; matching-method vocabulary and score semantics/ranges; exact candidate input fingerprint serialization; decision-method and reason-code vocabularies; decision-confidence semantics/calibration; and any authoritative multi-article group-decision model. These values must be established by approved policy, representative evaluation data and the relevant ADRs, not invented in repository code. The first-slice baseline is pairwise only and must not implement transitive near-duplicate clustering.

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
**Version:** 3.8  
**Status:** Proposed — Pending Project Owner Approval  
**Last Updated:** 2026-11-26

**Revision Note (v2.8):** Tightened provider-backed analysis provenance by requiring each provider request to create an LLMUsageRecord linked to the exact Analysis/ProcessingRun and to preserve privacy, purpose, data-category, region, transfer and content-rights decision references. Added the explicit privacy-processing authorization permission to the PersistAnalysis crosswalk. No provider egress is authorized by this contract.

**Revision Note (v3.3):** Gate B now requires the reproducible GENI-ADR-005-POC-001 evidence protocol, predeclared workload thresholds, complete correctness gates, and an accepted engine decision before persistence adapter selection. Added explicit actor and immutable authorization-reference fields to DuplicateCandidate and DuplicateDecision persistence contracts, and bound each reference to the exact deduplication permission and operation scope. This aligns the data model, security catalogue and first-slice DTOs; no decision policy or ADR status changed.

**Revision Note (v3.4):** Separates the deterministic fixture-slice repository/DTO subset from adjacent dormant contracts. Source collection/configuration, production source identity, PublicationDecision, material review actions, and provider-backed LLM execution are explicitly excluded from first-slice acceptance. The broader contract inventory remains available for later gated capabilities; no ADR is accepted by this revision.

**Revision Note (v3.5):** Records the Project Owner-selected source-aware mixed content-retention direction, adds revision-level content-availability states, and makes the content-reference invariant explicit. It also identifies the unresolved metadata-only revision idempotency fingerprint and content-hash semantics as blockers; no repository implementation or source-specific content permission is implied.

**Revision Note (v3.6):** Makes the source-identity canonicalization version an explicit required field, separate from content-normalization version, so identity normalization can be reproduced and audited. The metadata-only revision idempotency fingerprint and exact content-hash semantics remain open.

**Revision Note (v3.7):** Defines a versioned semantic revision fingerprint separate from retained-content SHA-256, specifies its exact JCS manifest and metadata-only behavior, and limits idempotency comparison to the current revision so historical returns remain append-only.

**Revision Note (v3.8):** Adds `author` as a historical ArticleRevision snapshot and fingerprint input, aligns the command schema and current-projection ownership, and closes the prior author/published-at/metadata snapshot gap for the core revision fields.

**End of Document**
