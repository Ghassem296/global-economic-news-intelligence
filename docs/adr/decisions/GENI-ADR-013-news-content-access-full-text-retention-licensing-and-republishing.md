# GENI-ADR-013 — News Content Access, Full-Text Retention, Licensing, and Republishing

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-013  
**Title:** News Content Access, Full-Text Retention, Licensing, and Republishing  
**Version:** 1.7
**Status:** Proposed  
**Date:** 2026-11-18
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence collects and analyzes news articles from multiple publishers, news agencies, official institutions, and other information sources.

The system requires access to source information to support:

- Article discovery and ingestion.
- Article normalization and classification.
- Entity and event extraction.
- Event matching and monitoring.
- Claim and evidence analysis.
- Economic intelligence generation.
- Text, audio, and video report production.

However, access to news content is subject to different technical, contractual, licensing, copyright, and data-retention conditions.

Sources may provide different levels of access:

- Public metadata.
- Headlines and short descriptions.
- RSS feed content.
- API-provided article information.
- Full article text.
- Licensed full-text feeds.
- Paywalled or subscription-based content.
- Official publications and public institutional documents.

These access methods do not necessarily grant identical rights.

For example:

- An RSS feed may expose an article title and excerpt without granting permission to retain or republish the full article.
- A publicly accessible webpage may still be protected by copyright.
- A subscription may permit personal reading but not automated collection or commercial redistribution.
- An API may permit retrieval but restrict persistent storage or third-party processing.
- A content provider may allow analytical use while prohibiting republication.
- A provider may permit temporary processing but require deletion after a specified period.

The system must also distinguish between different processing activities.

Permission to retrieve an article does not automatically imply permission to:

- Store its full text.
- Send its content to an external LLM provider.
- Retain extracted or derived content indefinitely.
- Publish quotations.
- Generate audio or video reproductions.
- Redistribute article content to customers.
- Use the content for purposes outside the original license.

Without explicit content-rights controls, the system may unintentionally retain, process, or redistribute material beyond its permitted scope.

This creates legal, operational, financial, and reputational risks.

The product therefore requires a source-aware content-access and rights-management architecture.

This ADR establishes the proposed principles for content acquisition, processing permissions, retention, deletion, attribution, and republication.

It does not provide a legal determination that any particular source or processing activity is lawful.

## 2. Decision Question

How should Global Economic News Intelligence manage source content so that it can support automated economic intelligence while respecting applicable access conditions, licenses, copyright restrictions, retention requirements, and republication permissions?

Specifically:

1. How should the system distinguish technical accessibility from permitted content use?
2. Which content types may be collected and stored?
3. Under what conditions may full article text be retained?
4. How should content be processed by internal and external LLM services?
5. How should source-specific retention and deletion requirements be enforced?
6. Which derived outputs may be generated from source material?
7. What attribution and citation requirements should apply?
8. How should the system handle quotations, summaries, audio, and video?
9. How should licensing restrictions affect reports delivered to customers?
10. How should permission changes, license expiration, and deletion requests be handled?

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Support multiple news acquisition methods.
- Maintain source-specific content-access information.
- Distinguish metadata access from full-text access.
- Record the legal or contractual basis for permitted processing.
- Support source-specific retention policies.
- Track permission to use content for individual processing activities.
- Support content deletion and retention expiration.
- Preserve source attribution and article provenance.
- Support licensed and unlicensed content under different policies.
- Distinguish internal analysis from external redistribution.
- Prevent unauthorized article republication.
- Preserve the traceability of generated reports to their source material.
- Support changes to source permissions over time.
- Provide auditable records of content-rights decisions.

### 3.2 Technical Constraints

- Content-rights enforcement must be independent of the acquisition provider.
- Rights information must be associated with the relevant source and content artifact.
- Rights checks must occur before restricted processing or storage.
- Retention enforcement must be automated where practical.
- The system must support multiple content-storage policies.
- The design must support temporary processing without persistent full-text storage.
- Content access and rights decisions must be versioned.
- Deletion operations must be recoverable and auditable.
- Rights enforcement must work across ingestion, analysis, storage, and delivery.
- The architecture must not require a particular database or cloud provider.

### 3.3 Business and Product Constraints

- The product provides economic intelligence rather than reproducing news publishers' original products.
- The system may use multiple sources to understand one underlying event.
- Source diversity and independent corroboration must be preserved.
- Reports must communicate relevant information without unnecessarily reproducing protected source material.
- Content-rights restrictions must not silently invalidate the product's core workflow.
- Licensed content may be used when its permissions and costs are justified.
- The architecture must support future commercial distribution.
- The product must be able to operate with sources that provide metadata but not persistent full-text access.

### 3.4 Security and Privacy Constraints

- Retrieved content must be treated as untrusted data.
- Source content must not override system instructions or application policies.
- Content-processing permissions must be checked before external transmission.
- Credentials and subscription tokens must be protected.
- Content deletion must include relevant stored copies and controlled derived artifacts where required.
- Access to restricted content must be limited to authorized application components.
- Logs must not retain unnecessary full article text.
- External processing must follow applicable provider and contractual restrictions.
- Source access mechanisms must be protected against SSRF and unauthorized internal network access.
- Acquisition mechanisms must not bypass authentication, paywalls, or technical access controls.

### 3.5 Operational and Cost Constraints

- Content acquisition must respect source rate limits and access conditions.
- Licensed feeds may introduce recurring costs.
- Full-text storage must have explicit retention and storage-cost policies.
- Rights checks should avoid unnecessary repeated external calls.
- Expired permissions must not remain active because of stale cached configuration.
- Deletion and retention jobs must be observable.
- The system must support source suspension and reactivation.
- Rights-related failures must not silently become successful processing outcomes.

### 3.6 Legal and Content-Rights Constraints

The system must recognize that content rights depend on applicable law, license terms, contractual arrangements, jurisdiction, and the specific use being performed.

Relevant considerations may include:

- Copyright and related rights.
- Database rights where applicable.
- Publisher and news-agency licensing.
- Subscription and API terms.
- Website terms of service.
- Privacy and data-protection requirements.
- Commercial redistribution restrictions.
- Attribution and quotation requirements.
- Data-processing and third-party service agreements.

The system must not assume that public accessibility, RSS availability, subscription access, or successful API retrieval grants unrestricted rights.

Legal requirements must be reviewed for the jurisdictions and business activities relevant to the product.

### 3.7 Explicit Non-Goals

This ADR does not determine:

- Whether a particular publisher's content may legally be collected.
- Whether a particular source license is sufficient for every intended use.
- Universal quotation limits or fair-use thresholds.
- The final legal basis for every source.
- A universal full-text retention period.
- The specific content licensing vendors to use.
- The final legal terms of customer subscriptions.
- The complete privacy policy or terms of service.
- The final storage technology.
- The complete copyright compliance program.

These issues require source-specific review, legal advice where appropriate, and subsequent implementation policies.

## 4. Alternatives Considered

### 4.1 Alternative A: Store All Retrieved Article Content

**Description:**

Collect and retain complete article text whenever it can be technically retrieved.

Use stored content for all subsequent processing, analysis, reporting, and delivery.

**Advantages:**

- Simple initial ingestion architecture.
- Full content is available for repeated analysis.
- Reduced dependency on source availability.
- Easier historical reprocessing.
- Convenient implementation of search and event enrichment.

**Disadvantages:**

- Does not distinguish accessibility from permission.
- May violate source licenses or contractual restrictions.
- Creates unnecessary copyright and redistribution exposure.
- Increases storage requirements.
- Makes deletion and retention compliance more difficult.
- May permit unauthorized third-party processing.
- Does not provide a defensible basis for customer-facing republication.

**Risks:**

- Unauthorized retention.
- Unauthorized commercial use.
- Legal claims and licensing disputes.
- Inability to demonstrate compliance with source-specific conditions.

**Estimated Complexity:** Low initially; High legal and operational risk.

### 4.2 Alternative B: Store Only Metadata and Never Retain Full Text

**Description:**

Collect only basic article metadata, such as:

- Title.
- Publisher.
- Publication time.
- Source URL.
- Available identifiers.
- Limited metadata permitted by the source.

Perform all subsequent analysis using information that can be retrieved again when required.

**Advantages:**

- Reduces persistent full-text storage.
- Limits some content-retention risks.
- Reduces storage requirements.
- Simplifies certain deletion procedures.

**Disadvantages:**

- Some sources may become unavailable.
- Historical reprocessing becomes difficult.
- Source changes may make previous analysis irreproducible.
- Some intelligence tasks require more than metadata.
- Repeated retrieval can increase operational costs.
- Does not eliminate licensing or access restrictions.
- Does not automatically authorize external processing or republication.

**Risks:**

- Incomplete event analysis.
- Loss of historical source context.
- Dependence on continued source availability.
- Misinterpretation of limited excerpts.

**Estimated Complexity:** Low to Medium.

### 4.3 Alternative C: Source-Aware Rights Management With Controlled Content Processing and Retention

**Description:**

Introduce a content-rights management capability that evaluates permissions for each source and relevant content-processing activity.

The system stores only the content artifacts and metadata permitted by the applicable access and licensing conditions.

Processing permissions are evaluated separately for:

- Retrieval.
- Temporary processing.
- Persistent storage.
- External LLM processing.
- Derived analytical use.
- Quotation.
- Audio and video generation.
- Customer-facing republication.

Content retention and deletion are controlled by source-specific policies.

Where permissions are unknown or insufficient, the system applies a restrictive default and may continue with permitted metadata or alternative sources.

**Advantages:**

- Separates technical access from permitted use.
- Supports multiple licensing models.
- Enables controlled full-text retention.
- Supports licensed and restricted sources.
- Provides a foundation for commercial intelligence delivery.
- Improves auditability.
- Allows processing to continue when full-text retention is not permitted.
- Supports future licensing integrations.

**Disadvantages:**

- Requires additional rights metadata and policy enforcement.
- Increases initial architecture and implementation effort.
- Requires ongoing maintenance of source permissions.
- May restrict some processing workflows.
- Requires explicit handling of unknown or conflicting rights information.

**Risks:**

- Incorrect rights metadata may permit unauthorized processing.
- Outdated permissions may cause non-compliant retention.
- Overly restrictive rules may reduce useful source coverage.
- Incomplete deletion propagation may leave restricted artifacts.

**Estimated Complexity:** Medium to High.

### 4.4 Alternative D: Use Only Fully Licensed Content Providers

**Description:**

Restrict the system to providers that supply explicit commercial rights for the required acquisition, storage, processing, and redistribution activities.

**Advantages:**

- More explicit contractual permissions.
- Potentially simpler rights verification.
- Better support for commercial full-text workflows.
- More predictable source access.
- Reduced reliance on ambiguous website access conditions.

**Disadvantages:**

- Potentially high licensing costs.
- Limited source coverage.
- Dependence on a small number of providers.
- Not all relevant economic information is available through licensed providers.
- Contractual restrictions may still apply to derived outputs and republication.

**Risks:**

- Vendor dependency.
- Cost increases.
- Coverage gaps.
- Incorrect assumptions about the scope of a license.

**Estimated Complexity:** Medium; potentially high recurring cost.

## 5. Evaluation and Comparison

| Evaluation Criterion | Alternative A | Alternative B | Alternative C | Alternative D |
|---|---|---|---|---|
| Rights Awareness | Low | Medium | High | High within licensed scope |
| Full-Text Availability | High | Low | Policy-dependent | High within license |
| Historical Reprocessing | High | Low | Policy-dependent | Policy-dependent |
| Legal Risk Control | Low | Medium | High if correctly enforced | High if license is sufficient |
| Source Coverage | Potentially High | High | High | Provider-dependent |
| Storage Cost | High | Low | Controlled | Contract-dependent |
| Processing Flexibility | High | Low | High within permissions | License-dependent |
| Commercial Scalability | Risky | Limited | High | High within license |
| Implementation Complexity | Low | Low | High | Medium |
| Vendor Dependency | Low | Low | Low to Medium | High |
| Operational Complexity | Low initially | Low | High | Medium |

### 5.1 Evaluation Priorities

The most important criteria are:

1. Compliance with applicable content rights.
2. Preservation of source provenance.
3. Support for analytical processing.
4. Ability to generate original intelligence outputs.
5. Controlled retention and deletion.
6. Commercial scalability.
7. Cost and source coverage.

The system must not optimize source coverage at the expense of unauthorized content use.

Technical accessibility must not be treated as a substitute for permission.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Source-Aware Rights Management With Controlled Content Processing and Retention.

### 6.1 Architectural Decision

Introduce a source-aware Content Rights Management capability.

Every source and relevant content artifact must have an associated rights and processing policy.

Before performing a restricted operation, the system must evaluate whether the operation is permitted under the available rights information.

The policy must distinguish between:

- Access to information.
- Processing of information.
- Retention of information.
- External transmission of information.
- Creation of derived outputs.
- Redistribution of original or derived content.

The architecture must not treat these activities as one universal permission.

### 6.2 Rights Management Model

The proposed model has four primary dimensions.

**A. Source Rights Profile**

Describes the known rights and access conditions associated with a publisher, provider, feed, or official source.

**B. Content Access Record**

Describes how a specific article or content artifact was obtained and what access conditions applied.

**C. Processing Permission**

Determines whether a particular activity is permitted for the relevant content.

**D. Retention and Deletion Policy**

Defines how long a content artifact may be retained and what must happen when the retention period expires or permission is withdrawn.

The source profile provides defaults, but content-specific contractual conditions must be able to override those defaults.

### 6.3 Separate Access and Usage Permissions

The system must distinguish the following activities:

| Activity | Description |
|---|---|
| `DISCOVERY` | Discovering that an article exists. |
| `METADATA_ACCESS` | Retrieving permitted article metadata. |
| `FULL_TEXT_ACCESS` | Retrieving the article's full text. |
| `TEMPORARY_PROCESSING` | Temporarily processing content without persistent retention. |
| `PERSISTENT_STORAGE` | Retaining full or partial content. |
| `INTERNAL_ANALYSIS` | Using content to support internal intelligence tasks. |
| `EXTERNAL_LLM_PROCESSING` | Sending content to an external LLM provider. |
| `DERIVED_OUTPUT_GENERATION` | Creating summaries, classifications, or other derived outputs. |
| `TRANSLATION` | Translating source content or creating a translated derivative; this permission is distinct from general analysis and distribution. |
| `EMBEDDING_GENERATION` | Creating vector or other machine-readable representations from content; storage and external-provider transmission require separate applicable checks. |
| `QUOTATION` | Including excerpts from source content. |
| `AUDIO_TRANSFORMATION` | Transforming content into spoken audio or narration. |
| `VIDEO_TRANSFORMATION` | Transforming content into video, including narration, visuals, or captions. |
| `CUSTOMER_DISTRIBUTION` | Delivering derived outputs to customers. |
| `CONTENT_REPUBLICATION` | Reproducing original or substantial source content. |

Permission for one activity must not automatically grant permission for another. The operation catalog is canonical across Documents 02 and 03: rights assessments must use these exact operation identifiers, and each request must identify the operation, content scope, policy version, and enforcement point. `DISCOVERY` is distinct from `METADATA_ACCESS`; translation and embedding generation are distinct from generic derived-output generation; audio and video transformation are separate operations. External transmission for translation or embedding generation must additionally pass `EXTERNAL_LLM_PROCESSING` or the applicable external-provider permission check.

For a report, briefing, or other composite output containing source-derived material from multiple articles or providers, `CUSTOMER_DISTRIBUTION` permission must be established for every exact source-derived content scope included in the outbound representation. A RightsAssessment for one source, article, license, or derived artifact does not authorize material from another. The distribution decision must preserve the complete set of exact allowed RightsAssessment references used to authorize that scope. If any included source-derived item has missing, unknown, expired, revoked, denied, or review-required permission, that item must be excluded from the authorized payload or the requested distribution must be denied/routed for review. A reduced payload may be authorized only when its actual content is reduced to the same explicit scope recorded by the authorization decision. This rule applies to text, audio, video, and other customer-facing transformations.

For example, permission for `INTERNAL_ANALYSIS` does not automatically authorize `CONTENT_REPUBLICATION`.

### 6.4 Rights Assessment States

Rights assessments should distinguish between the following states:

| State | Meaning |
|---|---|
| `ALLOWED` | Sufficient documented permission exists for the specific operation. |
| `DENIED` | The operation is prohibited or explicitly disallowed. |
| `UNKNOWN` | Permission has not been established. |
| `EXPIRED` | A previously valid permission has expired. |
| `REVOKED` | A permission has been withdrawn. |
| `REQUIRES_REVIEW` | Available information is insufficient or conflicting and requires review. |

The system must not convert `UNKNOWN` into `ALLOWED` merely because a source is publicly accessible.

An operation requiring permission must not proceed when the relevant status is `DENIED`, `UNKNOWN`, `EXPIRED`, `REVOKED`, or `REQUIRES_REVIEW`.

A separately authorized metadata-only or restricted processing path may remain available.

### 6.5 Source Rights Profiles

Each source should have a structured rights profile.

Proposed attributes include:

- Source identifier.
- Publisher or provider name.
- Source category.
- Acquisition method.
- Source website or feed reference.
- Applicable license or contractual reference.
- Rights documentation reference.
- Permitted content types.
- Permitted processing activities.
- Storage permissions.
- Retention conditions.
- Attribution requirements.
- Quotation conditions.
- Redistribution restrictions.
- External processing restrictions.
- Rate limits.
- License start date.
- License expiration date.
- Rights review status.
- Last verification timestamp.
- Rights policy version.

A source may have multiple rights profiles when different feeds, products, contracts, or content types have different permissions.

### 6.6 Acquisition Policy

The acquisition pipeline must distinguish between source discovery and content retrieval.

The proposed acquisition sequence is:

1. Identify the source and acquisition mechanism.
2. Retrieve source-level access and rights configuration.
3. Check whether the requested acquisition method is permitted.
4. Retrieve permitted metadata or content.
5. Record the acquisition method and relevant source identifiers.
6. Associate the retrieved content with its rights profile.
7. Determine which subsequent operations are permitted.
8. Store or process the content according to those permissions.

The system must not:

- Bypass paywalls.
- Circumvent authentication or technical access controls.
- Ignore source-specific rate limits.
- Assume that RSS access grants full-text rights.
- Assume that public webpage access grants persistent storage rights.
- Treat a subscription intended for personal reading as permission for automated commercial redistribution.
- Use undocumented scraping behavior as a substitute for a licensing agreement.

When full text cannot be obtained through a permitted mechanism, the system should use available metadata, authorized excerpts, licensed alternatives, or other permitted information.

### 6.7 Full-Text Retention Policy

Full article text must only be retained when the relevant rights profile permits persistent storage.

The system should support at least the following retention modes:

| Retention Mode | Description |
|---|---|
| `NO_PERSISTENT_CONTENT` | Do not persist full article text. |
| `TEMPORARY_PROCESSING_ONLY` | Allow temporary processing with a defined expiration. |
| `LIMITED_RETENTION` | Retain content for a specified period. |
| `LICENSED_PERSISTENT_STORAGE` | Retain content within the scope and duration of a valid license. |
| `UNRESTRICTED_BY_DOCUMENTED_POLICY` | Use only when an appropriate documented basis establishes that the relevant storage restrictions do not apply. |

The last mode must not be assigned merely because content is publicly accessible.

Retention policies must define:

- Maximum retention duration.
- Start of the retention period.
- Expiration behavior.
- Deletion requirements.
- Whether content can be reprocessed.
- Whether backups require delayed deletion.
- Whether derived artifacts are subject to additional restrictions.
- Whether legal holds or contractual exceptions apply.

Retention periods must be configured according to the applicable rights and operational requirements rather than using one universal duration.

### 6.8 Temporary Processing

Some sources may permit processing but not persistent storage.

The architecture should support temporary content processing where permitted.

For example:

1. Retrieve authorized article content.
2. Process it in memory or controlled temporary storage.
3. Extract permitted structured information.
4. Persist only permitted results and provenance.
5. Remove temporary content according to the applicable policy.

Temporary processing must not become an indirect method of unauthorized persistent retention.

Temporary files, caches, queues, logs, and provider-side retention must also be considered.

### 6.9 External LLM Processing

Sending source content to an external LLM provider is a separate processing activity.

Before transmission, the system must evaluate:

- Whether external processing is permitted.
- Whether the source license restricts third-party processing.
- Whether the provider's data-retention terms are acceptable.
- Whether submitted content may be used for provider training.
- Whether the provider acts as an appropriate processor or service provider under applicable arrangements.
- Whether data residency or jurisdictional restrictions apply.
- Whether the content can be minimized or redacted.

The execution layer defined by GENI-ADR-006 must receive only content that has passed the relevant rights checks.

Where external processing is not permitted, the system may use an authorized internal processing path or a metadata-only workflow.

Successful LLM execution does not establish permission to submit the source content.

### 6.10 Derived Content and Original Source Content

The architecture must distinguish original source content from derived analytical artifacts.

Examples of derived artifacts include:

- Topic classifications.
- Entity extraction results.
- Event associations.
- Structured claims.
- Evidence references.
- Analytical summaries.
- Economic impact assessments.
- Internal intelligence notes.
- Generated report sections.

The fact that an artifact is generated by an LLM does not automatically make it free of copyright, licensing, contractual, or other restrictions.

Derived artifacts must retain provenance and any applicable usage restrictions.

The system should avoid storing unnecessary verbatim source passages in derived outputs.

Rights policies must define which derived artifacts may be retained and distributed.

### 6.11 Summarization and Original Analysis

The product should focus on producing original economic intelligence rather than reproducing publisher content.

Reports should prioritize:

- Verified event facts.
- Cross-source evidence.
- Relevant economic context.
- Market observations.
- Analytical interpretation.
- Explicit uncertainty.
- Source references.

Summaries should not function as substitutes for the original article or reproduce substantial protected expression.

A summary must not be assumed permissible solely because it is shorter than the source article.

The applicable rights and legal requirements must be considered for the actual content, purpose, and distribution context.

### 6.12 Attribution and Source References

Published intelligence outputs should provide source attribution where appropriate and required.

A source reference should support traceability through attributes such as:

- Publisher or source name.
- Article title, where permitted.
- Source URL.
- Publication time.
- Retrieval time.
- Relevant license attribution requirements.
- Access or content restrictions where necessary.

Attribution is not a replacement for permission.

Providing a link to the original article does not automatically authorize the reproduction of its contents.

Source references should remain available even when full article text must be deleted, subject to applicable retention and privacy requirements.

### 6.13 Quotation Policy

Quotations must be treated as a separate usage category.

Before including an excerpt in a report, the system must consider:

- Applicable permission or license.
- Applicable legal exceptions.
- Purpose of the quotation.
- Amount and significance of the quoted material.
- Attribution requirements.
- Commercial distribution context.
- Source-specific contractual restrictions.

The system must not implement one universal word-count limit and treat it as legally sufficient for every publisher and jurisdiction.

Where permission is unknown or insufficient, reports should use original analysis and source references rather than reproducing quotations.

### 6.14 Audio and Video Transformation

Audio and video generation introduce additional content-use considerations.

Transforming an article into spoken narration or video may reproduce or communicate protected source expression.

Therefore:

- Audio and video workflows must use content that has passed the relevant rights checks.
- A license permitting text analysis must not automatically authorize audio or video reproduction.
- Source quotations must follow applicable quotation permissions.
- Generated narration must not reproduce substantial protected article text without appropriate authorization.
- Visual presentation must respect source image and media rights.
- Customer distribution must be covered by the relevant permissions.

The phased delivery strategy in GENI-ADR-010 must account for these requirements.

### 6.15 Rights Expiration, Revocation, and Deletion

The system must support changes to content permissions over time.

When a license expires, is revoked, or changes:

1. Identify affected sources and content artifacts.
2. Identify processing and retention permissions affected by the change.
3. Stop prohibited new operations.
4. Identify stored content that must be deleted or restricted.
5. Identify affected derived artifacts where required.
6. Apply deletion or access restrictions according to the relevant policy.
7. Preserve permitted audit and provenance records.
8. Record the action and its execution status.
9. Verify completion of required deletion operations.

Deletion must consider:

- Primary content storage.
- Temporary files.
- Caches.
- Search indexes.
- Queues and intermediate artifacts.
- Backups according to applicable deletion policies.
- External processing providers where deletion is required and supported.

The system must distinguish successful deletion from a requested but incomplete deletion.

Where legal or contractual retention exceptions apply, those exceptions must be documented and restricted.

### 6.15.1 Derived-Rights Invalidation and Downstream Reauthorization

A permission change must propagate through the provenance dependency graph of every affected DerivedArtifact and report item. A permission to access, store, process, translate, embed, quote, transform, or distribute source content is operation-specific; permission for one operation does not automatically survive revocation or authorize another operation.

ContentRightsService must identify the exact source/article revision, DerivedArtifact versions, transformations, and downstream report items that depend on the changed permission. It must invalidate or mark stale affected assessments and prevent new processing or distribution until the dependency chain has been re-evaluated. An existing CUSTOMER_DISTRIBUTION assessment is not sufficient if a required upstream permission has expired, been revoked, or materially changed.

Before dispatch, ReportDelivery must require:
- The exact linked CUSTOMER_DISTRIBUTION RightsAssessment set to remain current, effective, and ALLOWED.
- The upstream rights dependencies captured in each source-derived artifact's provenance to remain effective for the operations actually performed.
- A newly evaluated assessment and successor DistributionAuthorizationDecision when a rights change affects the prior authorization scope.

The system must fail closed when dependency status is unknown or cannot be re-evaluated. It must not silently revive or mutate an earlier immutable assessment or authorization decision. A reduced payload may proceed only after prohibited items are actually excluded, the reduced manifest is fingerprinted, and a new complete authorization decision is recorded.

Already completed deliveries remain immutable historical facts. Where a later rights change requires remedial action, the system must initiate the applicable correction, restriction, deletion, or withdrawal workflow; it must not rewrite delivery history or claim that an external recipient's copy was recalled unless that outcome is verified.

### 6.15.2 Deterministic Distribution Fingerprints

Distribution authorization must use reproducible fingerprints so that the authorized scope can be compared with the scope actually dispatched.

The authorized_content_scope_fingerprint is the SHA-256 digest, represented as 64 lowercase hexadecimal characters, of a versioned ContentScopeManifest serialized as UTF-8 using RFC 8785 JSON Canonicalization Scheme (JCS). The manifest contains:
- A manifest schema version and exact immutable report-version reference.
- One entry per atomic outbound content item, with a stable item identifier.
- Immutable ArticleRevision or DerivedArtifact/version references.
- Transformation and output-language identifiers where applicable.
- The SHA-256 digest of the exact immutable artifact bytes of each item (UTF-8 bytes for text; exact stored bytes for binary media). A content edit, normalization, transcode, or recompression creates a new immutable artifact version and digest.
- Complete typed source-scope lineage for every source-derived item.

Set-valued arrays must be sorted by stable identifiers before canonical serialization. Arrays whose order changes meaning must retain their semantic order. Content bytes must not be normalized before item-level hashing. The same manifest rules apply when the scope is reduced.

The rights_assessment_set_fingerprint is the SHA-256 digest of a versioned array containing the complete immutable RightsAssessment references required by every source-derived manifest item. Each entry identifies the assessment and version, exact operation, typed content-scope reference, outcome, policy/profile version, and validity boundary. Sort entries by (content_scope_reference, operation, rights_assessment_id, assessment_version) before JCS serialization. Only current ALLOWED CUSTOMER_DISTRIBUTION assessments qualify. A source-derived manifest requires a non-empty complete set; a manifest with no source-derived items has no rights links and a null rights-assessment-set fingerprint.

The DeliveryRecord content_scope_fingerprint must equal the authorized manifest fingerprint. The digest of the channel-specific serialized outbound request is a separate outbound_payload_sha256; it must never be compared directly with the manifest fingerprint. The dispatcher must prove that the serialized request was constructed exclusively from the exact authorized manifest items and must reject additions, omissions, substitutions, or changed transformations before creating an external side effect.

### 6.15.3 Canonicalization and Transaction Requirements

All services must use one shared canonicalization implementation and test vectors. They must reject unsupported schema versions, duplicate item or assessment identifiers, missing required references, invalid Unicode, non-finite numbers, and ambiguous timestamps. Timestamps included in manifests must use UTC RFC 3339 with exactly millisecond precision and a trailing Z (YYYY-MM-DDTHH:mm:ss.sssZ). Internal UUIDs use lowercase canonical hyphenated form; external/source identifiers preserve their exact source-defined, case-sensitive representation and include a namespace. SHA-256 digests use 64 lowercase hexadecimal characters. Unicode strings are preserved exactly as stored and are not normalized during canonicalization. JCS object-key ordering is authoritative; application code must not invent a second JSON key-ordering rule.

The DistributionAuthorizationDecision and its complete immutable RightsAssessment link set must be committed in one UnitOfWork transaction. Fingerprints must be computed from the exact records committed by that transaction. A failed transaction must leave neither a partially linked decision nor an externally dispatchable authorization.

### 6.16 Syndication and Source Independence

Multiple publishers may distribute identical or substantially similar content originating from the same news agency.

The system must preserve source provenance and distinguish content duplication from independent corroboration.

In particular:

- Syndicated copies must not automatically count as independent evidence.
- Multiple URLs do not necessarily represent multiple independent sources.
- Similar or identical content must retain its original attribution where identifiable.
- Article deduplication must not erase the identities of contributing publishers.
- Content licenses must be evaluated independently for the relevant source and distribution channel.

This policy must remain consistent with GENI-ADR-002 and GENI-ADR-008.

### 6.17 Recommendation Summary

The recommended architecture establishes source-aware content-rights management, controlled full-text retention, explicit processing permissions, and separate republication controls.

The core rule is:

**Technical access to source content does not automatically grant permission to store, process, transform, or redistribute that content.**

## 7. Final Decision

This ADR is currently **Proposed**.

**Recommended Alternative:** Alternative C.

**Owner-Selected Direction (2026-11-26):** The Project Owner selected the source-aware, mixed-retention policy represented by Alternative C. Full or partial article text may be retained only where the applicable source/content-specific persistent-storage permission is current and verified. Where that permission is absent, unknown, expired, revoked, or unverifiable, the system may retain only metadata and other content expressly permitted for the relevant operation, or record the revision as unavailable. Permission to retrieve or analyze content does not imply permission to persist, transmit externally, quote, or republish it.

**Selected Alternative:** Alternative C is the Project Owner's selected architectural direction. Formal ADR acceptance remains pending.

**Decision Status:** Proposed

**Decision Owner:** Project Owner

**Approved By:** Not yet approved

**Approval Date:** N/A

**Decision Rationale:**

Alternative C is recommended because it provides the necessary controls for source acquisition, full-text retention, processing, and commercial intelligence delivery while preserving the event-centric architecture.

It allows the system to use sources with different access and licensing conditions without assuming unrestricted rights.

The Project Owner must explicitly accept or reject this recommendation.

**Conditions or Restrictions:**

- Rights must be evaluated separately for each relevant activity.
- Unknown permissions must not be treated as approved.
- Full-text retention must be controlled by explicit policy.
- External LLM processing requires a separate permission check.
- Attribution must not be treated as a substitute for permission.
- Republication must have its own authorization.
- Retention and deletion requirements must be enforceable.
- Legal and contractual assumptions must be reviewed before production use.

**Deferred Questions:**

- Which content providers should be licensed initially?
- Which sources permit persistent full-text storage?
- Which sources permit external LLM processing?
- What retention periods apply to each source?
- Which derived artifacts may be retained after source-text deletion?
- What customer-facing attribution format is required?
- Which legal jurisdictions require specific policy treatment?
- Which license-management responsibilities belong to operations or the Project Owner?
- How should rights restrictions affect historical reports and generated media?

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Clear separation between technical access and permitted use.
- Better control over full-text retention.
- Explicit permission checks before external processing.
- Improved source provenance.
- Support for different licensing models.
- Reduced risk of unauthorized republication.
- Better foundation for commercial distribution.
- More controlled deletion and retention operations.
- Greater transparency around source limitations.

### 8.2 Negative Consequences

- Additional rights-management infrastructure.
- Increased metadata and policy-maintenance requirements.
- Potential reduction in available full-text content.
- Additional processing checks.
- Increased operational responsibility.
- Possible licensing and legal review costs.

### 8.3 Technical Trade-Offs

The architecture prioritizes explicit rights enforcement over unrestricted content availability.

This means some sources may only contribute metadata or limited permitted information.

Historical reprocessing may be restricted when the original content can no longer be retained.

The system must preserve permitted analytical information and provenance without assuming that every source artifact can be retained indefinitely.

### 8.4 Operational Consequences

Operations must support:

- Source rights configuration.
- License monitoring.
- Permission expiration.
- Source suspension.
- Content retention monitoring.
- Deletion execution and verification.
- External provider compliance.
- Rights-related incident handling.
- Audit records.

### 8.5 Product and Business Consequences

The product can use a broader range of sources while maintaining explicit boundaries around content use.

However, some sources may require licensing costs or may not permit all desired processing activities.

Product capabilities must be aligned with actual content permissions rather than assuming that every source can support every delivery format.

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Unauthorized full-text retention | Medium | High | Source-specific retention policies and pre-storage rights checks |
| Unauthorized external LLM processing | Medium | High | Explicit external-processing permission checks |
| Incorrect rights configuration | Medium | High | Documented source evidence, review, and versioned policies |
| Expired license remains active | Medium | High | Expiration monitoring and automatic restriction |
| Incomplete deletion | Medium | High | Deletion workflows, verification, and audit records |
| Unauthorized republication | Medium | High | Separate publication permission checks |
| Attribution requirements omitted | Medium | Medium | Structured attribution metadata and report validation |
| Derived content retains restricted material | Medium | High | Provenance and derived-artifact policy |
| Excessive dependence on licensed providers | Medium | Medium | Multiple sources and alternative permitted acquisition paths |
| Rights policy changes break workflows | Medium | Medium | Graceful restricted processing and operational monitoring |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- Source Registry.
- News Acquisition Service.
- Article Ingestion Pipeline.
- Content Normalization.
- Content Rights Management.
- Article Storage.
- Temporary Content Processing.
- LLM Execution Layer.
- Analysis Pipeline.
- Evidence and Provenance Management.
- Report Generation.
- Audio and Video Generation.
- Publication and Delivery.
- Retention and Deletion Services.
- Audit and Observability.

### 9.2 Affected Data Models and Interfaces

Proposed domain entities include:

- `Source`
- `SourceRightsProfile`
- `SourceLicense`
- `ContentAccessRecord`
- `ContentArtifact`
- `ContentUsagePermission`
- `ContentRetentionPolicy`
- `RightsAssessment`
- `RightsPolicyVersion`
- `ContentDeletionRequest`
- `ContentDeletionRecord`
- `ContentAttribution`
- `ContentProcessingRecord`
- `DerivedArtifact`
- `ContentUsageAuditRecord`

Potential application operations include:

- `evaluate_content_permission`
- `check_source_access`
- `record_content_access`
- `authorize_content_storage`
- `authorize_external_processing`
- `authorize_content_distribution`
- `apply_content_retention_policy`
- `schedule_content_deletion`
- `execute_content_deletion`
- `verify_content_deletion`
- `record_content_attribution`
- `suspend_source_processing`

These are conceptual names. Final interfaces and persistence requirements must be defined during detailed design.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-001 | Related to | Establishes the event-centric intelligence architecture. |
| GENI-ADR-002 | Related to | Defines article deduplication and source-preserving event matching. |
| GENI-ADR-006 | Depends on / Related to | LLM execution must respect external content-processing permissions. |
| GENI-ADR-008 | Related to | Defines evidence provenance and uncertainty representation. |
| GENI-ADR-010 | Related to | Audio and video delivery must respect content transformation and distribution permissions. |
| GENI-ADR-014 | Related to | Human review and publication correction procedures may handle rights-related restrictions. |
| GENI-ADR-016 | Related to | Retention, deletion, and recovery operations require reliable execution. |
| GENI-ADR-018 | Related to | Translation and multilingual processing may introduce additional content-use considerations. |
| GENI-ADR-009 | Related to | Acquisition modes and polling must observe source access restrictions and terms. |
| GENI-ADR-012 | Related to | Embedding and semantic retrieval may create derived artifacts subject to source rights and retention policy. |

These relationships do not imply that the related ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work

If accepted, implementation should include:

1. Define the source rights profile.
2. Define content-access records.
3. Define processing permission contracts.
4. Define retention policy contracts.
5. Add rights checks to the acquisition pipeline.
6. Add rights checks before persistent full-text storage.
7. Add rights checks before external LLM processing.
8. Separate original content from derived artifacts.
9. Implement source attribution records.
10. Implement retention expiration.
11. Implement content deletion workflows.
12. Add license expiration monitoring.
13. Add audit records for rights decisions.
14. Add restricted-processing paths for metadata-only sources.
15. Add validation to report and media-generation workflows.
16. Add tests for unknown, denied, expired, and revoked permissions.
17. Document source-specific legal and contractual assumptions.

### 10.2 Migration or Compatibility Requirements

If the system already stores article content:

- Existing sources must be assigned a rights-review status.
- Unverified sources must not automatically receive unrestricted permissions.
- Existing content should be assessed against available source terms and licenses.
- Content with unresolved retention permission may require restriction, review, or deletion.
- Existing reports must preserve permitted source references and provenance.
- Migration must not silently assume that previous collection establishes ongoing permission.
- Existing derived artifacts must be evaluated where source restrictions require it.

### 10.3 Dependencies

Potential dependencies include:

- Source registry.
- Acquisition connectors.
- Content storage.
- Rights policy configuration.
- LLM execution layer.
- Report generation.
- Retention scheduler.
- Deletion infrastructure.
- Audit and observability.
- Legal and contractual review.
- Content provider agreements.

### 10.4 Implementation Sequence

**Stage 1 — Rights-Aware Source Registry**

- Define source rights metadata.
- Identify access methods.
- Define unknown and restricted states.
- Document initial source policies.

**Stage 2 — Acquisition Enforcement**

- Check permissions before content retrieval.
- Record acquisition provenance.
- Separate metadata access from full-text access.
- Prevent prohibited access methods.

**Stage 3 — Storage and Retention Controls**

- Define permitted storage modes.
- Implement retention configuration.
- Implement expiration checks.
- Add content deletion operations.

**Stage 4 — Processing Controls**

- Add internal-processing permission checks.
- Add external LLM permission checks.
- Separate original content and derived artifacts.
- Record processing provenance.

**Stage 5 — Publication and Delivery Controls**

- Add attribution validation.
- Add quotation checks.
- Add derived-output restrictions.
- Add audio and video permission checks.
- Add customer-distribution validation.

**Stage 6 — Monitoring and Compliance Verification**

- Monitor permission expiration.
- Monitor retention and deletion.
- Audit rights decisions.
- Test restricted-source scenarios.
- Review licensing assumptions.

### 10.5 Verification Requirements

Verification must demonstrate that:

- A source can provide metadata without granting full-text storage permission.
- Publicly accessible content is not automatically treated as unrestricted.
- Unknown permissions block restricted operations.
- Expired permissions prevent prohibited new operations.
- External LLM processing is checked separately.
- Temporary processing does not create unauthorized persistent copies.
- Full-text retention follows configured policies.
- Deletion operations are traceable and verifiable.
- Attribution metadata can be preserved independently of full-text retention.
- Unauthorized quotations and republication are blocked by policy.
- Derived artifacts retain their provenance.
- Syndicated articles are not automatically treated as independent corroboration.
- Rights restrictions do not silently disappear during report generation.

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Every registered source has an identifiable rights-review state. | Source registry tests |
| AC-02 | Technical access and permitted content use are represented separately. | Domain model inspection |
| AC-03 | Metadata access does not automatically authorize full-text storage. | Permission tests |
| AC-04 | Unknown permissions cannot authorize restricted operations. | Policy tests |
| AC-05 | Persistent full-text storage requires an applicable permission. | Storage integration tests |
| AC-06 | Retention policies define expiration behavior. | Retention tests |
| AC-07 | External LLM processing has a separate permission check. | Execution integration tests |
| AC-08 | Temporary processing does not silently become persistent retention. | Lifecycle tests |
| AC-09 | Content deletion operations are auditable. | Deletion workflow tests |
| AC-10 | Expired or revoked permissions prevent prohibited new operations. | Policy and integration tests |
| AC-11 | Attribution information can be retained independently of full article text where permitted. | Data model tests |
| AC-12 | Quotation and republication are separate permission categories. | Publication policy tests |
| AC-13 | Derived artifacts preserve source provenance. | Provenance tests |
| AC-14 | Audio and video workflows respect relevant content permissions. | Media workflow tests |
| AC-15 | Syndicated content does not automatically count as independent corroboration. | Source relationship tests |
| AC-16 | Rights-related restrictions produce observable outcomes. | Operational tests |
| AC-17 | Source rights policy changes can be versioned and audited. | Policy history tests |
| AC-18 | Restricted sources can continue through permitted metadata-only workflows. | End-to-end tests |

Implementation verification is deferred until this ADR is formally accepted and the corresponding capabilities are implemented.

## 12. Review and Reconsideration

### 12.1 Review Triggers

This ADR should be reviewed when:

- The product begins commercial distribution.
- New content providers or licensing agreements are introduced.
- Source terms materially change.
- New jurisdictions become relevant.
- External LLM processing arrangements change.
- Audio or video delivery introduces new content-use requirements.
- Retention or deletion requirements change.
- Legal review identifies additional restrictions.
- The product introduces new forms of customer-facing content.

### 12.2 Review Schedule

**Review Date:** Not scheduled.  
**Review Owner:** Project Owner.

### 12.3 Reconsideration Conditions

The recommendation should be reconsidered if a different content-rights architecture can demonstrate equivalent permission enforcement, traceability, retention control, and commercial suitability with lower overall complexity.

Any replacement decision must preserve the separation between technical access and permitted content use.

## 13. References and Supporting Evidence

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Establishes the product's intelligence and reporting objectives. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines acquisition, analysis, and delivery component boundaries. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines article, source, evidence, and storage requirements. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Establishes implementation stages and dependencies. |
| `docs/05-architecture-decision-records.md` | Internal | Defines architectural decision governance. |
| `GENI-ADR-002` | Related Proposed ADR | Defines article deduplication and source provenance considerations. |
| `GENI-ADR-006` | Related Proposed ADR | Defines provider-independent LLM execution. |
| `GENI-ADR-008` | Related Proposed ADR | Defines evidence provenance and uncertainty. |
| `GENI-ADR-010` | Related Proposed ADR | Defines phased audio and video delivery. |
| Applicable source licenses and provider agreements | External contractual evidence | Must establish the actual permissions applicable to each source. |
| Applicable copyright and data-protection requirements | External legal evidence | Must be evaluated for the relevant jurisdictions and activities. |

No specific source license or legal permission is claimed by this proposal.

Source-specific rights and legal requirements must be verified before production use.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-17 | Proposed | Initial proposal covering source access, full-text retention, licensing, processing, attribution, and republication. | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Synchronized version history and end-of-document metadata with the current Proposed ADR revision; no approval status changed. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |
| 1.3 | 2026-11-18 | Proposed | Canonicalized operation permissions, separated translation, embedding, audio, and video transformations, and aligned decision/review authority with the Project Owner role. | AI Architecture Assistant |
| 1.4 | 2026-11-18 | Proposed | Defined complete per-source CUSTOMER_DISTRIBUTION rights coverage for composite reports and other multi-source derived outputs; clarified reduced-scope authorization. | AI Architecture Assistant |
| 1.5 | 2026-11-18 | Proposed | Defined deterministic content-scope and rights-assessment fingerprints, upstream-rights revocation propagation, fail-closed reauthorization, and atomic persistence requirements. | AI Architecture Assistant |
| 1.6 | 2026-11-18 | Proposed | Clarified exact immutable artifact-byte hashing for text and binary media, timestamp precision, and identifier canonicalization. | AI Architecture Assistant |
| 1.7 | 2026-11-26 | Proposed | Recorded the Project Owner's selection of source-aware mixed retention (Alternative C) while preserving the formal ADR acceptance and source-specific legal/contractual permission gates. | Project Owner direction recorded by AI Architecture Assistant |

---

**End of ADR**

**ADR ID:** `GENI-ADR-013`  
**File:** `GENI-ADR-013-news-content-access-full-text-retention-licensing-and-republishing.md`  
**Version:** 1.6  
**Status:** Proposed