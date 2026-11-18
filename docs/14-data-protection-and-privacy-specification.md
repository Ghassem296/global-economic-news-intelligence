# GENI-PRIV-014 — Data Protection and Privacy Specification

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-PRIV-014  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

---

## 1. Purpose, Authority, and Scope

Defines proposed privacy and personal-data protection requirements for GENI. This is an engineering specification, not legal advice, a jurisdiction-specific compliance determination, or a claim of compliance. Applicable obligations depend on operating entities, data subjects, purposes, providers, and deployment locations. Qualified counsel and an accountable privacy owner must determine applicable law, roles, lawful bases, notices, transfer mechanisms, and timelines before production processing. Publishing this proposal does not authorize production processing.

It applies to personal data in public/licensed news, user and customer accounts, reviewer/operator identities, authentication and security telemetry, provider prompts and outputs, evaluation datasets, reports, embeddings, exports, caches, backups, and support artifacts. Public availability does not make personal data unrestricted for collection, profiling, retention, model processing, or republication. Privacy, copyright, database rights, confidentiality, and source terms are separate control dimensions.

## 2. Governance and Accountability

| Role | Responsibility |
|---|---|
| Project Owner / accountable business owner | Approves purposes, risk acceptance, retention policy, and production readiness |
| Privacy lead / designated responsible person | Maintains inventory; coordinates rights requests, privacy reviews, and incident assessment |
| Security owner | Implements access, encryption, logging, containment, and technical safeguards |
| Data/product owner | Documents purpose, fields, necessity, recipients, processors, and retention |
| Engineering and operations | Enforces minimization, access restrictions, deletion propagation, and evidence |
| Legal counsel | Determines applicable law, controller/processor roles, lawful bases, notices, and transfer requirements |
| Processor/subprocessor | Processes only under documented instructions and approved safeguards |

Controller, joint-controller, and processor roles must be assessed for each service and relationship, not inferred from product terminology. Owners, request channels, escalation contacts, and approval authorities must be assigned before production.

## 3. Data Inventory and Classification

A maintained data inventory is a production prerequisite. Each processing activity records ID, data subjects, elements, source, purpose, necessity, lawful basis or authorization, sensitivity, system locations, recipients, processors, transfer locations, retention trigger, deletion method, access roles, risks, and owner.

| Category | Examples | Minimum handling |
|---|---|---|
| Public-source identity data | Names, public roles, quotations, bylines | Purpose-bound collection, attribution, accuracy and context controls |
| Sensitive or special-category data | Health, political opinions, religion, ethnicity, sexual life, union membership, biometrics where applicable | Avoid unless strictly necessary, authorized, and legally reviewed; restrict access |
| Account/contact data | Name, email, authentication identifiers, preferences | Collect only what the enabled service requires; separate from editorial records |
| Reviewer/workforce data | Identity, role, assignment, review action | Role-scoped access, audit, limited retention |
| Security/operational data | IP, device/session identifiers, timestamps, diagnostics | Minimize, aggregate or pseudonymize where possible |
| Model/provider data | Prompts, request metadata, outputs, usage records | Send only approved minimized fields; verify provider and region controls |
| Derived/evaluation data | Embeddings, labels, scores, test cases, report excerpts | Treat as personal if linkable or re-identifiable; inherit restrictions |

Classification applies to raw, normalized, derived, cached, indexed, exported, and backed-up representations. Pseudonymized data remains personal where re-identification is reasonably possible. Do not infer sensitive traits or create unrelated personal profiles.

## 4. Processing Principles and Purpose Control

Every processing activity requires a documented specific purpose and necessity assessment before implementation.

- **Purpose limitation:** No incompatible reuse without documented assessment and required authorization.
- **Data minimization:** Collect, transmit, expose, and retain only necessary fields.
- **Accuracy and context:** Preserve provenance, timestamps, corrections, uncertainty, and distinctions between allegations, claims, and verified facts.
- **Storage limitation:** Define a retention trigger and deletion/review action for each data class.
- **Integrity and confidentiality:** Apply least privilege, encryption, access logging, and controlled exports.
- **Accountability:** Preserve proportionate evidence of policy, access, review, and deletion decisions.
- **Privacy by design/default:** Start new workflows with least-intrusive settings and explicit opt-in where required.

A lawful basis or other applicable authorization must be determined for each purpose and jurisdiction. Consent is not a universal substitute for legal analysis. Public-interest, journalistic, research, legitimate-interest, contractual, or other exceptions must not be assumed without jurisdiction-specific legal review.

## 5. Collection, Editorial Processing, and Transparency

1. Record source identity, acquisition time, collection method, terms, and data-protection restrictions.
2. Limit entity resolution and profiling to documented editorial or service purposes.
3. Preserve source attribution, evidentiary status, uncertainty, correction history, and context for claims about identifiable people.
4. Do not turn material allegations into established facts through automated summarization or repetition.
5. Exclude unnecessary contact details, private identifiers, credentials, and sensitive personal details from public reports.
6. Corrections, withdrawals, and source removals trigger review of affected claims, reports, indexes, caches, and pending distributions.
7. Data concerning children or vulnerable people requires heightened necessity, minimization, access, and legal review.
8. Notices must describe actual purposes, recipients, retention, and transfers; do not assume a generic notice covers every source, provider, or secondary use.

For each activity, document roles, jurisdictions, purpose, necessity, lawful basis, notices, objection/opt-out/withdrawal controls, and any claimed exemption or special regime. Privacy authorization and content-rights authorization are independent gates; both must pass where applicable.

## 6. Retention, Deletion, and Individual Rights

An approved retention schedule is required before production. For each category/activity it defines period or event trigger, purpose, owner, review frequency, legal-hold handling, deletion method, backup expiry, and minimum evidence retained. This document sets no universal number of days; durations must be justified by purpose, law, source terms, operational need, and risk.

Deletion propagation covers primary records, relational references, search indexes, caches, materialized views, derived features, linkable embeddings, prompts/provider artifacts where controllable, exports, evaluation datasets, support attachments, downstream recipients, and backups through documented expiry and restoration-reconciliation controls.

Where immediate deletion from immutable backups is infeasible, isolate data from ordinary use, prevent restoration without reapplying deletion records, and expire backups under the approved schedule. Exceptions for records that must lawfully be retained require documented basis, scope, access restriction, and review/expiry date. Privacy deletion interoperates with source-rights withdrawal and editorial correction while preserving only minimum audit evidence.

A documented data subject request process supports intake, proportionate identity verification, classification, scope discovery, deadline tracking, response approval, secure delivery, legally permitted refusal/restriction rationale, and auditable outcome. Requests may include access, correction, deletion, restriction, objection, portability, or consent withdrawal where applicable. Do not promise every right applies to every record or jurisdiction. Discovery covers source-derived and derived data, recipients, and processors while protecting other people's information and assessing exceptions with counsel.

## 7. Processors, Subprocessors, Model Providers, and International Transfers

Before enabling a processor or model provider, assess purpose, data categories, necessity, security, retention, training/secondary-use terms, personnel access, subprocessor chain, incident notification, deletion support, audit evidence, and processing locations. Maintain a provider register recording service, purpose, data sent/excluded, region, subprocessors, retention/deletion terms, training-use position, safeguards, and owner.

Never send credentials, account secrets, unnecessary direct identifiers, or unrelated personal data to a model provider. Prefer redaction, pseudonymization, minimization, and local processing where appropriate. Use only approved providers/configurations for the data classification and jurisdiction. Verify training/secondary-use settings and contractual terms; do not assume. Record provider/model/version, purpose, classification, region, and retention posture. Do not use personal data for model training/fine-tuning without a separate documented purpose, authorization, governance process, and explicit approval.

Map where data is collected, stored, accessed, backed up, supported, and processed by every processor/subprocessor. Before international transfer or remote access, determine restrictions, destination and onward-transfer chain, required adequacy/contractual/other mechanism, transfer-risk assessment, safeguards, and review date. No country or transfer mechanism is pre-approved here. If required terms or safeguards cannot be established, block the processing.

## 8. Access, Security, and Audit

Apply Document 08: resource-scoped authorization; separation of editorial, account, security, and support access; encryption in transit/at rest according to risk; identifier redaction in logs, traces, prompts, and errors; restricted exports; access review; pseudonymization/aggregation for analytics where feasible; and tamper-evident records for rights requests and deletion outcomes.

Audit records must themselves be minimized and assigned a retention schedule. Logging complete personal-data payloads is not an acceptable default. If provider retention, deletion, access, or transfer conditions cannot be established, the affected processing remains disabled.

## 9. Privacy Impact, Incidents, and Change Assessment

A privacy impact assessment (PIA/DPIA where applicable) precedes processing likely to create high risk or where required by law. Triggers include large-scale monitoring, sensitive/special-category data, systematic profiling, vulnerable people, novel identity resolution, large-scale dataset linking, significant automated inference, external model processing, and material international transfers.

Record processing, purpose, necessity, data subjects/categories/flows/recipients/locations, applicable law and lawful basis determined with counsel, risks to individuals, safeguards, residual risk, approval, owner, and review date. Reassess material changes to purpose, data, model/provider, source coverage, audience, retention, transfers, or scale.

Incident handling covers suspected unauthorized access, disclosure, loss, alteration, unavailability, or unlawful processing: containment, credential/session revocation, evidence preservation, scope assessment, processor coordination, recovery, and review. The incident owner and counsel determine whether notification is required, to whom, and within what jurisdiction-specific timeline. No universal statutory deadline is set here.

## 10. Verification and Production Gates

Production personal-data processing remains blocked until controls are implemented and evidenced.

| Gate | Required evidence |
|---|---|
| Data inventory | Every activity has owner, purpose, categories, recipients, locations, and retention |
| Lawful basis/transparency | Jurisdiction-specific review and accurate notices/controls approved |
| Minimization | Field-level necessity and redaction tests pass |
| Access | Positive and negative role/resource authorization tests pass |
| Retention/deletion | Tests cover primary, derived, indexed, provider-controlled, export, and backup-restoration paths |
| Rights requests | Intake, verification, discovery, deadline, response, and exception workflow tested |
| Provider governance | Processor/subprocessor and model-provider terms, regions, training use, and deletion verified |
| International transfers | Required mechanism and transfer-risk assessment approved |
| Incident readiness | Escalation, evidence preservation, provider coordination, and notification assessment exercised |
| Privacy impact | Required PIA/DPIA completed and residual risks approved |

Critical privacy failures, unresolved high risks, unauthorized transfers, or unapproved model processing block the affected workflow. Exceptions require scope, compensating controls, expiry, risk owner, and explicit approval plus legal/privacy review where required.

## 11. Open Decisions

Before production, resolve operating entity and jurisdictions; controller/processor roles; user/account model; privacy owner and request channel; purposes and lawful bases; retention periods, legal holds, deletion service levels, and backup expiry; approved processors, subprocessors, model providers and regions; notice/consent/objection requirements; PIA/DPIA authority; and incident ownership/notification procedures. These are unresolved decisions, not implied approvals.

## 12. Related Documents

Documents 01–13, especially Documents 02, 03, 08, 09, 12, and 13; GENI-ADR-013 (content access, retention, licensing, and republication); and GENI-ADR-018 (multilingual processing and language policy). Related documents and ADRs retain their own lifecycle and approval status. This specification does not accept them.

---

**Document ID:** GENI-PRIV-014  
**Version:** 1.0  
**Status:** Draft — Under Architecture Review  
**End of Document**
