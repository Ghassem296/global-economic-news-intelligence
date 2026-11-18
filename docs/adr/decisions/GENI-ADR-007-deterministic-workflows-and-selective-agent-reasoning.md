# GENI-ADR-007 — Deterministic Workflows and Selective Agent Reasoning

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-007  
**Title:** Deterministic Workflows and Selective Agent Reasoning  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

GENI combines deterministic operations—collection, normalization, persistence, policy enforcement, state transitions, retries, and delivery—with tasks that may benefit from probabilistic interpretation, such as extracting claims, assessing semantic similarity, or drafting analysis. A general autonomous agent loop could blur authority, make execution difficult to reproduce, introduce uncontrolled tool use, or allow model output to modify authoritative domain state.

This ADR is a proposal for formal review. It does not approve a production implementation or override an existing accepted decision.

## 2. Decision Question

Which processing responsibilities must remain deterministic and workflow-controlled, and where may bounded LLM or agent-style reasoning be used?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Business workflows and state transitions must be explicitly orchestrated and observable.
- Deterministic validation, persistence, authorization, idempotency, and external side effects must remain application-controlled.
- LLMs may assist bounded tasks with explicit input/output schemas and versioned prompts.
- Model output must never directly create or mutate authoritative Event, publication, rights, or delivery state.
- Any tool capability must be explicitly scoped, allowlisted, validated, and bounded.
- Execution must support timeout, cancellation, retry classification, and audit correlation.

### 3.2 Technical Constraints
- The overall architecture is workflow-first, not a general conversational agent.
- Provider-independent execution is covered by GENI-ADR-006.
- Persistence, idempotency, and recovery are covered by GENI-ADR-016.
- Content supplied by external sources is untrusted input.

### 3.3 Business and Product Constraints
- The initial product remains text-based economic intelligence.
- The approach must support incremental implementation and traceable quality evaluation.
- Proposed technology and policy choices are not mandatory until formally accepted.

### 3.4 Security and Privacy Constraints
- External source content and model outputs are untrusted until validated.
- Apply least privilege to tools, services, and external integrations.
- Do not expose secrets or unnecessary protected content through ordinary logs.

### 3.5 Operational and Cost Constraints
- The initial deployment should avoid unnecessary distributed infrastructure.
- Operational cost and complexity must be measured against expected workload.
- Timeouts, retries, recovery, and observability must be explicitly designed.

### 3.6 Legal and Content-Rights Constraints
- Technical access to source content does not imply permission to store, process externally, transform, quote, or republish it.
- Applicable licensing, privacy, contract, and jurisdictional requirements must be reviewed before production use.

### 3.7 Explicit Non-Goals
- This ADR does not select unmeasured numeric thresholds or invent performance claims.
- This ADR does not approve a database, provider, model, or external service unless explicitly stated as a proposed conditional choice.
- This ADR does not replace the approval process defined in the ADR governance document.

## 4. Alternatives Considered

### 4.1 Alternative A — Fully deterministic rules only

**Description:** Implement all extraction, classification, matching, and analysis without LLM reasoning.

**Advantages:**
- Highly reproducible and controllable
- easier to bound side effects.

**Disadvantages:**
- Weak semantic coverage for varied multilingual news
- large rule-maintenance burden.

**Risks:**
- Coverage and quality may be inadequate for unstructured language.

**Estimated Complexity:** Medium to High

### 4.2 Alternative B — General autonomous agent framework

**Description:** Allow an agent to plan, select tools, execute multi-step tasks, and update product state dynamically.

**Advantages:**
- Flexible for exploratory tasks and changing information needs.

**Disadvantages:**
- Harder to audit, reproduce, constrain, and evaluate
- risks uncontrolled side effects.

**Risks:**
- Prompt injection or planning errors may alter authoritative state.

**Estimated Complexity:** High

### 4.3 Alternative C — Workflow-first with selective bounded reasoning

**Description:** Use deterministic workflows for orchestration and authority; invoke LLMs only for explicit bounded tasks whose outputs are validated by application components.

**Advantages:**
- Combines control with semantic capability
- clear trust boundaries.

**Disadvantages:**
- Requires explicit task contracts and validation after every model call.

**Risks:**
- Poorly designed task boundaries may still create brittle workflows.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Fully deterministic rules only | General autonomous agent framework | Workflow-first with selective bounded reasoning |
|---|---|---|---|
| Workflow reproducibility | High | Variable | High for orchestration |
| Semantic flexibility | Low to Medium | High | High within bounded tasks |
| Authority control | High | Low to Medium | High |
| Auditability | High | Variable | High |
| Prompt-injection exposure | Lower | Higher | Bounded and controlled |

The principal evaluation priorities are:
- Business workflows and state transitions must be explicitly orchestrated and observable.
- Deterministic validation, persistence, authorization, idempotency, and external side effects must remain application-controlled.
- LLMs may assist bounded tasks with explicit input/output schemas and versioned prompts.
- Model output must never directly create or mutate authoritative Event, publication, rights, or delivery state.

Unmeasured latency, throughput, quality, and cost are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Workflow-first orchestration with selective bounded LLM reasoning.

The system should use deterministic application workflows as the authority for execution order, state transitions, retries, authorization, persistence, and external side effects. LLMs may perform bounded interpretation tasks such as extraction, candidate assessment, classification assistance, and draft analysis. Every model result must pass schema and domain validation before it can influence subsequent workflow decisions. Autonomous agents must not directly write authoritative state or execute unrestricted tools.

**Rationale:**
- Matches the product's need for recoverable and auditable workflows.
- Retains semantic flexibility where deterministic rules are insufficient.
- Defines a clear trust boundary between probabilistic suggestions and authoritative decisions.

**Assumptions:**
- LLM calls can be expressed as task-oriented requests.
- Application services can validate outputs and apply authorized transitions.
- The first release does not require autonomous multi-tool planning.

**Deferred Questions:**
- Whether a narrowly scoped agent loop is justified for a future research workflow.
- Specific model/task routing and fallback policies, governed by ADR-006.
- Quantitative task quality thresholds.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The authorized decision owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Product Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Not formally recorded; see the recommendation in Section 6.

**Conditions or Restrictions:**
- Keep this ADR in Proposed status until explicit approval is recorded.
- Do not treat deferred questions or illustrative examples as accepted implementation values.
- Any implementation assumption made before approval must be reversible, documented, and assigned a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- Clear authority boundary and audit trail.
- LLM use remains targeted to tasks where semantic reasoning adds value.
- Recovery and testing are easier than in an autonomous control loop.

### 8.2 Negative Consequences
- Requires more explicit interfaces and validation code.
- Some exploratory tasks may be less flexible.
- Probabilistic outputs still require evaluation and review.

### 8.3 Technical Trade-Offs
The design intentionally trades unrestricted autonomy for control. An agent-style loop may be introduced only as an isolated, bounded workflow with explicit tool permissions, state boundaries, budgets, and evaluation. It must not become the default product orchestration mechanism.

### 8.4 Operational Consequences
Operators need visibility into workflow stage, task identity, model call, validation result, retry count, and failure category. Model/provider outages must not corrupt domain state.

### 8.5 Product and Business Consequences
The product receives semantic extraction and analysis without exposing users or the system to uncontrolled agent behavior.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Workflow over-complexity | Medium | Medium | Keep orchestration at meaningful business boundaries. |
| LLM output accepted without domain checks | Medium | Critical | Use schema plus domain validation and separate decision authority. |
| Premature agent framework adoption | Medium | High | Require a concrete use case and accepted follow-up ADR. |
| Non-deterministic regression | Medium | High | Version prompts/models and retain reference evaluations. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- WorkflowOrchestrator
- SharedLLMExecutionLayer
- EventMatcher
- ClaimExtractor
- EvidenceAnalyzer
- EconomicRelevanceAssessor
- ImportanceRanker
- ImpactAnalyzer
- PublicationPolicy

### 9.2 Affected Data Models and Interfaces
- ProcessingRun
- ProcessingStep
- Analysis
- EventMatchCandidate
- EventMatchDecision
- PublicationDecision

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-006 | Depends on / Related to | Defines the provider-independent execution layer for bounded LLM tasks. |
| GENI-ADR-016 | Depends on / Related to | Defines durable workflow execution, retries, idempotency, and recovery. |
| GENI-ADR-008 | Related to | Defines provenance and uncertainty requirements for model-assisted outputs. |
| GENI-ADR-002 | Related to | Defines matching decisions that must remain controlled by application workflows. |

These relationships do not imply that any related Proposed ADR has been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Represent each workflow as explicit stages, inputs, outputs, and state transitions.
- Define LLM task contracts for bounded tasks.
- Validate model output structurally and semantically.
- Require application services to authorize any persistent state change.
- Enforce tool allowlists, quotas, timeouts, cancellation, and trace correlation.
- Add failure-injection and prompt-injection tests.

### 10.2 Migration or Compatibility Requirements
Existing data and implementation choices must be inspected before migration is designed. No production migration is claimed by this proposal. Any schema or interface migration must preserve historical traceability and must be tested from the current baseline.

### 10.3 Dependencies
- GENI-ADR-006 — Defines the provider-independent execution layer for bounded LLM tasks.
- GENI-ADR-016 — Defines durable workflow execution, retries, idempotency, and recovery.
- GENI-ADR-008 — Defines provenance and uncertainty requirements for model-assisted outputs.
- GENI-ADR-002 — Defines matching decisions that must remain controlled by application workflows.

### 10.4 Implementation Sequence
1. Identify deterministic and probabilistic responsibilities for each use case.
2. Define workflow and task interfaces.
3. Implement bounded LLM execution through GENI-ADR-006.
4. Implement application-side validation and decision services.
5. Add idempotent persistence and recovery from GENI-ADR-016.
6. Measure task value and failure rate before considering agent-style planning.

### 10.5 Verification Requirements
- Verify an LLM result cannot directly create an Event or publish a report.
- Inject malicious instructions into source content and verify that they cannot expand tool permissions.
- Verify timeout/cancellation/retry does not duplicate external effects.
- Verify same inputs and workflow versions preserve deterministic state transitions where expected.
- Trace every model-assisted output to its task, prompt/schema version, and workflow run.

Implementation verification remains deferred until this ADR is accepted and the corresponding capability is implemented.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Workflow stages and state transitions are explicitly represented and persisted. | Workflow contract tests |
| AC-02 | LLM tasks have bounded schemas, deadlines, and execution policies. | LLM interface tests |
| AC-03 | Model output cannot directly mutate authoritative domain state. | Architecture and security tests |
| AC-04 | Tools are allowlisted and least-privilege; no unrestricted tool loop exists in the initial release. | Security review |
| AC-05 | Retries and cancellation preserve idempotency and audit history. | Failure-injection tests |

Any quantitative threshold must be grounded in representative datasets, operational measurements, contractual requirements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- A concrete multi-step task cannot be expressed cleanly through the workflow model.
- A bounded agent prototype demonstrates measurable benefit without weakening authority controls.
- Security or provider capabilities materially change.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Product Owner

### 12.3 Reconsideration Conditions
A concrete multi-step task cannot be expressed cleanly through the workflow model. A bounded agent prototype demonstrates measurable benefit without weakening authority controls. Security or provider capabilities materially change.

Reconsider this recommendation when its core assumptions are no longer valid or measured evidence demonstrates that it does not meet project requirements. A replacement decision must be recorded in a new or superseding ADR.

## 13. References and Supporting Evidence

The references below are internal project documents used to establish the current documented context. They are not claimed as empirical performance measurements or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Establishes workflow-first system boundaries and non-goals. |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines WorkflowOrchestrator and SharedLLMExecutionLayer contracts. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines ProcessingRun and ProcessingStep persistence. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Stages the initial vertical slice and automation. |
| `GENI-ADR-006` | Internal | Defines provider-independent task execution. |
| `GENI-ADR-016` | Internal | Defines idempotent persistence and recovery. |

External legal review, provider measurements, market-data coverage measurements, and model-quality benchmarks remain outstanding wherever relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Initial proposal prepared for architecture review | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |

**End of ADR**
