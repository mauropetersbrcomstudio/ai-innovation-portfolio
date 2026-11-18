# Agent State Store — SQLite Persistence

**Status: DEMO**

A local persistence component for workflow state and append-only event records, built with Python's SQLite support. It is designed to complement the in-memory orchestration framework when a demo needs state to survive process restarts.

## Capabilities

- Create and retrieve workflow state as JSON objects.
- Update state with optimistic version checks to reject stale writes.
- Persist workflow status and increment a state version on each accepted update.
- Append ordered event records for a workflow.
- Retrieve events in insertion order.
- Use SQLite transactions and foreign-key constraints.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Example

```python
from state_store import StateStore

store = StateStore("runtime/workflows.db")
store.create("wf-001", {"status": "RUNNING", "current_step": "intake"})
store.append_event("wf-001", "STEP_STARTED", {"step_id": "intake"})
store.save("wf-001", {"status": "COMPLETED", "current_step": None}, expected_version=1)
print(store.get("wf-001"))
print(store.events("wf-001"))
```

## Boundaries

- Local SQLite file only; no network database, distributed locking, multi-region replication, or backup automation.
- Optimistic version checks prevent stale state overwrites but do not provide workflow-level exactly-once execution.
- Event records are append-only through this API, but the SQLite file itself is not tamper-proof or immutable against a privileged operator.
- No encryption-at-rest, user authentication, retention policy, or access-control layer is included.
- Hosts must define safe backup, recovery, privacy, and operational policies before production use.
