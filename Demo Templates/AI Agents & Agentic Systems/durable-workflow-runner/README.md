# Durable Workflow Runner

**Status: DEMO**

A local, sequential workflow runner that checkpoints state after each step in SQLite and records lifecycle events in both SQLite and JSONL. It reuses the portfolio's Agent State Store and Agent Observability components.

## Run

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Execution contract

- A workflow is identified by a stable ID and a fingerprint of its ordered step list and input context.
- State is persisted before a handler starts and after each successful completion.
- Completed steps are skipped on resume.
- Failed steps may be retried by calling the runner again with the same workflow ID, plan, and context.
- Every handler receives a deterministic `idempotency_key` for its workflow step.
- A changed plan or context is rejected rather than silently changing an in-flight workflow.

## Critical idempotency requirement

There is an unavoidable crash window after an external handler performs its side effect but before the runner persists the completion checkpoint. A retry can call that handler again. Therefore every handler that performs side effects **must enforce the supplied idempotency key at the destination** (or use an equivalent deduplication mechanism). The runner supplies the key but cannot enforce idempotency in an external system.

## Boundaries

- SQLite and JSONL files are local; no distributed coordination, queue, encryption, access control, or backup automation.
- Sequential execution only; no parallel branches, deadlines, leases, or distributed workers.
- The runner does not automatically compensate partially completed workflows. Use the separate Agent Recovery saga component only where explicit, tested compensations exist.
- A local checkpoint is not proof that an external side effect occurred exactly once.
- Handler output must be JSON-serializable.
- This is a reference demo, not a production orchestration service.
