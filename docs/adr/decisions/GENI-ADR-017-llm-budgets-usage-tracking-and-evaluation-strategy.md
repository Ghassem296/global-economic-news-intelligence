# GENI-ADR-017 — LLM Budgets, Usage Tracking, and Evaluation Strategy

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-017  
**Title:** LLM Budgets, Usage Tracking, and Evaluation Strategy  
**Status:** Proposed  
**Version:** 1.1  
**Date:** 2026-11-18  
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

LLM calls vary by model, provider, task, prompt size, latency, availability, and output quality. Without budgets and consistent usage telemetry, cost can grow unpredictably and quality regressions may go unnoticed. Model-reported confidence is not a calibrated measure of correctness. GENI must evaluate task quality independently from provider API success and connect usage to workflow and analysis versions.

This ADR is a proposal for formal review; it does not authorize implementation as accepted architecture.

## 2. Decision Question

How should LLM usage be budgeted, measured, evaluated, and governed across providers and workflow stages?

## 3. Requirements and Constraints

### 3.1 Functional Requirements
- Define configurable budgets at task, workflow, and operational levels.
- Record provider, model, task, prompt/schema versions, token usage, latency, retry count, and known cost where available.
- Distinguish provider-reported, internally estimated, and unavailable usage/cost.
- Use task-specific quality datasets and rubrics.
- Measure quality, cost, and latency together.
- Make fallback explicit, observable, and subject to task compatibility.
- Handle budget exhaustion without corrupting workflow state.

### 3.2 Technical Constraints
- Provider pricing and usage fields differ and may change.
- Not all providers return reliable costs or token details.
- Material task evaluation requires human-reviewed reference data.
- Provider-independent execution is governed by ADR-006.

### 3.3 Business and Product Constraints
- The initial product remains event-centric economic intelligence with text reports as its first release.
- The design must support incremental implementation and explicit evaluation.
- Proposals remain provisional until the decision owner records approval.

### 3.4 Security and Privacy Constraints
- Source content and model output are untrusted until validated.
- Only authorized application services and reviewers may change authoritative state.
- Secrets and unnecessary protected content must not appear in ordinary logs.

### 3.5 Operational and Cost Constraints
- Avoid unnecessary distributed infrastructure in the initial release.
- Measure cost and complexity against workload and reliability requirements.
- Failures, retries, recovery, and audit must be observable.

### 3.6 Legal and Content-Rights Constraints
- Access does not itself authorize retention, external processing, transformation, quotation, or republication.
- Source terms, licensing, privacy, and jurisdictional restrictions must be reviewed before production use.

### 3.7 Explicit Non-Goals
- This ADR does not invent unmeasured numerical thresholds or performance guarantees.
- This ADR does not approve a provider, database, or model merely by listing it as an alternative.
- This proposal does not supersede the ADR approval process.

## 4. Alternatives Considered

### 4.1 Alternative A — Unbounded model use

**Description:** Allow components to invoke models without shared budgets or consistent accounting.

**Advantages:**
- Minimal implementation work.

**Disadvantages:**
- No cost ceiling or comparable telemetry.

**Risks:**
- Unexpected spend and unnoticed task proliferation.

**Estimated Complexity:** Low initially

### 4.2 Alternative B — Fixed global call cap

**Description:** Apply one request-count or token limit to the entire product.

**Advantages:**
- Simple operational guardrail.

**Disadvantages:**
- Does not distinguish task value, pricing, or quality.

**Risks:**
- Useful tasks may be blocked while low-value usage continues.

**Estimated Complexity:** Low

### 4.3 Alternative C — Task/workflow budgets with telemetry and evaluation

**Description:** Apply scoped budgets, record normalized usage, and evaluate task quality/cost/latency with controlled fallback.

**Advantages:**
- Task-aware controls and comparable data.

**Disadvantages:**
- Requires usage schema, price catalog maintenance, and evaluation operations.

**Risks:**
- Incomplete provider data may limit cost accuracy.

**Estimated Complexity:** Medium

## 5. Evaluation and Comparison

The comparison is qualitative and reflects architectural fit, not measured performance or cost.

| Evaluation Criterion | Unbounded model use | Fixed global call cap | Task/workflow budgets with telemetry and evaluation |
|---|---|---|---|
| Cost predictability | Low | Medium | High potential |
| Task sensitivity | Low | Low | High |
| Quality visibility | Low | Low | High |
| Provider comparison | Low | Low | High |

The requirements in Section 3 are the primary decision drivers. Unmeasured cost and performance values are intentionally left unspecified.

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Task- and workflow-scoped budgets, normalized usage telemetry, and task-specific evaluation.

The shared LLM execution layer should enforce configurable per-task and per-workflow limits, with an operational ceiling. Each execution records provider/model, task, prompt/schema/config versions, available token usage, latency, retry/fallback data, and cost provenance. Budget breach must produce an explicit normalized outcome or use an approved fallback; it must not silently change models or bypass the budget. Evaluation datasets and rubrics must measure task quality, cost, and latency. Numeric budgets and quality thresholds remain configuration decisions grounded in measured workload and approved economics.

**Rationale:**
- Provides cost controls aligned with task value.
- Makes provider/model performance comparable where telemetry permits.
- Connects regression detection to reproducible task versions.

**Deferred Questions:**
- Initial per-task token/cost budgets.
- Provider-specific pricing catalog and refresh frequency.
- Fallback policies and acceptable quality degradation.
- Evaluation thresholds and sampling/review rates.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-18

A recommendation is not an approval. The Project Owner must explicitly accept or reject this proposal.

## 7. Final Decision

**Selected Alternative:** Pending formal approval  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review; Section 6 contains the recommendation.

**Conditions or Restrictions:**
- Maintain Proposed status until explicit approval is recorded.
- Do not treat deferred questions or example values as settled implementation details.
- Any temporary implementation assumption must be reversible and documented with a review trigger.

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences
- More predictable model usage.
- Evidence-based provider/model decisions.
- Quality and cost can be reviewed together.

### 8.2 Negative Consequences
- Requires telemetry normalization and pricing-data maintenance.
- Evaluation datasets and human review consume resources.

### 8.3 Technical Trade-Offs
Budgets should be enforceable but task-aware. A single global call limit is too crude; unbounded per-task spending is unsafe. Cost estimates must retain provenance and must not be represented as exact when provider data is incomplete.

### 8.4 Operational Consequences
Monitor usage by task, provider, model, source class, and workflow. Alert on budget exhaustion, cost drift, retries, fallback, and quality regression.

### 8.5 Product and Business Consequences
The product can prioritize model calls that materially improve intelligence while controlling unpredictable costs.

### 8.6 Risks and Mitigations
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cost estimation error | Medium | Medium | Record cost provenance and uncertainty; refresh pricing data. |
| Quality regression after model change | Medium | High | Version tasks and run regression evaluation before rollout. |
| Budget too restrictive | Medium | Medium | Tune using measured task value and explicit escalation. |
| Silent fallback quality loss | Medium | High | Require explicit fallback policy and output comparison. |

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components
- SharedLLMExecutionLayer
- WorkflowOrchestrator
- ObservabilityService
- Task evaluation runners

### 9.2 Affected Data Models and Interfaces
- LLMUsageRecord
- ProcessingRun and ProcessingStep as the authoritative task/workflow execution records (no duplicate TaskExecutionRecord entity)
- Model/Prompt/Schema configuration versions
- Versioned EvaluationRun and EvaluationResult artifacts in the repository/CI evaluation artifact store, not production business tables

### 9.3 Affected Documents
- docs/01-product-and-system-architecture.md
- docs/02-component-architecture-and-interfaces.md
- docs/03-data-model-and-storage-design.md
- docs/04-implementation-plan-and-roadmap.md

### 9.4 Related ADRs
| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-006 | Depends on | Defines the shared provider-independent LLM execution interface. |
| GENI-ADR-007 | Related to | Defines bounded model reasoning inside deterministic workflows. |
| GENI-ADR-016 | Related to | Defines durable budget outcomes and workflow recovery. |
| GENI-ADR-008 | Related to | Defines uncertainty and limits on treating model confidence as truth. |

These relationships do not imply that related Proposed ADRs have been accepted.

## 10. Implementation Implications

### 10.1 Required Implementation Work
- Define normalized usage and cost-provenance schema.
- Add task/workflow budget configuration and enforcement.
- Record provider/model/prompt/schema/config identifiers and link usage to ProcessingRun/ProcessingStep.
- Record provider-reported cost separately from internally estimated cost, with cost-source and pricing-catalog version provenance.
- Implement pricing catalog versioning where cost estimates are required.
- Create human-reviewed task-specific reference datasets and rubrics.
- Define versioned EvaluationRun and EvaluationResult artifact schemas, including dataset/case versions, output references or hashes, metrics/rubrics, model and prompt versions, evaluator provenance, and aggregate quality/cost/latency.
- Build quality/cost/latency reports and regression gates.
- Define explicit provider fallback compatibility and observability.

### 10.2 Migration or Compatibility Requirements
Inspect the actual implementation and data before defining migration. This proposal does not claim that a migration or implementation is complete. Any migration must preserve applicable history, provenance, and compatibility.

### 10.3 Dependencies
- GENI-ADR-006 — Defines the shared provider-independent LLM execution interface.
- GENI-ADR-007 — Defines bounded model reasoning inside deterministic workflows.
- GENI-ADR-016 — Defines durable budget outcomes and workflow recovery.
- GENI-ADR-008 — Defines uncertainty and limits on treating model confidence as truth.

### 10.4 Implementation Sequence
1. Define usage schema and budget scopes.
2. Implement enforcement at task and workflow boundaries.
3. Record provider/model/prompt/schema versions and usage provenance.
4. Create representative datasets and evaluation rubrics.
5. Compare model quality, cost, and latency by task.
6. Introduce explicit fallback and rollout gates.

### 10.5 Verification Requirements
- Test budget exhaustion before and during execution.
- Verify unavailable cost is not recorded as zero.
- Verify provider-reported and internally estimated costs remain distinguishable.
- Compare models on the same task dataset and output schema.
- Test fallback and ensure it is never silent.
- Verify prompt/model changes trigger traceable evaluation.

Implementation verification remains deferred until formal acceptance and implementation of the dependent capability.

## 11. Acceptance Criteria
| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | LLM execution records task, provider/model, and prompt/schema versions. | Telemetry tests |
| AC-02 | Budget limits are enforced at configured scopes. | Policy tests |
| AC-03 | Known, estimated, and unavailable cost are distinct. | Accounting tests |
| AC-04 | Fallback is explicit and observable. | Execution integration tests |
| AC-05 | Task quality is measured on reviewed reference data. | Evaluation report |
| AC-06 | Budget and quality changes are versioned and auditable. | Configuration/history tests |

Any quantitative threshold must be supported by representative datasets, measurements, or formal policy review.

## 12. Review and Reconsideration

### 12.1 Review Triggers
- Provider pricing, usage telemetry, or model capabilities materially change.
- Measured cost or quality violates an approved objective.
- New high-cost task classes or external providers are introduced.

### 12.2 Review Schedule
**Review Date:** Not scheduled  
**Review Owner:** Project Owner

### 12.3 Reconsideration Conditions
Reconsider when assumptions are invalidated or measurements show the proposal fails project requirements. A replacement must be recorded through the ADR lifecycle.

## 13. References and Supporting Evidence

The references below are internal project sources used to establish documented context. They are not empirical performance benchmarks or legal opinions.

| Reference | Type | Relevance |
|---|---|---|
| `docs/02-component-architecture-and-interfaces.md` | Internal | Defines SharedLLMExecutionLayer and normalized usage/error contracts. |
| `docs/03-data-model-and-storage-design.md` | Internal | Defines LLM usage persistence. |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Defines shared LLM and evaluation stages. |
| `GENI-ADR-006` | Internal | Provider-independent execution. |
| `GENI-ADR-007` | Internal | Workflow-first bounded reasoning. |
| `GENI-ADR-008` | Internal | Uncertainty representation. |

External legal, provider, and empirical evidence must be added during formal review where relevant.

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-18 | Proposed | Expanded ADR proposal prepared for architecture review | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Clarified ProcessingRun/ProcessingStep as the authoritative execution records, separated evaluation artifacts from production business tables, and strengthened provider-reported versus estimated cost provenance. | AI Architecture Assistant |

**End of ADR**
