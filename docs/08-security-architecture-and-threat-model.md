# GENI-SEC-008 — Security Architecture and Threat Model

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-SEC-008  
**Version:** 1.5  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-24

---

## 1. Purpose and Status

Defines the proposed security model, trust boundaries, threat scenarios, controls, and verification expectations. It complements Documents 02, 03, 09–14 and the rights-related ADRs. Personal-data processing, retention, deletion, data-subject requests, processors, and international-transfer controls are specified in [Document 14](14-data-protection-and-privacy-specification.md); this threat model does not replace that specification. Publication is not implementation or approval evidence; deployment choices and numeric objectives remain open.

## 2. Security Objectives

Protect credentials, source material, unpublished reports, reviewer information, and authoritative domain records; preserve availability and recoverability; and prevent unauthorized content use or distribution. Preserve the separation between untrusted inputs, model proposals, authoritative decisions, and external side effects.

## 3. Assets and Trust Boundaries

| Asset/boundary | Main risk | Minimum protection |
|---|---|---|
| Secrets/provider credentials | Theft or disclosure | Protected runtime injection, least privilege, redaction, rotation |
| External content and URLs | Prompt injection, SSRF, parser abuse | Treat as untrusted; constrained fetch and parsing |
| Domain/decision history | Unauthorized mutation | Service-owned writes, authorization, transaction and audit |
| Rights/retention records | Unauthorized processing | Fail-closed operation-specific checks |
| LLM/provider boundary | Data leakage or manipulated output | Data minimization, approved scope, schema validation |
| Review/publication | Privilege abuse or irreversible effects | Scoped authorization, approval provenance, idempotency/reconciliation |
| Build/release pipeline | Dependency/artifact compromise | Locked dependencies, reviewed updates, minimal CI permissions |

Trust boundaries exist between GENI and source providers; application and persistence; workflows and LLM providers; reviewers/operators and the platform; and GENI and delivery targets. Validate data crossing each boundary and preserve its trust classification.

## 4. Threat Model

| Threat | Example | Required control | Verification |
|---|---|---|---|
| Prompt injection | Article text asks a model to reveal secrets or alter decisions | Mark source text untrusted; restrict tools; validate output; authorization stays outside models | Adversarial fixtures |
| SSRF/redirect abuse | URL resolves to private IP or redirects to prohibited host | Scheme/host/IP policy, DNS and redirect revalidation, private/link-local blocking, egress limits | IPv4/IPv6, DNS, redirect tests |
| Malicious content | HTML/document exploits parser | Content-type/size limits, safe parsers, sandboxing where appropriate, no execution | Malformed/oversized fixtures |
| Credential leakage | Secret appears in prompt/log/exception | Protected injection, redaction, telemetry allowlist | Canary-secret tests |
| Unauthorized state change | Model or unprivileged user changes event/publication | Models propose only; domain services enforce authorization/invariants | Negative authorization tests |
| Reviewer abuse | Reviewer approves outside assigned scope | Resource-scoped roles, separation of duties for high-impact actions, audit | Role-matrix tests |
| Replay/duplicate side effect | Retry publishes twice | Idempotency keys, durable operation state, reconciliation | Replay/timeout tests |
| Supply-chain compromise | Malicious dependency/CI action | Dependency pinning, update review, least-privilege workflows | Dependency/workflow checks |
| Data exfiltration | Restricted content sent to unapproved model | Rights check, minimization, provider/egress policy | Rights/provider tests |
| DoS/cost exhaustion | Fetch/model-call storm | Per-source/workflow/global limits, deadlines, bounded retries/budgets | Load/retry-storm tests |

## 5. Identity and Authorization

Proposed logical roles (not an identity-provider or RBAC technology selection):

| Role | Responsibility | Default restriction |
|---|---|---|
| Project Owner | Approve architecture/high-impact policy | Not a routine service identity |
| Administrator/Operator | Operate approved infrastructure and controlled recovery | Cannot rewrite evidence or bypass approval history |
| Reviewer | Review assigned items within granted scope | Cannot mutate unrelated state |
| Application service identity | Execute only workflow-required permissions | No interactive/broad human privileges |
| Read-only consumer | Read explicitly published/authorized outputs | No restricted content, internal assessments, secrets, or unpublished reports |

Check authorization server-side for every protected operation. UI visibility is not authorization. Record actor, action, resource, scope, policy/version, outcome, and timestamp. Denials fail closed.

### 5.1 Deny-by-default role boundary matrix

The roles above are logical identity categories, not grants. A role name, group membership, successful login, service registration, or possession of an object identifier does not by itself authorize an operation. Every grant must be explicit, resource-scoped, purpose-limited where applicable, time-bounded where appropriate, and evaluated against the current policy. The following matrix defines the maximum responsibility boundary implied by each role; it intentionally does not grant blanket permissions.

| Role | Governance approval | Infrastructure operation/recovery | Assigned review actions | Workflow execution | Authoritative domain decisions | External publication/delivery | Restricted audit/security records |
|---|---|---|---|---|---|---|---|
| Project Owner | May approve architecture and high-impact policy through the controlled approval process | No implicit operational grant | No implicit review grant | No routine service grant | No implicit domain-decision grant | No implicit dispatch grant | No implicit unrestricted audit grant |
| Administrator/Operator | No architecture/policy approval by operational role alone | Explicitly scoped operational/recovery grant only | No implicit grant | No implicit workflow grant | Must not rewrite evidence or bypass approval history; no implicit grant | No implicit grant | Explicitly scoped operational/security access only |
| Reviewer | No governance approval | No operational grant | Explicitly assigned item and action only | No general workflow grant | Review outcome is not itself an authoritative domain decision unless a separate approved policy and permission expressly make it so | No grant | No implicit grant |
| Application service identity | No human governance approval | No infrastructure administration | No human review grant | Exact workflow, operation, resource class, and environment grant only | Only the specific policy-governed transition assigned to that workflow | No dispatch grant unless separately authorized for the exact delivery operation | No general audit browsing |
| Read-only consumer | None | None | None | None | None | Read only outputs explicitly released to that consumer | None |

A Project Owner's governance approval is recorded as an approval artifact; it is not automatically a runtime authorization token. An Administrator/Operator cannot change authoritative domain history merely because they can recover infrastructure. A Reviewer may submit an assigned review action but cannot approve their own scope expansion. Service identities cannot inherit human privileges. Any exception requires a separate, approved, scoped, expiring grant and must not weaken immutable history.

### 5.2 Minimum operation-permission catalogue

The following permission identifiers are a proposed logical vocabulary for implementation and testing. They are not a role assignment, a deployment configuration, or approval to enable the corresponding capability. All permissions are denied unless an explicit grant is present.

| Operation family | Permission identifier | Minimum resource/scope binding | Additional mandatory gate |
|---|---|---|---|
| Read source configuration | `source.config.read` | Exact Source or explicitly bounded source set | Never returns secrets; content access is not implied |
| Change source configuration | `source.config.update` | Exact Source and permitted fields | Authenticated actor, expected version, audit; rights must be re-evaluated after endpoint/type changes |
| Collect from a source | `source.collect` | Exact Source, adapter/endpoint and collection operation | Current operation-specific access/collection rights; SSRF and egress controls |
| Read article metadata/content | `article.metadata.read` / `article.content.read` | Exact Article/revision and permitted content scope | Content-rights check for restricted content; metadata permission is not content permission |
| Append an article revision | `article.revision.append` | Exact Source and source-scoped Article identity | Collection authorization, rights/retention scope, idempotency and concurrency checks |
| Evaluate event candidates | `event.match.evaluate` | Exact EventMatchCase and candidate set | Evaluation may append candidate evidence but cannot activate an ArticleEventLink |
| Append an event-match decision | `event.match.decide` | Exact case, candidate, predecessor and aggregate version | Immutable authorization reference; approved decision policy; atomic successor/link reconciliation |
| Create an Event | `event.create` | Exact preassigned Event ID and candidate/case | Effective NEW_EVENT_CANDIDATE decision, approved EventCreationPolicy and idempotency |
| Append evidence | `evidence.append` | Exact claim/analysis context and evidence origin | Exact rights/retention permission for any stored quotation or extract |
| Append analysis | `analysis.append` | Exact input revision/evidence set and analysis purpose | If a provider is used: current privacy authorization, provider/model/region/purpose and content-rights decisions |
| Generate a report version | `report.generate` | Exact report aggregate, version and input snapshot | Provenance completeness; generation does not authorize publication |
| Perform review actions | `review.action` | Exact assigned ReviewRecord, action and subject | Assignment, separation-of-duties and approved review policy; outcome does not bypass the authoritative decision command |
| Append publication decision | `publication.decide` | Exact immutable report version and publication scope | Approved publication policy and authorized decision actor |
| Authorize distribution | `distribution.authorize` | Exact report version, recipient, destination, channel and content-scope fingerprint | Complete current source-rights assessment set and approved DistributionAuthorizationPolicy |
| Dispatch delivery | `delivery.dispatch` | Exact effective distribution decision and authorized content manifest | Revalidate decision, rights dependencies, expiry, payload fingerprint and idempotency immediately before side effect |
| Administer privacy processing policy | `privacy.policy.administer` | Exact purpose, operation, data category and policy record | Separate authorized policy-administration process; never inferred from provider availability |
| Read restricted audit/security records | `security.audit.read` | Exact record class, incident or operational purpose | Explicit least-privilege grant and access audit |
| Change security-sensitive configuration | `security.config.change` | Exact setting/environment and change window | Authenticated, authorized, audited change with rollback/recovery plan |

Permission identifiers may be refined when the API and policy schemas are approved, but implementations must preserve the separation between metadata and content, evaluation and decision, publication and distribution authorization, and authorization and external dispatch. A broader permission must not be inferred from a narrower one.

### 5.3 Authorization decision and reference requirements

For every protected command, the application evaluates authorization server-side before mutation or external side effect. The evaluation input must include the authenticated actor/service identity, action, exact resource, requested scope, purpose where relevant, environment, applicable policy/version, and current validity/revocation state. The result is one of ALLOW, DENY, or REQUIRES_REVIEW; only ALLOW can proceed. Unknown, missing, malformed, expired, revoked, stale, mismatched, or unverifiable inputs fail closed. A retry is a new authorization evaluation against the exact retry context; a prior ALLOW is not a transferable capability.

For state-changing operations that require an authorization decision, persist an immutable `authorization_reference` from trusted security/application context. It must resolve to the decision record and its actor/service, action, exact resource, scope, purpose where relevant, policy/version, evaluation time, validity/expiry, outcome, and revocation/supersession state. The reference is not a caller-supplied role string, free-form claim, or bearer permission. Repositories validate reference integrity and binding but do not independently invent or broaden grants. The audit record must preserve DENY and REQUIRES_REVIEW outcomes as well as ALLOW outcomes; a denied attempt must not mutate the protected aggregate.

Protected reads are also authorized server-side. Persist or audit sensitive read decisions according to the approved audit policy; do not log restricted payloads merely to prove access. A permission to read a record does not grant permission to export, quote, retain, send to a provider, or distribute its contents.

For high-impact actions, enforce separation of duties where policy requires it: the same principal must not approve their own policy/grant expansion or use operational administration to bypass a domain decision. Exact conflict-of-interest rules, emergency break-glass eligibility, grant administration, and numeric validity periods remain deployment/policy decisions and are not selected by this logical contract.

## 6. Secure Processing Controls

1. Treat source metadata, article text, URLs, files, provider errors, and model output as untrusted.
2. Models produce proposals only; they cannot grant permissions or perform privileged state transitions.
3. Validate structured output against versioned schemas and domain rules.
4. Constrain network access and re-check redirects/resolved addresses at every hop.
5. Every external call has timeout, response-size limit, bounded retry, and cancellation behavior.
6. Never place secrets in prompts, source records, ordinary logs, or exception messages.
7. Technical access does not grant rights to store, externally process, quote, or redistribute content.
8. Security-sensitive configuration changes must be authenticated, authorized, auditable, and reversible where feasible.

## 7. Audit and Incident Handling

Operational logs contain correlation identifiers, component/workflow, outcome, duration, retry class, and safe error codes; exclude credentials and unnecessary restricted content. Security audit records are append-only or tamper-evident and identify actor/service, action, resource, authorization context, timestamp, and result. Logs and authoritative business history are distinct.

Incident procedures cover detection, triage, containment, credential revocation/rotation, evidence preservation, recovery, applicable notifications, and post-incident review. Incident ownership and jurisdiction-specific obligations must be established for the actual service; this document invents no legal requirements.

## 8. Release Gates

Before external release verify authorization denials; SSRF protections for private/loopback/link-local/IPv4/IPv6/redirect cases; prompt-injection resistance; secret redaction in success/failure/timeout paths; request/parser/concurrency/cost limits; dependency and CI permissions; rights enforcement; backup access controls; and incident/rotation procedures. A failed critical gate blocks release. Exceptions require risk owner, scope, expiry, compensating control, and explicit approval.

## 9. Open Decisions

Identity provider and session/token lifecycle; final role-to-permission assignments and grant-administration workflow; permission catalogue/API schema and policy evaluation point; separation-of-duties exceptions and break-glass controls; secret-management mechanism; network segmentation/egress; security scanning/remediation service levels; incident owner/escalation; and exception workflow. The deny-by-default logical role and operation matrices in Section 5 are a proposed baseline only. Resolve these deployment and policy decisions against actual exposure before production authorization.

## 10. Related Documents

Documents 02, 03, 09, 10, 12, 13, and [14 — Data Protection and Privacy Specification](14-data-protection-and-privacy-specification.md); GENI-ADR-004, 008, 013, 014, 016, 017, and 020. Related ADRs retain their own status; this document does not accept them.

## 11. Privacy Processing Authorization and LLM Egress

`ContentRightsService` and `PrivacyProcessingAuthorization` are separate controls. For a provider request involving both source content and personal data, both must independently authorize the exact purpose, operation, payload classification, provider/model and processing region. A positive content-rights decision cannot substitute for privacy authorization.

SharedLLMExecutionLayer fails closed if the privacy decision, processor register entry, transfer assessment or provider retention/training-use posture is missing, unknown, expired, revoked or inconsistent. Minimize/redact before transmission; do not include direct subject identifiers unless strictly necessary and explicitly authorized. Bind each request/usage record to the immutable PrivacyAuthorizationDecision ID, applicable content-rights decision references, purpose, data category, provider/model, region and policy version. Persist the decision reference in LLMUsageRecord whenever personal data is processed. Re-evaluate when any attribute changes, including retries.

Logs, traces, prompts, exception messages and evaluation artifacts are privacy-relevant stores. Use allowlisted telemetry, opaque subject references, redaction and access controls. Test synthetic canary values. Provider deletion acknowledgement and backup restoration must reconcile with the privacy deletion ledger. See Documents 02, 03, 09, 12, 13 and 14; GENI-ADR-020.

---

**Document ID:** GENI-SEC-008  
**Version:** 1.4  
**Status:** Draft — Under Architecture Review  


**End of Document**