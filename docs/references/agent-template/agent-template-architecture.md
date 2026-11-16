# Agent Template — Architecture

## 1. Purpose

This project provides a production-oriented Python template for building AI agents.

The architecture prioritizes:

- Async-first execution.
- Provider-agnostic LLM integration.
- Modular and replaceable components.
- Explicit execution budgets and deadlines.
- Secure tool execution.
- Predictable lifecycle and cancellation behavior.
- Testability and observability.
- Extensibility without unnecessary infrastructure dependencies.

The core package must remain independent of any mandatory API framework, database, vector database, or cloud provider.

## 2. Architectural Principles

### 2.1 Small Core, Explicit Extensions

The core should contain only the capabilities required to execute a reliable agent:

- Agent orchestration.
- LLM abstraction.
- Tool abstraction and execution.
- Execution context and budgets.
- Short-term conversation memory.
- Input and output guardrails.
- Security boundaries.
- Basic observability.

External infrastructure belongs behind interfaces or optional integrations.

### 2.2 Async-First

Core execution APIs are asynchronous.

The agent exposes:

- `run()`
- `stream()`
- `aclose()`

LLM providers and tools follow asynchronous contracts.

Blocking integrations must be isolated explicitly rather than blocking the event loop.

### 2.3 Dependency Inversion

The Agent depends on interfaces, not provider-specific implementations.

The Factory acts as the Composition Root and constructs concrete dependencies.

### 2.4 Workflow Before Agent

An agent is appropriate when execution requires dynamic decisions, adaptation, or model-driven tool selection.

A deterministic sequence of operations should generally be implemented as a workflow rather than an agent loop.

Hybrid systems may use deterministic workflows for predictable stages and agents for uncertain decision-making.

The framework does not include a workflow engine in Tier 1.

### 2.5 Fail Securely

- Tool permissions are default-deny.
- External content is untrusted.
- Secrets must not appear in logs.
- Cancellation must propagate.
- Budget and deadline limits must be enforced before expensive operations.
- Runtime failures must not be silently converted into successful results.

## 3. High-Level Architecture

The system is organized into the following layers:

1. Agent orchestration
2. Context and execution state
3. LLM abstraction and provider adapters
4. Tool definitions, registry, and executor
5. Memory interfaces and short-term implementation
6. Guardrails
7. Security
8. Observability
9. Factory and configuration

The Agent coordinates execution. It does not own provider-specific logic, tool implementation details, or persistence mechanisms.

The Factory wires concrete implementations together.

## 4. Project Structure

```text
agent-template/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── security.yml
│       ├── eval.yml
│       └── release.yml
├── docs/
│   ├── architecture.md
│   ├── implementation-spec.md
│   ├── security.md
│   ├── development.md
│   └── extension-guide.md
├── examples/
│   ├── basic_agent.py
│   └── custom_tool.py
├── evals/
│   ├── datasets/
│   ├── runners/
│   ├── judges/
│   ├── metrics/
│   ├── rubrics/
│   └── failure_analysis/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   ├── security/
│   ├── e2e/
│   └── fixtures/
├── src/
│   └── agent_template/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── factory.py
│       ├── config.py
│       ├── exceptions.py
│       ├── py.typed
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── core.py
│       │   ├── loop.py
│       │   ├── context.py
│       │   └── prompts/
│       │       ├── __init__.py
│       │       ├── system.md
│       │       └── tool_instructions.md
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── schemas.py
│       │   └── providers/
│       │       ├── __init__.py
│       │       └── litellm_provider.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── registry.py
│       │   ├── executor.py
│       │   ├── mcp/
│       │   │   ├── __init__.py
│       │   │   ├── client.py
│       │   │   ├── adapter.py
│       │   │   ├── config.py
│       │   │   ├── schemas.py
│       │   │   └── manager.py
│       │   └── builtin/
│       │       ├── __init__.py
│       │       └── calculator.py
│       ├── memory/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── short_term.py
│       │   └── in_memory.py
│       ├── guardrails/
│       │   ├── __init__.py
│       │   ├── input_checks.py
│       │   └── output_checks.py
│       ├── security/
│       │   ├── __init__.py
│       │   ├── redaction.py
│       │   ├── tool_permissions.py
│       │   └── sandbox.py
│       └── observability/
│           ├── __init__.py
│           ├── logging_config.py
│           └── tracing.py
├── .dockerignore
├── .editorconfig
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── CHANGELOG.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── Makefile
├── README.md
├── SECURITY.md
├── pyproject.toml
├── uv.lock
└── .python-version
```

The MCP integration is an optional integration layer. Its dependencies must not become mandatory dependencies of the core package.

## 5. Component Responsibilities

### 5.1 Agent

Location: `agent/`

Responsibilities:

- Coordinate the execution lifecycle.
- Validate incoming requests.
- Load conversation history.
- Build LLM requests.
- Run the decision loop.
- Coordinate tool execution.
- Apply output guardrails.
- Persist successful conversation updates.
- Emit execution events.
- Handle cancellation and cleanup.

The Agent must not contain provider-specific or storage-specific logic.

### 5.2 Execution Context

Location: `agent/context.py`

`RunContext` represents immutable information associated with one execution.

It includes:

- `run_id`
- `conversation_id`
- Optional `user_id`
- Immutable metadata
- Run budget configuration
- Deadline information

`RunContext` is frozen and must not be used as a mutable counter container.

Runtime usage is tracked separately through `BudgetTracker`.

### 5.3 Budget Management

The budget subsystem contains:

- `RunBudget`: configured limits.
- `RunUsage`: immutable usage snapshot.
- `BudgetTracker`: mutable execution counters.

Supported limits:

- Maximum LLM decision cycles.
- Maximum total tool calls.
- Maximum cumulative tokens.
- Maximum estimated or reported cost.
- Maximum execution duration.

`max_steps` counts LLM decision cycles.

`max_tool_calls` counts all tool invocations.

Token usage includes prompt and completion tokens.

Unknown cost must remain unknown (`None`), not be represented as zero.

All budget checks and counter updates must be atomic.

### 5.4 LLM Layer

Location: `llm/`

The LLM layer defines provider-independent contracts.

The initial implementation uses LiteLLM as an adapter.

The Agent must never depend directly on LiteLLM-specific types.

Provider capabilities must be explicit, including:

- Tool calling.
- Streaming.
- Structured output.
- Usage reporting.

Provider-specific exceptions and response formats must be normalized.

### 5.5 Tools

Location: `tools/`

Tool responsibilities are divided into:

**Tool Definition**

Defines:

- Name
- Description
- Input schema
- Expected output
- Category and tags
- Risk and side-effect metadata
- Timeout and size limits

**Tool Registry**

Only handles registration and lookup.

It must not execute tools or implement authorization.

**Tool Executor**

Handles:

- Tool resolution.
- Permission checks.
- Input validation.
- Size limits.
- Budget consumption.
- Timeout enforcement.
- Invocation.
- Output validation.
- Error normalization.
- Execution metadata.

Tool outputs are untrusted data. They must never be treated as system or developer instructions.

### 5.6 MCP Integration

Location: `tools/mcp/`

Tier 1 includes an MCP Client integration.

Responsibilities:

- Connect to configured MCP servers.
- Initialize and manage sessions.
- Discover available tools.
- Convert MCP tools into internal tool definitions.
- Invoke remote tools.
- Normalize responses and errors.
- Handle cancellation and lifecycle.
- Refresh or reconcile dynamic tool lists.

MCP tools must pass through the same internal ToolExecutor policies as native tools.

MCP servers are not inherently trusted.

For stdio transports, process commands, arguments, environment variables, and executable paths must be explicitly controlled and allowlisted.

Tier 1 does not implement an MCP Server.

MCP Resources and Prompts are deferred to Tier 2.

The MCP implementation must follow the current official protocol and SDK contracts rather than assuming older transport or package APIs remain valid.

### 5.7 Memory

Location: `memory/`

Memory policy and memory storage are separate concerns.

`memory/base.py` defines the interfaces.

`memory/short_term.py` handles conversation history and sliding-window policies.

`memory/in_memory.py` provides the initial storage implementation.

The memory interface must not assume that all future memory systems use the same storage mechanism.

Conversation memory is distinct from a knowledge base or retrieval system.

Tier 1 includes short-term conversation memory only.

### 5.8 Guardrails

Location: `guardrails/`

Guardrails validate content.

They include:

- Input validation.
- Output validation.

Tool argument validation belongs to ToolExecutor.

Guardrails do not replace authorization or security controls.

### 5.9 Security

Location: `security/`

Security responsibilities include:

- Tool permissions.
- Secret redaction.
- Security-related execution boundaries.
- Future sandbox integration interfaces.

Tool permissions are default-deny.

The sandbox module is an interface placeholder only. It must not enable arbitrary code execution in Tier 1.

### 5.10 Observability

Location: `observability/`

Tier 1 includes structured logging and basic tracing.

The trace model should make it possible to inspect:

- Run start and completion.
- LLM requests and responses.
- Tool selection and execution.
- Tool outcomes.
- Token usage.
- Cost when known.
- Latency.
- Retry attempts.
- Budget events.
- Errors and terminal outcomes.

Logs, traces, and metrics are distinct concepts.

Advanced metrics infrastructure is deferred to Tier 2.

Sensitive data must be redacted before logging.

## 6. Context and Harness Engineering

The LLM request must be treated as a deliberately constructed view of execution state, not as a dump of all available information.

The execution context may contain:

- Conversation history.
- System and developer instructions.
- Available tool descriptions.
- Tool results.
- Relevant metadata.
- Retrieved information in future extensions.
- Execution constraints.

The LLM request is a curated subset of that information.

Context construction should follow five conceptual operations:

1. Generate: create task-relevant context.
2. Retrieve: select relevant existing information.
3. Write: persist useful state outside the immediate prompt.
4. Reduce: remove redundant or unnecessary information.
5. Isolate: separate unrelated tasks, data, and execution state.

Tier 1 requirements:

- Keep execution state separate from the final LLM request.
- Enforce context and token limits.
- Avoid blindly forwarding large tool outputs.
- Preserve system and developer instructions.
- Preserve complete tool-call/result relationships.
- Treat external content as untrusted.
- Keep conversation history separate from long-term knowledge.

A dedicated context-engine or advanced compaction subsystem is deferred to Tier 2.

## 7. Tool Discovery and Progressive Disclosure

The framework should avoid exposing an unnecessarily large collection of detailed tool definitions to every LLM request.

Tier 1 establishes metadata and extension points for tool discovery.

Tool metadata should support:

- Name.
- Short description.
- Category and tags.
- Input schema.
- Risk level.
- Side-effect information.
- Availability and permission information.

The architecture should permit future progressive disclosure:

1. Expose a compact list of available capabilities.
2. Select a relevant capability.
3. Load its detailed instructions or associated tools when needed.

A full Skills Engine, skill filesystem, and dynamic instruction loader are Tier 2 features.

## 8. Execution Lifecycle

A run follows a controlled lifecycle:

`STARTED → INPUT_VALIDATED → LLM_REQUESTED → TOOL_EXECUTION_PENDING → TOOL_EXECUTING → LLM_CONTINUATION → COMPLETED`

Terminal outcomes include:

- `FAILED`
- `CANCELLED`
- `BUDGET_EXCEEDED`

Terminal states cannot transition back into active execution.

Before every resource-consuming operation, the system checks the remaining budget and deadline.

### 8.1 Multiple Tool Calls

Tool calls returned in one LLM response execute sequentially in the order provided.

If a tool returns a controlled, recoverable failure, the result may be returned to the LLM and execution of the remaining calls in that batch stops.

Terminal execution failures stop the run.

No automatic tool retries are allowed.

### 8.2 Cancellation

Cancellation is control flow, not an ordinary error.

`asyncio.CancelledError` must propagate through:

- Agent.
- ToolExecutor.
- LLM provider adapters.
- MCP integration.

The runtime must stop scheduling new work, release owned resources, and avoid persisting incomplete assistant responses as completed turns.

Cancellation of a local coroutine does not guarantee cancellation of an external provider request or remote side effect.

## 9. Conversation Consistency

A conversation is identified by `conversation_id`, which is distinct from `run_id`.

When memory is enabled:

- A conversation ID is required.
- Only one active run per conversation is permitted in Tier 1.
- Lock acquisition is bounded to five seconds and further bounded by the remaining run deadline.
- A lock timeout raises `ConversationConflictError`.
- The lock is released in `finally`.
- Memory saves use optimistic version checking.
- Messages and version are updated atomically.
- A successful save increments the version exactly once.
- A failed save must not increment the version.

Sliding-window memory removes complete turns only and must preserve system/developer messages and tool-call/result pairs.

## 10. Retry Policy

Retries are limited to transient LLM provider failures.

Requirements:

- Bounded attempts.
- Exponential backoff.
- Jitter.
- Deadline awareness.
- No retry on cancellation.
- No retry on authentication, authorization, or validation failures.
- No automatic retry of tool invocations.

Retries must not violate the execution budget.

## 11. Evaluation Architecture

Evaluation is a first-class engineering activity.

The evaluation system should inspect three levels:

1. Final output quality.
2. Component behavior.
3. Execution trajectory.

Trajectory evaluation should inspect the sequence of model decisions and tool interactions, not only the final answer.

Evaluation should use traces where possible.

A failure taxonomy should be maintained before adding increasingly complex evaluation metrics.

Tier 1 evaluation foundations include:

- Task success rate.
- Tool selection accuracy.
- Tool selection precision and recall where applicable.
- Unnecessary tool calls.
- Budget violation rate.
- Cost per successful task when cost is available.
- Median and P95 latency.
- Tool permission and execution failures.

Evaluation regression gates should be task-specific and based on a maintained dataset.

Confidence calibration, ECE, calibration curves, and advanced uncertainty-based escalation are deferred to Tier 2 or use-case-specific extensions.

## 12. Extension Points

The architecture should allow future implementations of:

- Long-term memory.
- Semantic, episodic, and procedural memory.
- Retrieval and knowledge bases.
- Context compaction.
- Progressive tool disclosure.
- Skills.
- Planning and task decomposition.
- Reflection and replanning.
- Human approval.
- Workflow orchestration.
- Advanced tracing and metrics.
- Additional LLM providers.
- Additional tool transports.

These extension points must not make Tier 1 dependent on Tier 2 infrastructure.

Planning and reflection must never override security permissions, cancellation, or exhausted budgets.

## 13. Dependency Rules

- Agent depends on interfaces, not concrete providers.
- Factory may import concrete implementations.
- LLM adapters implement the LLM interface.
- ToolExecutor depends on tool and permission interfaces.
- ToolRegistry does not depend on ToolExecutor.
- Memory policy is separate from storage.
- Guardrails and Security must not import Agent or concrete Tool implementations.
- MCP adapters must integrate through the internal tool contracts.
- Observability must not become a dependency of business logic beyond its interfaces.
- Configuration and exceptions remain independent of runtime implementation details.

## 14. Tier Boundaries

### Tier 1 — Reliable Core

- Async Agent runtime.
- Provider abstraction.
- LiteLLM adapter.
- Tool contracts and registry.
- Secure ToolExecutor.
- Calculator builtin.
- MCP Client and tool integration.
- Short-term in-memory conversation memory.
- RunContext and budget management.
- Input/output guardrails.
- Default-deny permissions.
- Secret redaction.
- Basic tracing and structured logging.
- Streaming final text responses.
- CLI and configuration validation.
- Unit, integration, contract, security, and evaluation foundations.

### Tier 2 — Advanced Capabilities

- Optional FastAPI integration.
- PostgreSQL persistence.
- Redis.
- RAG and vector databases.
- Document ingestion.
- Search integrations.
- MCP Resources, Prompts, and MCP Server.
- Skills Engine and progressive disclosure.
- Long-term memory and memory summarization.
- Context compaction.
- Planning and reflection.
- Parallel tool execution.
- Streaming tool-call support.
- Human approval.
- Controlled filesystem tools.
- Production sandbox.
- Advanced metrics.
- Background execution.
- Calibration and use-case-specific uncertainty handling.

### Tier 3 — Enterprise and Distributed Systems

- Multi-tenancy.
- Enterprise IAM.
- Distributed execution.
- Persistent execution state.
- Workflow orchestration.
- Advanced audit and policy management.
- Enterprise governance.
- Multi-agent orchestration.
- A2A integration.
- Computer-use infrastructure.
- Enterprise deployment patterns.

## 15. Tier 1 Non-Goals

Tier 1 does not implement:

- Mandatory API framework.
- Database persistence.
- Vector database.
- Full RAG pipeline.
- Built-in web search.
- Arbitrary code execution.
- Production sandbox.
- Human approval infrastructure.
- Multi-tenancy.
- Distributed execution.
- Advanced planning engine.
- Multi-agent orchestration.
- Enterprise IAM.

The goal is a reliable and extensible foundation, not an all-inclusive agent platform.