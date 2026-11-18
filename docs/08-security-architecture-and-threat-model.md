# GENI-SEC-008 — Security Architecture and Threat Model

**Project:** Global Economic News Intelligence  
**Document ID:** GENI-SEC-008  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  
**Owner:** Project Owner  
**Last Updated:** 2026-11-18

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

Identity provider and session/token lifecycle; role-to-permission matrix; secret-management mechanism; network segmentation/egress; security scanning/remediation service levels; incident owner/escalation; and exception workflow. Resolve against actual deployment exposure before production authorization.

## 10. Related Documents

Documents 02, 03, 09, 10, 12, 13, and 14; GENI-ADR-004, 008, 013, 014, 016, and 017. Related ADRs retain their own status; this document does not accept them.

---

**Document ID:** GENI-SEC-008  
**Version:** 1.1  
**Status:** Draft — Under Architecture Review  
**End of Document**
