# Agent Template — Implementation Specification

## 1. Purpose

This document defines the implementation contracts and runtime behavior of the Tier 1 agent framework.

The implementation must follow the architecture document and preserve the separation between core abstractions and concrete integrations.

The framework is async-first, provider-agnostic, modular, and testable.

## 2. Technology and Packaging

- Python with `src/` layout.
- `uv` for dependency and environment management.
- Pydantic for configuration and structured validation where appropriate.
- LiteLLM as the initial LLM adapter.
- pytest and pytest-asyncio for testing.
- Ruff for linting and formatting.
- A static type checker such as mypy or pyright.
- Import architecture checks.
- Dependency and secret scanning in CI.

The core package must not require FastAPI, PostgreSQL, Redis, or a vector database.

Optional dependency groups should be used for integrations such as:

- `dev`
- `eval`
- `mcp`
- `api`
- `retrieval`

Prompt Markdown files must be included as package data.

## 3. Public Agent API

The Agent exposes asynchronous operations:

```python
class Agent:
    async def run(
        self,
        user_input: str,
        *,
        conversation_id: str | None = None,
        user_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> AgentResult:
        ...

    async def stream(
        self,
        user_input: str,
        *,
        conversation_id: str | None = None,
        user_id: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> AsyncIterator[AgentStreamEvent]:
        ...

    async def aclose(self) -> None:
        ...
```

Exact optional parameters may be refined during implementation, but the async lifecycle and separation of run and conversation identity must remain.

The Agent must not create a new provider client for each run.

## 4. Execution Context and Budget

### 4.1 RunContext

`RunContext` is immutable and specific to one execution.

It contains:

- `run_id`
- `conversation_id`
- Optional `user_id`
- Immutable metadata.
- `RunBudget`.
- Deadline information.

It must not contain mutable usage counters.

### 4.2 RunBudget

```python
@dataclass(frozen=True)
class RunBudget:
    max_steps: int
    max_tool_calls: int
    max_tokens: int | None
    max_cost: Decimal | None
    timeout_seconds: float
```

All limits must be validated at configuration time.

### 4.3 RunUsage

`RunUsage` is an immutable snapshot containing:

- LLM decision cycles.
- Tool calls.
- Prompt tokens.
- Completion tokens.
- Total tokens.
- Cost, if known.
- Retry count.
- Elapsed time.

Estimated and provider-reported usage should be distinguishable.

Unknown cost is `None`, not zero.

### 4.4 BudgetTracker

`BudgetTracker` is mutable and owns the counters.

All consume operations and limit checks must use one shared `asyncio.Lock`.

The following must be atomic:

- Checking a limit.
- Incrementing the associated counter.
- Rejecting an operation that would exceed a limit.

`snapshot()` must also acquire the same lock and return a consistent immutable snapshot.

Token consumption is cumulative prompt plus completion usage.

The runtime must check limits before scheduling expensive work.

### 4.5 Deadline

Timeout calculations use a monotonic clock.

For any nested operation:

`effective_timeout = min(configured_timeout, remaining_deadline)`

If no time remains, the operation must not start.

The runtime must distinguish a local timeout from guaranteed cancellation of a remote operation.

## 5. LLM Provider Contract

### 5.1 Interface

```python
class LLMProvider(Protocol):
    async def complete(
        self,
        request: LLMRequest,
    ) -> CompletionResponse:
        ...

    def stream(
        self,
        request: LLMRequest,
    ) -> AsyncIterator[LLMStreamEvent]:
        ...

    async def aclose(self) -> None:
        ...
```

### 5.2 Normalized Schemas

Messages use normalized roles:

- `system`
- `developer`
- `user`
- `assistant`
- `tool`

Tool call IDs must be preserved between assistant messages and tool results.

A normalized `ToolCall` includes:

- `id`
- `name`
- `arguments`

`CompletionResponse` includes:

- Assistant message.
- Tool calls.
- Finish reason.
- Optional usage.
- Provider ID.
- Model ID.

Provider-specific types must not leak into Agent or ToolExecutor code.

### 5.3 Capabilities

Provider capabilities must be declared or validated.

Capabilities include:

- Tool calling.
- Streaming.
- Structured output.
- Usage reporting.

The Agent must not assume every provider supports every capability.

### 5.4 Retry Policy

Retry only transient LLM provider failures.

Use:

- Bounded attempts.
- Exponential backoff.
- Jitter.
- Deadline-aware delays.

Do not retry:

- Cancellation.
- Authentication failures.
- Authorization failures.
- Invalid requests.
- Schema or validation failures.

Retry attempts must be visible in usage and tracing.

### 5.5 Cancellation

Provider adapters must preserve `asyncio.CancelledError`.

They should close local stream resources when possible.

They must not retry or normalize cancellation as an ordinary provider error.

## 6. Tool Contracts

### 6.1 Tool Definition

Every tool must expose:

- Unique name.
- Clear description.
- Input schema.
- Expected output.
- Category or tags.
- Risk and side-effect metadata.
- Timeout.
- Input and output size limits.

Descriptions should explain:

- What the tool does.
- When it should be used.
- When it should not be used.
- Important side effects.
- Constraints and expected results.

Tool metadata is part of the model-facing contract and should be tested.

### 6.2 Tool Registry

The registry supports:

- Registration.
- Lookup.
- Listing.

It must not execute tools.

It must reject duplicate names unless an explicit replacement policy is introduced.

### 6.3 ToolExecutor

Execution order:

1. Resolve tool.
2. Check permissions.
3. Validate input schema.
4. Enforce input size limit.
5. Check and consume tool-call budget.
6. Compute effective timeout.
7. Invoke the tool.
8. Validate output.
9. Verify output serializability.
10. Enforce output size limit.
11. Normalize result or error.
12. Attach execution metadata.

Every Tier 1 tool follows an asynchronous interface.

Synchronous adapters must explicitly isolate blocking operations, for example with `asyncio.to_thread`.

The executor must not automatically retry tool invocations.

### 6.4 ToolResult

```python
@dataclass(frozen=True)
class ToolResult:
    content: str
    success: bool
    metadata: Mapping[str, object]
    error_category: str | None = None
    recoverable: bool = False
```

Semantics:

| success | recoverable | Meaning |
|---|---|---|
| True | False | Successful execution |
| False | True | Controlled, recoverable tool failure |
| False | False | Non-recoverable failure; terminal handling required |
| True | True | Invalid combination |

Recoverability must be explicit and must not be inferred from arbitrary exception messages.

A recoverable failure is only appropriate when:

- The tool executed and returned a known controlled failure.
- The result is safe to serialize.
- The runtime can safely continue.
- The model can make a meaningful next decision.

Permission denial, cancellation, budget exhaustion, timeout, invalid tool contract, and unexpected internal failures are terminal by default.

### 6.5 Multiple Tool Calls

Tool calls in one LLM response execute sequentially and in the order returned.

Example:

```python
for call in response.tool_calls:
    result = await executor.execute(call, context)
    append_tool_result(result)

    if result.is_recoverable_failure:
        break
```

A recoverable failure stops the remaining calls in that batch. The Agent may then ask the LLM to decide what to do next.

A terminal failure raises or propagates a typed exception and stops the run.

No remaining calls from that batch may execute after a terminal failure.

### 6.6 Cancellation

The executor must:

- Propagate `CancelledError`.
- Stop scheduling additional work.
- Clean up resources and owned tasks.
- Release resources in `finally`.
- Avoid swallowing cancellation.
- Preserve the original cancellation if cleanup itself fails.

Timeout cancellation of a coroutine does not guarantee that an external operation or remote side effect has stopped.

## 7. MCP Client Integration

MCP is an optional integration.

The implementation should follow the current official MCP specification and current Python SDK APIs.

### 7.1 Modules

```text
tools/mcp/
├── __init__.py
├── client.py
├── adapter.py
├── config.py
├── schemas.py
└── manager.py
```

### 7.2 Responsibilities

`client.py`:

- Establishes MCP connections.
- Initializes sessions.
- Lists tools.
- Calls tools.
- Closes sessions and transports.

`adapter.py`:

- Converts MCP tool definitions into internal tool definitions.
- Converts internal calls into MCP calls.
- Normalizes MCP responses.

`config.py`:

- Defines server and transport configuration.
- Validates connection parameters.
- Defines timeouts and controlled process settings.

`schemas.py`:

- Defines normalized internal MCP-related models.
- Prevents SDK-specific objects from leaking into the core.

`manager.py`:

- Manages multiple configured server connections.
- Owns session lifecycle.
- Handles reconnection policy where appropriate.
- Tracks discovered tool definitions.
- Handles tool-list refresh and reconciliation.

### 7.3 Security

MCP servers are untrusted integration boundaries.

Every MCP tool must pass through internal permission checks, input validation, budget enforcement, timeout handling, and output validation.

For stdio transports:

- Executable paths must be controlled.
- Commands and arguments must be allowlisted.
- Environment variables must be explicitly configured.
- Secrets must not be exposed unnecessarily.
- Process lifecycle must be owned and cleaned up.

Remote transports must use explicitly configured endpoints and appropriate transport security.

### 7.4 Scope

Tier 1:

- MCP Client.
- Tool discovery.
- MCP tool adapter.
- Tool invocation.
- Session and connection lifecycle.
- Error normalization.
- Cancellation handling.

Deferred:

- MCP Resources.
- MCP Prompts.
- MCP Server implementation.

MCP SDK versions and protocol compatibility must be pinned and covered by contract tests.

## 8. Memory Contracts

### 8.1 Interfaces

The memory layer separates policy from storage.

`Memory` represents conversation-level memory behavior.

`MemoryStore` represents persistence operations.

A storage contract should support:

```python
class MemoryStore(Protocol):
    async def load(self, conversation_id: str) -> ConversationSnapshot:
        ...

    async def save(
        self,
        conversation_id: str,
        messages: Sequence[Message],
        *,
        expected_version: int,
    ) -> ConversationSnapshot:
        ...

    async def clear(self, conversation_id: str) -> None:
        ...
```

### 8.2 ConversationSnapshot

A snapshot contains:

- Messages.
- Version.

A new conversation begins at version `0`.

A successful save increments the version exactly once.

A failed save must leave the version unchanged.

Messages and version must be updated atomically.

A stale `expected_version` must be rejected.

### 8.3 Conversation Locking

Tier 1 permits one active run per conversation.

Lock acquisition:

- Maximum wait: five seconds.
- Further bounded by the remaining run deadline.
- Raises `ConversationConflictError` on expiry.
- Lock release occurs in `finally`.

### 8.4 Sliding Window

Sliding-window memory must:

- Preserve system and developer instructions.
- Remove complete conversation turns.
- Preserve assistant tool calls and their corresponding tool results.
- Never leave an incomplete tool-call/result pair.

Tier 1 does not implement summarization.

### 8.5 Memory and Knowledge Separation

Conversation memory is not a knowledge base.

Future implementations may support:

- Semantic memory.
- Episodic memory.
- Procedural memory.
- Long-term memory.
- Retrieval-backed knowledge.

These are extension points, not Tier 1 requirements.

## 9. Agent Execution Lifecycle

The execution lifecycle is conceptually:

`STARTED → INPUT_VALIDATED → LLM_REQUESTED → TOOL_EXECUTION_PENDING → TOOL_EXECUTING → LLM_CONTINUATION → COMPLETED`

Terminal states:

- `FAILED`
- `CANCELLED`
- `BUDGET_EXCEEDED`

Terminal states cannot transition back into active execution.

### 9.1 Run Sequence

1. Create `RunContext`.
2. Create `BudgetTracker`.
3. Acquire conversation lock if memory is enabled.
4. Validate user input.
5. Load the current conversation snapshot.
6. Construct the initial context.
7. Build the LLM request.
8. Check deadline and budget.
9. Request an LLM completion.
10. Account for provider-reported usage.
11. If tool calls exist, execute them under ToolExecutor policies.
12. Append normalized tool results.
13. Continue the LLM loop if appropriate.
14. Validate the final output.
15. Persist the completed conversation using the expected version.
16. Emit completion information.
17. Release locks and owned resources.

No expensive operation may start after the deadline or relevant budget is exhausted.

### 9.2 Persistence

Only completed, valid conversation turns should be persisted as completed turns.

An incomplete assistant response caused by cancellation must not be stored as a completed response.

Persistence errors must not be represented as successful saves.

## 10. Streaming

Tier 1 supports streaming final text responses.

Tool-call streaming and incremental tool execution are deferred.

### 10.1 Events

```python
class AgentStreamEvent:
    ...
```

Supported event types:

- `run_started`
- `text_delta`
- `run_completed`
- `run_failed`
- `run_cancelled`

A terminal event may occur at most once.

### 10.2 Output Validation

If the output guardrail requires the complete response, buffer the response until validation succeeds.

Do not publish unvalidated text as though it had passed a full-response guardrail.

Incremental validation is permitted only when the guardrail explicitly supports it.

### 10.3 Stream Completion

Consumer code must not interpret stream exhaustion without a completion event as success.

Stream failures must preserve typed exception semantics.

Cancellation must propagate and owned resources must be closed.

Incomplete output must not be persisted as a completed turn.

## 11. Context Construction

The framework must separate execution state from the LLM request.

The Agent should construct an LLM request from a curated subset of available context.

Tier 1 requirements:

- Enforce configured token/context limits.
- Preserve system and developer instructions.
- Include only relevant conversation history.
- Avoid forwarding oversized tool outputs without control.
- Preserve tool-call/result consistency.
- Treat tool outputs and retrieved external content as untrusted.
- Track token estimates when provider usage is unavailable.
- Distinguish estimated usage from provider-reported usage.

The implementation should provide extension points for:

- Context selection.
- Retrieval.
- Context reduction.
- Tool-output summarization.
- Context isolation.

A full context engine and automatic compaction are Tier 2.

## 12. Tool Discovery and Skills Extension

Tier 1 tool metadata must support future progressive disclosure.

The model-facing tool description should be concise and informative.

The registry should permit categorization and filtering.

A future Skills Engine may expose:

1. A compact skill name and description.
2. Detailed instructions loaded only when selected.
3. Additional references or execution resources loaded on demand.

Tier 1 does not implement a full Skills Engine or dynamic skill filesystem.

## 13. Guardrails and Security

### 13.1 Input Guardrails

Run before the first LLM request.

### 13.2 Tool Argument Validation

Performed by ToolExecutor using each tool's schema.

### 13.3 Output Guardrails

Run before final output publication and successful persistence.

### 13.4 Permissions

Default-deny.

A tool must be explicitly permitted before execution.

Permission denial is terminal by default.

### 13.5 Untrusted Content

Tool results, external documents, retrieved content, and MCP responses are untrusted.

They must not be promoted to system or developer instructions.

Prompt-injection defenses are defense-in-depth. Simple text filters cannot guarantee prevention.

### 13.6 Secrets

Configuration must use secret-aware types such as `SecretStr` where appropriate.

Redaction must happen before data reaches logs.

Error messages must not expose credentials or sensitive request content.

### 13.7 Sandbox

Tier 1 contains only a sandbox interface placeholder.

It does not execute arbitrary code or expose unrestricted filesystem or shell access.

## 14. Factory and Resource Lifecycle

`factory.py` is the Composition Root.

It constructs:

- LLM provider.
- Memory implementation.
- Tool definitions.
- Tool registry.
- Tool executor.
- Permission policy.
- Guardrails.
- Observability components.
- Agent.

Factory helpers may remain in the same file until implementation complexity justifies splitting them.

Provider clients and shared resources are created at application composition time, not for every run.

Lifecycle ownership must be explicit.

`aclose()` must close resources owned by the Agent or its composition root without closing externally owned resources unexpectedly.

## 15. Configuration and CLI

Configuration must fail fast.

The CLI includes:

- `validate-config`
- Evaluation execution.

`validate-config` must not make network requests by default.

A provider connectivity check may be exposed explicitly through `--check-provider`.

Secrets must be supplied through environment variables or supported secret providers, not committed configuration files.

## 16. Evaluation

Evaluation is organized into:

- `evals/datasets/`
- `evals/runners/`
- `evals/judges/`
- `evals/metrics/`
- `evals/rubrics/`
- `evals/failure_analysis/`

### 16.1 Evaluation Levels

1. Final output evaluation.
2. Component evaluation.
3. Trajectory evaluation.

### 16.2 Trace-Based Evaluation

Where possible, evaluation should inspect:

- LLM decisions.
- Selected tools.
- Tool arguments.
- Tool results.
- Retry behavior.
- Budget events.
- Execution errors.
- Final result.

### 16.3 Failure Taxonomy

Maintain categories such as:

- Incorrect final answer.
- Wrong tool selection.
- Missing tool selection.
- Unnecessary tool call.
- Invalid tool arguments.
- Permission denial.
- Tool timeout.
- Provider failure.
- Budget exhaustion.
- Context overflow.
- Memory consistency failure.
- Output validation failure.
- Cancellation or cleanup failure.

### 16.4 Initial Metrics

- Task success rate.
- Tool selection accuracy.
- Tool precision and recall where applicable.
- Unnecessary tool calls.
- Budget violation rate.
- Cost per successful task when cost is available.
- Median latency.
- P95 latency.
- Tool execution success and failure rates.

Evaluation thresholds must be task-specific and grounded in the dataset.

CI evaluation gates should detect regressions without relying on arbitrary universal thresholds.

Advanced calibration metrics such as ECE and calibration curves are deferred to Tier 2 or domain-specific extensions.

## 17. Observability

Every run should be traceable.

Trace data should make it possible to reconstruct:

- Run identity.
- Conversation identity where appropriate.
- LLM requests and responses.
- Tool selection and execution.
- Tool outcomes.
- Token usage.
- Cost when known.
- Latency.
- Retry attempts.
- Budget consumption.
- Terminal outcome.

Sensitive content must be redacted.

Avoid logging full prompts, credentials, or unrestricted tool outputs by default.

Tier 1 includes structured logging and basic tracing.

Advanced metrics infrastructure is deferred.

## 18. Testing Requirements

### 18.1 Unit Tests

Test individual components:

- BudgetTracker.
- Context construction.
- Tool registry.
- ToolExecutor.
- Permission checks.
- Guardrails.
- Memory policies.
- Provider normalization.
- MCP adapters.
- Redaction.

### 18.2 Integration Tests

Test interactions between:

- Agent and fake provider.
- Agent and ToolExecutor.
- Agent and memory.
- MCP client and tool adapter.
- Factory and configuration.

### 18.3 Contract Tests

Verify that:

- Providers conform to normalized LLM schemas.
- Tools conform to tool contracts.
- Memory implementations satisfy versioning semantics.
- MCP adapters preserve tool schemas and error semantics.

### 18.4 Security Tests

Verify:

- Default-deny behavior.
- Permission enforcement.
- Input and output limits.
- Secret redaction.
- Untrusted tool output handling.
- MCP process configuration restrictions.
- No accidental arbitrary code execution.

### 18.5 Lifecycle Tests

Verify:

- Cancellation propagation.
- Resource cleanup.
- Lock release.
- Timeout behavior.
- No work after cancellation.
- No incomplete conversation persistence.

### 18.6 Concurrency Tests

Verify:

- Atomic budget consumption.
- Consistent usage snapshots.
- Conversation lock contention.
- Stale version rejection.
- Atomic memory saves.

Use an injected/fake clock where possible instead of relying on flaky sleeps.

### 18.7 Fake Provider

The test provider should support:

- Normal completions.
- Tool-call responses.
- Recoverable and terminal errors.
- Usage reporting.
- Transient provider failures.
- Streaming.
- Cancellation.
- Configurable latency.

CI must not require paid API keys.

## 19. CI and Quality Gates

CI should run:

- Formatting and lint checks.
- Type checks.
- Unit tests.
- Integration tests.
- Contract tests.
- Security tests.
- Architecture dependency checks.
- Package build and installation tests.
- Evaluation regression checks where configured.
- Dependency vulnerability scanning.
- Secret scanning.

The package should be tested after installation, including prompt package-data availability.

## 20. Implementation Order

### Phase 1 — Project Foundation

- Packaging.
- Configuration.
- Exceptions.
- Logging configuration.
- Architecture dependency rules.

### Phase 2 — Core Contracts

- LLM schemas.
- LLM provider interface.
- Tool interface.
- Memory interfaces.
- RunContext.
- RunBudget.
- RunUsage.
- BudgetTracker.

### Phase 3 — Core Runtime

- ToolRegistry.
- ToolExecutor.
- Permission interface.
- Calculator tool.
- Agent loop.
- Conversation locking.
- Memory implementation.

### Phase 4 — Provider Integration

- LiteLLM adapter.
- Error normalization.
- Usage normalization.
- Retry policy.
- Provider lifecycle.

### Phase 5 — Guardrails and Security

- Input validation.
- Output validation.
- Secret redaction.
- Default-deny permissions.
- Size and timeout enforcement.

### Phase 6 — MCP Integration

- MCP configuration.
- Client and session lifecycle.
- Tool discovery.
- Internal tool adapter.
- Error normalization.
- Security and contract tests.

### Phase 7 — Streaming and Observability

- Final text streaming.
- Stream events.
- Cancellation behavior.
- Trace instrumentation.
- Run usage reporting.

### Phase 8 — CLI, Documentation, and Evaluation

- CLI commands.
- Examples.
- Evaluation runner.
- Datasets and rubrics.
- Failure analysis.
- CI quality gates.
- Package verification.

## 21. Acceptance Criteria

Tier 1 is ready when:

1. A basic async agent can run with a fake provider.
2. The Agent is independent of provider-specific SDK types.
3. Tools execute only through ToolExecutor.
4. Tool permissions are default-deny.
5. Tool input and output limits are enforced.
6. Run budgets are atomic and deadline-aware.
7. Cancellation propagates without being swallowed.
8. Memory updates are atomic and version-checked.
9. Concurrent runs for one conversation are controlled.
10. MCP tools are adapted to internal contracts and execute through ToolExecutor.
11. Final output guardrails run before successful completion.
12. Streaming has explicit terminal events.
13. Incomplete runs are not persisted as completed turns.
14. Secrets are redacted from logs.
15. Traces expose meaningful execution behavior.
16. Core tests run without paid external services.
17. Package installation includes required prompt resources.
18. Optional integrations do not become mandatory core dependencies.
19. Architecture dependency rules are enforced in CI.
20. Evaluation regression checks can detect task-specific failures.

The objective is a dependable core with explicit extension boundaries, not an attempt to implement every advanced agent capability in the first release.