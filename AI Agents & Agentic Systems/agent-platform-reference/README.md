# Agent Platform Reference Integration

**Status: DEMO**

A runnable integration example that connects three reusable portfolio components: the sequential Agent Orchestration framework, SQLite Agent State Store, and structured Agent Observability logger.

## Run

Requires Python 3.10+ and uses only the standard library. From this directory:

```bash
python platform.py --request "Review a new support request"
```

The demo creates local files under `runtime/`. To keep generated runtime data out of source control, do not commit those files.

## Flow

1. Create an initial workflow state in SQLite.
2. Emit a workflow-created event to JSONL.
3. Run two deterministic steps: request validation and preparation of a human-review queue recommendation.
4. Persist the final workflow snapshot with optimistic version checking.
5. Persist orchestration events in SQLite and emit structured JSONL log entries.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Boundaries

- The workflow is deterministic and sequential; it is not an LLM-powered autonomous agent.
- The human-review queue is a returned recommendation only; no ticket or external record is created.
- State and logs are local files; no encryption, access control, distributed locking, or backup automation is provided.
- The example demonstrates component integration, not production deployment or fault-tolerant execution.
