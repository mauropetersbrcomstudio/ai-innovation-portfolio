# Agent Recovery — Compensating Actions (Saga Pattern)

**Status: DEMO**

A small sequential saga runner that executes declared steps and, after a failure, invokes available compensating handlers in reverse completion order. It distinguishes a completed rollback from a partial rollback.

## Capabilities

- Execute a bounded sequence of explicitly supplied steps.
- Retry each step up to its configured attempt count.
- Record step start, completion, failure, and compensation events.
- Run compensations in reverse order for previously completed steps.
- Report compensation failures as `PARTIAL_ROLLBACK`.
- Explicitly report when a completed step has no compensation handler.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Important semantics

Compensation is not a database rollback and cannot guarantee restoration of the original world state. Each compensation is a separately executed handler that may fail or only partially reverse an action. Steps without a compensation handler are reported as skipped; they are not silently treated as reversed.

## Boundaries

- Sequential in-process execution only; no distributed transaction manager or durable recovery journal.
- No automatic compensation discovery, idempotency enforcement, timeout, or retry policy for compensations.
- Side effects performed by a failed step before it raises may not be known or reversible.
- The host must design and test compensations for each external action and persist the event trace if recovery across process restarts is required.
- No external integrations are included.
