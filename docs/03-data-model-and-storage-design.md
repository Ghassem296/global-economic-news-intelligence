# Global Economic News Intelligence — Data Model & Storage Design

**Document ID:** GENI-DATA-003
**Version:** 1.62
**Status:** Draft — Under Architecture Review
**Project:** Global Economic News Intelligence  
**Owner:** Project Owner
**Last Updated:** 2026-11-27

---

## 1. Purpose

This document defines the logical domain data model, entity relationships, persistence requirements, integrity constraints, and storage contracts for Global Economic News Intelligence.

The system is event-centric rather than article-centric. It collects information from international sources, identifies and correlates real-world economic developments, evaluates claims and evidence, produces analytical outputs, and delivers versioned reports.

The data model must support:

- Source and article management.
- Article normalization, revision tracking, and deduplication.
- Topic classification and entity extraction.
- Event detection, matching, continuation, merging, and splitting.
- Claim and evidence provenance.
- Analysis and report versioning.
- Publication decisions and human review.
- Report delivery and retry tracking.
- Workflow execution, recovery, and observability.
- LLM usage and cost tracking.
- Reproducibility of analytical outputs.
- Content retention and rights management.

This document defines logical domain requirements. Physical database implementation details must remain behind repository and transaction boundaries.

The component responsibilities and application-level contracts are defined in Document 02. If a conflict exists, the documents must be reconciled rather than allowing either document to silently override the other.

## 2. Design Principles

### 2.1 Event-Centric Domain Model

An Article represents a publication. An Event represents a real-world development.

They are separate entities connected through an explicit many-to-many relationship.

A single event may be covered by multiple articles. An article may describe multiple events when justified.

Article deduplication and event matching are separate operations:

- Article deduplication identifies identical or substantially equivalent publications.
- Event matching determines whether an article or observation concerns an existing event.
- Event relationships represent developments that are related but not necessarily identical.

### 2.2 Provenance and Traceability

Important analytical conclusions must be traceable to their inputs.

The system should be able to identify:

- Which source published or supplied the information.
- Which article revision or external document contains it.
- Which exact passage, data point, or document location supports it, when available.
- When the information was published, collected, and observed.
- Which claim the evidence supports, contradicts, or contextualizes.
- Which analysis used the evidence.
- Which report version contains the resulting conclusion.
- Which model, prompt, schema, and processing version produced the analysis.

Provenance must not depend solely on free-text descriptions.

### 2.3 Explicit Uncertainty

Unknown information must remain unknown.

Examples:

- Unknown economic impact must not be represented as zero impact.
- Missing publication time must remain null.
- An unverified claim must not be represented as confirmed.
- Missing market data must not be replaced with an invented market reaction.
- Model confidence must not be treated as objective probability unless calibrated and explicitly defined.
- Event importance, economic relevance, and economic impact must not be represented as one interchangeable score.
- An event with unknown economic impact must not automatically receive low importance or low economic relevance.

### 2.4 Historical Integrity

Material changes to articles, events, analyses, reports, publication decisions, reviews, and delivery attempts must be traceable.

Completed analyses and published reports must not be silently overwritten.

New analytical or report versions must preserve references to their inputs.

### 2.5 Idempotency and Recoverability

Repeated execution must not create duplicate domain effects.

Processing must support safe retries and recovery after partial failures.

A completed step should not be repeated unnecessarily, while a failed, interrupted, or outdated step should be eligible for controlled reprocessing.

External side effects must be treated separately from transactional database operations.

### 2.6 Database Independence

Domain entities must not depend on SQLite-specific or PostgreSQL-specific types, SQL statements, or behavior.

Persistence must be accessed through repository interfaces and application-level transaction boundaries.

### 2.7 Separation of Facts, Claims, and Analysis

The model must distinguish:

- **Observed information:** content directly available from a source or dataset.
- **Source claim:** an assertion attributed to a person, organization, publication, or institution.
- **Evidence assessment:** an evaluation of evidence supporting or contradicting a claim.
- **AI analysis:** an interpretation generated from available inputs.
- **Forecast:** a forward-looking estimate or scenario.

These categories must not be conflated in reports.

### 2.8 Logical Model Versus Initial Implementation

The logical model describes the capabilities and relationships required by the product.

It does not require every logical entity to become a separate physical table in the first migration. Initial implementation must prioritize the first usable end-to-end workflow while preserving the ability to evolve.

### 2.9 Separate Assessment Semantics

Event importance, economic relevance, and economic impact are three different assessment questions. They must be represented as separately versioned analytical results, with independent result schemas and methodology versions. A shared execution pipeline or shared evidence inputs do not make the assessments interchangeable.

The Event record is not the authoritative storage location for these assessment results. The versioned Analysis records are authoritative. A current-value projection or cache may be maintained for efficient reads only if it can be rebuilt from the underlying Analysis history.

## 3. Persistence Strategy

### 3.1 Initial Relational Storage

PostgreSQL is the Project Owner-selected target relational engine for GENI, as recorded in GENI-ADR-005 v1.5 on 2026-11-26. SQLite is not an active implementation target. The PostgreSQL qualification workload, correctness/failure matrix, measurement controls, and required evidence artifacts are defined in GENI-ADR-005-POC-001. That protocol is a test plan, not evidence that qualification has passed or that production is authorized. Exact PostgreSQL, driver, query/ORM, migration, async, transaction, and connection-pool versions/settings remain gated by qualification evidence and formal ADR acceptance.

The selected implementation must support relational integrity, versioned migrations, transactional updates, controlled connection lifecycle, explicit isolation/locking behavior, async access, indexes, and tested backup/restore.

The PostgreSQL implementation must explicitly configure and test foreign-key enforcement, transaction isolation and boundaries, row/advisory-lock strategy, deadlock handling, connection-pool sizing/lifecycle/timeouts, backup and restore, migrations, indexes, and async cancellation/connection cleanup.

PostgreSQL durability settings, checkpointing, autovacuum, indexes, and pool behavior must be tested against the approved workload. Durability must not be weakened merely to improve benchmark results.

### 3.2 Production Qualification Gate

PostgreSQL is the sole target for the initial relational persistence implementation. Production activation remains gated by the PostgreSQL qualification protocol and formal acceptance of GENI-ADR-005. No SQLite adapter or dual-engine portability promise is in scope.

### 3.3 Logical Storage Categories

The logical storage model consists of:

1. Relational domain data.
2. Article content and article revisions.
3. Event, claim, and evidence history.
4. Analytical and report versions.
5. Publication, review, and delivery records.
6. Workflow execution and recovery metadata.
7. Scheduling and operational metadata.
8. LLM usage and operational metadata.
9. Optional semantic search representations.

These categories may initially share one relational database. Their logical separation must remain clear.

### 3.4 Storage Decisions Requiring ADR Approval

The following are not considered permanently approved by this document:

- Initial database engine and operating mode.
- Embedding generation and storage strategy.
- Full-text and external content retention.
- Article content retention and licensing rules.
- Asynchronous database library and concurrency strategy.
- Future object storage requirements.
- Scheduling and worker execution infrastructure.

## 4. Domain Relationship Overview

The following is a conceptual overview. It does not replace the detailed ownership and relationship rules below.

```text
Source
  |
  +---- SourceHealthRecord
  |
  +---- CollectionCheckpoint
  |
  +---- Article
          |
          +---- ArticleRevision
                    |
                    +---- EventMatchCase
                           |
                           +---- EventMatchCandidate --------> Event
                           |
                           +---- EventMatchDecision
                                  |
                                  +---- ArticleEventLink -----> Event
                                  |
                                  +---- ReviewRecord
          |
          +---- ArticleProcessingRecord
          |
          +---- ArticleTopicClassification
          |
          +---- ArticleEntityMention
          |
          +---- DuplicateCandidate
                    |
                    +---- DuplicateDecision (immutable outcome and supersession history)

Event
  |
  +---- EventHistory
  |
  +---- EventRelationship
  |
  +---- EventEntityLink
  |
  +---- Claim
         |
         +---- ClaimAssessment (immutable versions)
                |
                +---- ClaimAssessmentEvidenceLink ----> Evidence
                |
                +---- AssessmentHistory (append-only)
         |
         +---- ClaimObservation
         |
         +---- ClaimEvidenceLink
                           |                    |
                           +---- Analysis      Evidence
                           |      |
                           |      +---- AnalysisEvidenceLink
                           |      |
                           |      +---- AnalysisInput
                           |
                           +---- ReportEventLink
                                  |
                                  +---- Report
                                         |
                                         +---- ReportArticleLink
                                         +---- ReportEvidenceLink
                                         +---- ReportAnalysisLink
                                         +---- PublicationDecision
                                         +---- ReviewRecord
                                         +---- DeliveryRecord

EventIdentityOperation
  |
  +---- EventIdentityOperationInput
  |
  +---- EventIdentityOperationOutput

ProcessingRun
  |
  +---- ProcessingStep

LLMUsageRecord
  |
  +---- ProcessingRun / ProcessingStep / Analysis

Schedule
  |
  +---- ScheduledExecution
```

## 5. Core Domain Entities

### 5.1 Source

Represents a configured information source.

Fields:

| Field | Type | Description |
|---|---|---|
| id | UUID/string | Internal identifier |
| name | string | Display name |
| source_type | enum/string | RSS, API, web, official dataset, etc. |
| base_url | string | Validated source URL |
| language | string/null | Primary language, if known |
| country_code | string/null | Source country, if applicable |
| ownership_group | string/null | Known ownership grouping |
| syndication_group | string/null | Known syndication grouping |
| reliability_profile | JSON/null | Documented source reliability context and assessment basis |
| reliability_profile_version | string/null | Version of the source reliability profile and its evaluation criteria |
| collection_config | JSON | Non-secret source configuration |
| is_active | boolean | Whether collection is enabled |
| version | opaque version | Configuration aggregate version used for optimistic concurrency; concrete representation is implementation-defined |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

Constraints:

- Source identifiers must be stable.
- `version` is server-managed and participates in optimistic concurrency for configuration changes; callers must supply the expected current version, and a stale version must fail with `CONFLICT`/`STALE_VERSION`. Its concrete encoding and comparison mechanism remain implementation choices.
- Source URL validation is mandatory.
- Credentials and secrets must not be stored in ordinary configuration fields.
- Reliability information must have documented semantics, a version, an evidence basis, and explicit unknown values.
- A SourceAssessmentResult is a derived context value, not an authoritative claim-verification outcome or separate persistent entity.
- Historical ClaimAssessment input provenance must preserve the source-profile version and source-metadata fingerprint it consumed.
- Source ownership and syndication relationships must not be inferred solely from domain names.
- Source configuration changes must be auditable where operationally significant.

A numeric reliability score may be added only with a documented scale, calculation method, version, and calibration policy.

### 5.2 SourceHealthRecord

Represents a source collection health observation.

Fields:

- `id`
- `source_id`
- `checked_at`
- `health_status`
- `response_status`
- `latency_ms`
- `error_category`
- `error_summary`
- `items_discovered`
- `items_collected`
- `metadata`

Possible health states:

- `HEALTHY`
- `DEGRADED`
- `UNAVAILABLE`
- `UNKNOWN`

Records should preserve historical health observations rather than only storing the latest source status.

### 5.3 SourceRelationship

Represents a known, evidence-backed relationship between two publisher/source identities. It is not a relationship between individual articles or article revisions.

Fields:

- `id`
- `source_id_from`
- `source_id_to`
- `relationship_type`
- `assessment_status` — `UNASSESSED`, `PROPOSED`, `CONFIRMED`, `DISPUTED`, `REJECTED`, or `UNKNOWN`
- `confidence` nullable, with semantics defined by the applicable assessment method
- `evidence_reference`
- `valid_from` nullable
- `valid_until` nullable
- `relationship_version`
- `supersedes_relationship_id` nullable
- `created_at`
- `updated_at`
- `metadata`

Relationship types include `OWNED_BY`, `OPERATED_BY`, `SAME_EDITORIAL_GROUP`, `SYNDICATES_TO`, `SYNDICATED_FROM`, `REPUBLISHES`, `AFFILIATED_WITH`, and `UNKNOWN_RELATIONSHIP`. `SAME_EDITORIAL_GROUP` is symmetric; the other types are directional. The `from` and `to` orientation is normative and must not be replaced by an unordered pair.

Constraints:

- Both source references must resolve to distinct Source records.
- Only symmetric relationships may use canonical source-pair ordering; directional relationships preserve their declared orientation.
- A validity interval must satisfy `valid_from < valid_until` when both endpoints are known.
- A correction or changed assessment creates a successor version; historical relationship assertions are not overwritten.
- Unassessed, disputed, rejected, or unknown relationships must not be treated as confirmed facts.
- Relationships must not be inferred from domain similarity alone.
- Unknown independence must not be interpreted as confirmed independence.

### 5.3.1 ArticleOriginRelationship

Represents a provenance relationship between one exact ArticleRevision and another article revision, a source, or an explicitly identified external origin. It is separate from publisher ownership/affiliation relationships in SourceRelationship.

Fields:

- `id`
- `article_revision_id_from` — the publication whose information origin is being described
- `article_revision_id_to` nullable — the cited, copied, syndicated, or otherwise related origin article revision
- `origin_source_id` nullable — a known source-level origin when no exact origin revision is available
- `external_origin_reference` nullable — a stable reference to a press release, dataset, statement, document, or other external origin
- `relationship_type`
- `assessment_status`
- `confidence` nullable
- `evidence_reference`
- `valid_from` nullable
- `valid_until` nullable
- `relationship_version`
- `supersedes_relationship_id` nullable
- `created_at`
- `metadata`

Relationship types include `SYNDICATED_FROM`, `REPRINTED_FROM`, `DERIVED_FROM`, `ATTRIBUTES_TO`, `QUOTES`, `SUMMARIZES`, `CITES`, `USES_COMMON_PRIMARY_SOURCE`, and `UNKNOWN_RELATIONSHIP`. `ORIGINAL_REPORTING` is an evidence/source role, not an edge type; it must be recorded as a role on the relevant evidence or source assessment.

Constraints:

- `article_revision_id_from` must reference the exact ArticleRevision being assessed.
- Exactly one of `article_revision_id_to`, `origin_source_id`, or `external_origin_reference` must identify the target origin for a known relationship. An `UNKNOWN_RELATIONSHIP` may have no target, but must retain the evidence and assessment basis for its unknown state.
- A relationship between article revisions must preserve direction from the dependent/subject publication to the origin publication.
- A validity interval must satisfy `valid_from < valid_until` when both endpoints are known.
- Corrections create successor versions and preserve the prior assertion and its evidence.
- Missing provenance must remain unknown; it must not be converted into a guessed origin.

### 5.4 Article

Represents one collected publication.

Fields:

| Field | Type | Description |
|---|---|---|
| id | UUID/string | Internal identifier |
| source_id | UUID/string | Source reference |
| external_id | string/null | Source-provided identifier |
| url | string | Original article URL |
| canonical_url | string/null | Normalized canonical URL |
| title | string | Current normalized title |
| content | text/null | Current content projection, subject to rights policy |
| summary | text/null | Available source summary or permitted extract |
| author | string/null | Author, if known |
| language | string/null | Detected or declared language |
| published_at | timestamp/null | Original publication time |
| collected_at | timestamp | First successful collection time |
| last_seen_at | timestamp | Most recent observation |
| content_hash | SHA-256/null | Hash of the exact permitted normalized content representation referenced by the current revision; null when content is not persistently retained. Not an article/revision identity. |
| content_availability | enum/string | Available, partial, metadata-only, unavailable |
| rights_status | string/null | Non-authoritative current content-rights summary for display/operations monitoring; never an authorization decision. |
| current_revision_id | UUID/string/null | Current revision reference |
| metadata | JSON | Additional source metadata |
| created_at | timestamp | Record creation |
| updated_at | timestamp | Last modification |

Constraints:

- `source_id` must reference an existing source.
- Original and canonical URLs must remain distinguishable.
- Missing content must not be represented as an empty article without an explicit availability state.
- Content hashes must use a documented normalization and hashing algorithm.
- Article content must not be silently replaced when the source changes.
- External identifiers should be unique within a source when present.
- Canonical URL and content fingerprints may support duplicate detection but must not automatically merge articles without the configured matching policy.

A unique constraint on `(source_id, external_id)` should apply only when `external_id` is present and meaningful.

`Article.rights_status` is a display/monitoring projection only. Every restricted operation must resolve a current, immutable RightsAssessment for the exact source/content scope and operation; this summary field must never authorize retrieval, persistent storage, external processing, quotation, or distribution.

The exact treatment of nullable unique values must be verified for each database implementation.

**Current content ownership rule:** `Article` is the current searchable projection of the latest valid persisted article revision. `ArticleRevision` is the historical record of meaningful content changes. Updates to the current projection and creation of a revision must occur atomically. The application must not maintain two independently editable copies of the same current content.

### 5.5 ArticleRevision

Preserves meaningful article changes.

Fields:

- `id`
- `article_id`
- `revision_number`
- `normalized_title` — normalized source title snapshot for this revision
- `content_availability` — the availability state of this exact revision: `available`, `partial`, `metadata-only`, or `unavailable`
- `content_reference`
- `content_hash` — SHA-256 of the exact normalized content bytes retained by this revision; null for metadata-only/unavailable revisions
- `content_normalization_version` — required with content_hash; identifies the exact normalization rules used before hashing
- `revision_fingerprint` — SHA-256 identity of the semantic revision snapshot, independent of the content hash and storage location
- `revision_fingerprint_schema_version` — exact schema/canonicalization version used for the revision fingerprint
- `summary`
- `author` — source-reported author snapshot, when permitted and available
- `language`
- `published_at` — source publication time snapshot
- `observed_at`
- `change_reason`
- `rights_assessment_references` — immutable references to the exact operation/content-scope assessments relied on when the revision was persisted
- `metadata` — permission-filtered semantic source metadata snapshot
- `created_at`

Constraints:

- `(article_id, revision_number)` must be unique.
- Repeated collection of unchanged content must not create a revision.
- Material changes must preserve the previous revision.
- `content_availability` is required on every revision and uses exactly one of: `available`, `partial`, `metadata-only`, or `unavailable`.
- `available` and `partial` require a non-null `content_reference`; the reference must resolve only to the exact content representation permitted for the relevant operation.
- `metadata-only` and `unavailable` require null `content_reference`, `content_hash`, and `content_normalization_version`; an empty string or placeholder object is not a substitute for an absent value.
- `content_hash` is the lowercase 64-hex SHA-256 digest of the exact UTF-8 bytes of the retained normalized content representation. The normalization algorithm/version must be explicit. The hash is itself content-derived data and may be persisted only when the applicable rights decision permits retention of that fingerprint; this baseline requires it only for persistently retained `available`/`partial` content.
- `revision_fingerprint` is a separate lowercase 64-hex SHA-256 digest used only to identify semantic equality with the current revision of the same Article. It is not a content hash, a cross-article identity, or evidence of rights permission. It must be computed from the versioned revision-fingerprint manifest defined in Document 15 and verified on persistence/read.
- Repeated collection is compared only with the Article's current revision. If the current fingerprint and schema version match, no new revision is created. If the article changes away and later returns to an earlier representation, the return is a new chronological revision; fingerprints are not globally unique across all historical revisions.
- A metadata-only or unavailable revision uses a metadata-derived revision fingerprint; it must never persist a content hash merely to obtain idempotency.
- A metadata-only revision may retain only metadata and other source-derived fields explicitly permitted by the applicable source/content rights decision.
- `Article.content_availability` is a current-state projection and must agree with the `content_availability` of `Article.current_revision_id`; it must not be independently edited.
- Content references must comply with the project's content retention and licensing policy.
- A revision must identify the text representation and content-normalization version to which its hashes and offsets refer.
- Technical access, retrieval, temporary processing, persistent storage, external transmission, derived use, quotation, and republication are separate permission scopes. Permission for one operation does not imply permission for another.
- Unknown, expired, revoked, or unverifiable permission must fail closed for the affected restricted operation; it must not be converted into a permissive rights status.

`content_reference` may point to relationally stored content or an approved external content store. The physical storage method is an implementation decision. Under the selected source-aware policy, a reference is created only after the applicable persistent-storage permission has been verified; metadata-only and unavailable revisions remain valid revision records without a content reference.

### 5.6 Event

Represents a real-world economic or economically relevant geopolitical development.

Fields:

| Field | Type | Description |
|---|---|---|
| id | UUID/string | Stable event identifier |
| title | string | Current event title |
| description | text/null | Current event description |
| event_type | string | Event classification |
| primary_topic | string | Main economic topic |
| geographic_scope | string/null | Global, regional, national, or local |
| primary_country_code | string/null | Primary country, when applicable |
| occurrence_start_at | timestamp/null | Estimated or observed start |
| occurrence_end_at | timestamp/null | Estimated or observed end |
| occurrence_time_precision | string/null | Exact, approximate, date-only, unknown |
| status | string | Current lifecycle state |
| first_observed_at | timestamp | First system observation |
| last_updated_at | timestamp | Latest meaningful update |
| resolved_at | timestamp/null | Resolution time |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

Constraints:

- Event identifiers remain stable during ordinary updates.
- Event identity changes must use explicit merge or split operations.
- Lifecycle transitions must be validated against an approved transition policy.
- Importance, economic relevance, and economic impact assessments must be stored as separate versioned Analysis records rather than independent scalar fields on Event.
- A latest-assessment projection, if maintained, must be rebuildable from Analysis history.
- Missing occurrence time must remain null.
- `UPDATED` is not a persistent lifecycle state. It is represented through event history and update events.

The event record represents current state. `EventHistory` preserves meaningful prior states.

### 5.7 ArticleEventLink

Represents an applied, decision-authorized association between an ArticleRevision and an Event.

Fields:

- `id`
- `article_revision_id`
- `event_match_case_id` — the EventMatchCase that authorized this specific association
- `event_id`
- `relationship_type`
- `association_confidence`
- `association_method`
- `matching_policy_version`
- `event_match_decision_id`
- `associated_at`
- `is_active`
- `deactivated_at`
- `deactivated_by_decision_id`
- `metadata`

Relationship types may include:

- `INITIAL_REPORT`
- `FOLLOW_UP`
- `CONFIRMATION`
- `CONTEXT`
- `CONTRADICTION`
- `RELATED_DEVELOPMENT`

Constraints:

- Every association must reference the exact EventMatchCase and EventMatchDecision that authorized its creation.
- The referenced EventMatchDecision must belong to the referenced EventMatchCase, have outcome MATCH and must identify the linked event through its selected candidate.
- At most one active ArticleEventLink may exist for an EventMatchCase; historical inactive links must be retained.
- The link's article_revision_id must equal the ArticleRevision referenced by its EventMatchCase.
- The link's event_id must equal the Event selected by the referenced MATCH decision.
- A link is active only while its authorizing MATCH decision remains the effective decision for that case.
- Association confidence must use documented semantics and must not be copied from candidate similarity without an explicit calibration rule.
- Deactivation must preserve the original link and identify the successor EventMatchDecision in the same case that deactivated it.
- An inactive link must have both `deactivated_at` and `deactivated_by_decision_id`; an active link must have neither.
- `deactivated_by_decision_id` must reference a decision in the same case whose `supersedes_decision_id` identifies the link's authorizing decision.
- A correction creates a new decision and a new association where appropriate; it must not rewrite historical decisions or silently repoint an existing link.
- A rejected, ambiguous, or review-required match must not be represented as an active association.

### 5.8 DuplicateCandidate

Represents an immutable evaluation candidate comparing two exact ArticleRevision records for possible duplicate or near-duplicate content. It is candidate evidence only and does not hold the authoritative decision.

Fields:

- `id`
- `article_id_a`
- `article_revision_id_a`
- `article_id_b`
- `article_revision_id_b`
- `similarity_score` nullable
- `matching_method`
- `matching_policy_version`
- `input_fingerprint`
- `evaluated_at`
- `actor_reference` — authenticated service/human identity that initiated the evaluation
- `authorization_reference` — immutable authorization/audit reference bound to the exact `article.duplicate.evaluate` action, revision pair, scope, policy/version and input fingerprint
- `metadata`

Constraints:

- The same ArticleRevision must not be compared with itself.
- The article/revision pair must be stored in canonical order.
- Each revision must belong to its corresponding Article.
- Repeated evaluation with the same canonical revision pair, method/policy version, and input fingerprint must be idempotent.
- Candidate evaluations are immutable; changed inputs or policy versions create new evaluations.
- A candidate score is not a final duplicate decision and must not be interpreted as a calibrated probability unless explicitly validated.

### 5.9 DuplicateDecision

Represents one immutable case-level decision for a DuplicateCandidate.

Fields:

- `id`
- `duplicate_candidate_id`
- `outcome`
- `decision_reason`
- `decision_method`
- `decision_policy_version`
- `decision_confidence` nullable, with documented semantics
- `actor_reference`
- `authorization_reference` — immutable authorization/audit reference bound to the exact `article.duplicate.decide` action, candidate, outcome, predecessor and policy/version
- `decided_at`
- `supersedes_decision_id` nullable
- `metadata`

Outcomes:

- `CONFIRMED_DUPLICATE`
- `NOT_DUPLICATE`
- `REVIEW_REQUIRED`

Constraints and behavior:

- A decision must reference a candidate and cannot select a candidate from another comparison scope.
- A correction creates a successor decision; it never edits or deletes the prior decision.
- At most one effective decision may exist for a candidate.
- A superseding decision must reference a prior decision for the same candidate.
- Duplicate confirmation must not erase either Article or ArticleRevision, source identity, or provenance.
- The number of articles or candidate similarity must not be substituted for independent-source corroboration.
- Candidate generation and decision authorization remain separate operations.

## 6. Topic Classification and Entity Model

### 6.1 ArticleTopicClassification

Records topic classification results for an article revision.

Fields:

- `id`
- `article_id`
- `article_revision_id`
- `topic`
- `confidence`
- `classification_method`
- `model_provider`
- `model_id`
- `prompt_version`
- `taxonomy_version`
- `created_at`
- `is_current`

The initial economic taxonomy includes:

- `MONETARY_POLICY`
- `FINANCIAL_MARKETS`
- `MACROECONOMICS`
- `TRADE_AND_INDUSTRY`
- `ENERGY_AND_RESOURCES`
- `FISCAL_POLICY_AND_PUBLIC_DEBT`
- `GEOPOLITICAL_ECONOMIC_RISK`

An article may have multiple topic classifications.

The primary topic should be explicitly identifiable, either through a primary indicator or a deterministic domain rule. Classification history must remain available when a new taxonomy or model version produces a different result.

### 6.2 Entity

Represents a resolved real-world entity.

Entity types may include:

- `PERSON`
- `ORGANIZATION`
- `COUNTRY`
- `REGION`
- `INSTITUTION`
- `COMPANY`
- `INDUSTRY`
- `COMMODITY`
- `FINANCIAL_INSTRUMENT`

Fields:

- `id`
- `canonical_name`
- `entity_type`
- `country_code`
- `description`
- `external_identifiers`
- `metadata`
- `created_at`
- `updated_at`

The entity table represents resolved entities, not every raw mention.

### 6.3 EntityAlias

Stores alternative names and identifiers for an entity.

Fields:

- `id`
- `entity_id`
- `alias`
- `language`
- `alias_type`
- `source`
- `created_at`

Examples include:

- Abbreviations.
- Former organization names.
- Transliterations.
- Local-language names.
- Common alternative spellings.

Alias matching must not automatically merge distinct entities when ambiguity exists.

### 6.4 ArticleEntityMention

Represents an entity mention extracted from an article revision.

Fields:

- `id`
- `article_id`
- `article_revision_id`
- `entity_id` nullable
- `mention_text`
- `mention_type`
- `confidence`
- `start_offset`
- `end_offset`
- `offset_representation`
- `extraction_method`
- `extraction_version`
- `created_at`

An unresolved mention may have a null `entity_id` until entity resolution succeeds.

Offsets must specify the exact text representation and revision they reference. Offsets must not be assumed to remain valid across article revisions.

### 6.5 EventEntityLink

Associates entities with events.

Fields:

- `id`
- `event_id`
- `entity_id`
- `relationship_type`
- `confidence`
- `created_at`
- `metadata`

Relationship types may include:

- `PRIMARY_ACTOR`
- `AFFECTED_ENTITY`
- `REGULATOR`
- `COUNTERPARTY`
- `LOCATION`
- `MARKET`
- `OTHER`

An event may be linked to multiple entities with different roles.

## 7. Event Matching and Identity History

### 7.1 EventMatchCase

Represents one independent event-resolution case for one development identified within one immutable ArticleRevision. An article revision may have multiple cases when it describes multiple distinct developments.

Fields:

- `id`
- `article_revision_id`
- `development_key` — deterministic, stable within the ArticleRevision, and identifying one development scope using a stable source-span/section anchor or canonical development-scope fingerprint; it must not be a random run identifier
- `scope_description`
- `case_status`
- `effective_decision_id` — nullable pointer to the current effective EventMatchDecision; a projection updated transactionally when a new decision is recorded
- `created_at`
- `closed_at`
- `metadata`

Case states may include `OPEN`, `PENDING_REVIEW`, `RESOLVED`, `CLOSED`, and `CANCELLED`. The case is the unit of candidate evaluation, final decision, and human review. A case must not be reused for a materially different article revision or development scope. Reprocessing the same ArticleRevision and same development scope must reuse the same development_key and case. The effective-decision pointer is a mutable current-state projection; historical EventMatchDecision records remain immutable.

The canonical initial-state rule, decision-to-case projection, allowed transitions, terminal states, and reopening/cancellation behavior are defined in Document 17, Section 6. That lifecycle contract is the normative executable baseline for the pure domain policy and its tests; it must be changed together with implementation and tests. This section remains the logical data-model summary and does not independently redefine the transition graph. A case-status change, effective-decision pointer update, decision supersession, and ArticleEventLink activation/deactivation must be coordinated atomically in one UnitOfWork under expected-version concurrency. The lifecycle policy does not waive the separate ADR-002/011 approval, authorization, durable-adapter, and production activation gates.

### 7.2 EventMatchCandidate

Represents one existing Event considered as a possible match within an EventMatchCase. Candidate generation and evaluation do not establish an association.

Fields:

- `id`
- `case_id`
- `candidate_event_id`
- `lexical_similarity` nullable
- `semantic_similarity` nullable — null when semantic retrieval is disabled or not evaluated
- `entity_overlap_score` nullable
- `temporal_compatibility_score` nullable
- `geographic_compatibility_score` nullable
- `overall_score` nullable
- `matching_method`
- `matching_policy_version`
- `candidate_input_fingerprint` — deterministic fingerprint of the ArticleRevision/development scope, candidate Event version, and evaluation inputs/configuration
- `supersedes_candidate_id` — nullable reference to the prior evaluation of the same candidate Event in the same case
- `candidate_status`
- `evaluation_reason`
- `created_at`
- `evaluated_at`
- `metadata`

Each candidate record represents one versioned evaluation of one candidate Event within one case. An evaluated candidate record is immutable. A changed matching policy or changed evaluation input creates a new candidate record rather than overwriting the earlier evaluation. Repeating an identical evaluation input must resolve to the same logical candidate record through its fingerprint.

Candidate status describes candidate-evaluation processing only (for example `GENERATED`, `EVALUATED`, or `INELIGIBLE`). `ACCEPTED`, `REJECTED`, and `SUPERSEDED` are not candidate statuses: acceptance/rejection are case-level decisions, and supersession is represented by a new immutable candidate record referencing the prior evaluation. After reaching `EVALUATED` or `INELIGIBLE`, a candidate evaluation is immutable.

The complete candidate-status enum and mutable status-transition graph are intentionally not represented as a mutable lifecycle: candidate records are created as `GENERATED`, then evaluation produces one immutable `EVALUATED` or `INELIGIBLE` record. The creation/evaluation boundary, eligibility guards, and interrupted-generation behavior are defined by Document 17, Section 7. Candidate generation interrupted before persistence creates no record; interrupted evaluation leaves the persisted candidate `GENERATED` and may be resumed idempotently. Changed inputs or policy create a successor evaluation record rather than mutating an evaluated record.

Every candidate score is nullable when its signal was not evaluated; a missing signal must remain null and must never be defaulted to zero. Every non-null score must use the scale, direction, normalization, and comparability rules defined by its recorded matching-policy/model version. `semantic_similarity` must remain null when semantic retrieval is disabled. Scores from different model or policy versions must not be compared as though they shared a calibrated scale. A candidate score is not a decision confidence and must not be interpreted as one.

### 7.3 EventMatchDecision

Represents an immutable, authoritative outcome for one EventMatchCase.

Fields:

- `id`
- `case_id`
- `outcome`
- `selected_candidate_id` — required only for `MATCH`
- `proposed_event_reference` — required stable, preassigned Event identifier for `NEW_EVENT_CANDIDATE`; used to make authorized Event creation idempotent
- `decision_method`
- `decision_confidence` — optional and distinct from candidate similarity
- `decision_rationale`
- `matching_policy_version`
- `decided_by_type`
- `decided_by_reference`
- `authorization_reference` — immutable reference to the exact security/audit authorization context for this decision
- `supersedes_decision_id`
- `created_at`
- `metadata`

Allowed outcomes:

- `MATCH`
- `NEW_EVENT_CANDIDATE`
- `NO_MATCH`
- `AMBIGUOUS`
- `REVIEW_REQUIRED`

Outcome semantics:

- `MATCH` selects exactly one eligible EventMatchCandidate belonging to this case.
- `NEW_EVENT_CANDIDATE` proposes event creation but does not itself create an Event or authorize an ArticleEventLink. After separate authorized and idempotent event creation, the new Event must be recorded as a candidate and a subsequent MATCH decision must authorize association.
- `NO_MATCH` means none of the evaluated candidates matches the development represented by this case. It does not prevent another case from the same ArticleRevision from matching another Event.
- `AMBIGUOUS` means the available candidates/evidence do not support a reliable selection.
- `REVIEW_REQUIRED` means policy requires an authorized human review before the case can be resolved.

Constraints:

- `MATCH` must reference exactly one eligible candidate belonging to the same case.
- Non-`MATCH` outcomes must not authorize an active ArticleEventLink.
- `NEW_EVENT_CANDIDATE` must carry a stable `proposed_event_reference`; it proposes event creation but does not itself create an Event or authorize an ArticleEventLink.
- Event creation is permitted only when this is the effective case decision and the versioned EventCreationPolicy authorizes it (including any required human review).
- The proposed Event identifier is used as the idempotency key for creation. Retrying the same authorized creation must resolve to the same Event and must not create a duplicate.
- After creation, the Event is persisted as an EventMatchCandidate in the same case and a new MATCH EventMatchDecision must supersede the NEW_EVENT_CANDIDATE decision before an ArticleEventLink can be activated.
- A later reassessment or human correction creates a new decision and references the decision it supersedes.
- Historical decisions are immutable.
- A review record is not a decision; an authorized review outcome must be materialized as a new EventMatchDecision.
- Every decision must persist an immutable `authorization_reference` supplied by trusted application/security context. It must resolve to the actor/service, action, exact case/resource, authorization scope, policy/version, timestamp, and result. Caller-supplied role strings are not authorization evidence. Missing, stale, revoked, or unverifiable references block the append.
- Decision confidence, candidate similarity, and reviewer certainty are separate measurements and must not be substituted for one another.

### 7.4 Event Matching Case and Decision Constraints

- Every EventMatchCandidate must belong to exactly one EventMatchCase.
- Every EventMatchCase must identify exactly one ArticleRevision and one development scope.
- `(case_id, candidate_event_id, matching_policy_version, candidate_input_fingerprint)` must be unique for idempotent candidate evaluation while permitting historical evaluations under changed inputs or policy versions.
- An evaluated EventMatchCandidate is immutable; a new evaluation creates a new candidate record whose `supersedes_candidate_id`, when present, references a prior evaluation of the same candidate Event in the same case. The application must reject cross-case or cross-Event supersession references.
- Every EventMatchDecision must belong to exactly one case.
- A selected candidate must belong to the same case as its decision.
- A case may have multiple historical decisions, but only one effective decision at a time; the EventMatchCase.effective_decision_id pointer identifies it.
- A new decision supersedes the prior effective decision without modifying it and updates the case pointer in the same transaction.
- In that same transaction, all active ArticleEventLinks authorized by the prior effective decision must be deactivated; if the new effective decision is MATCH, a new ArticleEventLink referencing that exact decision must be activated.
- A non-MATCH effective decision leaves the case with no active ArticleEventLink.
- A decision may supersede at most one prior decision, and a prior decision may have at most one direct successor in the same case.
- A decision for one case must not implicitly decide another case from the same article revision.
- Human review must reference the case and the decision under review; the review outcome must be recorded as a new decision.
- Database constraints and application validation must prevent cross-case candidate references and invalid decision-to-link references.

### 7.5 Event Identity Operations

Event merging and splitting are explicit, auditable identity operations. They must preserve stable event identifiers, decision lineage, and historical traceability. They are not ordinary event updates and must not silently rewrite ArticleEventLink records.

A merge operation must record every participating Event as an input, including the selected surviving canonical Event, and exactly one output that is the same survivor. The record must preserve the survivor-selection rationale, supporting evidence, decision method, actor and authorization, policy version, operation status, idempotency key, expected input versions, timestamps, and affected records. A split operation must record exactly one original input Event, at least two distinct successor output Events, the allocation of articles/claims/evidence/observations, unresolved allocations, rationale, actor and authorization, policy version, status, idempotency key, expected input version, and affected records. Identity corrections must record their policy-authorized input/output cardinality and compensating purpose.

Fields:

- `id`
- `operation_type` — `MERGE`, `SPLIT`, or `IDENTITY_CORRECTION`
- `status` — `PENDING`, `IN_PROGRESS`, `SUCCEEDED`, `FAILED`, `CANCELLED`, or `RECONCILIATION_REQUIRED`
- `identity_effect_state` — `NOT_APPLIED`, `APPLIED`, or `UNKNOWN`; this records whether the core identity projection is durably applied independently of downstream reconciliation status.
- `reason`
- `decision_method`
- `decision_confidence` nullable
- `policy_version`
- `actor_type`
- `actor_reference`
- `authorization_reference`
- `idempotency_key` — required and unique for the logical operation
- `processing_run_id` nullable
- `requested_at`
- `started_at` nullable
- `completed_at` nullable
- `created_at`
- `metadata`

The actor may be an authorized system policy or a human reviewer. Human-initiated or high-impact automated operations must carry an authorization reference resolvable by the security/audit layer. Every status/effect transition is recorded in EventIdentityOperationHistory; EventHistory separately records the resulting change to each affected Event. The current operation status and identity_effect_state are projections rebuildable from the append-only operation history. A retry reuses the same operation identifier and idempotency key. An uncertain core-transaction outcome sets identity_effect_state to `UNKNOWN` and status to `RECONCILIATION_REQUIRED` until the durable effect is established; an applied core effect with pending downstream work also remains `RECONCILIATION_REQUIRED`.

Possible operation types:

- `MERGE`
- `SPLIT`
- `IDENTITY_CORRECTION`

The event input and output relationships must be stored through explicit relational link entities:

**EventIdentityOperationInput**

- `id`
- `operation_id`
- `event_id`
- `expected_event_history_version` — required version observed when the operation was prepared; the core transaction must compare it with the current EventHistory version before applying the identity effect
- `role`
- `position`

**EventIdentityOperationOutput**

- `id`
- `operation_id`
- `event_id`
- `role`
- `position`

Input links must additionally preserve the expected current EventHistory version used for compare-and-swap validation. For `MERGE`, every participating Event is an input, the survivor input has role `SURVIVING_CANONICAL`, and the one output references that same Event with role `CANONICAL_SURVIVOR`. Other merge inputs use role `MERGED_SOURCE`. For `SPLIT`, the input identifies the original Event and outputs identify preallocated successor Event identifiers; no Event identifier may overlap the input and output sets. Positions are unique and define stable ordering within an operation.

This avoids relying on JSON arrays as the only representation of event identity relationships.

The operation must also persist an explicit allocation record for every affected event-scoped subject whose association is examined or changed. Input/output links identify the participating Event identities; they do not by themselves identify which Article, Claim, Evidence, or MarketObservation belongs to which successor after a split.

**EventIdentityOperationAllocation**

- `id`
- `operation_id`
- `subject_type` — one of the explicitly supported event-scoped record types: `ARTICLE_EVENT_ASSOCIATION`, `CLAIM`, `EVIDENCE`, or `MARKET_OBSERVATION`; extensions require a versioned contract change.
- `subject_id` — opaque identifier resolved and validated by the type-specific authoritative repository; this is not an unchecked polymorphic reference.
- `target_event_id` nullable — required when the allocation is resolved; must reference an Event in this operation's output set.
- `allocation_status` — `ASSIGNED` or `UNRESOLVED`.
- `allocation_method` — method/policy identifier used for the allocation.
- `allocation_rationale`
- `evidence_references` — immutable references to the evidence/context supporting the allocation, when applicable.
- `created_at`

Constraints:

- Each affected subject may have at most one effective allocation within an operation; duplicate subject entries are rejected unless an explicitly versioned correction mechanism is defined.
- `ASSIGNED` requires exactly one `target_event_id` from the operation's output set. `UNRESOLVED` requires a null target and an explicit rationale; it must never be assigned to an arbitrary successor.
- For `MERGE`, every resolved allocation targets the canonical survivor output.
- For `SPLIT`, each resolved allocation targets exactly one successor output. Unresolved allocations remain explicitly unresolved and must not create or repoint ArticleEventLinks.
- The subject type/identifier must be validated by its authoritative repository inside the same application-controlled operation boundary. Implementations must not treat `subject_id` as a trusted free-form reference or bypass aggregate ownership.
- Allocation records, operation input/output links, the core identity effect, and the corresponding EventHistory/operation-history writes must be transactionally consistent. If the allocation set cannot be durably established, the core effect must not be reported as successfully completed.
- Allocation corrections after a completed operation require an authorized compensating identity operation; historical allocation records are not silently overwritten.
- Allocation completeness and unresolved-item counts must be available to downstream reconciliation and audit. An unresolved allocation is a valid explicit outcome, not evidence that the subject belongs to every successor.

Constraints:

- A MERGE requires at least two distinct input Events, including the selected survivor, and exactly one output Event equal to that survivor.
- A SPLIT requires exactly one original input Event and at least two distinct successor output Events; the input and output sets must be disjoint.
- An IDENTITY_CORRECTION must declare its permitted input/output cardinality in the operation policy.
- The only permitted input/output overlap is the MERGE survivor, with the required input/output roles defined above.
- Every input must match its expected EventHistory version; stale inputs and overlapping unresolved identity operations must be rejected or serialized.
- Operation status/effect transitions, operation-history entries, operation links, and affected EventHistory records must be committed atomically within their UnitOfWork boundaries.
- `FAILED` and `CANCELLED` are valid only when the core identity effect is definitively `NOT_APPLIED`; after an applied effect, incomplete downstream work remains `RECONCILIATION_REQUIRED`.
- A completed operation is immutable. A correction after application requires a new compensating `IDENTITY_CORRECTION` operation.
- Input/output roles and ordering must be validated by the application layer.
- Operation creation, status transition, input/output links, and affected event-history records must be transactionally consistent.
- External notifications and downstream report reconciliation must use durable follow-up work; they must not be executed as an untracked side effect inside the identity transaction.

**Report-impact discovery and preservation:** After the core identity effect is durably applied, the reconciliation workflow must discover every immutable Report version that references any input Event through either its primary `Report.event_id` convenience reference or an authoritative `ReportEventLink`. Discovery must be deterministic, paginated/restartable, and durably checkpointed; a report version is recorded once per identity operation even if it references multiple input Events. Existing Report rows, ReportEventLinks, ReportEvidenceLinks, ReportArticleLinks, ReportAnalysisLinks, PublicationDecisions, PublicationRecords, and DeliveryRecords are historical facts and must not be silently rewritten or repointed.

**EventIdentityOperationReportImpact**

One EventIdentityOperationReportImpact aggregate tracks the effect of one identity operation on one exact immutable Report version. Its current status is a rebuildable projection; every status transition and assessment/remediation action is preserved in append-only EventIdentityOperationReportImpactHistory.

Fields:

- `id`
- `operation_id`
- `report_id` — exact immutable Report version, not a mutable report-family identifier
- `impact_classification` — versioned classification describing why the report was selected and the nature of the event-identity change
- `impact_status` — `PENDING`, `ASSESSED`, `REMEDIATION_REQUIRED`, `RECONCILIATION_REQUIRED`, or `RESOLVED`
- `reason_codes`
- `assessment_summary`
- `policy_version`
- `actor_type`
- `actor_reference`
- `authorization_reference`
- `created_at`
- `assessed_at` nullable
- `remediation_work_item_reference` nullable — typed reference to a durable, owned remediation work item; required while status is `REMEDIATION_REQUIRED`
- `resolved_at` nullable — required when status is `RESOLVED`
- `resolution_reference` nullable — typed reference to the separately persisted remediation outcome; required when status is `RESOLVED`
- `metadata`

Constraints:

- `(operation_id, report_id)` must be unique. Repeated discovery is idempotent and must not create duplicate impact records.
- The report version and all of its provenance links remain immutable. The impact record is not permission to rewrite the report or its historical event links.
- The assessment must consider all input Event references, persisted allocation outcomes including unresolved subjects, the exact report evidence/article/analysis provenance, and whether the report was previously published or delivered.
- An unresolved allocation or unavailable provenance needed to determine the report's scope must not be treated as no impact; the impact remains `RECONCILIATION_REQUIRED` until resolved.
- `ASSESSED` means the impact has been evaluated and its outcome recorded and no further report remediation is required.
- `REMEDIATION_REQUIRED` means a concrete remediation is necessary and a durable work item with an accountable owner/workflow has been created and referenced. A free-text note or an unassigned queue entry is insufficient.
- `RESOLVED` requires a durable resolution reference and timestamp; it means the tracked remediation has been completed and verified, not merely scheduled.
- Allowed transitions are `PENDING` to `ASSESSED` or `RECONCILIATION_REQUIRED`; `ASSESSED` to `REMEDIATION_REQUIRED` or `RESOLVED`; `REMEDIATION_REQUIRED` to `RESOLVED` or `RECONCILIATION_REQUIRED`; and `RECONCILIATION_REQUIRED` to `PENDING`, `ASSESSED`, or `REMEDIATION_REQUIRED` after a successful retry. Terminal `RESOLVED` records are immutable; a later material change requires a successor impact record through a new/compensating identity operation.
- A material correction creates a new immutable Report version through ReportVersionService, with new exact provenance links and a new publication-eligibility decision where applicable. The prior Report version and its PublicationDecision remain historical.
- Replacing or withdrawing an external publication is a separate, explicitly authorized PublicationService operation. An identity operation must never automatically replace or withdraw an external publication.
- A completed DeliveryRecord remains historical. Any recipient correction or notification requires a separately authorized ReportDelivery operation and its own rights authorization.
- The identity operation may reach `SUCCEEDED` only after report-impact discovery is complete and every discovered report has a durable impact record in `ASSESSED`, `REMEDIATION_REQUIRED` with a valid durable work-item reference, or `RESOLVED`. Technical discovery/assessment failures and unassigned remediation remain `RECONCILIATION_REQUIRED`; they must not be hidden by marking the identity operation complete.
- The system must not delete or reuse event identifiers after a merge or split.
- ArticleEventLink changes require case-scoped successor EventMatchDecision records and EventService application; the identity operation must not directly repoint a historical link.
- Survivor selection must use a documented, versioned policy and must not assume that the newest or oldest event is always correct.

### 7.5.1 EventIdentityOperationHistory

Represents one immutable status/effect transition or auditable action in the lifecycle of an EventIdentityOperation. It is distinct from EventHistory: operation history tracks execution/reconciliation state, while EventHistory records the affected Event's domain-state change.

Fields:

- `id`
- `operation_id`
- `sequence` — monotonically increasing within the operation
- `action_type`
- `previous_status` nullable
- `new_status`
- `previous_identity_effect_state` nullable
- `new_identity_effect_state`
- `actor_type`
- `actor_reference` nullable
- `authorization_reference` nullable
- `reason_code` and/or `reason`
- `processing_run_id` nullable
- `idempotency_key` — unique within the operation
- `created_at`
- `metadata`

Operation-history records are append-only. `(operation_id, sequence)` must be unique, and a non-null idempotency key must be unique within the operation. EventIdentityOperation.status and identity_effect_state are current projections that must be rebuildable from this history. A status transition and its history row must be written in the same transaction.

The permitted operation-status transitions are `PENDING` to `IN_PROGRESS` or `CANCELLED`; `IN_PROGRESS` to `SUCCEEDED`, `FAILED`, or `RECONCILIATION_REQUIRED`; and `RECONCILIATION_REQUIRED` to `IN_PROGRESS`, `SUCCEEDED`, or `FAILED` only after reconciliation determines whether the core effect was applied. `SUCCEEDED`, `FAILED`, and `CANCELLED` are terminal. The core identity effect state moves only from `NOT_APPLIED` to `APPLIED` or `UNKNOWN`, and from `UNKNOWN` to the reconciled `APPLIED` or `NOT_APPLIED` result; it must never revert from `APPLIED` to `NOT_APPLIED`.

Identity resolution is a read contract as well as a storage concern. Resolving a historical identifier must return one of: `CANONICAL` (one current canonical event), `MULTIPLE_SUCCESSORS` (two or more candidate successor events after a split), or `UNRESOLVED` (no safe deterministic resolution). A merge may resolve to one survivor with its operation lineage. A split must return the complete successor set and relevant operation references; the resolver must never select an arbitrary successor. A core identity effect with state `APPLIED` is authoritative even while downstream work remains `RECONCILIATION_REQUIRED`. If the effect is `UNKNOWN`, the resolver must return `UNRESOLVED` until reconciliation determines the durable state. Callers must supply case/evidence context to choose among multiple successors, and unresolved associations remain unlinked.

### 7.5.2 EventIdentityOperationReportImpactHistory

Represents one immutable transition or auditable assessment/remediation action for an EventIdentityOperationReportImpact aggregate.

Fields:

- `id`
- `report_impact_id`
- `sequence` — monotonically increasing within the report-impact aggregate
- `action_type`
- `previous_status` nullable
- `new_status`
- `actor_type`
- `actor_reference` nullable
- `authorization_reference` nullable
- `reason_code` and/or `reason`
- `remediation_work_item_reference` nullable
- `resolution_reference` nullable
- `idempotency_key`
- `created_at`
- `metadata`

History records are append-only. `(report_impact_id, sequence)` and the non-null idempotency key within the aggregate must be unique. A status/projection update and its history row must be committed in one UnitOfWork. The current impact status and remediation/resolution references must be rebuildable from the history. The history must preserve who assessed the report, why remediation was or was not required, when a work item was assigned, and what evidence established resolution.

### 7.6 EventRelationship

Represents a typed relationship between two distinct event identities. The canonical vocabulary shared with GENI-ADR-011 is:

- `RELATED_TO` — contextual relationship without a stronger asserted meaning; symmetric and stored once using deterministic event-id ordering.
- `CAUSED_BY` — the source event was caused by the target event; directed.
- `TRIGGERED_BY` — the target event directly initiated the source event; directed and narrower than general causation.
- `PART_OF` — the source event is a bounded constituent/sub-event of the target event; directed.
- `FOLLOWED_BY` — the target event occurred after the source event; directed.
- `ESCALATION_OF` — the source event is a distinct escalation in severity or scope of the target event; directed.
- `CONTINUATION_OF` — the source event is a distinct later phase continuing the target development; directed.
- `SUPERSEDES` — the source event supersedes the target event as the current occurrence/decision being tracked; directed.

Fields:

- `id`
- `source_event_id`
- `target_event_id`
- `relationship_type`
- `confidence` nullable
- `policy_version`
- `created_at`
- `metadata`

The source/target orientation is defined by the relationship descriptions above; a separate free-form direction field is not permitted. The application derives inverse navigation where appropriate rather than storing duplicate inverse edges.

Constraints:

- Self-referential relationships are rejected.
- `RELATED_TO` must be canonicalized to one stored edge for an unordered event pair.
- Directed relationships preserve source/target orientation.
- A relationship never authorizes a merge or an ArticleEventLink.
- Event relationships do not alter event identity or lifecycle status.
- Cycles are rejected for `PART_OF`, `FOLLOWED_BY`, `ESCALATION_OF`, and `CONTINUATION_OF`; causal cycles are rejected unless a future explicitly approved policy defines another treatment.
- Similarity, shared entities, or an existing relationship must never be used alone to merge events.

## 8. Claims and Evidence

### 8.1 Claim

Represents a factual assertion, attributed statement, estimate, or forecast. Claim identity and source observations are stable domain records; assessment outcomes are stored separately.

Fields:

- `id`
- `claim_text`
- `claim_type`
- `attribution`
- `current_assessment_id` nullable — reference to the effective ClaimAssessment for this Claim
- `verification_status` — read-only current projection derived from the effective assessment; initially UNVERIFIED
- `confidence` nullable — read-only projection of the effective assessment confidence
- `first_observed_at`
- `last_observed_at`
- `created_at`
- `updated_at`

Claim types:

- `FACTUAL`
- `OFFICIAL_STATEMENT`
- `SOURCE_CLAIM`
- `ESTIMATE`
- `FORECAST`

Verification projection states:

- `UNVERIFIED`
- `SUPPORTED`
- `CONTRADICTED`
- `PARTIALLY_SUPPORTED`
- `DISPUTED`
- `INSUFFICIENT_EVIDENCE`
- `UNRESOLVED`

The Claim's verification status and confidence are not independently writable assessment facts. They must be derived from the exact effective ClaimAssessment and updated atomically with its current_assessment_id. When no assessment exists, status remains UNVERIFIED and confidence is null.

A claim must not be considered verified merely because an LLM labels it credible. Verification must be based on recorded evidence assessments and an explicit evaluation policy.

A Claim is a logical assertion. Its relationship to events and observations must be represented separately.

### 8.2 EventClaimLink

Associates claims with events.

Fields:

- `id`
- `event_id`
- `claim_id`
- `relationship_type`
- `created_at`
- `metadata`

A claim may be associated with more than one event when justified. This association must not imply that the claim is independently verified for every event.

### 8.3 ClaimObservation

Records where and how a claim was observed or attributed.

Fields:

- `id`
- `claim_id`
- `article_id` nullable
- `article_revision_id` nullable
- `source_id` nullable
- `evidence_id` nullable
- `attributed_to` nullable
- `observed_at`
- `publication_reference` nullable
- `content_location` nullable
- `observation_type`
- `extraction_method`
- `extraction_version`
- `metadata`

This allows the same claim to appear in multiple articles or documents without duplicating its logical identity.

The observation record must preserve the source and context of the assertion. Repeated publication of the same claim must not automatically count as independent corroboration.

### 8.4 Evidence

Represents information used to assess a claim or support an analysis.

Fields:

- `id`
- `origin_type`
- `source_id` nullable
- `article_id` nullable
- `article_revision_id` nullable
- `source_document_reference` nullable
- `evidence_text`
- `evidence_type`
- `observed_at`
- `content_location` nullable
- `language`
- `content_fingerprint` nullable
- `created_at`
- `metadata`

Evidence types may include:

- `DIRECT_QUOTE`
- `REPORTED_FACT`
- `OFFICIAL_DOCUMENT`
- `DATA_POINT`
- `SOURCE_INTERPRETATION`
- `SYSTEM_DERIVED`
- `OTHER`

Evidence may originate from an article, official document, structured dataset, approved system-derived calculation, or another approved information source.

The `origin_type` determines which origin references are expected. An evidence record must identify its origin or explicitly state that its origin is unavailable.

A system-derived evidence item must identify the input records and calculation or processing version used to produce it.

### 8.5 EvidenceLocation

Where exact provenance is available, the evidence location should be represented in a structured form.

Fields may include:

- `id`
- `evidence_id`
- `location_type`
- `page_number`
- `section_reference`
- `paragraph_reference`
- `start_offset`
- `end_offset`
- `offset_representation`
- `external_locator`
- `metadata`

Examples include:

- URL fragment.
- Document page and paragraph.
- Article revision and text offsets.
- Dataset row and field.
- Table, sheet, or cell reference.

Not every source provides precise locations. Missing location information must remain null rather than being fabricated.

### 8.6 ClaimEvidenceLink

Connects claims and evidence.

Fields:

- `id`
- `claim_id`
- `evidence_id`
- `relationship`
- `relevance_score`
- `assessment_method`
- `assessment_version`
- `created_at`

Relationships:

- `SUPPORTS`
- `CONTRADICTS`
- `CONTEXTUALIZES`
- `MENTIONS`

The same evidence may relate to multiple claims.

### 8.7 ClaimAssessment

Represents one immutable, versioned assessment of a Claim against a defined evidence set and assessment policy.

Fields:

- `id`
- `claim_id`
- `assessment_sequence`
- `assessment_outcome`
- `assessment_method`
- `methodology_version`
- `policy_version`
- `evidence_set_fingerprint`
- `rationale`
- `confidence` nullable, with documented semantics
- `model_provider` nullable
- `model_id` nullable
- `prompt_version` nullable
- `schema_version` nullable
- `assessed_at`
- `assessor_reference` nullable
- `supersedes_assessment_id` nullable
- `created_at`
- `metadata`

Assessment outcomes must use the canonical values `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTRADICTED`, `DISPUTED`, `INSUFFICIENT_EVIDENCE`, and `UNRESOLVED`. `SUPERSEDED` and `WITHDRAWN` are lifecycle states/actions recorded in AssessmentHistory, not assessment outcomes. `UNVERIFIED` is not a final assessment outcome; use `INSUFFICIENT_EVIDENCE` or `UNRESOLVED` according to whether the evidence set is inadequate or has been examined without a reliable conclusion. A missing confidence value remains null. Confidence must not be described as probability unless calibrated for that interpretation.

Each assessment is immutable. A new evaluation creates a new assessment that references the prior assessment it supersedes. The Claim.current_assessment_id projection and the new assessment must be committed atomically. The assessment must be reproducible from its recorded methodology/policy version and evidence-set fingerprint where source rights permit.

### 8.8 ClaimAssessmentEvidenceLink

Connects a ClaimAssessment to the exact Evidence records considered by that assessment.

Fields:

- `id`
- `claim_assessment_id`
- `evidence_id`
- `relationship` — supports, contradicts, contextualizes, or mentions
- `relevance` nullable
- `metadata`

The exact evidence set used by an assessment must be reconstructable. Evidence links are immutable once the assessment is finalized.

### 8.9 AssessmentHistory

Represents an append-only audit action concerning a ClaimAssessment.

Fields:

- `id`
- `claim_assessment_id`
- `action_type`
- `actor_type`
- `actor_reference` nullable
- `reason` nullable
- `idempotency_key`
- `created_at`
- `metadata`

AssessmentHistory records creation, supersession, authorized correction, or review actions. It is an audit log, not a second mutable assessment result. Its action identity must be idempotent and historical records must not be silently overwritten.

### 8.10 Evidence Independence

Source independence must not be inferred from different domain names alone.

Where known, source relationships should capture:

- Syndication.
- Shared original reporting.
- Common ownership.
- Republishing.
- Direct attribution to another source.

Evidence assessment must prevent multiple copies of one original report from being counted as independent corroboration.

Unknown source independence must remain explicitly unknown.

## 9. Analysis and Analytical Provenance

### 9.1 Analysis

Represents one analytical execution or completed analytical result.

Fields:

- `id`
- `event_id`
- `analysis_type`
- `version`
- `content`
- `structured_output`
- `confidence`
- `status`
- `model_provider`
- `model_id`
- `prompt_version`
- `schema_version`
- `analysis_policy_version`
- `input_fingerprint`
- `created_at`
- `completed_at`

Analysis types may include:

- `EVENT_SUMMARY`
- `IMPORTANCE_ASSESSMENT`
- `ECONOMIC_RELEVANCE_ASSESSMENT`
- `ECONOMIC_IMPACT_ASSESSMENT`
- `MARKET_REACTION_ASSESSMENT`
- `MARKET_IMPLICATIONS`
- `RISK_ASSESSMENT`
- `EVIDENCE_ASSESSMENT`
- `SCENARIO_ANALYSIS`

An analysis should be immutable after successful completion.

A new analysis execution must create a new record or version rather than silently overwrite a completed result. For event assessments, the combination of event identity, analysis type, and version must identify a distinct immutable result. The methodology and schema versions must be recorded independently of the model or prompt version.

The `confidence` field describes the degree of evidential support or reliability of the analytical assessment under its defined methodology. It must not be used as a substitute for importance, economic relevance, economic-effect magnitude, or forecast probability. Forecast probability, when supplied, must be a separately defined and calibrated output.

### 9.2 AnalysisEvidenceLink

Connects an analysis to evidence used during the execution.

Fields:

- `id`
- `analysis_id`
- `evidence_id`
- `usage_type`
- `created_at`

Usage types may include:

- `PRIMARY_SUPPORT`
- `CONTRADICTING_EVIDENCE`
- `CONTEXT`
- `BACKGROUND`

### 9.3 AnalysisInput

Records other inputs used by an analysis.

Fields:

- `id`
- `analysis_id`
- `input_type`
- `input_reference`
- `input_fingerprint`
- `input_version`
- `created_at`

Input types may include:

- `ARTICLE_REVISION`
- `EVENT_VERSION`
- `CLAIM`
- `EVIDENCE`
- `MARKET_OBSERVATION`
- `HISTORICAL_CONTEXT`
- `EXTERNAL_DATASET`
- `OTHER`

Polymorphic references must use an explicit type discriminator and validated identifier format.

Where practical, frequently used input types should use dedicated relational link entities rather than relying exclusively on a generic reference.

The application layer must validate that every referenced input exists and is eligible for use.

### 9.4 Assessment Output Classification

Analytical content must distinguish:

- Observed facts and measurements.
- Source-attributed claims and reported effects.
- AI-generated interpretation.
- Forecasts and scenarios.
- Explicitly unknown, unavailable, or not-established information.

A free-text analysis field alone is insufficient for important structured conclusions. Every assessment type must use a versioned structured-output schema and preserve material claims, uncertainty, methodology version, and supporting or contradicting evidence references.

The three event assessments use separate structured output contracts:

**Importance assessment (`IMPORTANCE_ASSESSMENT`)** should preserve the importance dimensions considered, qualitative rank or optional numeric score, rationale, evidence references, uncertainty, and methodology/schema versions. It must not derive its result by adding the economic relevance or impact outputs.

**Economic relevance assessment (`ECONOMIC_RELEVANCE_ASSESSMENT`)** should preserve a relevance classification, identified direct/indirect/contextual transmission pathways, affected entities and geographies, supporting evidence references, and uncertainty. Suggested classifications are `DIRECT`, `INDIRECT`, `CONTEXTUAL`, `NO_MATERIAL_LINK_ESTABLISHED`, and `UNKNOWN`. These are descriptive classifications, not numeric magnitudes.

**Economic impact assessment (`ECONOMIC_IMPACT_ASSESSMENT`)** should preserve one or more channel-level impact results. Each result should identify the channel, affected entity or geography, transmission mechanism, direction (`POSITIVE`, `NEGATIVE`, `MIXED`, `NEUTRAL`, or `UNCLEAR`), magnitude or defensible range where supported, time horizon/duration, evidence status, evidence references, and uncertainty. The result must not force distinct channels into one aggregate value.

Evidence status for an economic effect must distinguish:

1. `OBSERVED_ECONOMIC_EFFECT` — supported by an identified economic or market observation.
2. `SOURCE_REPORTED_EFFECT` — reported by a source but not independently verified by integrated data.
3. `INFERRED_POTENTIAL_EFFECT` — an analytical inference or forward-looking consequence.
4. `UNKNOWN` — insufficient information to characterize the effect.

The schema may also preserve separate forecast probability when a validated forecasting methodology supports it. Assessment confidence, forecast probability, effect direction, and magnitude must remain distinct values.

### 9.5 Market Reaction and Market Data Evidence

A market reaction is an observed or reported market response, not the same concept as economic relevance or the full economic impact of an event.

The model must distinguish at least:

1. `OBSERVED_MARKET_REACTION` — supported by an identified market data source and observation.
2. `SOURCE_REPORTED_REACTION` — reported by a publication but not independently confirmed by integrated market data.
3. `INFERRED_MARKET_IMPLICATION` — an analytical expectation or interpretation without direct observed market data.
4. `UNKNOWN` — insufficient information.

Where market data is integrated, a `MarketObservation` entity may record:

- `id`
- `event_id` nullable — optional contextual association; an observation may exist independently of any event.
- `instrument_reference`
- `market`
- `observation_type`
- `value`
- `unit`
- `observed_at`
- `baseline_reference`
- `data_source`
- `source_reference`
- `metadata`

Market data integration and its source rights require a separate architecture decision.

A market observation must preserve its measurement time, source, unit, and baseline context. It records a market measurement; it does not establish that an event caused the movement. It may be ingested and retained independently of an event; any association with an event must be an explicit, provenance-bearing relationship or analysis input rather than a mandatory ownership field. Any causal interpretation must be a separate analysis with its own evidence, methodology, and uncertainty.

## 10. Event History

### 10.1 EventHistory

Preserves meaningful changes to an event.

Fields:

- `id`
- `event_id`
- `version`
- `change_type`
- `previous_state`
- `new_state`
- `change_reason`
- `processing_run_id` nullable
- `actor_type`
- `actor_reference` nullable
- `event_match_case_id` nullable
- `source_event_match_decision_id` nullable
- `event_identity_operation_id` nullable — exact identity operation responsible for this history change
- `event_creation_policy_version` nullable
- `idempotency_key` nullable
- `metadata`
- `created_at`

For an Event created from a NEW_EVENT_CANDIDATE decision, the initial `CREATED` history record must preserve the exact EventMatchCase, source NEW_EVENT_CANDIDATE decision, EventCreationPolicy version, actor/authorization reference, and idempotency key. These references must be written atomically with Event creation.

Possible change types:

- `CREATED`
- `TITLE_UPDATED`
- `DESCRIPTION_UPDATED`
- `STATUS_CHANGED`
- `IMPORTANCE_ASSESSED`
- `ECONOMIC_RELEVANCE_ASSESSED`
- `ECONOMIC_IMPACT_ASSESSED`
- `ENTITY_ADDED`
- `ARTICLE_ASSOCIATED`
- `ARTICLE_DISASSOCIATED`
- `ANALYSIS_COMPLETED`
- `RESOLVED`
- `REOPENED`
- `MERGED`
- `SPLIT`

History should be append-only from the application perspective. A non-null EventHistory idempotency_key must be unique. For candidate-driven creation, the source decision must belong to event_match_case_id and have outcome NEW_EVENT_CANDIDATE; retries must reuse the same Event identifier and creation-history idempotency key.

### 10.2 Lifecycle Transitions

The canonical states and allowed transitions are defined below and align with Section 9 of Document 01.

| Current State | Allowed Next State | Guard |
|---|---|---|
| `DETECTED` | `ENRICHING` | Initial triage passed and accountable processing exists. |
| `ENRICHING` | `ACTIVE` | Minimum identity, attribution, and evidence/enrichment requirements are met. |
| `ENRICHING` | `RESOLVED` | A sufficiently evidenced short-lived development is already concluded. |
| `ACTIVE` | `MONITORING` | No material new development is currently expected but monitoring remains justified. |
| `ACTIVE` | `RESOLVED` | Domain-specific resolution criteria and supporting evidence are recorded. |
| `MONITORING` | `ACTIVE` | A material new development requires active monitoring. |
| `MONITORING` | `RESOLVED` | Domain-specific resolution criteria are met. |
| `MONITORING` | `ARCHIVED` | Retention/archival policy permits it and no unresolved high-priority work remains. |
| `RESOLVED` | `MONITORING` | New material or contradictory evidence justifies authorized reopening. |
| `RESOLVED` | `ARCHIVED` | Retention and archival policy permits it. |
| `ARCHIVED` | `MONITORING` | Authorized restoration identifies new material evidence or continuing monitoring need. |

Any unlisted transition is rejected. A same-state request is an idempotent no-op. Reopening/restoration requires actor, reason, supporting evidence/context, and lifecycle-policy version. Archival does not delete the Event or its history. The policy must not create a backward transition to `DETECTED` to conceal a later correction; identity corrections use the explicit event identity operation workflow.

The domain/application layer validates the guard before persistence. A successful transition updates the current Event projection and appends an EventHistory record in the same transaction. The history must preserve previous/new state, actor and authorization reference, reason, lifecycle-policy version, and correlation/idempotency context.

A transient update notification must not be modeled as a persistent lifecycle state.

### 10.3 Event Versioning

Event history must make it possible to reconstruct or inspect material prior states.

The implementation must define whether `previous_state` and `new_state` are full snapshots or structured change sets.

If snapshots are used, their schema must be versioned. If change sets are used, the reconstruction rules must be documented and tested.

## 11. Reports and Publication

### 11.1 Report

Represents one generated report version.

Fields:

- `id`
- `event_id` nullable
- `version`
- `report_type`
- `report_scope`
- `title`
- `content`
- `content_format`
- `language`
- `generation_status`
- `generated_at`
- `created_at`
- `supersedes_report_id` nullable

Report types may include:

- `INITIAL_EVENT_REPORT`
- `EVENT_UPDATE`
- `EVENT_CLOSURE_REPORT`
- `PERIODIC_SUMMARY`

Generation status may include:

- `DRAFT`
- `GENERATED`
- `FAILED`
- `SUPERSEDED`

Publication status must not be stored as an independently mutable field on Report and must not be inferred from PublicationDecision. PublicationDecision records eligibility; PublicationRecord records external publication operations. The effective publication state for a target is derived from the history of successful PublicationRecord operations.

Constraints:

- `(event_id, version)` must be unique for event-specific reports.
- Reports must preserve their input and evidence references.
- A material update creates a new report version.
- Published reports must not be silently modified.
- Reports not associated with one event must be supported through explicit report scope and event relationships.


### 11.2 ReportEventLink

Connects an immutable report version to one or more events. Its rows are immutable provenance links: event identity operations must not update or repoint them. Current event identity is resolved separately through the event-identity history/operation graph; report-impact assessment records whether a new report version or other separately authorized remediation is required.

Connects a report to one or more events.

Fields:

- `id`
- `report_id`
- `event_id`
- `relationship_type`
- `is_primary`
- `created_at`

This supports periodic summaries, regional briefings, and other reports that cover multiple events.

`Report.event_id` may be retained as an optional primary-event convenience reference for event-specific reports. `ReportEventLink` is the authoritative relationship for reports covering multiple events.

### 11.3 ReportEvidenceLink

Connects reports to evidence.

Fields:

- `id`
- `report_id`
- `evidence_id`
- `section_reference`
- `usage_type`
- `created_at`

### 11.4 ReportArticleLink

Connects a report version to the exact source ArticleRevision used to generate or support it. The parent Article is resolved through ArticleRevision.article_id; a report must not rely only on a mutable current Article projection.

Fields:

- `id`
- `report_id`
- `article_revision_id`
- `reference_type`
- `created_at`

Constraints:

- The referenced ArticleRevision must exist and must be permitted for the report's use under the applicable content-rights policy.
- Replacing an Article's current projection must not change the revision referenced by an existing report.
- The same report version must not contain duplicate links to the same ArticleRevision for the same reference_type.

### 11.5 ReportAnalysisLink

Connects reports to analyses.

Fields:

- `id`
- `report_id`
- `analysis_id`
- `section_reference`
- `created_at`

This ensures that a report can be traced to the analytical results from which it was generated.

### 11.6 PublicationDecision

Records a publication policy decision.

Fields:

- `id`
- `report_id`
- `decision`
- `reason_codes`
- `explanation`
- `caveats` nullable
- `policy_version`
- `actor_type`
- `actor_reference`
- `authorization_reference`
- `decided_at`
- `supersedes_decision_id` nullable
- `metadata`

Decision values:

- `PUBLISH`
- `PUBLISH_WITH_CAVEATS`
- `HOLD_FOR_REVIEW`
- `REJECT`

A decision is an immutable record. A new decision must be created when the publication outcome changes or a review produces a material outcome.

The system must preserve which policy version produced the decision. The current effective decision must be derived through an explicit supersession rule. Historical decisions must remain queryable.

The effective-decision rule must yield at most one effective PublicationDecision for the exact immutable report version. The first decision has no predecessor; each successor must name the current effective decision as its predecessor. Only one direct successor may reference a predecessor for the same report version. The append operation validates the expected aggregate version and predecessor, then appends the immutable decision and advances the effective pointer in one transaction. A stale or concurrent successor receives CONFLICT; timestamps or storage order are never tie-breakers. This algorithm is specified in GENI-FOUNDATION-017 §8.

Every decision must preserve `actor_type` and `actor_reference` from the authenticated command context, plus an immutable `authorization_reference` resolvable by the security/audit layer. These are typed provenance references, not caller-supplied role strings or free text. The actor may be a human reviewer or an authorized application/policy service. A missing or unverifiable authorization reference must fail closed; the security layer records actor/service, action, resource, authorization context, timestamp and result. This follows the common command metadata contract in GENI-IMPL-015 §3.2 and the audit requirements in Document 08 §5.

A `PUBLISH` or `PUBLISH_WITH_CAVEATS` decision authorizes a publication operation only while it remains effective and all other authorization, rights, and target requirements are satisfied. It does not prove that publication occurred.

For `PUBLISH_WITH_CAVEATS`, the caveats must be explicit and must be included in the published representation.

A `HOLD_FOR_REVIEW` decision must create or reference an operational review task. It must not silently remain unprocessed. An authorized review outcome must produce a new effective publication decision when it changes eligibility; the original decision and review record must remain intact.

### 11.7 ReviewRecord

Represents an operational human-review task for a typed domain subject. ReviewRecord is a task and audit record; it is not itself an authoritative event-matching or publication decision.

Fields:

- `id`
- `review_type`
- `subject_type`
- `subject_reference`
- `related_decision_reference` nullable
- `report_id` nullable
- `publication_decision_id` nullable
- `review_status`
- `priority` — required; value must come from the versioned review-priority policy defined by GENI-ADR-014.
- `assignee_reference` nullable
- `reviewer_reference` nullable — reviewer who completed the task, when applicable
- `assigned_at` nullable — current assignment projection
- `due_at` nullable
- `review_reason`
- `review_notes`
- `priority_policy_version` — required when priority is assigned or recalculated.
- `review_outcome` nullable
- `created_at`
- `completed_at`
- `metadata`

Review states may include:

- `PENDING`
- `IN_PROGRESS`
- `COMPLETED`
- `CANCELLED`

The initial state, allowed transitions, terminal-state semantics, action-to-status projection, and REOPENED successor-segment behavior are defined normatively in GENI-FOUNDATION-017 §10. ReviewAction remains append-only audit evidence. Reopening creates a new ReviewRecord ID with predecessor_review_id and a new CREATED action; the completed/cancelled predecessor remains immutable. Material review actions remain disabled until GENI-ADR-014, reviewer identity/authorization, DTO schemas, and integration tests are approved.

Review types identify the subject and required follow-up. The canonical six subject families and successor routes are:

| Review Type | Exact Subject | Material Successor |
|---|---|---|
| `ARTICLE_DEDUPLICATION` | DuplicateCandidate plus the DuplicateDecision under review | New DuplicateDecision for the same candidate through Article Deduplication Workflow. |
| `EVENT_MATCHING` | EventMatchCase plus the EventMatchDecision under review | New EventMatchDecision through Event Resolution Workflow; EventService applies only an effective MATCH. |
| `CLAIM_ASSESSMENT` | Claim plus the exact ClaimAssessment | New ClaimAssessment and exact evidence links; append AssessmentHistory and atomically refresh the Claim projection through EvidenceService. |
| `REPORT_VERSION` | Exact immutable Report version plus the exact effective PublicationDecision under review | New immutable corrected Report version and, when eligibility changes, a successor PublicationDecision; external replacement remains a separate PublicationService operation. |
| `PUBLICATION_OPERATION` | Exact PublicationRecord and operation state | Reconciliation or separately authorized successor operation through PublicationService; prior attempts remain immutable. |
| `CONTENT_RIGHTS` | Exact RightsAssessment or SourceRightsProfile version | New RightsAssessment/profile revision and applicable restriction/deletion workflow through ContentRightsService. |

Both `review_type` and `subject_type` must use the same canonical family value and resolve to exactly one typed subject. For `REPORT_VERSION`, the subject is the exact immutable Report version and the related decision is its exact effective PublicationDecision. For `PUBLICATION_OPERATION`, the subject is the exact PublicationRecord and its current operation/reconciliation state. The canonical vocabulary, reference cardinality, priority scale, triggers, and authorization matrix are governed by ADR-014. The target first-slice review scope is exactly `ARTICLE_DEDUPLICATION`, `EVENT_MATCHING`, and `REPORT_VERSION`. `REPORT_VERSION` means publication-eligibility review for an exact immutable Report version and its exact effective `PublicationDecision`; it is not review of an external publication operation. This is target scope, not current enablement: no ReviewService material action may be enabled until the `ReviewRepository` and `ReviewContextLinkRepository` contracts, field-level command/query schemas, ReviewRecord/ReviewAction transition and projection rules, reviewer authorization rules, and the applicable GENI-ADR-014 approval are complete and verified by integration tests. `CLAIM_ASSESSMENT`, `PUBLICATION_OPERATION`, and `CONTENT_RIGHTS` remain deferred and disabled.

Constraints and behavior:

- Exactly one typed subject must be identified by `subject_type` and `subject_reference`; the reference must be validated by the application layer where a database foreign key cannot express the polymorphic relationship.
- For article-deduplication review, the subject must identify a DuplicateCandidate and the related decision must identify the DuplicateDecision under review; a material outcome creates a successor DuplicateDecision for that same candidate.
- For `REPORT_VERSION` review, the subject and related-decision reference must resolve to the exact Report version and its exact effective PublicationDecision. `PUBLICATION_OPERATION` review instead resolves to an existing PublicationRecord and its current operation/reconciliation state.
- For event-matching review, the subject must identify an EventMatchCase and the related decision must identify the EventMatchDecision under review.
- Review completion records the reviewer, time, and outcome. It does not mutate the related decision.
- An article-deduplication review outcome that changes the effective result creates a new DuplicateDecision referencing the previous effective decision for the same candidate.
- An event-matching review outcome that changes the effective result creates a new EventMatchDecision referencing the previous effective decision.
- A publication review outcome that changes publication eligibility creates a new PublicationDecision.
- A claim-assessment review must create a successor ClaimAssessment with exact evidence links, append AssessmentHistory, and atomically update Claim.current_assessment_id and its verification projections.
- A report-version review must create a new immutable Report version; any new publication eligibility must be decided by PublicationPolicy, while external replacement/withdrawal remains a separate PublicationService operation.
- A publication-operation review must reconcile an unknown external outcome before deciding whether a new logical operation is needed; it must never edit an earlier PublicationRecord or PublicationAttempt.
- A content-rights review must create a new RightsAssessment or SourceRightsProfile revision and trigger only the authorized content restriction/retention/deletion workflow; it does not retroactively rewrite completed deliveries.
- Review history must not be silently overwritten. Reassignment and status changes must be auditable.
- Reviewer identity and authorization must be managed by the application's security layer.
- ReviewRecord is the current task/projection; all lifecycle actions, assignment changes, reviewer notes, escalation, completion, and cancellation must be preserved in append-only ReviewAction records.
- Current status, priority, and assignee fields on ReviewRecord must be rebuildable from its ReviewAction history. Priority changes must be recorded as actions with the applicable priority-policy version. Final reviewer outcome and completion actor/time must be represented by an immutable completion action and must not be silently overwritten.

### 11.7.1 ReviewContextLink

Connects a ReviewRecord to the exact evidence or domain records needed to understand the review without copying restricted source content into the task.

Fields:

- `id`
- `review_record_id`
- `context_type`
- `context_reference`
- `context_role`
- `created_at`
- `metadata`

`context_type` must identify a supported typed reference such as `EVIDENCE`, `CLAIM_ASSESSMENT`, `DUPLICATE_DECISION`, `EVENT_MATCH_DECISION`, `REPORT_VERSION`, `PUBLICATION_OPERATION`, `RIGHTS_ASSESSMENT`, or `SOURCE_RIGHTS_PROFILE_VERSION`. The application layer must validate that the reference exists, belongs to the review subject where required, and is accessible to the assigned reviewer. Context links are immutable once the review is completed; corrections require a successor task or an append-only action.

### 11.7.2 ReviewAction

Represents one immutable action in the lifecycle of a ReviewRecord.

Fields:

- `id`
- `review_record_id`
- `action_sequence`
- `action_type`
- `actor_type`
- `actor_reference`
- `actor_role` nullable
- `previous_status` nullable
- `new_status` nullable
- `previous_priority` nullable
- `new_priority` nullable
- `priority_policy_version` nullable — required for a priority change.
- `assignee_reference` nullable
- `review_outcome` nullable
- `reason_or_notes` nullable
- `authorization_reference` nullable
- `idempotency_key`
- `created_at`
- `metadata`

Action types may include `CREATED`, `ASSIGNED`, `REASSIGNED`, `PRIORITY_CHANGED`, `STARTED`, `NOTE_ADDED`, `ESCALATED`, `COMPLETED`, `CANCELLED`, and `REOPENED`.

Constraints:

- ReviewAction records are append-only and immutable.
- `(review_record_id, action_sequence)` must be unique and assigned atomically.
- A non-null idempotency_key must be unique within the ReviewRecord.
- Actor identity and role must be validated by the authorization layer at action time.
- `COMPLETED` must record the final reviewer outcome and actor; a material outcome must create the required successor DuplicateDecision, EventMatchDecision, or PublicationDecision through the appropriate domain workflow.
- `REOPENED` creates a new task lifecycle segment; it must not delete or rewrite the previous completion action.
- ReviewAction must reference exactly one existing ReviewRecord.

### 11.8 PublicationRecord

Represents one logical operation against a publication target. It is distinct from a PublicationDecision and from a DeliveryRecord.

Fields:

- `id`
- `report_id`
- `publication_decision_id` nullable for withdrawal operations
- `publication_target_reference`
- `publication_key`
- `operation_sequence`
- `operation_type`
- `target_publication_id` nullable
- `status`
- `idempotency_key`
- `external_reference` nullable
- `external_url` nullable
- `authorization_reference` nullable
- `reason` nullable
- `requested_by` nullable
- `requested_at`
- `started_at` nullable
- `completed_at` nullable
- `error_category` nullable
- `error_summary` nullable
- `created_at`
- `metadata`

Operation types:

- `PUBLISH`
- `REPLACE`
- `WITHDRAW`

Operation statuses:

- `PENDING`
- `IN_PROGRESS`
- `SUCCEEDED`
- `FAILED`
- `CANCELLED`
- `RECONCILIATION_REQUIRED`

The status represents the current state of the logical operation. The expected transitions are `PENDING` to `IN_PROGRESS`, followed by a confirmed terminal result or `RECONCILIATION_REQUIRED`. After reconciliation confirms that the external effect did not occur, a retry may resume the same logical operation under its original idempotency key and with a new attempt. A confirmed successful operation must not be reset and executed again.

Operation semantics and constraints:

- A publication key identifies one logical publication slot within a target. A target may host many independent publication keys.
- `PUBLISH` requires an effective `PUBLISH` or `PUBLISH_WITH_CAVEATS` decision and must not reference a previous publication as its target. It may establish a new publication chain only when that target/key has no currently effective publication.
- `REPLACE` requires an effective publication decision for the new report version and a reference to the currently effective earlier publication it intends to supersede. The target and publication key must match the referenced operation.
- `WITHDRAW` requires a reference to the currently effective publication for the same target and publication key and explicit authorization/reason information. Its `report_id` must match the referenced publication's report. Its publication-decision reference may be null because withdrawal is an authorized lifecycle operation rather than permission to publish content.
- The target publication and new operation must refer to the same configured publication target.
- The operation sequence must be assigned atomically and increase within the target/publication-key chain.
- A stable idempotency key must be unique within the target and publication-key scope.
- The same logical operation must reuse its idempotency key on retry.
- Only one unresolved side-effecting operation may exist for a target/publication-key chain at a time; unrelated keys at the same target may proceed independently.
- A successful replacement supersedes the earlier publication. A failed or uncertain replacement leaves the earlier confirmed publication effective.
- A successful withdrawal records that the target has withdrawn the referenced publication. A failed or uncertain withdrawal must not be treated as complete.
- A timeout or transport failure with an unknown external outcome must produce `RECONCILIATION_REQUIRED`; the operation must be reconciled before another side-effecting attempt.
- The current effective publication for a target/publication-key pair is derived from its ordered chain of successful operations: PUBLISH establishes the publication, REPLACE supersedes the referenced publication and establishes the replacement, and WITHDRAW removes the referenced publication from the effective state. Failed, cancelled, or unresolved operations must not silently replace the last confirmed effective state.
- Publication operation history must remain append-oriented and auditable. Corrections must not overwrite previous report content or publication records.

### 11.9 PublicationAttempt

Represents one external execution attempt for a PublicationRecord.

Fields:

- `id`
- `publication_record_id`
- `attempt_number`
- `attempt_type`
- `started_at`
- `completed_at` nullable
- `outcome`
- `external_reference` nullable
- `error_category` nullable
- `error_summary` nullable
- `reconciliation_reference` nullable
- `metadata`

Attempt types:

- `EXECUTE`
- `RECONCILE`

Attempt outcomes:

- `CONFIRMED_SUCCESS`
- `CONFIRMED_FAILURE`
- `OUTCOME_UNKNOWN`
- `RECONCILED_SUCCESS`
- `RECONCILED_NOT_APPLIED`

Each attempt must be separately traceable. An `OUTCOME_UNKNOWN` result must place the PublicationRecord in `RECONCILIATION_REQUIRED`. Reconciliation must determine whether the external effect occurred before the operation is retried or finalized.

The outcome-to-operation mapping is defined normatively in GENI-FOUNDATION-017 §9 and applies to PublicationRecord and DeliveryRecord. EXECUTE is allowed only while IN_PROGRESS; CONFIRMED_SUCCESS produces SUCCEEDED, CONFIRMED_FAILURE produces FAILED, and OUTCOME_UNKNOWN produces RECONCILIATION_REQUIRED. RECONCILE is allowed only while RECONCILIATION_REQUIRED; RECONCILED_SUCCESS produces SUCCEEDED, while RECONCILED_NOT_APPLIED returns to PENDING only when the same operation remains authorized and retry policy explicitly permits it, otherwise FAILED. Attempt records are immutable. Unknown outcomes prohibit another side-effecting attempt until reconciliation.

## 12. Delivery Records

### 12.1 DeliveryRecord

Represents a logical delivery operation for a report or a notification related to a report.

Fields:

- `id`
- `report_id` — exact immutable report version
- `recipient_reference` — exact recipient or recipient-group identity addressed by the operation
- `publication_record_id` nullable
- `delivery_mode`
- `channel`
- `destination_reference`
- `distribution_authorization_decision_id` — required exact effective authorization reference
- `content_scope_fingerprint` — required SHA-256 fingerprint of the versioned canonical ContentScopeManifest; must equal the referenced decision's `authorized_content_scope_fingerprint`.
- `outbound_payload_sha256` — required SHA-256 digest of the exact serialized outbound request bytes immediately before dispatch; distinct from the content-scope fingerprint.
- `idempotency_key`
- `status`
- `external_reference`
- `attempt_count`
- `scheduled_at`
- `last_attempt_at`
- `delivered_at`
- `error_category`
- `error_summary`
- `created_at`
- `updated_at`
- `metadata`

Delivery modes:

- `REPORT_CONTENT`
- `PUBLICATION_LINK`
- `NOTIFICATION`

Possible statuses:

- `PENDING`
- `IN_PROGRESS`
- `DELIVERED`
- `FAILED`
- `CANCELLED`
- `RECONCILIATION_REQUIRED`

Constraints:

- An idempotency key must be present for externally visible delivery operations.
- The idempotency key must be unique within its relevant destination and operation scope.
- Retries must not create duplicate external deliveries when the destination supports idempotency.
- Delivery attempts must remain traceable.
- Every outbound DeliveryRecord must reference exactly one `DistributionAuthorizationDecision` whose outcome is `ALLOW`, which is effective and unexpired at dispatch time.
- The decision must match the exact report version, recipient, destination, delivery mode, channel, and authorized content scope. It must not be reused for a different recipient, destination, report version, or content scope.
- The DeliveryRecord.content_scope_fingerprint must equal the authorized_content_scope_fingerprint of the referenced DistributionAuthorizationDecision. Dispatch must validate the exact manifest item set and each immutable item-content digest against that manifest, reject any payload addition, omission, substitution, or transformation drift, and record the serialized request digest separately as outbound_payload_sha256.
- A `PUBLICATION_LINK` delivery must reference a PublicationRecord whose publication operation is confirmed successful and still effective for that target.
- `REPORT_CONTENT` or `NOTIFICATION` delivery may reference a PublicationRecord when relevant, but must be independently authorized by the applicable distribution policy.
- Where source-derived content is distributed, the DistributionAuthorizationDecision must reference the applicable allowed `CUSTOMER_DISTRIBUTION` RightsAssessment; publication approval or source permission alone is insufficient.
- Authorization revocation/expiry blocks future dispatch. Completed deliveries remain immutable history and must be addressed through a separate correction/withdrawal workflow.
- Delivery status must not be confused with publication approval or publication success.
- A delivery failure must not reverse or invalidate a confirmed publication.
- The logical delivery operation must be distinct from individual delivery attempts.

### 12.2 DeliveryAttempt

Represents one delivery attempt.

Fields:

- `id`
- `delivery_record_id`
- `attempt_number`
- `started_at`
- `completed_at`
- `outcome`
- `external_reference`
- `error_category`
- `error_summary`
- `metadata`

Each attempt must be separately traceable.

A retry must reuse the logical delivery operation and its idempotency key unless the operation itself has been explicitly superseded.

DeliveryRecord uses the common external-operation transition and attempt-outcome mapping defined in GENI-FOUNDATION-017 §9. Its successful terminal status is DELIVERED rather than SUCCEEDED. DeliveryAttempt uses the same closed attempt vocabulary as PublicationAttempt: CONFIRMED_SUCCESS, CONFIRMED_FAILURE, OUTCOME_UNKNOWN, RECONCILED_SUCCESS, and RECONCILED_NOT_APPLIED, with EXECUTE and RECONCILE attempt types. Unknown outcomes require reconciliation before retry. Delivery state remains independent of publication state and authorization decisions.

### 12.3 DistributionAuthorizationDecision

Represents an immutable policy outcome authorizing or blocking one precisely scoped recipient-delivery operation. It is independent from PublicationDecision and source-content RightsAssessment.

Fields:

- `id`
- `report_id` — exact immutable report version
- `recipient_reference`
- `destination_reference`
- `delivery_mode`
- `channel`
- `authorized_content_scope`
- `decision` — `ALLOW`, `DENY`, or `REQUIRES_REVIEW`
- `distribution_policy_version`
- `authorized_content_scope_fingerprint` — required SHA-256 digest of the versioned canonical ContentScopeManifest
- `rights_assessment_set_fingerprint` — required when source-derived content is included; SHA-256 digest of the complete immutable RightsAssessment reference set represented by DistributionAuthorizationRightsLink records
- `idempotency_key` — required and unique within the exact report/recipient/destination authorization scope
- `decided_by_type`
- `decided_by_reference`
- `reason_codes`
- `decided_at`
- `valid_until` nullable
- `supersedes_decision_id` nullable
- `metadata`

Constraints:

- The decision is immutable; correction or revocation is represented by a successor decision (normally a DENY outcome) that supersedes the prior decision. The prior decision remains queryable and must not be edited.
- `ALLOW` is valid only for the exact report version, recipient, destination, delivery mode, channel, and content scope it names.
- The applicable content-rights assessment must authorize customer distribution of the relevant source-derived content; it does not replace recipient-specific authorization.
- Dispatch must re-check that the referenced decision remains effective, unexpired, and allowed; every linked RightsAssessment remains effective for its exact source-derived content scope; and every upstream permission dependency recorded in the DerivedArtifact provenance remains effective. Revocation, expiry, or material policy change invalidates the affected derived scope until ContentRightsService re-evaluates the complete dependency chain and issues a current allowed assessment. The prior decision remains immutable and cannot be revived.
- An authorization decision is not evidence that delivery occurred.
- An `ALLOW` decision for a composite report must link every source-derived content scope in its authorized payload to an exact `CUSTOMER_DISTRIBUTION` RightsAssessment with outcome `ALLOWED`. A missing, unknown, expired, revoked, denied, or review-required assessment prevents authorization of the affected scope. A reduced scope is permitted only when the restricted content is actually excluded and the reduced content-scope fingerprint is recorded.
- The `authorized_content_scope_fingerprint` must be reproducible from the canonical ContentScopeManifest using RFC 8785 JCS, UTF-8, and SHA-256; set-valued arrays are sorted by stable identifiers before serialization. Item digests cover the exact immutable artifact bytes (UTF-8 bytes for text and exact stored bytes for binary media); any content transformation or transcoding creates a new immutable artifact version and digest.
- The `rights_assessment_set_fingerprint` must be reproducible from the complete sorted immutable RightsAssessment reference set using the same canonicalization and hashing rules. The decision and all links are committed atomically.
- The `DeliveryRecord.content_scope_fingerprint` must equal the authorized manifest fingerprint. `outbound_payload_sha256` records the exact serialized request bytes and must not be confused with the manifest fingerprint.

### 12.3.1 DistributionAuthorizationRightsLink

Connects one DistributionAuthorizationDecision to one exact RightsAssessment and the precise source-derived content scope that assessment authorizes.

Fields:

- `id`
- `distribution_authorization_decision_id`
- `rights_assessment_id`
- `content_scope_type` — typed scope reference such as a ReportArticleLink or DerivedArtifact
- `content_scope_reference` — exact scope-item identifier
- `created_at`
- `metadata`

Constraints:

- The referenced RightsAssessment must identify `CUSTOMER_DISTRIBUTION`, have outcome `ALLOWED`, and apply to the exact source/content scope represented by the link.
- Every source-derived scope included in the authorization decision must be covered by one or more exact links; a link for one source or artifact cannot authorize another.
- Links are immutable. A changed source-rights result or authorized content scope creates a successor DistributionAuthorizationDecision and a new complete link set.
- The link set and its deterministic fingerprint are persisted in the same transaction as the parent decision.

### 12.4 Delivery State Consistency

External delivery operations cannot generally be included in a database transaction.

The system must use explicit state transitions, idempotency keys, and recovery handling.

If an external destination supports idempotency, the same key must be reused for retries of the same logical operation.

If the destination does not support idempotency, the system must document the duplicate-delivery risk and apply a reconciliation strategy.

Publication and delivery are independent operations. A delivery may reference a successful publication, but must not create, replace, or withdraw a publication.

A delivery containing a publication link must not be created until the referenced publication is confirmed successful and effective. Direct delivery of report content remains subject to a separate distribution authorization.

## 13. Processing and Operational Data

### 13.1 ProcessingRun

Represents one workflow execution.

Fields:

- `id`
- `run_type`
- `target_type`
- `target_id`
- `status`
- `idempotency_key`
- `input_fingerprint`
- `started_at`
- `heartbeat_at`
- `lease_expires_at` — denormalized projection of the current ExecutionLease; not the ownership authority
- `current_lease_id` nullable
- `lease_fencing_token` nullable — latest fencing token observed for this run
- `next_retry_at`
- `completed_at`
- `error_category`
- `error_summary`
- `metadata`

Possible statuses:

- `PENDING`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`
- `PARTIALLY_COMPLETED`

The ProcessingRun lifecycle is defined normatively in GENI-FOUNDATION-017 §4. A new run starts PENDING. COMPLETED, FAILED, and CANCELLED are terminal; retrying a terminal run creates a successor run with parent_run_id. PARTIALLY_COMPLETED is recoverable and may resume the same run only under explicit recovery authorization, current fencing, and idempotency checks. Run status is a deterministic projection of the versioned required step set. An empty step set remains PENDING. Run/step state transitions and their append-only history must commit atomically.

`target_type` and `target_id` form a polymorphic reference and cannot be protected by an ordinary foreign key to multiple target tables.

The application layer must validate the target reference. Where stronger relational integrity is required, target-specific link tables should be introduced.

A running workflow must have a recoverable execution lease or equivalent ownership mechanism.

A stale execution must not be resumed concurrently with a still-active worker.

### 13.2 ProcessingStep

Represents an individual step within a processing run.

Fields:

- `id`
- `processing_run_id`
- `step_name`
- `status`
- `step_version`
- `input_fingerprint`
- `output_reference`
- `started_at`
- `heartbeat_at`
- `lease_expires_at` — denormalized projection of the current ExecutionLease; not the ownership authority
- `current_lease_id` nullable
- `lease_fencing_token` nullable — latest fencing token observed for this step
- `next_retry_at`
- `completed_at`
- `attempt_number`
- `error_category`
- `error_summary`
- `metadata`

The ProcessingStep status vocabulary and transitions are defined normatively in GENI-FOUNDATION-017 §5. A new step starts PENDING. FAILED may return to READY only under explicit retry authorization and a new immutable attempt; BLOCKED may return to READY only after dependencies/preconditions are revalidated. SUCCEEDED, SKIPPED, and CANCELLED are terminal for the logical step. A blocked step is not a failed attempt.

A step must be safely repeatable or explicitly marked as non-repeatable.

Completed step outputs should be reusable when the input fingerprint and relevant processing versions have not changed.

A step with an expired lease may be considered for recovery only after the application layer verifies that the previous execution is no longer active.

Each execution attempt must be represented by an immutable ProcessingStepAttempt record containing at minimum: attempt ID, processing step ID, attempt number, input fingerprint, worker identity, fencing token, start/completion timestamps, outcome, safe error category, output reference, and idempotency reference. The attempt number is allocated atomically. A retry appends a new attempt; it never overwrites the prior attempt. The current ProcessingStep status is a projection over the logical step and its latest valid attempt, subject to GENI-FOUNDATION-017.

**Event Identity reconciliation work-item mapping:** An Event Identity Operation is represented by a ProcessingRun whose target_type is EVENT_IDENTITY_OPERATION and whose target_id is the exact operation ID. Each independently recoverable downstream unit is a ProcessingStep in that run; no in-memory queue entry is authoritative. The supported step_name vocabulary for this workflow is EVENT_IDENTITY_CASE_REEVALUATION, EVENT_IDENTITY_ANALYSIS_RECONCILIATION, EVENT_IDENTITY_REPORT_IMPACT_DISCOVERY, EVENT_IDENTITY_REPORT_IMPACT_ASSESSMENT, and EVENT_IDENTITY_FINALIZATION. A step's metadata must contain typed, validated operation_id, work_kind, target_type, target_id (nullable only for a bounded discovery/finalization cursor), target_version where applicable, and the exact policy/version references needed to repeat the work. The step input_fingerprint is a server-derived canonical digest over operation ID, step kind, typed target, target version, cursor/partition identity, and relevant policy/input fingerprints; callers cannot supply it. output_reference must identify the durable result or aggregate reference. ProcessingStepAttempt records every worker attempt immutably, while ExecutionLease and its fencing token establish exclusive ownership. Report-impact status and its append-only history remain authoritative in EventIdentityOperationReportImpact and EventIdentityOperationReportImpactHistory; the ProcessingStep tracks orchestration progress only. A completed step is reusable only for the same fingerprint. Changed target state or policy requires a successor logical step or run under the approved reprocessing policy; it must not rewrite a completed attempt.

`heartbeat_at` and `lease_expires_at` on ProcessingRun/ProcessingStep are query projections only. The authoritative owner, lease status, expiry, and fencing token are stored in ExecutionLease. A worker must present the current fencing token for every state-changing write; stale tokens are rejected even if the old worker is still running.

### 13.2.1 ExecutionLease

Represents the durable, exclusive ownership claim for one ProcessingRun or ProcessingStep.

Fields:

- `id`
- `resource_type` — `PROCESSING_RUN` or `PROCESSING_STEP`
- `resource_id`
- `owner_id` — stable worker/process identity
- `fencing_token` — monotonically increasing integer for the resource
- `status` — `ACTIVE`, `RELEASED`, or `EXPIRED`
- `acquired_at`
- `heartbeat_at`
- `expires_at`
- `released_at` nullable
- `created_at`
- `metadata`

Constraints and behavior:

- At most one active lease may exist for a resource; acquisition must be an atomic compare-and-set/transaction, not a read-then-write sequence.
- Every successful acquisition increments the resource fencing token. Tokens must never be reused for the same resource.
- Renewal and release must match the lease ID, owner ID, and current fencing token.
- Every worker write that changes run/step state or commits a domain effect must validate the current fencing token within the same transaction boundary.
- Expiry permits recovery to be considered; it does not prove that the former worker stopped. Fencing prevents a late former worker from committing.
- Lease duration and heartbeat interval are deployment settings, not hard-coded domain truths.

### 13.2.2 IdempotencyRecord

Represents the durable result or in-progress state of one logical operation, including operations whose side effects extend beyond a ProcessingRun.

Fields:

- `id`
- `operation_scope` — canonical operation/target scope
- `idempotency_key`
- `request_fingerprint`
- `status` — `IN_PROGRESS`, `COMPLETED`, `FAILED`, or `RECONCILIATION_REQUIRED`
- `processing_run_id` nullable
- `owner_id` nullable
- `result_reference` nullable
- `started_at`
- `completed_at` nullable
- `created_at`
- `metadata`

Constraints and behavior:

- `(operation_scope, idempotency_key)` must be unique.
- Reuse of a key with the same request fingerprint returns or resumes the existing logical operation; it must not create a second domain effect.
- Reuse of a key with a different request fingerprint is a conflict and must be rejected.
- Creation/claim of the record and the corresponding local database effect must share an atomic transaction where possible.
- External side effects require durable intent and explicit reconciliation; an unknown outcome must not be retried as though failure were confirmed.
- Retention/expiry of idempotency records must not permit a still-retriable external operation to execute twice.

### 13.3 ArticleProcessingRecord

Represents processing state for an article across processing stages.

Fields:

- `id`
- `article_id`
- `article_revision_id`
- `processing_run_id`
- `stage`
- `status`
- `processing_version`
- `input_fingerprint`
- `output_reference`
- `started_at`
- `completed_at`
- `error_category`
- `metadata`

Possible stages include:

- `NORMALIZATION`
- `DEDUPLICATION`
- `LANGUAGE_DETECTION`
- `TOPIC_CLASSIFICATION`
- `ENTITY_EXTRACTION`
- `ENTITY_RESOLUTION`
- `CLAIM_EXTRACTION`
- `EVENT_MATCHING`
- `EVIDENCE_PROCESSING`

The current article processing state may be derived from the latest records or maintained as a projection. If a projection is maintained, it must be rebuildable from processing history.

### 13.4 CollectionCheckpoint

Tracks incremental source collection.

Fields:

- `id`
- `source_id`
- `checkpoint_type`
- `checkpoint_value`
- `updated_at`
- `metadata`

Constraints:

- A checkpoint must only advance after corresponding collection results have been safely persisted.
- Checkpoint updates must be atomic with the ingestion state they represent.
- Checkpoint uniqueness must be defined by source and checkpoint type.
- Repeated collection of the same source item must be idempotent.

### 13.5 LLMUsageRecord

Records LLM execution usage and cost information.

Fields:

- `id`
- `processing_run_id` nullable
- `processing_step_id` nullable
- `analysis_id` nullable
- `provider`
- `model_id`
- `operation_type`
- `privacy_authorization_decision_id` nullable — immutable PrivacyAuthorizationDecision reference for personal-data processing
- `processing_purpose_id` nullable
- `data_category` nullable
- `processing_region` nullable
- `transfer_assessment_id` nullable
- `content_rights_decision_refs` nullable — exact applicable source-content decisions
- `prompt_version`
- `schema_version`
- `input_tokens` nullable
- `output_tokens` nullable
- `total_tokens` nullable
- `provider_reported_cost` nullable
- `estimated_cost` nullable
- `currency` nullable
- `cost_source` — `PROVIDER_REPORTED`, `INTERNAL_ESTIMATE`, or `UNAVAILABLE`
- `pricing_catalog_version` nullable
- `retry_count`
- `fallback_used`
- `fallback_policy_version` nullable
- `duration_ms` nullable
- `outcome`
- `recorded_at`
- `metadata`

Unknown usage or cost must remain null, not zero.

Usage records should support cost reporting, provider comparison, budget enforcement, and operational evaluation.

`provider_reported_cost` and `estimated_cost` are distinct. `cost_source` must identify which value is authoritative for a report; `UNAVAILABLE` requires both cost values to remain null. An internally estimated cost must reference the exact `pricing_catalog_version`; the system must not present an estimate as a provider-reported charge. Retry and fallback use must be explicit and traceable to the applicable fallback policy. Unknown token usage or cost must remain null, not zero.

Provider-specific usage metadata may be retained in JSON, but commonly queried values should have explicit fields.

Every recorded LLM operation should be traceable to the Shared LLM Execution Layer and, where applicable, to its processing run, step, or analysis.

### 13.6 EvaluationRun and EvaluationResult (Evaluation Artifacts)

Evaluation execution is a development/quality-governance activity, not a production business transaction. To avoid duplicating the authoritative runtime workflow record, `ProcessingRun` and `ProcessingStep` are the task/workflow execution records referenced by GENI-ADR-017; a separate production `TaskExecutionRecord` table is not introduced.

Evaluation results are retained as versioned, machine-readable evaluation artifacts in the repository/CI artifact store, rather than as operational production tables.

An `EvaluationRun` artifact must include:

- `evaluation_run_id`
- `dataset_id` and `dataset_version`
- `task_type` and `task_version`
- model, provider, prompt, schema, taxonomy, and policy versions where applicable
- `started_at`, `completed_at`, and run status
- runner/tool version and baseline-run reference
- aggregate quality, cost, and latency metrics with explicit unknown values
- artifact references and execution environment identifier

Each `EvaluationResult` artifact must include:

- `evaluation_run_id`
- stable `case_id`
- expected/reference-output version
- produced-output reference or content hash
- metric/rubric identifier and version
- score or categorical verdict, nullable when not evaluated
- evaluator type/version and human reviewer reference when applicable
- error/skip reason and provenance references

Evaluation artifacts must not contain restricted source content unless the relevant rights permit their storage. They must preserve dataset and model/prompt/schema versions so a run can be reproduced or compared. A failed or incomplete run must not be represented as a successful quality gate.

### 13.7 Schedule

Represents a configured recurring or one-time workflow schedule.

Fields:

- `id`
- `schedule_type`
- `target_type`
- `target_id` nullable
- `schedule_config`
- `timezone`
- `is_active`
- `created_at`
- `updated_at`
- `metadata`

Schedule configuration must be validated and versioned.

### 13.8 ScheduledExecution

Represents one execution initiated by a schedule.

Fields:

- `id`
- `schedule_id`
- `scheduled_for`
- `processing_run_id` nullable
- `status`
- `started_at`
- `completed_at`
- `error_category`
- `error_summary`
- `metadata`

Constraints:

- Duplicate execution of the same schedule occurrence must be prevented through an idempotency rule.
- Schedule execution history must remain traceable.
- Scheduling metadata must not replace ProcessingRun as the authoritative workflow execution record.

## 14. Semantic Matching and Search Storage

### 14.1 Matching Requirements

Event matching may combine:

- Lexical similarity.
- Entity overlap.
- Temporal compatibility.
- Geographic compatibility.
- Semantic similarity.
- Event type and topic compatibility.
- Explicit domain rules.

The matching method and policy version must be recorded.

A similarity score is a signal for a decision, not proof that two articles describe the same event.

### 14.2 EmbeddingRecord

If semantic embeddings are used, they may be represented through a logical `EmbeddingRecord`.

Fields:

- `id`
- `target_type`
- `target_id`
- `embedding_model`
- `embedding_version`
- `vector_reference` or `vector_data`
- `content_fingerprint`
- `created_at`

The physical vector representation is not fixed by this document. Where an embedding is created from restricted source content or sent to an external provider, its creation/storage must reference the applicable operation-specific RightsAssessment. An embedding is a derived artifact and must be included in rights-aware retention/deletion where required.

Embeddings may be stored in an approved vector-capable database, a compatible extension, or another search service.

A dedicated vector database is not a mandatory Phase 1 dependency. The semantic retrieval implementation remains optional and subject to GENI-ADR-012; a lexical retrieval baseline must remain available for evaluation and fallback.

### 14.3 Search and Retrieval

Search infrastructure must not become the authoritative store of domain identity.

The relational domain model remains authoritative for:

- Article identity.
- Event identity.
- Accepted article-event relationships.
- Claims and evidence.
- Analysis and report history.

Search indexes and embeddings must be rebuildable from authoritative records where technically feasible.

## 15. Recommended Logical Table Inventory

The logical table inventory is:

| Table | Purpose |
|---|---|
| `sources` | Source configuration |
| `source_rights_profiles` | Versioned source rights and license context |
| `source_licenses` | Referenced licenses and contractual terms associated with sources |
| `content_access_records` | Source/content access and retrieval provenance |
| `rights_assessments` | Operation-specific permission outcomes |
| `content_retention_policies` | Versioned content retention rules |
| `content_deletion_requests` | Requested content restriction/deletion work |
| `content_deletion_records` | Deletion execution and verification history |
| `content_usage_audit_records` | Audit trail for content use and external transmission |
| `derived_artifacts` | Versioned derived outputs with source-rights provenance |
| `source_health_records` | Source health history |
| `source_relationships` | Versioned, directed publisher/source relationships |
| `articles` | Current normalized article projection |
| `article_revisions` | Article revision history |
| `article_origin_relationships` | Versioned provenance links between exact article revisions and their information origins |
| `article_topic_classifications` | Topic classification history |
| `article_entity_mentions` | Extracted entity mentions |
| `entities` | Resolved entities |
| `entity_aliases` | Alternative entity names |
| `article_event_links` | Decision-authorized article-event associations |
| `event_match_cases` | Per-revision, per-development event-resolution cases |
| `event_match_decisions` | Immutable case-level event matching outcomes |
| `duplicate_candidates` | Immutable article duplicate evaluation candidates |
| `duplicate_decisions` | Immutable duplicate outcomes and supersession history |
| `events` | Current event state |
| `event_match_candidates` | Candidate events evaluated within a matching case |
| `event_history` | Event change history |
| `event_relationships` | Relationships between events |
| `event_identity_operations` | Event merge and split operations |
| `event_identity_operation_inputs` | Input events and expected EventHistory versions for identity operations |
| `event_identity_operation_outputs` | Result events from identity operations |
| `event_identity_operation_histories` | Append-only operation status/effect transitions and reconciliation actions |
| `event_entity_links` | Event entities |
| `claims` | Logical claims and current assessment projection |
| `event_claim_links` | Claim-event relationships |
| `claim_observations` | Claim source observations |
| `evidence` | Evidence records |
| `evidence_locations` | Precise evidence provenance |
| `claim_evidence_links` | Claim-evidence relationships |
| `claim_assessments` | Immutable, versioned claim assessment results |
| `claim_assessment_evidence_links` | Exact evidence set considered by each claim assessment |
| `assessment_history` | Append-only claim-assessment audit actions |
| `analyses` | Analytical results |
| `analysis_evidence_links` | Analysis provenance |
| `analysis_inputs` | Analysis input references |
| `market_observations` | Optional observed market data |
| `reports` | Report versions |
| `report_event_links` | Report-event relationships |
| `report_evidence_links` | Report evidence references |
| `report_article_links` | Report references to exact ArticleRevision records |
| `report_analysis_links` | Report analysis references |
| `publication_decisions` | Publication policy history |
| `review_records` | Human review records |
| `review_context_links` | Immutable typed evidence and domain-context links attached to review tasks |
| `review_actions` | Append-only human-review lifecycle and audit actions |
| `publication_records` | Publish, replace, and withdraw operations |
| `publication_attempts` | External publication attempt and reconciliation history |
| `delivery_records` | Logical delivery operations |
| `distribution_authorization_decisions` | Immutable recipient- and operation-specific delivery authorization outcomes |
| `distribution_authorization_rights_links` | Exact source-rights assessments covering each source-derived content scope in an authorization decision |
| `delivery_attempts` | Delivery retry history |
| `processing_runs` | Workflow execution records |
| `processing_steps` | Workflow step records |
| `execution_leases` | Atomic worker ownership and fencing-token history |
| `idempotency_records` | Scoped logical-operation idempotency and reconciliation state |
| `article_processing_records` | Article processing stage history |
| `collection_checkpoints` | Incremental collection state |
| `llm_usage_records` | LLM usage and cost |
| `schedules` | Workflow schedule definitions |
| `scheduled_executions` | Schedule execution history |
| `embedding_records` | Optional semantic representations |
| `personal_data_inventory` | Logical inventory of personal-data categories, systems, purposes and retention references |
| `processing_purposes` | Versioned approved processing purposes and permitted operations/categories |
| `privacy_processing_bases` | Reviewed basis assessments and jurisdiction-specific evidence references |
| `privacy_authorization_decisions` | Immutable scoped privacy-processing decisions and policy evidence |
| `data_subject_references` | Restricted opaque subject linkage; identity map stored separately/protected |
| `data_subject_requests` | Data-subject request lifecycle and verified scope |
| `data_subject_request_actions` | Idempotent target-level request actions and evidence |
| `privacy_deletion_records` | Deletion/restriction outcomes, processor acknowledgements and restore reconciliation |
| `processor_register` | Approved processor/subprocessor posture, purpose, region, retention and deletion capability |
| `international_transfer_assessments` | Transfer destination, safeguards and approval evidence |
| `privacy_impact_assessments` | Processing risk assessments and mitigation/approval evidence |
| `personal_data_lineage` | Subject-linked source, processing, provider and derived-artifact lineage |

Not every logical entity must be implemented in the first migration. The implementation roadmap should prioritize a usable end-to-end workflow while preserving the domain contracts.

## 16. Indexing and Constraints

### 16.1 Initial Indexes

Indexes should support:

- Article lookup by source.
- Article lookup by publication time.
- Article lookup by collection time.
- Content hash lookup.
- Canonical URL lookup.
- Article revision lookup.
- Article classification lookup.
- Entity lookup by canonical name and type.
- Entity alias lookup.
- Event lookup by status, topic, and update time.
- Event lookup by occurrence time.
- Article-event lookup in both directions.
- Event match case lookup by ArticleRevision and development key.
- Event match candidate lookup by case, status, and score.
- Event match decision lookup by case and decision time.
- EventIdentityOperationHistory lookup by operation and sequence.
- Event match review lookup by status, assignment, and due date.
- Duplicate candidate lookup.
- Claim lookup by event and observation.
- Evidence lookup by source, article, and origin type.
- Analysis lookup by event, analysis type, status, version, and creation time.
- Report lookup by event and version.
- Report-event lookup in both directions.
- Publication decision lookup by report and decision.
- Publication operation lookup by target, publication key, status, report, and operation sequence.
- Publication attempt lookup by operation and attempt number.
- Review queue lookup by status, assignment, due date, and creation time.
- Delivery lookup by status, target, and scheduled time.
- Delivery lookup by referenced publication where applicable.
- DistributionAuthorizationDecision lookup by exact report, recipient, destination, decision, and expiry.
- DistributionAuthorizationRightsLink lookup by authorization decision and content scope.
- Delivery attempt lookup by delivery operation.
- Processing run lookup by type, status, target, and lease expiry.
- Processing step lookup by run and status.
- LLM usage lookup by provider, model, and time.
- Schedule lookup by active status and next execution time.

### 16.2 Unique Constraints

Where applicable, enforce:

- Source-scoped external article identity.
- Source rights-profile version uniqueness within a source.
- Content-access and rights-assessment identifiers must be unique and auditable.
- Content-deletion request/record identity and idempotency keys must be unique within their defined operation scope.
- Article revision number uniqueness.
- Composite uniqueness of `(article_id, id)` on ArticleRevision for same-Article current-revision references.
- Event match case uniqueness by ArticleRevision and development key.
- Composite uniqueness of `(id, article_revision_id)` on EventMatchCase for case/article-revision consistency.
- Composite uniqueness of `(case_id, id)` on EventMatchCandidate and EventMatchDecision for case-scoped references.
- Candidate evaluation uniqueness by case, candidate Event, matching-policy version, and candidate input fingerprint.
- One effective decision pointer per EventMatchCase.
- At most one direct successor per superseded EventMatchDecision.
- At most one active ArticleEventLink per EventMatchCase, with historical inactive links retained.
- Review action sequence uniqueness within a review record.
- Review action idempotency key uniqueness within a review record.
- Canonical ArticleRevision-pair uniqueness for duplicate candidates, scoped by method/policy version and input fingerprint.
- DuplicateDecision supersession-chain consistency and at most one effective decision per candidate.
- ClaimAssessment sequence uniqueness within a Claim.
- At most one direct successor per superseded ClaimAssessment.
- Claim.current_assessment_id must reference an assessment belonging to that same Claim.
- ClaimAssessmentEvidenceLink uniqueness per assessment/evidence/relationship.
- AssessmentHistory idempotency-key uniqueness within its defined assessment scope.
- Event-specific report version uniqueness.
- Event analysis type and version uniqueness.
- Source and checkpoint type uniqueness.
- SourceRelationship version uniqueness within its directed source pair and relationship type; only symmetric relationship types may canonicalize the pair.
- ArticleOriginRelationship version uniqueness within its subject revision, target origin, relationship type, and assessment lineage.
- Processing step identity within a run.
- ProcessingStepAttempt uniqueness by (processing_step_id, attempt_number), and idempotency-reference uniqueness within the logical step. For Event Identity reconciliation, enforce uniqueness by (processing_run_id, step_name, input_fingerprint), permitting multiple steps with the same step_name only when their server-derived fingerprints bind distinct logical work identities (operation ID, work kind, typed target and target version/cursor). A changed target state or policy creates a successor step/run under the approved reprocessing policy; it does not overwrite a completed step.
- At most one active ExecutionLease per resource and strictly increasing fencing tokens per resource.
- IdempotencyRecord uniqueness by `(operation_scope, idempotency_key)`.
- ProcessingRun idempotency-key uniqueness within its documented run-type scope.
- Publication operation sequence uniqueness within a target/publication-key chain.
- Publication idempotency key uniqueness within its target/publication-key scope.
- Publication attempt number uniqueness within a publication operation.
- Delivery idempotency key uniqueness within its scope.
- Schedule occurrence uniqueness.
- Event identity operation input/output uniqueness.
- EventIdentityOperationHistory sequence uniqueness within an operation and idempotency-key uniqueness within its operation scope.
- DistributionAuthorizationDecision idempotency-key uniqueness within its exact report/recipient/destination scope.
- At most one direct successor per superseded DistributionAuthorizationDecision.
- DistributionAuthorizationRightsLink uniqueness by decision, RightsAssessment, and typed content-scope reference.
- EventMatchDecision selected-candidate and case consistency.
- EventMatchDecision supersession-chain consistency.
- EventMatchCase.effective_decision_id must reference a decision belonging to that same case.
- Entity alias uniqueness where the language and alias type make it unambiguous.

Only one unresolved side-effecting publication operation should be allowed to modify the same target/publication-key chain at a time; enforce this through an appropriate transaction/locking rule or database constraint for the selected engine. Do not serialize unrelated publication keys merely because they share a target.

All uniqueness rules involving nullable fields must be tested against the selected database engine.

### 16.3 Referential Integrity

Foreign keys should protect ordinary relational relationships.

The following composite relationships must be enforced by database constraints where supported, or by application validation inside the same UnitOfWork transaction when the selected database cannot express them directly:

- `SourceRightsProfile.source_id` must reference an existing Source; a rights assessment must reference the exact rights-profile/policy version used for its operation.
- `ContentAccessRecord` must reference the source and, where applicable, the exact Article/ArticleRevision and RightsAssessment that authorized access.
- A `DerivedArtifact` must retain typed provenance references to the source content/revision and processing/rights assessment records on which it depends.
- A `ContentDeletionRecord` must reference its request and the affected content/artifact scope, and record whether deletion was confirmed or remains incomplete.
- `Article(current_revision_id, id)` must resolve to an ArticleRevision whose `article_id` is that same Article.
- `DuplicateCandidate` must reference the exact Article and ArticleRevision pair being compared; both revisions must belong to the referenced Articles.
- `DuplicateDecision` and its superseded decision must reference the same DuplicateCandidate; one candidate cannot have multiple effective decisions.
- `DuplicateCandidate.authorization_reference` must resolve to an ALLOW decision for the exact `article.duplicate.evaluate` action, canonical revision pair, comparison scope, policy/version and input fingerprint.
- `DuplicateDecision.authorization_reference` must resolve to an ALLOW decision for the exact `article.duplicate.decide` action, candidate, outcome, effective predecessor and policy/version.
- `Claim.current_assessment_id` must reference a ClaimAssessment whose claim_id equals that Claim's id.
- `ClaimAssessment.supersedes_assessment_id` must reference an assessment for the same Claim; a new assessment and current pointer update must be atomic.
- `ClaimAssessmentEvidenceLink` must connect an assessment to evidence included in that assessment's immutable evidence set.
- `AssessmentHistory` must reference an existing ClaimAssessment and preserve append-only action identity.
- `EventMatchCase(id, effective_decision_id)` must resolve to `EventMatchDecision(case_id, id)`; the referenced decision must belong to that case.
- `EventMatchDecision(case_id, selected_candidate_id)` must resolve to `EventMatchCandidate(case_id, id)`; a decision cannot select a candidate from another case.
- `ArticleEventLink(event_match_case_id, event_match_decision_id)` must resolve to the same case and decision.
- `ArticleEventLink(event_match_case_id, article_revision_id)` must resolve to the case's exact ArticleRevision.
- The linked `event_id` must equal the `candidate_event_id` selected by the referenced MATCH decision.
- `EventHistory(event_match_case_id, source_event_match_decision_id)`, when both are present, must reference the same case and its NEW_EVENT_CANDIDATE decision.
- `EventIdentityOperationHistory.operation_id` must reference an existing EventIdentityOperation; the operation projection and append-only history transition must be committed atomically.
- Every EventIdentityOperationInput.expected_event_history_version must be checked against the exact input Event's current EventHistory version inside the core identity UnitOfWork transaction.
- `DistributionAuthorizationDecision.report_id` must reference the exact immutable Report version it authorizes.
- Every DistributionAuthorizationRightsLink must reference its parent DistributionAuthorizationDecision and an existing RightsAssessment whose operation is `CUSTOMER_DISTRIBUTION`, whose outcome is `ALLOWED`, and whose subject/content scope matches the link's typed scope reference.
- Every source-derived manifest item must have complete typed provenance to the source/article revision and derived-artifact versions used to create it; each required upstream RightsAssessment must remain effective at dispatch, or the item must be excluded and a successor authorization decision created for the reduced manifest.
- The DistributionAuthorizationDecision.rights_assessment_set_fingerprint must be reproducible from the exact linked set; source-derived content in its authorized scope cannot be omitted from that set.
- `DeliveryRecord.distribution_authorization_decision_id` must reference an effective, unexpired `ALLOW` decision whose report, recipient, destination, delivery mode, channel, and canonical content-scope manifest fingerprint exactly match the DeliveryRecord. Dispatch must also verify that the outbound payload is constructed only from the exact manifest items and item digests, and persist its separate `outbound_payload_sha256`. A `PUBLICATION_LINK` delivery must additionally reference a confirmed successful and currently effective PublicationRecord.
- A link may be active only while its authorizing MATCH decision is the effective decision for that case.

The corresponding database constraints and application checks must be covered by repository contract and transactional integration tests. If composite/deferred foreign keys are used, their migration and behavior must be verified against the selected engine.

Polymorphic references must be explicitly documented and validated by the application layer. PublicationAttempt must reference an existing PublicationRecord. A replacement or withdrawal target_publication_id must reference an earlier successful PublicationRecord with the same publication target and publication key. A DeliveryRecord in PUBLICATION_LINK mode must reference a confirmed effective publication operation; this semantic constraint must be enforced by the application workflow even where it cannot be expressed as a simple foreign key.

Deletion policies must protect historical evidence, reports, and provenance. Cascading deletion must not silently remove records referenced by published reports.

## 17. Score and Confidence Semantics

Scores and assessment outputs must not be treated as interchangeable values.

The system must preserve the following distinctions:

| Assessment | Question answered | What it must not represent |
|---|---|---|
| Event Importance | How significant and attention-worthy is this event overall? | Economic transmission strength, economic-effect magnitude, or forecast probability |
| Economic Relevance | How direct and material is the event's connection to economic activity, policy, institutions, or markets? | The size, direction, or certainty of the resulting economic effect |
| Economic Impact | What realized or potential economic consequences exist, by channel and time horizon? | Overall editorial importance or proof of causal market attribution |
| Market Reaction | What market movement is observed or reported at a defined time and context? | Proof that the event caused that movement |

For each assessment or score type, the system must document:

- The question and construct being measured.
- Valid categories, range, and scale where applicable.
- Whether higher values indicate stronger or weaker results.
- Calculation or assessment method.
- Methodology, policy, and schema version.
- Whether the value is calibrated.
- Whether it is comparable across models, sources, event classes, or time periods.
- Evidence requirements and uncertainty handling.

Numeric values are optional. A numeric score must not be persisted or displayed without its defined scale, direction, interpretation, methodology version, and calibration status. Scores from different assessment types must not be added, averaged, or compared unless a separately approved and evaluated composite methodology explicitly defines that operation.

An assessment's confidence value describes support for the assessment, not its importance or impact magnitude. A forecast probability must be represented separately and may be described as a probability only when its methodology and calibration support that interpretation.

At minimum, separate semantics must be defined for:

- Source reliability.
- Article duplicate similarity.
- Event matching similarity.
- Entity resolution confidence.
- Claim-evidence relevance.
- Claim verification confidence.
- Event importance.
- Economic relevance.
- Economic impact by channel.
- Analytical confidence.
- Forecast probability, where used.

Unknown, unavailable, not-established, and not-applicable values must remain distinguishable. Missing values must remain null or use the explicitly defined unknown state; they must not silently become zero, neutral, or a low score.

## 18. JSON Storage Policy

JSON may be used for flexible, versioned metadata.

Appropriate examples:

- Source-specific configuration.
- External identifiers.
- Provider metadata.
- Classification details.
- Model metadata.
- Error context.
- Event identity operation metadata.
- Schedule configuration.

JSON must not replace relational tables for core domain relationships.

Important queryable fields must have explicit relational columns.

JSON structures must have documented schemas and versioning expectations.

Secrets, credentials, and access tokens must not be stored in ordinary metadata.

## 19. Timestamp and Identity Policy

### 19.1 Timestamps

Persist timestamps in UTC.

Use timezone-aware datetime values in application code.

Distinguish:

- `published_at`: source publication time.
- `collected_at`: first successful system collection time.
- `last_seen_at`: latest observation of an article.
- `occurrence_start_at`: estimated or observed start of an event.
- `occurrence_end_at`: estimated or observed end of an event.
- `observed_at`: time an observation was made.
- `created_at`: record creation time.
- `updated_at`: last modification time.
- `completed_at`: processing completion time.
- `scheduled_for`: intended schedule execution time.

Missing timestamps must remain null.

When time precision is limited, record the precision explicitly rather than inventing a precise timestamp.

### 19.2 Identifiers

Use stable internal identifiers for domain entities.

UUIDs are recommended, subject to the final database implementation decision.

External source identifiers must be stored separately.

Database row ordering must never be used as a domain identity.

Event identifiers must remain stable during ordinary updates. Merge and split operations must preserve the identity history.

## 20. Transactions and Consistency

The following operations require atomic transactions or an equivalent consistency mechanism:

- Article creation and ingestion metadata.
- Article revision creation and current article projection update.
- Event creation and initial event history.
- Event update and corresponding history creation.
- Article-event association and its decision record.
- Event merge or split and related identity history.
- Claim observation and its source references.
- Claim and evidence association.
- Analysis completion and its provenance links.
- Report version creation and report input links.
- Publication decision persistence.
- Review state changes.
- Publication-operation creation and state transitions.
- Publication-attempt persistence and reconciliation state changes.
- Delivery state transitions.
- Collection checkpoint updates after successful persistence.
- Schedule occurrence registration and scheduled execution creation.

A report must not be marked as published before the publication workflow has successfully recorded the publication outcome.

External publication and delivery operations cannot generally be included in a database transaction. A durable PublicationRecord or DeliveryRecord must be persisted before the corresponding external side effect. The external result and attempt outcome must then be recorded through explicit state transitions. Idempotency keys and reconciliation handling are required. A timeout with an unknown publication outcome must not trigger an unconditional retry.

## 21. Idempotency, Reprocessing, and Recovery

Idempotency is required for:

- Article ingestion.
- Article normalization.
- Duplicate detection.
- Topic classification.
- Entity extraction and resolution.
- Claim extraction.
- Event matching.
- Article-event association.
- Event update processing.
- Analysis generation.
- Report generation.
- Publication decisions.
- Publication execution, including publish, replace, and withdraw operations.
- Report delivery.
- Collection checkpoint advancement.
- Scheduled workflow execution.

A repeated operation with the same logical input and processing version should not create duplicate domain effects.

Processing fingerprints should include the relevant input identifiers and versions, such as:

- Article revision.
- Taxonomy version.
- Matching policy version.
- Prompt version.
- Model identifier.
- Analysis schema version.
- Relevant event version.
- Relevant source or dataset version.

Reprocessing must create a traceable new execution when relevant inputs or policies change.

Failed workflow steps must be recoverable without incorrectly repeating completed external side effects.

Expired execution leases must be detected and handled through a documented recovery policy. Lease ownership is represented by ExecutionLease; the run/step lease timestamps are projections only.

A workflow must not be resumed concurrently by multiple workers. Lease acquisition and renewal must be atomic, and every state-changing worker write must validate a monotonically increasing fencing token so that a stale worker cannot commit after ownership changes.

Logical operation idempotency is represented by IdempotencyRecord, uniquely scoped by `(operation_scope, idempotency_key)` and bound to a request fingerprint. Reuse with a different fingerprint is a conflict. External side effects require durable intent and reconciliation of unknown outcomes before retry.

## 22. Retention and Content Rights

Retention must comply with applicable source terms, licensing requirements, and legal obligations.

Technical access to content does not imply permission to store, reproduce, or republish it.

The model must distinguish:

- Article metadata.
- Short permitted extracts.
- Source-provided summaries.
- Retrieved full text.
- External content references.
- Derived analytical outputs.

Retention rules must define which content can be stored, for how long, and for what purpose.

Published reports must preserve sufficient provenance to identify their sources, subject to legal and contractual restrictions. ReportArticleLink must point to the exact ArticleRevision used, not only to the mutable current Article projection.

Deletion or withdrawal requests must not be silently ignored. The system needs an auditable correction, withdrawal, or restricted-retention process.

Where content must be deleted, the system should preserve legally permissible metadata and audit information without retaining prohibited content.

### 22.1 Content Rights Records and Enforcement Boundaries

The following are proposed logical records aligned with GENI-ADR-013. Their final fields, permission vocabulary, retention/deletion mechanics, and physical persistence design remain subject to formal ADR acceptance and detailed implementation design.

**SourceRightsProfile**

A versioned profile linked to a Source and, where applicable, one or more SourceLicense records. It should preserve the rights-document reference, profile status, permitted and restricted operation categories, content types, effective dates, verification date, retention-policy reference, supersession lineage, and the reviewer/authority that recorded the profile. Source defaults must not override more restrictive content-specific terms.

**SourceLicense**

A referenced license or contractual instrument associated with a SourceRightsProfile. It should identify the licensor/provider, license or agreement reference, scope and permitted use categories, restrictions, effective/expiry dates, and supporting evidence reference. The system stores provenance and approved policy interpretation; it does not generate legal conclusions.

**ContentAccessRecord**

An immutable record of a retrieval/access event. It should identify the Source, content and exact ArticleRevision where available, acquisition method, metadata/full-text/temporary-access mode, time, applicable rights profile, and resulting content reference or access limitation. It must not itself imply a continuing permission to retain or redistribute the content.

**RightsAssessment**

An immutable, operation-specific assessment. It must identify the subject/content, exactly one `requested_operation`, outcome (`ALLOWED`, `DENIED`, `UNKNOWN`, `EXPIRED`, `REVOKED`, or `REQUIRES_REVIEW`), rights-policy and source-profile versions, supporting basis/reference, evaluator/actor, timestamp, and reason codes. The canonical operation vocabulary from GENI-ADR-013 is `DISCOVERY`, `METADATA_ACCESS`, `FULL_TEXT_ACCESS`, `TEMPORARY_PROCESSING`, `PERSISTENT_STORAGE`, `INTERNAL_ANALYSIS`, `EXTERNAL_LLM_PROCESSING`, `DERIVED_OUTPUT_GENERATION`, `TRANSLATION`, `EMBEDDING_GENERATION`, `QUOTATION`, `AUDIO_TRANSFORMATION`, `VIDEO_TRANSFORMATION`, `CUSTOMER_DISTRIBUTION`, and `CONTENT_REPUBLICATION`. The application must reject unknown operation identifiers rather than silently mapping them to a broader permission. Each materially different operation requires its own assessment; an allowed metadata read does not authorize full-text storage or external LLM processing.

**ContentRetentionPolicy**

A versioned policy definition for permitted retention mode, purpose, duration/expiry, deletion behavior, backup treatment, and treatment of derived artifacts. A policy definition must not be confused with a per-content RightsAssessment.

**DerivedArtifact**

A versioned output derived from source content, such as a translation, embedding, extracted passage, or analytical artifact. It should preserve the exact source revision/content references, processing method/version, rights assessment(s), and applicable retention/distribution restrictions. Derived content is not automatically unrestricted merely because it is system-generated.

For a translation artifact, preserve at least the source ArticleRevision, source and output languages, translator/provider and model identity where applicable, prompt/configuration and processing version, created time, quality/validation status, and rights assessment for temporary/external processing and resulting retention. The source ArticleRevision remains authoritative; translation output must never overwrite it. For an embedding artifact, preserve the exact normalized input fingerprint, model/version, dimensions/representation, and applicable rights assessment. A material input/model change creates a distinct versioned artifact.

**ContentDeletionRequest / ContentDeletionRecord**

A request and its execution history for restriction or deletion across primary content storage, temporary files, caches, indexes, queues, backups, and external processors where required and supported. The records must distinguish requested, in-progress, confirmed, partially completed, and failed outcomes; a request must not be marked complete without verification evidence.

**ContentUsageAuditRecord**

An append-only record of material content-use operations, including operation type, subject, actor, destination/provider where relevant, RightsAssessment and policy version, timestamp, outcome, and audit reference. Sensitive source content and credentials must not be copied into the audit record.

**Fail-closed invariant:** absent, unknown, expired, revoked, denied, or review-required permission must not authorize a restricted operation. Technical access, public availability, or an earlier permission for a different operation is insufficient. Rights authorization is separate from publication eligibility and recipient-distribution authorization.

The `rights_status` field on Article/ArticleRevision is only a summary projection. It is not a substitute for versioned, operation-specific RightsAssessment records. Exact schema and policy rules remain provisional until GENI-ADR-013 is accepted.

## 23. Repository Contracts

The application layer should depend on domain-oriented repository interfaces.

Initial repository contracts include:

- `SourceRepository`
- `SourceRightsProfileRepository` (when GENI-ADR-013 is accepted)
- `SourceLicenseRepository` (when GENI-ADR-013 is accepted)
- `ContentAccessRepository` (when GENI-ADR-013 is accepted)
- `RightsAssessmentRepository` (when GENI-ADR-013 is accepted)
- `ContentRetentionPolicyRepository` (when GENI-ADR-013 is accepted)
- `ContentDeletionRepository` (when GENI-ADR-013 is accepted)
- `DerivedArtifactRepository` (when GENI-ADR-013 is accepted)
- `ContentUsageAuditRepository` (when GENI-ADR-013 is accepted)
- `SourceHealthRepository`
- `SourceRelationshipRepository`
- `ArticleOriginRelationshipRepository`
- `ExecutionLeaseRepository`
- `IdempotencyRecordRepository`
- `ArticleRepository`
- `ArticleRevisionRepository`
- `ArticleProcessingRepository`
- `ArticleClassificationRepository`
- `DuplicateCandidateRepository`
- `DuplicateDecisionRepository`
- `EntityRepository`
- `EntityAliasRepository`
- `ArticleEntityMentionRepository`
- `EventRepository`
- `ArticleEventLinkRepository`
- `EventMatchCaseRepository`
- `EventMatchCandidateRepository`
- `EventMatchDecisionRepository`
- `EventHistoryRepository`
- `EventRelationshipRepository`
- `EventIdentityOperationRepository`
- `EventIdentityOperationHistoryRepository`
- `ClaimRepository`
- `ClaimObservationRepository`
- `EvidenceRepository`
- `EvidenceLocationRepository`
- `ClaimEvidenceLinkRepository`
- `ClaimAssessmentRepository`
- `ClaimAssessmentEvidenceLinkRepository`
- `AssessmentHistoryRepository`
- `AnalysisRepository`
- `AnalysisInputRepository`
- `AnalysisEvidenceLinkRepository`
- `MarketObservationRepository` (only when GENI-ADR-015 is accepted and market-data integration is in scope)
- `ReportRepository`
- `ReportEventLinkRepository`
- `ReportEvidenceLinkRepository`
- `ReportArticleLinkRepository`
- `ReportAnalysisLinkRepository`
- `PublicationDecisionRepository`
- `ReviewRepository`
- `ReviewContextLinkRepository`
- `PublicationRepository`
- `PublicationAttemptRepository`
- `DeliveryRepository`
- `DeliveryAttemptRepository`
- `DistributionAuthorizationRepository` (persists DistributionAuthorizationDecision and its complete immutable DistributionAuthorizationRightsLink set as one aggregate)
- `ProcessingRunRepository`
- `ProcessingStepRepository`
- `CollectionCheckpointRepository`
- `LLMUsageRepository`
- `ScheduleRepository`
- `ScheduledExecutionRepository`
- `EmbeddingRepository`, when semantic storage is implemented.
- `PrivacyRequestRepository` (GENI-ADR-020; DataSubjectRequest, DataSubjectRequestAction and PrivacyDeletionRecord)
- `PersonalDataLineageRepository` (GENI-ADR-020)
- `PrivacyPolicyRepository` (GENI-ADR-020; inventory, purposes, processing bases, processor/transfer/PIA records)
- `DataSubjectReferenceRepository` (GENI-ADR-020; restricted subject linkage)
- `PrivacyAuthorizationRepository` (GENI-ADR-020; immutable scoped privacy authorization decisions)

Additional repositories may be introduced when implementation needs justify them.

Repository interfaces must expose domain-oriented operations rather than raw SQL.

Transaction boundaries must be managed through a unit-of-work or equivalent application-level transaction mechanism.

Repositories responsible for one aggregate or workflow may expose multiple related operations through a single application-facing contract. The logical entities do not require a one-to-one repository-per-table implementation.

Repository contracts must be consistent with the component interfaces defined in Document 02. The proposed method-level baseline for the first-slice repository set is GENI-IMPL-015; it supplements, but does not supersede, this logical model or the ownership/transaction requirements above. It remains Proposed pending Project Owner approval, and every repository used by a later stage still requires its own method-level contract before implementation.

## 24. Migration Strategy

Use versioned database migrations.

Requirements:

- Every schema change must be versioned.
- Migrations must be repeatable in test environments.
- Destructive migrations require explicit review.
- Migration state must be recorded.
- Database upgrades must be tested with representative data.
- Application code must handle expected schema compatibility during deployment.
- Migrations must preserve historical records and provenance.
- SQLite-specific behavior must not leak into domain models.

Migration tests must include both fresh database creation and upgrades from prior schema versions.

## 25. Backup and Recovery

The initial deployment must document:

- Database backup procedure.
- Backup frequency.
- Restore procedure.
- Data integrity checks.
- Recovery objectives.
- Treatment of in-progress workflows after restoration.
- Treatment of pending external delivery operations after restoration.

Backups must use a consistency-safe method supported by PostgreSQL. PostgreSQL-specific backup and restore procedures must be documented and restore-tested as part of GENI-ADR-005-POC-001; production operation remains blocked until the qualification evidence is reviewed and GENI-ADR-005 is formally accepted.

A restore test is required before backups are considered operationally reliable.

After restoration, workflow recovery must detect incomplete processing runs and determine whether they can safely resume.

External side effects must be reconciled before a restored workflow repeats a delivery or publication operation.

## 26. Testing Requirements

Data-layer tests must cover:

- Foreign key enforcement.
- Unique constraints.
- Operation-specific rights assessment and fail-closed permission handling.
- Source rights-profile versioning and content-access provenance.
- Content retention expiry and deletion request/verification lifecycle.
- Derived-artifact provenance and rights inheritance/restriction checks.
- Content usage audit completeness without sensitive-content leakage.
- Article ingestion idempotency.
- Article revision creation.
- Current article projection consistency.
- Duplicate candidate behavior.
- Event identity preservation.
- Event matching cases, candidates, and immutable decisions.
- Candidate-to-case and decision-to-case referential integrity.
- Human review creating a superseding decision.
- Link activation and deactivation with exact decision provenance.
- Event merge and split history.
- Many-to-many article-event relationships.
- Topic classification history.
- Entity aliases and resolution.
- Claim observations and provenance.
- Claim-evidence relationships.
- Evidence location traceability.
- Analysis provenance.
- Analysis input validation.
- Separate, versioned importance, economic relevance, and economic impact assessment records using explicit Analysis types.
- Report version uniqueness.
- Multi-event report relationships.
- Published report immutability.
- Publication decision history and decision supersession.
- Review queue state transitions and reviewer authorization.
- Publication idempotency by target and operation.
- Publication attempt history and attempt-number uniqueness.
- Replacement success and failure, including preservation of the previous effective publication on failure.
- Withdrawal authorization, success, and failure behavior.
- Reconciliation after an unknown external publication outcome.
- Publication-key isolation so independent items can publish concurrently to the same target.
- Prevention of concurrent conflicting publication operations within the same target/publication-key chain.
- Delivery idempotency and delivery attempt history.
- Distribution authorization decisions bound to exact recipient, destination, report version, delivery mode, channel, and content scope.
- Complete per-source `CUSTOMER_DISTRIBUTION` RightsAssessment coverage for every source-derived item in an authorized delivery scope.
- Immutable rights-link set and fingerprint consistency between authorization decisions and DeliveryRecords.
- Verification that delivery state changes do not mutate publication state.
- Validation that publication-link delivery references a confirmed effective publication.
- Processing run and step recovery.
- SourceRelationship direction, validity-window, versioning, and symmetric-only canonical uniqueness.
- ArticleOriginRelationship exact-revision references, target cardinality, and unknown-origin behavior.
- Expired execution lease handling, stale-worker fencing-token rejection, and atomic lease renewal/release.
- IdempotencyRecord replay for the same key/fingerprint, conflict for a different fingerprint, and reconciliation of unknown external outcomes.
- Atomic event history updates.
- Atomic publication-operation and attempt persistence.
- Collection checkpoint consistency.
- LLM usage recording.
- Schedule execution idempotency.
- Transaction rollback.
- Migration compatibility.
- Backup and restore behavior.

Repository contract tests should run against every supported persistence implementation.

Tests must also verify that unknown values remain null and that the system does not silently convert missing information into zero or false.

## 27. Initial Implementation Scope

The first usable end-to-end implementation should prioritize the smallest data model that supports collection, article processing, event intelligence, evidence-backed analysis, reporting, and controlled delivery.

### 27.1 Initial Operational Requirements

The initial implementation requires:

- Source records and collection checkpoints.
- Article records and content fingerprints.
- Article revisions or an explicitly versioned content strategy.
- Article processing records.
- Topic classification records.
- Entity records and entity mentions.
- Event records and event history.
- Article-event associations.
- Event match candidates and recorded decisions.
- Claims and evidence.
- Claim observations and evidence links.
- Analysis records and evidence links.
- Independent, versioned importance, economic relevance, and economic impact assessment outputs using distinct Analysis types.
- Report versions and source references.
- Report-event relationships where multi-event reporting is required.
- Publication decisions.
- Review records for held reports.
- Publication operation records for publish, replace, and withdraw.
- Publication attempt and reconciliation history.
- Delivery records with idempotency and explicit delivery mode.
- DistributionAuthorizationDecision records with immutable per-source RightsAssessment links for every source-derived content scope.
- Delivery attempt history.
- Processing runs and processing steps.
- Basic LLM usage records.

### 27.2 Deferred Capabilities

The following may be deferred where they are not required by the first operational workflow:

- PostgreSQL deployment.
- Dedicated vector database.
- Advanced embedding infrastructure.
- Object storage.
- Distributed caching.
- Data warehouse.
- Large-scale historical analytics.
- Advanced market data integration.
- Sophisticated source ownership graphs.
- Advanced scheduling infrastructure.

Deferral of a dedicated vector database does not mean semantic event matching can be ignored. The initial event matching implementation must use an explicit, testable matching strategy, which may begin with lexical, entity, temporal, and other available signals.

### 27.3 Implementation Sequencing

The implementation roadmap should introduce entities when the corresponding workflow requires them.

The first end-to-end slice should demonstrate:

1. Source configuration and collection.
2. Article persistence and deduplication.
3. Article classification and entity extraction.
4. Event candidate generation and event association.
5. Evidence and claim recording.
6. Structured analysis.
7. Report generation and provenance.
8. Publication decision and review handling.
9. Idempotent delivery.
10. Workflow execution tracking and recovery.

The logical model may contain additional entities that are implemented later.

## 28. Open Architecture Decisions

The following topics have published ADRs or supporting specifications, but publication does not mean that the underlying proposal has been accepted:

1. Initial relational database engine and engine-specific operating configuration — GENI-ADR-005.
2. Event identity, matching thresholds, merge, and split policy — GENI-ADR-011.
3. Embedding generation and semantic search storage — GENI-ADR-012.
4. Article full-text acquisition, retention, and licensing — GENI-ADR-013.
5. Source reliability context and source-independence assessment — GENI-ADR-008 and GENI-SRC-010. Calibration remains an evidence/evaluation task, not an uncreated ADR topic.
6. Publication review, target-adapter capabilities, idempotency/reconciliation, correction, replacement, and withdrawal — GENI-ADR-004, GENI-ADR-014, and GENI-ADR-016.
7. Market data sources and observed impact classification — GENI-ADR-015.
8. Reprocessing, checkpoint, and workflow recovery guarantees — GENI-ADR-016.
9. Multilingual content storage, translation, and reporting policy — GENI-ADR-018.
10. Retention, archival, and deletion requirements — GENI-ADR-013 and its rights/retention contracts.
11. Separate methodology, scales, calibration, and evaluation for event importance, economic relevance, and economic impact — GENI-ADR-019.
12. Scheduling and worker execution strategy — an implementation/deployment decision to be resolved against workload evidence and GENI-OPS-013.

Before implementation, the relevant ADR must be formally accepted where it governs an architectural decision, and the corresponding detailed contract or policy must be completed. The existence of an ADR file is not a substitute for approval. Conversely, an existing Proposed ADR must not be described as a missing ADR or trigger duplicate ADR creation.

## 29. Acceptance Criteria

The data model is acceptable for implementation when:

1. Articles and events have separate identities.
2. Multiple articles can be associated with one event.
3. Article deduplication is separate from event matching.
4. Event matching decisions are traceable.
5. Event merge and split operations preserve identity history.
6. Article processing stages and versions can be inspected.
7. Topic classifications retain method and taxonomy version.
8. Entity aliases and unresolved mentions can be represented.
9. Claims and their source observations have explicit relationships.
10. Evidence has traceable origin and location where available.
11. Analysis inputs and evidence references are traceable.
12. Reports retain their article, evidence, analysis, and event references.
13. Report versions are preserved.
14. Multi-event reports are supported.
15. Publication decisions are separately recorded from actual publication operations.
16. Held reports can enter a real review workflow, and review approval cannot bypass a new effective publication decision.
17. Publication, replacement, and withdrawal operations have immutable history, idempotency, attempt records, and a stable key that scopes each publication chain within a target.
18. Uncertain external publication outcomes require reconciliation before retry.
19. Delivery operations have separate idempotency and retry history and cannot change publication state.
20. Publication-link deliveries reference a confirmed effective publication.
21. Processing runs and steps support recovery.
22. LLM usage and known costs can be recorded.
23. Unknown values remain distinct from zero or false.
24. Critical state changes are transactionally consistent.
25. Migrations are versioned and tested.
26. Repository interfaces hide database-specific implementation details.
27. Backup and restore procedures are documented and tested.
28. Content retention respects applicable rights and licensing restrictions.
29. Event importance is independently represented and versioned.
30. Economic relevance is separately represented with direct/indirect/contextual, not-established, and unknown outcomes.
31. Economic impact is represented by channel, direction, magnitude where supported, time horizon, evidence status, and uncertainty.
32. Scores and assessment confidence have distinct semantics, methodology/schema versions, and calibration metadata where applicable.
33. Scheduled workflow execution can be tracked and made idempotent where scheduling is implemented.
34. The model is consistent with Document 02 component and interface contracts.
35. Content access, processing, storage, external transmission, quotation, and distribution can be authorized independently under versioned rights policies; unknown rights do not authorize restricted operations.

## 30. Final Design Statement

The data model is designed around economic events, their source publications, and the evidence required to understand them.

It preserves the distinction between articles, events, claims, observations, evidence, analyses, reports, publication decisions, reviews, and deliveries.

It also provides explicit support for event identity decisions, processing recovery, analytical provenance, historical integrity, and operational traceability.

The initial persistence implementation should remain deliberately simple, but must not sacrifice traceability, idempotency, or the ability to evolve.

PostgreSQL is the Project Owner-selected target relational engine. Exact PostgreSQL configuration and tooling, production activation, semantic storage, content retention, and other unresolved architecture choices remain subject to their respective qualification and formal ADR approval gates.

This document defines the intended logical data model. Physical schema design and migration implementation must follow the approved architecture and the component contracts defined in Document 02.

## 31. Privacy Domain Records and Personal Data Lineage

These are logical model contracts proposed by GENI-ADR-020 and required by GENI-PRIV-014. A logical record does not mandate one physical table; approved persistence design may use aggregates, normalized tables, immutable events or protected references.

| Logical record | Conceptual fields and purpose |
|---|---|
| PersonalDataInventory | inventory ID, category, system/store, purpose, source/owner, classification, retention-policy reference, discovery method, review time |
| ProcessingPurpose | stable purpose ID, description, permitted operations/categories, approval state, effective interval, policy version |
| PrivacyProcessingBasis | basis ID, purpose, jurisdiction, basis type/reference, assessment evidence, effective interval and review state; legal basis is a qualified-review input |
| DataSubjectReference | opaque linkage ID, verification state/reference and restricted identity-map reference; no direct identifier in ordinary lineage/telemetry |
| PrivacyAuthorizationDecision | decision ID, subject reference where needed, purpose, operation, data category, provider/model, region, policy version, transfer assessment, outcome/reason codes, decided/expiry/revocation timestamps and audit reference |
| DataSubjectRequest | request ID, subject reference, request type, intake channel/time, verification state, jurisdiction-policy reference, status, idempotency key, response reference |
| DataSubjectRequestAction | action ID, request ID, target, action type/state, attempts, outcome, exception/hold reference, verification evidence and timestamps |
| PrivacyDeletionRecord | deletion ID, request/action, target/lineage scope, tombstone/state, processor acknowledgements, backup reconciliation and exception evidence |
| ProcessorRegister | processor/subprocessor, service/provider, role assessment, purposes, categories, region, retention, training-use posture, deletion capability, contract/safeguard references and approval/review state |
| InternationalTransferAssessment | assessment ID, origin/destination, recipient, categories, transfer mechanism/safeguards reference, risk outcome, approver, effective interval and review state |
| PrivacyImpactAssessment | assessment ID, processing scope, necessity/proportionality analysis, risks/mitigations, residual risk, reviewer/approval, triggers and status |

### 31.1 PersonalDataLineage

PersonalDataLineage is distinct from Article provenance, ArticleOriginRelationship, Content Rights lineage and generic ProcessingRun history. It links an opaque DataSubjectReference and data-category reference to source/authoritative records; ProcessingRun/Step and purpose/policy version; minimized prompt/provider request reference; destination processor/provider, model and region; derived artifacts (embeddings, translations, analyses, reports, caches, evaluation artifacts); and downstream copies/exports and deletion/restriction state. Edges record stable identifiers, edge type, timestamps, source/destination references, purpose, policy version and integrity metadata. Subject-to-record resolution is separately restricted and audited.

### 31.2 Derived-data and deletion semantics

Rights actions traverse lineage to discover dependent artifacts and destinations. Distinguish authoritative deletion, derived deletion/rebuild, restriction/suppression, correction propagation, processor-side request/acknowledgement, cache invalidation, backup tombstone/reconciliation and legally retained exceptions. Record outcomes per target; never claim global completion if a required target is unavailable or unverifiable.

Backups may expire under an approved schedule. A deletion ledger/tombstone must survive restore; restored data must be reconciled before serving or reprocessing. Retention periods and legal-hold rules remain approved policy inputs.

### 31.3 Constraints

- Subject identifiers and linkage maps require restricted access and approved protection.
- PersonalDataLineage is not ArticleLineage or ContentRightsLineage.
- ContentRightsService and PrivacyProcessingAuthorization are independent.
- LLM/provider requests retain authorization decision IDs, purpose, provider/region and provenance.
- PrivacyAuthorizationDecision is immutable, scoped, time-bounded and independently auditable; stale/revoked/unknown decisions cannot authorize processing.
- No physical schema, legal basis, retention duration or jurisdictional rule is selected here.

See Documents 02, 08, 09, 12, 13 and 14; GENI-ADR-020.

---


**Revision Note (v1.47):** Aligns the persistence strategy with the Project Owner's PostgreSQL target selection recorded in GENI-ADR-005 v1.5. Replaces SQLite-specific initial-storage guidance with PostgreSQL qualification requirements; production activation and exact tooling remain gated by PoC evidence and formal ADR acceptance.

**Revision Note (v1.48):** Records the source-aware mixed-retention direction selected by the Project Owner: revision-level content availability distinguishes full/partial retained content from metadata-only/unavailable records, and full/partial persistence requires current source/content-specific permission. GENI-ADR-013 remains Proposed; this is not a source license or production authorization.

**Revision Note (v1.49):** Separates retained-content SHA-256 from the semantic ArticleRevision fingerprint, defines the no-content hash/reference invariant, and clarifies current-revision-only idempotency so a later return to prior content remains a new chronological revision. No production rights or persistence approval is implied.

**Revision Note (v1.50):** Adds a source-reported author snapshot to ArticleRevision so the Article current projection and historical revision preserve the same author semantics. The author is included in the semantic revision fingerprint and remains subject to source-specific metadata permissions.

**Revision Note (v1.51):** Makes ArticleRevision's rights provenance explicit as immutable operation/content-scope RightsAssessment references rather than a single ambiguous `rights_status` field. Adds the complete historical publication-time/metadata snapshot and server creation timestamp; operation-specific rights remain authoritative in RightsAssessment records.

**Revision Note (v1.52):** Clarifies that Article.rights_status is a non-authoritative summary projection only. Every restricted operation must consult the current operation- and content-scope-specific RightsAssessment; the summary field cannot grant permission.

**Revision Note (v1.53):** Removes stale pre-ADR SQLite assumptions from backup/recovery guidance and distinguishes the owner-selected PostgreSQL target from the still-gated production configuration and activation.


**Revision Note (v1.54):** Makes the Source configuration aggregate version explicit in the logical Source field inventory. This aligns the data model with the immutable SourceRecord version and the optimistic-concurrency contract for configuration updates; it does not define a version encoding or authorize configuration mutation.


**Revision Note (v1.55):** Replaces the stale statement that EventMatchCase lifecycle rules are undefined with the canonical lifecycle reference in Document 17, Section 6. The data model now aligns with the implemented pure state machine and its tests while preserving ADR, authorization, persistence, and production-activation gates.


**Revision Note (v1.56):** Aligns EventMatchCandidate creation, evaluation, and interruption semantics with the executable lifecycle in Document 17, Section 7. The data model no longer describes those already-specified rules as undefined; candidate evaluation remains immutable and policy-versioned.


**Revision Note (v1.57):** Adds the missing EventIdentityOperationAllocation logical record so MERGE/SPLIT can explicitly map affected articles, claims, evidence, and market observations to the canonical/successor Event identities or preserve them as unresolved. Clarifies type-specific repository validation and transaction consistency; this is a logical data-model correction, not an executable implementation or ADR approval.


**Revision Note (v1.58):** Defines durable per-report-version impact tracking for Event identity operations. Requires discovery through both primary Event references and ReportEventLinks, preserves immutable report/publication/delivery history, and separates report correction, external publication replacement/withdrawal, and recipient correction into their respective services. This is a logical contract update; implementation and ADR approval remain gated.


**Revision Note (v1.59):** Completes the report-impact lifecycle by adding append-only EventIdentityOperationReportImpactHistory, an explicit RESOLVED state, and a required durable work-item reference while remediation is outstanding. The identity operation cannot complete with an unassigned report remediation. This remains a logical contract, not an implementation claim.


**Revision Note (v1.60):** Places EventIdentityOperationReportImpactHistory under the Event Identity Operations section (§7.5), before EventRelationship (§7.6), correcting its structural placement without changing the lifecycle contract.

**Revision Note (v1.61):** Defines a durable Event Identity reconciliation work-item mapping over the existing ProcessingRun/ProcessingStep/ProcessingStepAttempt/ExecutionLease model, including typed target metadata, deterministic input fingerprints, supported step kinds, retry/fencing semantics, and a uniqueness rule. This avoids introducing a parallel queue entity; persistence adapters and method-level contracts remain required, and no Event Identity capability is enabled.


**Revision Note (v1.62):** Clarifies that Event Identity reconciliation may create multiple ProcessingSteps with the same step_name only when each server-derived input fingerprint identifies a distinct operation/work-kind/target/version unit, and adds immutable attempt-number/idempotency uniqueness. This prevents an ambiguous generic step-identity rule from collapsing distinct reconciliation targets or duplicating retries.
