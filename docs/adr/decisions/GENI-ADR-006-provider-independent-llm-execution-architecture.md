# GENI-ADR-006 — Provider-Independent LLM Execution Architecture

**Project:** Global Economic News Intelligence  
**ADR ID:** GENI-ADR-006  
**Title:** Provider-Independent LLM Execution Architecture  
**Version:** 1.2
**Status:** Proposed  
**Date:** 2026-11-18
**Decision Owner:** Project Owner  
**Prepared By:** AI Architecture Assistant  
**Approved By:** Not yet approved  
**Approval Date:** N/A

---

## 1. Context and Problem Statement

Global Economic News Intelligence requires Large Language Models (LLMs) for selected intelligence tasks across its processing workflow.

Potential LLM-assisted capabilities include:

- Article classification.
- Topic and economic category extraction.
- Entity extraction and normalization.
- Event candidate analysis.
- Event relevance assessment.
- Claim extraction.
- Evidence relationship assessment.
- Structured analytical summaries.
- Report generation.
- Translation and language normalization.

These capabilities have different input structures, output requirements, reliability expectations, and operational constraints.

The system must support these tasks without coupling its core business logic directly to a particular LLM provider, model, SDK, or agent framework.

Directly integrating provider-specific SDKs into individual components could create several problems:

- Provider dependencies spreading throughout the codebase.
- Inconsistent timeout, retry, and error-handling behavior.
- Different output validation strategies across components.
- Difficulty switching models or providers.
- Fragmented token and cost tracking.
- Inconsistent prompt and model version management.
- Difficulty evaluating and comparing model behavior.
- Security and privacy controls implemented inconsistently.

At the same time, introducing a large generic Agent framework could create unnecessary complexity.

The product is workflow-first. Its LLM interactions should be initiated by explicit application tasks, with controlled inputs, defined outputs, and predictable execution boundaries.

A shared LLM execution capability is therefore needed to centralize common execution concerns while allowing individual intelligence components to retain responsibility for their own business logic.

The architecture must also recognize that different providers expose different capabilities. A provider-independent interface should not pretend that every provider supports identical features or behavior.

---

## 2. Decision Question

How should Global Economic News Intelligence execute LLM-powered tasks so that:

1. Product components remain independent of specific LLM providers and SDKs.
2. LLM requests and responses have explicit, validated contracts.
3. Timeouts, retries, usage, cost, and execution errors are handled consistently.
4. Model selection and task configuration remain controllable.
5. Security, privacy, and prompt injection risks are addressed.
6. The architecture remains simple enough for incremental implementation.
7. The product does not become dependent on a generic conversational Agent runtime.

---

## 3. Requirements and Constraints

### 3.1 Functional Requirements

- Provide a shared execution boundary for LLM-powered application tasks.
- Support structured inputs and structured outputs.
- Support task-specific prompts and output schemas.
- Allow different models or providers to be selected through configuration.
- Return normalized execution results and errors.
- Support multiple LLM tasks within the same application workflow.
- Preserve task-level traceability and evaluation capability.
- Allow individual components to define their own domain-specific validation rules.

### 3.2 Technical Constraints

- The system should not depend on a single provider's SDK throughout the application.
- Provider-specific integration code must be isolated behind adapters.
- The execution layer should expose stable application-facing interfaces.
- Provider capabilities and limitations must remain visible when relevant.
- The system must support deterministic configuration of model selection.
- Execution must have explicit deadlines and resource limits.
- The architecture must support incremental addition of providers and models.
- The solution should be testable without making real provider requests.

### 3.3 Business and Product Constraints

- LLM usage must support measurable product capabilities.
- Model selection must consider output quality, latency, reliability, and cost.
- The architecture must avoid unnecessary infrastructure and operational complexity.
- Expensive models should not be used automatically for every task.
- Model or provider changes must be possible without rewriting core business logic.

### 3.4 Security and Privacy Constraints

- External article content must be treated as untrusted input.
- Article text must not be allowed to redefine system instructions or execution policies.
- LLM outputs must be treated as untrusted until validated.
- Analysis-stage LLM calls must not receive unrestricted tool-execution capabilities.
- Sensitive information must not be sent to external providers unless explicitly permitted by project policy.
- Credentials and provider secrets must not appear in prompts, logs, or application responses.
- Logging and observability must avoid unnecessary storage of sensitive source content.
- Provider data-retention and processing policies must be evaluated before production use.

### 3.5 Operational and Cost Constraints

- Every execution must have a configurable timeout or deadline.
- Retry policies must distinguish transient failures from permanent failures.
- Token usage and available cost information must be recorded.
- Execution limits must be configurable by task or workflow.
- Failures must be observable and traceable.
- The system must avoid uncontrolled retry loops.
- The execution layer must support graceful failure and application-level fallback policies.

### 3.6 Legal and Content-Rights Constraints

- The LLM execution layer must not assume that collected article content is legally available for unrestricted external processing.
- Source licensing and content-processing permissions must be respected.
- Provider terms concerning submitted content, retention, and training must be evaluated.
- The system must not interpret successful API execution as permission to process or redistribute source content.

### 3.7 Explicit Non-Goals

This ADR does not define:

- Which specific LLM provider must be selected.
- Which specific model must be used for each task.
- The final prompt content for every intelligence capability.
- The domain-specific evaluation criteria for individual tasks.
- A general-purpose conversational Agent.
- A mandatory multi-agent architecture.
- A generic autonomous tool-execution framework.
- A universal memory system.
- A vector database or embedding architecture.
- A complete model-training or fine-tuning strategy.
- A final deployment or infrastructure platform.

These concerns must be addressed separately when required.

---

## 4. Alternatives Considered

### 4.1 Alternative A: Direct Provider Integration in Each Component

**Description:**

Each application component integrates directly with the selected provider's SDK or API.

For example, Article Classification, Entity Extraction, and Report Generation would independently implement their own provider calls.

**Advantages:**

- Simple initial implementation for a very small system.
- Direct access to provider-specific features.
- Minimal initial abstraction.
- Each component can optimize its own integration.

**Disadvantages:**

- Provider dependencies spread across the application.
- Repeated timeout and retry implementations.
- Inconsistent output validation.
- Fragmented usage and cost tracking.
- Provider migration requires changes across multiple components.
- Difficult to enforce common security and privacy policies.
- Difficult to test application logic independently of provider APIs.

**Risks:**

- Tight coupling between business logic and provider SDKs.
- Inconsistent execution behavior.
- Increasing maintenance costs as the number of LLM tasks grows.

**Estimated Complexity:** Low initially; High over time.

### 4.2 Alternative B: Full Generic Agent Framework

**Description:**

Adopt or build a general-purpose Agent framework as the primary execution mechanism for all LLM-powered functionality.

The framework may include autonomous loops, tool execution, memory, planning, multi-agent coordination, and generalized task orchestration.

**Advantages:**

- Potentially reusable abstractions for complex autonomous workflows.
- Built-in support may exist for tools, memory, and planning.
- May simplify certain future capabilities if autonomous behavior becomes a real requirement.

**Disadvantages:**

- Introduces capabilities that are not currently required.
- Increases architectural and operational complexity.
- Can make execution behavior less predictable.
- May introduce framework-specific abstractions and dependencies.
- Can obscure task-specific input and output contracts.
- Does not automatically solve provider cost control, data rights, or output validation.
- Risks turning a deterministic processing pipeline into an unnecessarily generic Agent system.

**Risks:**

- Framework lock-in.
- Unnecessary operational overhead.
- Harder debugging and evaluation.
- Excessive abstraction before product requirements justify it.

**Estimated Complexity:** High.

### 4.3 Alternative C: Shared Provider-Independent LLM Execution Layer

**Description:**

Introduce a shared application-level LLM execution boundary.

Individual application components define their task-specific requirements and call the shared execution layer through stable interfaces.

The shared layer handles common execution responsibilities, while provider adapters isolate provider-specific APIs and behavior.

The architecture includes:

- Task-oriented execution requests.
- Explicit input and output contracts.
- Provider adapters.
- Model and task configuration.
- Structured output handling and schema validation.
- Deadlines and timeouts.
- Controlled retries.
- Usage and cost recording.
- Execution tracing and structured errors.
- Provider capability management.

The execution layer does not own product workflows, domain decisions, or autonomous planning.

**Advantages:**

- Reduces provider coupling.
- Centralizes common execution policies.
- Supports task-specific structured contracts.
- Enables consistent usage and cost tracking.
- Improves testability.
- Supports incremental provider integration.
- Preserves workflow-first product architecture.
- Avoids mandatory dependency on a generic Agent framework.

**Disadvantages:**

- Requires an initial abstraction and interface design.
- Provider differences must be handled explicitly.
- A poorly designed abstraction could become overly generic.
- Some advanced provider-specific capabilities may require controlled extensions.

**Risks:**

- An incomplete abstraction may hide important provider behavior.
- Excessive configuration may complicate task management.
- Incorrect retry or fallback behavior may produce duplicated work or inconsistent results.

**Estimated Complexity:** Medium.

---

## 5. Evaluation and Comparison

The most important evaluation criteria are product fit, maintainability, reliability, provider independence, security, and implementation complexity.

| Evaluation Criterion | Alternative A | Alternative B | Alternative C |
|---|---|---|---|
| Product Fit | Moderate | Low for current scope | High |
| Functional Suitability | High for simple tasks | Broad but excessive | High |
| Provider Independence | Low | Framework-dependent | High |
| Reliability Consistency | Fragmented | Framework-dependent | Centralized policies |
| Structured Output Control | Component-specific | Framework-dependent | Shared execution contract |
| Usage and Cost Tracking | Fragmented | Depends on framework | Centralized |
| Security Consistency | Fragmented | Framework-dependent | Centralized controls |
| Maintainability | Decreases with growth | Depends on framework complexity | Good if scope is controlled |
| Flexibility | Provider-specific | Framework-dependent | High |
| Initial Complexity | Low | High | Medium |
| Long-Term Complexity | Potentially high | High | Moderate |
| Reversibility | Moderate | Potentially low | High if interfaces remain stable |

### Evaluation Notes

**Alternative A** is initially convenient but creates duplicated infrastructure and provider coupling as LLM usage expands.

**Alternative B** offers broad capabilities but does not match the current workflow-first architecture. Its additional capabilities do not justify their cost without a concrete product requirement.

**Alternative C** provides the necessary common execution infrastructure while preserving the responsibilities of product-specific components.

The comparison is qualitative. Actual provider cost, latency, model quality, and performance must be measured through task-specific evaluation rather than assumed.

---

## 6. Recommended Decision

**Recommended Alternative:** Alternative C — Shared Provider-Independent LLM Execution Layer.

### 6.1 Architectural Decision

Introduce a shared LLM Execution Layer between application components and external LLM providers.

Application components must not directly depend on provider-specific SDKs for ordinary LLM task execution.

The shared layer will provide a stable application-facing execution interface and isolate provider-specific integration behind adapters.

The layer must remain task-oriented and must not become a general-purpose autonomous Agent framework.

### 6.2 Logical Architecture

```text
Application Workflow
        |
        v
Product Components
        |
        | Task-specific request
        v
LLM Execution Interface
        |
        v
Execution Policy and Configuration
        |
        +-------------------------+
        |                         |
        v                         v
Input / Contract Validation   Task Configuration
        |                         |
        +------------+------------+
                     |
                     v
              Model Selection
                     |
                     v
             Provider Adapter
                     |
                     v
              External LLM API
                     |
                     v
             Provider Response
                     |
                     v
          Response Normalization
                     |
                     v
          Structured Output Parsing
                     |
                     v
            Schema Validation
                     |
                     v
          Usage and Trace Recording
                     |
                     v
          Normalized Execution Result
                     |
                     v
             Product Component
```

This diagram describes logical responsibilities, not a mandatory deployment topology.

### 6.3 Core Architectural Responsibilities

The execution layer should provide the following capabilities.

#### A. Task-Oriented Execution Interface

Each LLM operation must have an explicit task identity.

Examples:

- `article.classification`
- `article.entity_extraction`
- `event.match_assessment`
- `claim.extraction`
- `evidence.relationship_assessment`
- `report.summary_generation`

Task identifiers must be stable and independent of provider-specific model names.

Each task must define its expected input and output contracts.

#### B. Provider Adapter Boundary

Provider-specific code must be isolated behind adapters.

An adapter is responsible for translating the application's execution request into the provider's API format and normalizing the provider response.

The application must not need to understand provider-specific request formats for ordinary supported operations.

Provider-specific capabilities must not be silently discarded. When a feature is not portable, the interface must either expose an explicit capability or reject unsupported configuration.

#### C. Structured Input and Output

LLM tasks should use structured input and output contracts wherever practical.

The execution layer must support:

- Input validation.
- Output parsing.
- Schema validation.
- Structured validation errors.
- Explicit handling of incomplete or malformed responses.

Successful API completion does not mean that the model produced a valid or correct result.

Domain-specific validation remains the responsibility of the relevant product component.

#### D. Model and Task Configuration

Model selection must be configurable without requiring changes to business logic.

Configuration should support:

- Task-to-model mapping.
- Provider selection.
- Model identifier.
- Task-specific parameters.
- Timeout and deadline settings.
- Token or cost budgets where supported.
- Retry policy.
- Structured output requirements.
- Provider capability requirements.

Default configuration must be explicit and version-controlled.

The system must not silently switch to a different model when a task fails unless an explicit fallback policy permits that behavior.

#### E. Execution Deadlines and Timeouts

Every execution must have a bounded execution time.

The execution layer must distinguish:

- Request timeout.
- Overall task deadline.
- Provider response failure.
- Application cancellation.
- Validation failure.

Retries must respect the remaining deadline.

A retry must not extend the original task deadline without an explicit application policy.

#### F. Retry and Fallback Policies

Retries should be limited to appropriate transient failures.

Examples include:

- Temporary network failures.
- Rate limiting.
- Provider service unavailability.
- Explicitly retryable server errors.

Permanent errors should not be retried automatically.

Examples include:

- Invalid credentials.
- Invalid request structure.
- Unsupported model capability.
- Invalid task configuration.
- Schema or contract incompatibility.

Retries must use bounded attempts and controlled backoff.

Fallback to another provider or model must be explicitly configured and observable. It must not silently change the task's expected quality, output behavior, or cost characteristics.

#### G. Usage and Cost Tracking

Execution results should include available usage information.

Where provided by the provider, record:

- Input tokens.
- Output tokens.
- Total tokens.
- Cached token usage.
- Model identifier.
- Provider identifier.
- Reported cost.
- Execution duration.

Cost must be marked as unavailable when it cannot be reliably calculated.

The system must distinguish provider-reported usage and cost from internally estimated values.

Usage records should be traceable to the task and workflow execution.

#### H. Prompt and Schema Versioning

Task prompts and output schemas must be versioned.

Each execution should record the relevant:

- Task identifier.
- Prompt version.
- Output schema version.
- Provider.
- Model identifier.
- Configuration version where applicable.

This is necessary for reproducibility, debugging, evaluation, and comparison of model behavior.

Prompt changes that materially affect output behavior must be evaluated before production rollout.

#### I. Normalized Errors and Observability

The execution layer should expose structured error categories.

Examples:

- `PROVIDER_UNAVAILABLE`
- `RATE_LIMITED`
- `REQUEST_TIMEOUT`
- `AUTHENTICATION_FAILED`
- `INVALID_REQUEST`
- `UNSUPPORTED_CAPABILITY`
- `OUTPUT_PARSE_FAILED`
- `OUTPUT_SCHEMA_INVALID`
- `BUDGET_EXCEEDED`
- `EXECUTION_CANCELLED`

These categories are illustrative and may be refined during implementation.

Execution logs should include correlation identifiers, task identifiers, provider and model information, execution duration, retry count, and error category.

Sensitive prompts, credentials, and unnecessary article content must not be written to ordinary logs.

### 6.4 Analysis-Stage Execution Restrictions

LLM execution for intelligence and analysis tasks must be bounded.

In particular:

- Article content is untrusted data.
- Source text must not override system instructions.
- Retrieved content must be clearly separated from trusted instructions.
- LLM output must be validated before it affects domain state.
- Analysis-stage calls must not receive unrestricted tool execution.
- An LLM must not directly publish reports or modify authoritative event state.
- Important low-confidence or conflicting results must be handled through the relevant application review process.

The execution layer provides technical controls. Product components remain responsible for deciding whether a result is accepted, reviewed, rejected, or used as supporting evidence.

### 6.5 Recommendation Rationale

Alternative C is recommended because it:

1. Matches the workflow-first architecture.
2. Centralizes repeated execution concerns.
3. Reduces provider-specific coupling.
4. Provides a foundation for consistent observability and evaluation.
5. Supports controlled model selection.
6. Enables independent testing of application components.
7. Avoids unnecessary autonomous Agent infrastructure.

The recommendation is intentionally limited to a shared execution boundary. It does not require every possible LLM capability to be implemented in the first development stage.

**Recommendation Prepared By:** AI Architecture Assistant  
**Recommendation Date:** 2026-11-17

> Important: This is a recommendation only. The Project Owner must explicitly accept or reject it.

---

## 7. Final Decision

This ADR is currently a proposal.

**Selected Alternative:** Not formally selected.  
**Decision Status:** Proposed  
**Decision Owner:** Project Owner  
**Approved By:** Not yet approved  
**Approval Date:** N/A

**Decision Rationale:** Pending formal review and approval.

**Conditions or Restrictions:**

- The proposed execution layer must remain task-oriented.
- It must not introduce a mandatory generic conversational Agent runtime.
- Provider independence must not hide meaningful differences between provider capabilities.
- Domain-specific business logic must remain outside the provider adapters.
- Implementation scope must be incremental and justified by actual product requirements.

**Deferred Questions:**

- Which provider or providers should be used initially?
- Which models should be assigned to individual tasks?
- Which structured-output mechanisms should be used for each provider?
- Should model routing be based only on configuration or also on measured task performance?
- Which usage and cost information can be reliably obtained from the selected providers?
- Which tasks require human review based on confidence or risk?
- What provider-specific capabilities require explicit extension interfaces?

These questions should be resolved through implementation planning, provider evaluation, or separate ADRs where necessary.

---

## 8. Consequences and Trade-Offs

### 8.1 Positive Consequences

- Provider-specific integrations are isolated.
- Common execution policies are centralized.
- Application components become easier to test.
- Model changes require fewer changes to business logic.
- Usage and execution tracing become more consistent.
- Structured output validation becomes a shared responsibility.
- Future provider integrations become easier to evaluate.

### 8.2 Negative Consequences

- An additional architectural layer must be designed and maintained.
- Provider adapters require testing and maintenance.
- A common interface may not expose every provider-specific feature directly.
- Initial development takes more effort than direct API integration.
- Usage and cost data may differ between providers.

### 8.3 Technical Trade-Offs

The system prioritizes stable application-facing contracts over complete uniformity across provider APIs.

This means some advanced provider capabilities may require explicit extensions.

The abstraction must not attempt to normalize fundamentally different capabilities into misleadingly identical behavior.

### 8.4 Operational Consequences

The system will need:

- Provider credential management.
- Model and task configuration management.
- Execution monitoring.
- Usage and cost reporting.
- Retry and timeout monitoring.
- Provider availability monitoring.
- Evaluation and regression testing.

### 8.5 Product and Business Consequences

The architecture supports controlled model selection and cost management.

It also allows model quality to be evaluated by task rather than assuming that one model is equally suitable for every capability.

No specific improvement in accuracy, latency, or cost is guaranteed until measured.

### 8.6 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Overly generic execution interface | Medium | High | Keep contracts task-oriented and add abstractions only when justified |
| Provider capability differences are hidden | Medium | High | Expose capability requirements and explicit unsupported-feature errors |
| Incorrect retry behavior | Medium | High | Use bounded retries, deadlines, and task idempotency |
| Invalid model output enters domain state | Medium | High | Apply parsing, schema validation, and domain-level validation |
| Sensitive content is exposed to providers | Medium | High | Enforce provider policies, data minimization, and content-rights controls |
| Usage and cost records are inaccurate | Medium | Medium | Preserve provider-reported and internally estimated values separately |
| Prompt injection influences analysis | Medium | High | Treat source content as untrusted and restrict execution capabilities |
| Model changes degrade task quality | Medium | High | Use task-specific evaluation and regression tests |

---

## 9. Impact on Architecture and Documentation

### 9.1 Affected Components

- LLM Execution Layer.
- Provider Adapters.
- Model and Task Configuration.
- Article Classification.
- Entity Extraction.
- Event Intelligence and Matching.
- Claim and Evidence Assessment.
- Analysis and Report Generation.
- Workflow Orchestration.
- Usage and Observability Services.

### 9.2 Affected Data Models and Interfaces

Potential interfaces and records include:

- `LLMExecutionRequest`
- `LLMExecutionResult`
- `LLMTaskDefinition`
- `LLMProviderAdapter`
- `LLMProviderCapabilities`
- `LLMModelConfiguration`
- `LLMUsageRecord`
- `LLMExecutionTrace`
- `LLMExecutionError`
- `PromptVersion`
- `OutputSchemaVersion`

These are conceptual names. Final naming and persistence requirements must be established during detailed design.

### 9.3 Affected Documents

- `docs/01-product-and-system-architecture.md`
- `docs/02-component-architecture-and-interfaces.md`
- `docs/03-data-model-and-storage-design.md`
- `docs/04-implementation-plan-and-roadmap.md`
- `docs/05-architecture-decision-records.md`
- `docs/adr/README.md`

The relevant sections must be updated after formal acceptance.

### 9.4 Related ADRs

| ADR ID | Relationship | Explanation |
|---|---|---|
| GENI-ADR-001 | Related to | Establishes the event-centric product architecture that the execution layer must support |
| GENI-ADR-002 | Related to | Defines deduplication and event matching responsibilities that may use LLM-assisted tasks |
| GENI-ADR-008 | Related to | Defines evidence provenance and uncertainty handling for outputs produced by intelligence tasks |
| GENI-ADR-011 | Related to | Defines event identity and lifecycle behavior that must remain controlled by application logic |
| GENI-ADR-007 | Related to | Defines deterministic workflow boundaries and selective use of bounded reasoning. |
| GENI-ADR-014 | Related to | Defines human review when model-assisted outputs are ambiguous or consequential. |
| GENI-ADR-017 | Related to | Defines task/workflow budgets, normalized usage telemetry, and evaluation. |
| GENI-ADR-018 | Related to | Translation and multilingual processing may use the shared execution interface subject to rights and quality constraints. |

These relationships do not imply that the related ADRs have been accepted.

---

## 10. Implementation Implications

### 10.1 Required Implementation Work

If accepted, implementation should include:

1. Define the application-facing LLM execution interface.
2. Define the task request and result contracts.
3. Define the provider adapter contract.
4. Implement one initial provider adapter.
5. Implement model and task configuration.
6. Add structured output parsing and schema validation.
7. Add timeout and deadline handling.
8. Add bounded retry policies.
9. Add normalized execution errors.
10. Add usage and cost recording where available.
11. Add correlation IDs and execution tracing.
12. Add prompt and schema version tracking.
13. Add provider-independent tests using a fake adapter.
14. Add provider adapter contract tests.
15. Add task-specific evaluation and regression tests.

### 10.2 Migration or Compatibility Requirements

If an initial implementation already uses direct provider calls, those integrations should be migrated incrementally.

A complete rewrite is not required.

Migration should preserve existing task behavior and output contracts where possible.

### 10.3 Dependencies

Potential dependencies include:

- Selected LLM provider APIs.
- Credential and secret management.
- Configuration management.
- Structured schema validation.
- Application logging and tracing.
- Usage and cost persistence.
- Evaluation datasets and test infrastructure.

The choice of specific SDKs, providers, and validation libraries remains open.

### 10.4 Implementation Sequence

A practical implementation sequence is:

**Stage 1 — Minimal Execution Contract**

- Define task-oriented request and result types.
- Define the provider adapter interface.
- Implement a fake provider for tests.

**Stage 2 — Initial Provider Integration**

- Implement one provider adapter.
- Add model configuration.
- Add basic execution and error normalization.

**Stage 3 — Reliability and Validation**

- Add structured output validation.
- Add timeouts and bounded retries.
- Add explicit execution deadlines.
- Add provider capability checks.

**Stage 4 — Observability and Cost**

- Add usage records.
- Add execution tracing.
- Add cost reporting where reliable data is available.
- Add prompt and schema version tracking.

**Stage 5 — Product Task Integration**

- Integrate the execution layer into selected product components.
- Define task-specific schemas.
- Add task-specific evaluation.
- Verify that domain logic remains independent of provider APIs.

### 10.5 Verification Requirements

The implementation must demonstrate that:

- Application components can execute tasks without importing provider SDKs.
- A fake provider can be used in automated tests.
- Invalid structured outputs are rejected.
- Provider errors are normalized.
- Timeouts and retries respect configured limits.
- Usage records can be associated with individual executions.
- Model selection is controlled through configuration.
- Unsupported provider capabilities produce explicit errors.
- Analysis-stage calls cannot autonomously execute unrestricted tools.

---

## 11. Acceptance Criteria

| ID | Acceptance Criterion | Verification Method |
|---|---|---|
| AC-01 | Application components use the shared execution interface rather than directly depending on provider SDKs for ordinary task execution | Code inspection and dependency tests |
| AC-02 | At least one provider adapter implements the defined adapter contract | Adapter contract tests |
| AC-03 | A fake provider can execute representative tasks without network access | Automated unit tests |
| AC-04 | Structured outputs are parsed and validated against task schemas | Positive and negative schema tests |
| AC-05 | Invalid output is not silently treated as a successful task result | Error-handling tests |
| AC-06 | Execution deadlines and timeouts are enforced | Timeout tests |
| AC-07 | Retry attempts are bounded and restricted to retryable errors | Retry policy tests |
| AC-08 | Provider and model selection are controlled through explicit configuration | Configuration tests |
| AC-09 | Usage information is recorded when available and unavailable values are represented honestly | Usage recording tests |
| AC-10 | Each execution can be traced through a correlation identifier | Integration tests |
| AC-11 | Prompt and output schema versions can be identified for an execution | Trace inspection |
| AC-12 | Provider-specific capabilities are not silently assumed to be universally supported | Capability contract tests |
| AC-13 | Analysis-stage execution does not provide unrestricted autonomous tool access | Security and architecture tests |
| AC-14 | Task-specific evaluation can detect material output regressions after model or prompt changes | Evaluation tests |

Implementation verification is deferred until this ADR is formally accepted and the corresponding implementation work is scheduled.

---

## 12. Review and Reconsideration

### 12.1 Review Triggers

This ADR should be reviewed if:

- The product adopts a substantially different LLM execution strategy.
- A selected provider cannot meet required structured-output or reliability needs.
- Provider independence introduces unacceptable complexity.
- New privacy, data-processing, or content-rights requirements emerge.
- Model routing becomes a major architectural capability.
- Autonomous Agent behavior becomes a demonstrated product requirement.
- Cost or latency measurements invalidate the original assumptions.

### 12.2 Review Schedule

**Review Date:** Not scheduled.  
**Review Owner:** Project Owner.

### 12.3 Reconsideration Conditions

The recommendation should be reconsidered if evidence demonstrates that:

- A simpler architecture can meet all requirements without creating unacceptable coupling.
- A specific framework provides necessary capabilities with lower total complexity.
- The shared execution boundary prevents required provider capabilities from being used effectively.
- Product requirements materially change toward autonomous Agent workflows.

Any replacement decision must be recorded through a new ADR referencing this one.

---

## 13. References and Supporting Evidence

| Reference | Type | Relevance |
|---|---|---|
| `docs/01-product-and-system-architecture.md` | Internal | Product architecture and workflow-first principles |
| `docs/02-component-architecture-and-interfaces.md` | Internal | Component boundaries and interface responsibilities |
| `docs/03-data-model-and-storage-design.md` | Internal | Data and execution record implications |
| `docs/04-implementation-plan-and-roadmap.md` | Internal | Implementation dependencies and sequence |
| `docs/05-architecture-decision-records.md` | Internal | Architectural decision governance |
| `docs/adr/adr-template.md` | Internal | ADR structure and approval requirements |

Provider-specific technical documentation and performance measurements must be added after candidate providers are selected and evaluated.

No provider benchmark or cost comparison is claimed by this proposal.

---

## 14. Decision History

| Version | Date | Status | Change Summary | Author or Reviewer |
|---|---|---|---|---|
| 1.0 | 2026-11-17 | Proposed | Initial proposal for a shared provider-independent LLM execution architecture | AI Architecture Assistant |
| 1.1 | 2026-11-18 | Proposed | Synchronized version history and end-of-document metadata with the current Proposed ADR revision; no approval status changed. | AI Architecture Assistant |
| 1.2 | 2026-11-18 | Proposed | Standardized decision authority terminology to Project Owner, consistent with GENI-GOV-005. | AI Architecture Assistant |

---

**End of ADR**

**ADR ID:** `GENI-ADR-006`  
**File:** `GENI-ADR-006-provider-independent-llm-execution-architecture.md`  
**Version:** 1.2  
**Status:** Proposed