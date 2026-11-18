# Global Economic News Intelligence — Data Model & Storage Design

**Document ID:** GENI-DATA-003
**Version:** 1.12
**Status:** Draft — Under Architecture Review
**Project:** Global Economic News Intelligence
**Last Updated:** 2026-11-18

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

SQLite is a candidate for the initial relational persistence proof-of-concept, not a selected production engine. The initial engine must be chosen under GENI-ADR-005 after measuring the expected workload, concurrent writers, locking and transaction behavior, backup/restore needs, deployment model, and operational capacity. PostgreSQL remains an alternative for the initial selection if those measurements require it.

The selected initial implementation should support:

- Local development and the intended deployment model.
- Relational integrity.
- Versioned migrations.
- Transactional updates.
- Controlled database connection lifecycle.

The implementation must explicitly configure and test:

- Foreign key enforcement.
- Transaction isolation and boundaries.
- Busy timeout and lock handling.
- Connection management.
- Backup and restore behavior.
- Migration execution.
- Appropriate indexes.
- Async access and write serialization strategy.

WAL mode may be considered after validating concurrency, deployment, and backup requirements. It must not be enabled without testing its operational implications.

SQLite concurrency limitations must be documented. Concurrent asynchronous workflows must not assume unrestricted concurrent writes.

### 3.2 Future Relational Storage

PostgreSQL is an alternative initial engine as well as a possible future implementation. Whether it is selected initially or introduced later must follow the workload proof-of-concept and formal approval under GENI-ADR-005.

Possible triggers include:

- Multiple application instances.
- Higher write concurrency.
- Multiple independent workers.
- Larger datasets.
- More advanced operational and backup requirements.

Migration must preserve domain behavior and repository contracts.

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

Event
  |
  +---- EventHistory
  |
  +---- EventRelationship
  |
  +---- EventEntityLink
  |
  +---- Claim
                           |      |
                           |      +---- ClaimObservation
                           |      |
                           |      +---- ClaimEvidenceLink
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
| reliability_profile | JSON/null | Documented source assessment context |
| collection_config | JSON | Non-secret source configuration |
| is_active | boolean | Whether collection is enabled |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

Constraints:

- Source identifiers must be stable.
- Source URL validation is mandatory.
- Credentials and secrets must not be stored in ordinary configuration fields.
- Reliability information must have documented semantics.
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

Represents a known relationship between information sources.

Fields:

- `id`
- `source_id_a`
- `source_id_b`
- `relationship_type`
- `confidence`
- `evidence_reference`
- `created_at`
- `updated_at`
- `metadata`

Relationship types may include:

- `SAME_OWNER`
- `SYNDICATES_CONTENT`
- `REPUBLISHES`
- `SHARES_ORIGINAL_REPORTING`
- `AFFILIATED_WITH`
- `UNKNOWN_RELATIONSHIP`

Constraints:

- Source pairs must use a canonical ordering or equivalent uniqueness rule.
- Relationships must not be inferred from domain similarity alone.
- Relationship confidence and supporting evidence must be recorded when available.
- Unknown independence must not be interpreted as confirmed independence.

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
| content_hash | string/null | Current normalized content fingerprint |
| content_availability | enum/string | Available, partial, metadata-only, unavailable |
| rights_status | enum/string | Content access and retention classification |
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

The exact treatment of nullable unique values must be verified for each database implementation.

**Current content ownership rule:** `Article` is the current searchable projection of the latest valid persisted article revision. `ArticleRevision` is the historical record of meaningful content changes. Updates to the current projection and creation of a revision must occur atomically. The application must not maintain two independently editable copies of the same current content.

### 5.5 ArticleRevision

Preserves meaningful article changes.

Fields:

- `id`
- `article_id`
- `revision_number`
- `title`
- `content_reference`
- `content_hash`
- `content_normalization_version`
- `summary`
- `language`
- `observed_at`
- `change_reason`
- `rights_status`
- `metadata`

Constraints:

- `(article_id, revision_number)` must be unique.
- Repeated collection of unchanged content must not create a revision.
- Material changes must preserve the previous revision.
- Content references must comply with the project's content retention and licensing policy.
- A revision must identify the text representation and content-normalization version to which its hashes and offsets refer.

`content_reference` may point to relationally stored content or an approved external content store. The physical storage method is an implementation decision.

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

Represents a possible duplicate relationship between two articles.

Fields:

- `id`
- `article_id_a`
- `article_id_b`
- `similarity_score`
- `matching_method`
- `matching_policy_version`
- `decision`
- `decision_reason`
- `created_at`
- `reviewed_at`
- `metadata`

Possible decisions:

- `PENDING`
- `CONFIRMED_DUPLICATE`
- `NOT_DUPLICATE`
- `SUPERSEDED`

Constraints:

- The same article must not be compared with itself.
- The article pair must be stored in a canonical order or protected by an equivalent uniqueness rule.
- Duplicate confirmation must not erase the identity or provenance of either original article.
- Duplicate detection must remain distinct from event matching.
- Similarity scores must identify their method and policy version.

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
- `development_key` — stable within the ArticleRevision and identifying the development being resolved
- `scope_description`
- `case_status`
- `effective_decision_id` — nullable pointer to the current effective EventMatchDecision; a projection updated transactionally when a new decision is recorded
- `created_at`
- `closed_at`
- `metadata`

Case states may include `OPEN`, `PENDING_REVIEW`, `RESOLVED`, `CLOSED`, and `CANCELLED`. The case is the unit of candidate evaluation, final decision, and human review. A case must not be reused for a materially different article revision or development scope. The effective-decision pointer is a mutable current-state projection; historical EventMatchDecision records remain immutable.

### 7.2 EventMatchCandidate

Represents one existing Event considered as a possible match within an EventMatchCase. Candidate generation and evaluation do not establish an association.

Fields:

- `id`
- `case_id`
- `candidate_event_id`
- `lexical_similarity`
- `semantic_similarity`
- `entity_overlap_score`
- `temporal_compatibility_score`
- `geographic_compatibility_score`
- `overall_score`
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

A candidate score is not a decision confidence and must not be interpreted as one.

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
- Decision confidence, candidate similarity, and reviewer certainty are separate measurements and must not be substituted for one another.

### 7.4 Event Matching Case and Decision Constraints

- Every EventMatchCandidate must belong to exactly one EventMatchCase.
- Every EventMatchCase must identify exactly one ArticleRevision and one development scope.
- `(case_id, candidate_event_id, matching_policy_version, candidate_input_fingerprint)` must be unique for idempotent candidate evaluation while permitting historical evaluations under changed inputs or policy versions.
- An evaluated EventMatchCandidate is immutable; a new evaluation creates a new candidate record whose `supersedes_candidate_id`, when present, references the prior evaluation of the same candidate Event in the same case.
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

Event merging and splitting must preserve stable identifiers and historical traceability.

A merge operation must record:

- The surviving event identifier.
- The identifiers of merged events.
- The reason for merging.
- The decision method and confidence, where applicable.
- The time of the operation.
- The resulting article and entity associations.

A split operation must record:

- The original event identifier.
- The new event identifiers.
- The reason for splitting.
- The reassignment of article-event relationships.
- The decision method and time.

The logical operation is represented by `EventIdentityOperation`.

Fields:

- `id`
- `operation_type`
- `reason`
- `decision_method`
- `decision_confidence`
- `policy_version`
- `created_at`
- `metadata`

Possible operation types:

- `MERGE`
- `SPLIT`
- `IDENTITY_CORRECTION`

The event input and output relationships must be stored through explicit relational link entities:

**EventIdentityOperationInput**

- `id`
- `operation_id`
- `event_id`
- `role`

**EventIdentityOperationOutput**

- `id`
- `operation_id`
- `event_id`
- `role`

This avoids relying on JSON arrays as the only representation of event identity relationships.

Constraints:

- The same event must not be an input and output of the same operation unless the operation type explicitly permits it.
- Operation inputs and outputs must be validated by the application layer.
- Event identity operations and affected association changes must be committed atomically.
- The system must not silently delete or reuse event identifiers after a merge or split.
- Survivor-selection and aliasing rules require a formal event identity policy.

### 7.6 EventRelationship

Represents relationships between distinct events.

Relationship types may include:

- `RELATED_TO`
- `CAUSED_BY`
- `TRIGGERED_BY`
- `PART_OF`
- `FOLLOWED_BY`
- `ESCALATION_OF`
- `CONTINUATION_OF`

Fields:

- `id`
- `source_event_id`
- `target_event_id`
- `relationship_type`
- `confidence`
- `direction`
- `policy_version`
- `created_at`
- `metadata`

Constraints:

- Self-referential relationships must be rejected unless explicitly supported by a documented rule.
- Directed relationship types must preserve direction.
- Related events must not be merged solely because a relationship exists.
- Relationship cycles must be handled according to the semantics of the relationship type.

## 8. Claims and Evidence

### 8.1 Claim

Represents a factual assertion, attributed statement, estimate, or forecast.

Fields:

- `id`
- `claim_text`
- `claim_type`
- `attribution`
- `verification_status`
- `confidence`
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

Verification states:

- `UNVERIFIED`
- `SUPPORTED`
- `CONTRADICTED`
- `PARTIALLY_SUPPORTED`
- `DISPUTED`

A claim must not be considered verified merely because an LLM labels it credible.

A claim's verification status must be based on recorded evidence assessments and an explicit evaluation policy.

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

### 8.7 Evidence Independence

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
- `event_id`
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

A market observation must preserve its measurement time, source, unit, and baseline context. It records a market measurement; it does not establish that an event caused the movement. Any causal interpretation must be a separate analysis with its own evidence, methodology, and uncertainty.

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

Event lifecycle states and allowed transitions must be defined in the event lifecycle policy and approved through architecture governance.

The data layer must not independently invent lifecycle transitions.

A transition must be validated by the domain/application layer and recorded in EventHistory within the same transaction as the event update.

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

Connects reports to source articles.

Fields:

- `id`
- `report_id`
- `article_id`
- `reference_type`
- `created_at`

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
- `reviewer_reference` nullable
- `assigned_at` nullable
- `due_at` nullable
- `review_reason`
- `review_notes`
- `review_outcome` nullable
- `created_at`
- `completed_at`
- `metadata`

Review states may include:

- `PENDING`
- `IN_PROGRESS`
- `COMPLETED`
- `CANCELLED`

Review types identify the subject and required follow-up, including publication review and event-matching review. The exact type vocabulary and authorization matrix must be finalized under ADR-014.

Constraints and behavior:

- Exactly one typed subject must be identified by `subject_type` and `subject_reference`; the reference must be validated by the application layer where a database foreign key cannot express the polymorphic relationship.
- For publication review, the subject and related decision must resolve to the relevant report version and PublicationDecision.
- For event-matching review, the subject must identify an EventMatchCase and the related decision must identify the EventMatchDecision under review.
- Review completion records the reviewer, time, and outcome. It does not mutate the related decision.
- An event-matching review outcome that changes the effective result creates a new EventMatchDecision referencing the previous effective decision.
- A publication review outcome that changes publication eligibility creates a new PublicationDecision.
- Review history must not be silently overwritten. Reassignment and status changes must be auditable.
- Reviewer identity and authorization must be managed by the application's security layer.

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

## 12. Delivery Records

### 12.1 DeliveryRecord

Represents a logical delivery operation for a report or a notification related to a report.

Fields:

- `id`
- `report_id`
- `publication_record_id` nullable
- `delivery_mode`
- `channel`
- `destination_reference`
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

Constraints:

- An idempotency key must be present for externally visible delivery operations.
- The idempotency key must be unique within its relevant destination and operation scope.
- Retries must not create duplicate external deliveries when the destination supports idempotency.
- Delivery attempts must remain traceable.
- A `PUBLICATION_LINK` delivery must reference a PublicationRecord whose publication operation is confirmed successful and still effective for that target.
- `REPORT_CONTENT` or `NOTIFICATION` delivery may reference a PublicationRecord when relevant, but must be independently authorized by the applicable distribution policy.
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

### 12.3 Delivery State Consistency

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
- `lease_expires_at`
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
- `lease_expires_at`
- `next_retry_at`
- `completed_at`
- `attempt_number`
- `error_category`
- `error_summary`
- `metadata`

A step must be safely repeatable or explicitly marked as non-repeatable.

Completed step outputs should be reusable when the input fingerprint and relevant processing versions have not changed.

A step with an expired lease may be considered for recovery only after the application layer verifies that the previous execution is no longer active.

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
- `prompt_version`
- `schema_version`
- `input_tokens` nullable
- `output_tokens` nullable
- `total_tokens` nullable
- `estimated_cost` nullable
- `currency` nullable
- `duration_ms` nullable
- `outcome`
- `recorded_at`
- `metadata`

Unknown usage or cost must remain null, not zero.

Usage records should support cost reporting, provider comparison, budget enforcement, and operational evaluation.

Provider-specific usage metadata may be retained in JSON, but commonly queried values should have explicit fields.

Every recorded LLM operation should be traceable to the Shared LLM Execution Layer and, where applicable, to its processing run, step, or analysis.

### 13.6 Schedule

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

### 13.7 ScheduledExecution

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

The physical vector representation is not fixed by this document.

Embeddings may be stored in an approved vector-capable database, a compatible extension, or another search service.

A dedicated vector database is not a mandatory Phase 1 dependency.

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
| `source_health_records` | Source health history |
| `source_relationships` | Known source relationships |
| `articles` | Current normalized article projection |
| `article_revisions` | Article revision history |
| `article_topic_classifications` | Topic classification history |
| `article_entity_mentions` | Extracted entity mentions |
| `entities` | Resolved entities |
| `entity_aliases` | Alternative entity names |
| `article_event_links` | Decision-authorized article-event associations |
| `event_match_cases` | Per-revision, per-development event-resolution cases |
| `event_match_decisions` | Immutable case-level event matching outcomes |
| `duplicate_candidates` | Article duplicate candidates |
| `events` | Current event state |
| `event_match_candidates` | Candidate events evaluated within a matching case |
| `event_history` | Event change history |
| `event_relationships` | Relationships between events |
| `event_identity_operations` | Event merge and split operations |
| `event_identity_operation_inputs` | Input events to identity operations |
| `event_identity_operation_outputs` | Result events from identity operations |
| `event_entity_links` | Event entities |
| `claims` | Logical claims |
| `event_claim_links` | Claim-event relationships |
| `claim_observations` | Claim source observations |
| `evidence` | Evidence records |
| `evidence_locations` | Precise evidence provenance |
| `claim_evidence_links` | Claim-evidence relationships |
| `analyses` | Analytical results |
| `analysis_evidence_links` | Analysis provenance |
| `analysis_inputs` | Analysis input references |
| `market_observations` | Optional observed market data |
| `reports` | Report versions |
| `report_event_links` | Report-event relationships |
| `report_evidence_links` | Report evidence references |
| `report_article_links` | Report article references |
| `report_analysis_links` | Report analysis references |
| `publication_decisions` | Publication policy history |
| `review_records` | Human review records |
| `publication_records` | Publish, replace, and withdraw operations |
| `publication_attempts` | External publication attempt and reconciliation history |
| `delivery_records` | Logical delivery operations |
| `delivery_attempts` | Delivery retry history |
| `processing_runs` | Workflow execution records |
| `processing_steps` | Workflow step records |
| `article_processing_records` | Article processing stage history |
| `collection_checkpoints` | Incremental collection state |
| `llm_usage_records` | LLM usage and cost |
| `schedules` | Workflow schedule definitions |
| `scheduled_executions` | Schedule execution history |
| `embedding_records` | Optional semantic representations |

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
- Delivery attempt lookup by delivery operation.
- Processing run lookup by type, status, target, and lease expiry.
- Processing step lookup by run and status.
- LLM usage lookup by provider, model, and time.
- Schedule lookup by active status and next execution time.

### 16.2 Unique Constraints

Where applicable, enforce:

- Source-scoped external article identity.
- Article revision number uniqueness.
- Composite uniqueness of `(article_id, id)` on ArticleRevision for same-Article current-revision references.
- Event match case uniqueness by ArticleRevision and development key.
- Composite uniqueness of `(id, article_revision_id)` on EventMatchCase for case/article-revision consistency.
- Composite uniqueness of `(case_id, id)` on EventMatchCandidate and EventMatchDecision for case-scoped references.
- Candidate evaluation uniqueness by case, candidate Event, matching-policy version, and candidate input fingerprint.
- One effective decision pointer per EventMatchCase.
- At most one direct successor per superseded EventMatchDecision.
- At most one active ArticleEventLink per EventMatchCase, with historical inactive links retained.
- Canonical article pair uniqueness for duplicate candidates.
- Event-specific report version uniqueness.
- Event analysis type and version uniqueness.
- Source and checkpoint type uniqueness.
- Processing step identity within a run.
- Publication operation sequence uniqueness within a target/publication-key chain.
- Publication idempotency key uniqueness within its target/publication-key scope.
- Publication attempt number uniqueness within a publication operation.
- Delivery idempotency key uniqueness within its scope.
- Schedule occurrence uniqueness.
- Event identity operation input/output uniqueness.
- EventMatchDecision selected-candidate and case consistency.
- EventMatchDecision supersession-chain consistency.
- EventMatchCase.effective_decision_id must reference a decision belonging to that same case.
- Entity alias uniqueness where the language and alias type make it unambiguous.

Only one unresolved side-effecting publication operation should be allowed to modify the same target/publication-key chain at a time; enforce this through an appropriate transaction/locking rule or database constraint for the selected engine. Do not serialize unrelated publication keys merely because they share a target.

All uniqueness rules involving nullable fields must be tested against the selected database engine.

### 16.3 Referential Integrity

Foreign keys should protect ordinary relational relationships.

The following composite relationships must be enforced by database constraints where supported, or by application validation inside the same UnitOfWork transaction when the selected database cannot express them directly:

- `Article(current_revision_id, id)` must resolve to an ArticleRevision whose `article_id` is that same Article.
- `EventMatchCase(id, effective_decision_id)` must resolve to `EventMatchDecision(case_id, id)`; the referenced decision must belong to that case.
- `EventMatchDecision(case_id, selected_candidate_id)` must resolve to `EventMatchCandidate(case_id, id)`; a decision cannot select a candidate from another case.
- `ArticleEventLink(event_match_case_id, event_match_decision_id)` must resolve to the same case and decision.
- `ArticleEventLink(event_match_case_id, article_revision_id)` must resolve to the case's exact ArticleRevision.
- The linked `event_id` must equal the `candidate_event_id` selected by the referenced MATCH decision.
- `EventHistory(event_match_case_id, source_event_match_decision_id)`, when both are present, must reference the same case and its NEW_EVENT_CANDIDATE decision.
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

Expired execution leases must be detected and handled through a documented recovery policy.

A workflow must not be resumed concurrently by multiple workers. The execution ownership mechanism must be atomic and must support recovery after process termination.

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

Published reports must preserve sufficient provenance to identify their sources, subject to legal and contractual restrictions.

Deletion or withdrawal requests must not be silently ignored. The system needs an auditable correction, withdrawal, or restricted-retention process.

Where content must be deleted, the system should preserve legally permissible metadata and audit information without retaining prohibited content.

## 23. Repository Contracts

The application layer should depend on domain-oriented repository interfaces.

Initial repository contracts include:

- `SourceRepository`
- `SourceHealthRepository`
- `SourceRelationshipRepository`
- `ArticleRepository`
- `ArticleRevisionRepository`
- `ArticleProcessingRepository`
- `ArticleClassificationRepository`
- `DuplicateCandidateRepository`
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
- `ClaimRepository`
- `ClaimObservationRepository`
- `EvidenceRepository`
- `EvidenceLocationRepository`
- `ClaimEvidenceLinkRepository`
- `AnalysisRepository`
- `AnalysisInputRepository`
- `AnalysisEvidenceLinkRepository`
- `MarketObservationRepository`
- `ReportRepository`
- `ReportEventLinkRepository`
- `ReportEvidenceLinkRepository`
- `ReportArticleLinkRepository`
- `ReportAnalysisLinkRepository`
- `PublicationDecisionRepository`
- `ReviewRepository`
- `PublicationRepository`
- `PublicationAttemptRepository`
- `DeliveryRepository`
- `DeliveryAttemptRepository`
- `ProcessingRunRepository`
- `ProcessingStepRepository`
- `CollectionCheckpointRepository`
- `LLMUsageRepository`
- `ScheduleRepository`
- `ScheduledExecutionRepository`
- `EmbeddingRepository`, when semantic storage is implemented.

Additional repositories may be introduced when implementation needs justify them.

Repository interfaces must expose domain-oriented operations rather than raw SQL.

Transaction boundaries must be managed through a unit-of-work or equivalent application-level transaction mechanism.

Repositories responsible for one aggregate or workflow may expose multiple related operations through a single application-facing contract. The logical entities do not require a one-to-one repository-per-table implementation.

Repository contracts must be consistent with the component interfaces defined in Document 02.

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

Backups must use a method safe for the selected SQLite operating mode.

A restore test is required before backups are considered operationally reliable.

After restoration, workflow recovery must detect incomplete processing runs and determine whether they can safely resume.

External side effects must be reconciled before a restored workflow repeats a delivery or publication operation.

## 26. Testing Requirements

Data-layer tests must cover:

- Foreign key enforcement.
- Unique constraints.
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
- Verification that delivery state changes do not mutate publication state.
- Validation that publication-link delivery references a confirmed effective publication.
- Processing run and step recovery.
- Expired execution lease handling.
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

The following topics require formal ADRs or explicit approval before their implementation is treated as fixed:

1. Initial relational database and SQLite operating configuration.
2. Event identity, matching thresholds, merge, and split policy.
3. Embedding generation and semantic search storage.
4. Article full-text acquisition, retention, and licensing.
5. Source reliability assessment and calibration.
6. Publication review, target-adapter capabilities, idempotency/reconciliation guarantees, correction, replacement, and withdrawal workflow.
7. Market data sources and observed impact classification.
8. Reprocessing, checkpoint, and workflow recovery guarantees.
9. Multilingual content storage, translation, and reporting policy.
10. Retention, archival, and deletion requirements.
11. Separate methodology, scales, calibration, and evaluation for event importance, economic relevance, and economic impact (GENI-ADR-019).
12. Scheduling and worker execution strategy.

Until the relevant decisions are accepted, implementation choices must remain replaceable and must not be presented as approved architecture.

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

## 30. Final Design Statement

The data model is designed around economic events, their source publications, and the evidence required to understand them.

It preserves the distinction between articles, events, claims, observations, evidence, analyses, reports, publication decisions, reviews, and deliveries.

It also provides explicit support for event identity decisions, processing recovery, analytical provenance, historical integrity, and operational traceability.

The initial persistence implementation should remain deliberately simple, but must not sacrifice traceability, idempotency, or the ability to evolve.

Database engine selection, semantic storage, content retention, and other unresolved architecture choices remain subject to formal ADR approval.

This document defines the intended logical data model. Physical schema design and migration implementation must follow the approved architecture and the component contracts defined in Document 02.