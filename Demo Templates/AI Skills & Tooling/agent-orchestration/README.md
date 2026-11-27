# Agent Execution & Orchestration

**Status: DEMO**

A deterministic Python workflow runner for sequencing registered handlers with bounded retries, human-approval pauses, cancellation, explicit state, and event traces.

## Capabilities

- Execute a declared list of steps in order.
- Validate step IDs, handler registration, retry limits, and workflow size before execution.
- Pause before steps marked as requiring approval.
- Resume only the matching waiting step through an explicit host call.
- Retry handler failures up to each step's configured attempt limit.
- Stop the workflow when retries are exhausted.
- Support cancellation before terminal completion.
- Capture workflow state, outputs, attempts, and lifecycle events.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Integration

The host application supplies the handler registry and workflow definition. The orchestrator passes workflow context and prior outputs to each handler. Use [state_to_dict](./orchestrator.py) to serialize the current state for an external persistence layer.

## Boundaries

- Sequential execution only; no parallel branches, distributed queue, scheduling, durable state store, or crash recovery.
- Approval is represented by a host-supplied method call. This component does not authenticate approvers or collect approval evidence.
- Retries are bounded but do not implement backoff, timeout, or automatic compensation.
- Handler side effects may occur before a failure; this component cannot roll them back.
- State and event traces are in memory and require host persistence for durability.
- No LLM, external API, browser, shell, or third-party service integration.
- This is a reference execution engine, not a production orchestration platform.
