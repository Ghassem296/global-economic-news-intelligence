# Global Economic News Intelligence — Data Model & Storage Design

**Document ID:** GENI-DATA-003
**Version:** 1.3
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

## 3. Persistence Strategy

### 3.1 Initial Relational Storage

SQLite is the proposed initial relational database, subject to formal architecture approval.

The initial implementation should support:

- Local development.
- Single-instance operation.
- Early deployment validation.
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

PostgreSQL is a potential future implementation when operational requirements justify it.

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
          +---- ArticleProcessingRecord
          |
          +---- ArticleTopicClassification
          |
          +---- ArticleEntityMention
          |
          +---- DuplicateCandidate
          |
          +---- ArticleEventLink
                    |
                    +---- Event
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

**Current content ownership rule:** `Article` is the current searchable projection of the latest accepted article revision. `ArticleRevision` is the historical record of meaningful content changes. Updates to the current projection and creation of a revision must occur atomically. The application must not maintain two independently editable copies of the same current content.

### 5.5 ArticleRevision

Preserves meaningful article changes.

Fields:

- `id`
- `article_id`
- `revision_number`
- `title`
- `content_reference`
- `content_hash`
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
- A revision must identify the text representation to which its hashes and offsets refer.

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
| importance_score | decimal/null | Importance assessment |
| economic_relevance_score | decimal/null | Economic relevance assessment |
| score_policy_version | string/null | Scoring policy version |
| first_observed_at | timestamp | First system observation |
| last_updated_at | timestamp | Latest meaningful update |
| resolved_at | timestamp/null | Resolution time |
| created_at | timestamp | Creation time |
| updated_at | timestamp | Last modification |

Constraints:

- Event identifiers remain stable during ordinary updates.
- Event identity changes must use explicit merge or split operations.
- Lifecycle transitions must be validated against an approved transition policy.
- Scores must include a documented scale and assessment version.
- Missing occurrence time must remain null.
- `UPDATED` is not a persistent lifecycle state. It is represented through event history and update events.

The event record represents current state. `EventHistory` preserves meaningful prior states.

### 5.7 ArticleEventLink

Associates an article with an event.

Fields:

- `id`
- `article_id`
- `event_id`
- `relationship_type`
- `association_confidence`
- `association_method`
- `matching_policy_version`
- `associated_at`
- `is_active`
- `deactivated_at`
- `decision_reference`
- `metadata`

Relationship types may include:

- `INITIAL_REPORT`
- `FOLLOW_UP`
- `CONFIRMATION`
- `CONTEXT`
- `CONTRADICTION`
- `RELATED_DEVELOPMENT`

Constraints:

- An active association must not be duplicated.
- Confidence must use a documented range and semantics.
- Association method and policy version must be recorded.
- Deactivation must preserve historical association information.
- A rejected match must not be represented as an active association.
- Association changes must be traceable to an event-matching decision or an explicit authorized correction.

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

### 7.1 EventMatchCandidate

Represents a candidate match between an incoming article or observation and an existing event.

Fields:

- `id`
- `article_id`
- `candidate_event_id`
- `lexical_similarity`
- `semantic_similarity`
- `entity_overlap_score`
- `temporal_compatibility_score`
- `geographic_compatibility_score`
- `overall_score`
- `matching_method`
- `matching_policy_version`
- `candidate_status`
- `decision_reason`
- `created_at`
- `decided_at`

Candidate states may include:

- `PENDING`
- `ACCEPTED`
- `REJECTED`
- `INCONCLUSIVE`
- `SUPERSEDED`

The system must preserve the difference between:

- A candidate match.
- An accepted association.
- A rejected association.
- A newly created event.

A similarity score is not, by itself, a final event identity decision.

The matching policy must define how candidate signals are interpreted and when a candidate requires review or creation of a new event. Exact thresholds and decision rules require a formal architecture decision or approved policy.

### 7.2 Event Identity Operations

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

### 7.3 EventRelationship

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
- `ECONOMIC_IMPACT`
- `MARKET_IMPLICATIONS`
- `RISK_ASSESSMENT`
- `EVIDENCE_ASSESSMENT`
- `SCENARIO_ANALYSIS`

An analysis should be immutable after successful completion.

A new analysis execution must create a new record or version rather than silently overwrite a completed result.

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

### 9.4 Analysis Output Classification

Analytical content must distinguish:

- Observed facts.
- Source-attributed claims.
- AI-generated interpretation.
- Forecasts and scenarios.
- Explicitly unknown or unavailable information.

A free-text analysis field alone is insufficient for important structured conclusions.

Structured analysis output should use a versioned schema. The schema must identify material claims, uncertainty, and supporting evidence references.

### 9.5 Market Impact Evidence

Market impact must not be inferred as observed fact when no market data is available.

The model must distinguish at least:

1. `OBSERVED_MARKET_REACTION` — supported by an identified market data source.
2. `SOURCE_REPORTED_REACTION` — reported by a publication or other source.
3. `AI_INFERRED_IMPACT` — analytical interpretation without direct observed market data.
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

A market observation must preserve its measurement time, source, unit, and baseline context. It must not imply causation between an event and a market movement without an explicit analytical assessment.

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
- `created_at`

Possible change types:

- `CREATED`
- `TITLE_UPDATED`
- `DESCRIPTION_UPDATED`
- `STATUS_CHANGED`
- `IMPORTANCE_UPDATED`
- `ENTITY_ADDED`
- `ARTICLE_ASSOCIATED`
- `ARTICLE_DISASSOCIATED`
- `ANALYSIS_COMPLETED`
- `RESOLVED`
- `REOPENED`
- `MERGED`
- `SPLIT`

History should be append-only from the application perspective.

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

Represents a human review or review action.

Fields:

- `id`
- `report_id`
- `publication_decision_id`
- `review_status`
- `reviewer_reference` nullable
- `assigned_at` nullable
- `due_at` nullable
- `review_reason`
- `review_notes`
- `created_at`
- `completed_at`
- `metadata`

Review states may include:

- `PENDING`
- `IN_PROGRESS`
- `APPROVED`
- `CHANGES_REQUESTED`
- `REJECTED`
- `CANCELLED`

A review record must support a real operational review queue.

The operational review queue must support:

- Finding pending reviews.
- Assigning or reassigning a reviewer.
- Recording review ownership.
- Recording due dates where required.
- Recording review actions and outcomes.
- Identifying overdue or abandoned reviews.
- Creating a new publication decision after a material review outcome where required.

Review history must not be silently overwritten.

Reviewer identity and authorization must be managed by the application's security layer.

### 11.8 PublicationRecord

Represents one logical operation against a publication target. It is distinct from a PublicationDecision and from a DeliveryRecord.

Fields:

- `id`
- `report_id`
- `publication_decision_id` nullable for withdrawal operations
- `publication_target_reference`
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

Operation semantics and constraints:

- `PUBLISH` requires an effective `PUBLISH` or `PUBLISH_WITH_CAVEATS` decision and must not reference a previous publication as its target.
- `REPLACE` requires an effective publication decision for the new report version and a reference to the earlier successful publication it intends to supersede.
- `WITHDRAW` requires a reference to an existing publication and explicit authorization/reason information. Its publication-decision reference may be null because withdrawal is an authorized lifecycle operation rather than permission to publish content.
- The target publication and new operation must refer to the same configured publication target.
- A stable idempotency key must be unique within the target and operation scope.
- The same logical operation must reuse its idempotency key on retry.
- A successful replacement supersedes the earlier publication. A failed or uncertain replacement leaves the earlier confirmed publication effective.
- A successful withdrawal records that the target has withdrawn the referenced publication. A failed or uncertain withdrawal must not be treated as complete.
- A timeout or transport failure with an unknown external outcome must produce `RECONCILIATION_REQUIRED`; the operation must be reconciled before another side-effecting attempt.
- The current effective publication for a target is derived from the chain of successful operations. Failed, cancelled, or unresolved operations must not silently replace the last confirmed effective state.
- Publication operation history must remain append-oriented and auditable. Corrections must not overwrite previous report content or publication records.

### 11.9 PublicationAttempt

Represents one external execution attempt for a PublicationRecord.

Fields:

- `id`
- `publication_record_id`
- `attempt_number`
- `started_at`
- `completed_at` nullable
- `outcome`
- `external_reference` nullable
- `error_category` nullable
- `error_summary` nullable
- `reconciliation_reference` nullable
- `metadata`

Each attempt must be separately traceable. Attempt outcomes should distinguish confirmed success, confirmed failure, and unknown external outcome. An unknown outcome must trigger reconciliation rather than an automatic blind retry.

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
| `article_event_links` | Article-event associations |
| `duplicate_candidates` | Article duplicate candidates |
| `events` | Current event state |
| `event_match_candidates` | Event matching candidates |
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
- Event match candidate lookup by status and score.
- Duplicate candidate lookup.
- Claim lookup by event and observation.
- Evidence lookup by source, article, and origin type.
- Analysis lookup by event and type.
- Report lookup by event and version.
- Report-event lookup in both directions.
- Publication decision lookup by report and decision.
- Review queue lookup by status, assignment, due date, and creation time.
- Delivery lookup by status and scheduled time.
- Delivery attempt lookup by delivery operation.
- Processing run lookup by type, status, target, and lease expiry.
- Processing step lookup by run and status.
- LLM usage lookup by provider, model, and time.
- Schedule lookup by active status and next execution time.

### 16.2 Unique Constraints

Where applicable, enforce:

- Source-scoped external article identity.
- Article revision number uniqueness.
- Active article-event association uniqueness.
- Canonical article pair uniqueness for duplicate candidates.
- Event-specific report version uniqueness.
- Source and checkpoint type uniqueness.
- Processing step identity within a run.
- Delivery idempotency key uniqueness within its scope.
- Schedule occurrence uniqueness.
- Event identity operation input/output uniqueness.
- Entity alias uniqueness where the language and alias type make it unambiguous.

All uniqueness rules involving nullable fields must be tested against the selected database engine.

### 16.3 Referential Integrity

Foreign keys should protect ordinary relational relationships.

Polymorphic references must be explicitly documented and validated by the application layer.

Deletion policies must protect historical evidence, reports, and provenance. Cascading deletion must not silently remove records referenced by published reports.

## 17. Score and Confidence Semantics

Scores must not be treated as interchangeable values.

For each score type, the system must document:

- What is being measured.
- Valid range and scale.
- Whether higher values indicate stronger or weaker results.
- Calculation or assessment method.
- Policy or model version.
- Whether the value is calibrated.
- Whether it is comparable across models, sources, or time periods.

At minimum, separate semantics must be defined for:

- Source reliability.
- Article duplicate similarity.
- Event matching similarity.
- Entity resolution confidence.
- Claim-evidence relevance.
- Claim verification confidence.
- Event importance.
- Economic relevance.
- Analytical confidence.

A score must not be interpreted as a probability unless the calculation and calibration support that interpretation.

Missing scores must remain null.

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
- `EventMatchCandidateRepository`
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
- Event matching decisions.
- Event merge and split history.
- Many-to-many article-event relationships.
- Topic classification history.
- Entity aliases and resolution.
- Claim observations and provenance.
- Claim-evidence relationships.
- Evidence location traceability.
- Analysis provenance.
- Analysis input validation.
- Report version uniqueness.
- Multi-event report relationships.
- Published report immutability.
- Publication decision history.
- Review queue state transitions.
- Delivery idempotency.
- Delivery attempt history.
- Processing run and step recovery.
- Expired execution lease handling.
- Atomic event history updates.
- Atomic publication state changes.
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
6. Publication review and correction workflow.
7. Market data sources and observed impact classification.
8. Reprocessing, checkpoint, and workflow recovery guarantees.
9. Multilingual content storage, translation, and reporting policy.
10. Retention, archival, and deletion requirements.
11. Score semantics, calibration, and versioning.
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
17. Publication, replacement, and withdrawal operations have immutable history, idempotency, and attempt records.
18. Uncertain external publication outcomes require reconciliation before retry.
19. Delivery operations have separate idempotency and retry history and cannot change publication state.
20. Processing runs and steps support recovery.
19. LLM usage and known costs can be recorded.
20. Unknown values remain distinct from zero or false.
21. Critical state changes are transactionally consistent.
22. Migrations are versioned and tested.
23. Repository interfaces hide database-specific implementation details.
24. Backup and restore procedures are documented and tested.
25. Content retention respects applicable rights and licensing restrictions.
26. Scores have documented semantics and versioning.
27. Scheduled workflow execution can be tracked and made idempotent where scheduling is implemented.
28. The model is consistent with Document 02 component and interface contracts.

## 30. Final Design Statement

The data model is designed around economic events, their source publications, and the evidence required to understand them.

It preserves the distinction between articles, events, claims, observations, evidence, analyses, reports, publication decisions, reviews, and deliveries.

It also provides explicit support for event identity decisions, processing recovery, analytical provenance, historical integrity, and operational traceability.

The initial persistence implementation should remain deliberately simple, but must not sacrifice traceability, idempotency, or the ability to evolve.

Database engine selection, semantic storage, content retention, and other unresolved architecture choices remain subject to formal ADR approval.

This document defines the intended logical data model. Physical schema design and migration implementation must follow the approved architecture and the component contracts defined in Document 02.