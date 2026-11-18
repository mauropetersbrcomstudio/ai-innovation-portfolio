# Agent Evaluation — Scenario Assertions

**Status: DEMO**

A small, deterministic evaluator for checking structured agent results against explicit scenario expectations. It is intended for regression checks and safety assertions in agent demos.

## Capabilities

- Assert an expected top-level status.
- Assert selected output fields.
- Require or forbid named agents in an execution trace.
- Require or forbid lifecycle events.
- Produce a machine-readable PASS/FAIL report with individual checks.
- Exit with a non-zero code when any expectation fails.

## Run tests

Requires Python 3.10+ and uses only the standard library.

```bash
python -m unittest discover -s tests -v
```

## Evaluate JSON files

```bash
python evaluate.py --actual examples/actual.json --expectations examples/expectations.json
```

## Boundaries

- Assertions are only as meaningful as the scenarios and expectations supplied by the test author.
- No model grading, semantic evaluation, benchmark dataset, statistical confidence, or automatic test generation.
- No execution of agents or external tools; the evaluator inspects already-produced JSON.
- It does not establish production safety or correctness outside the tested cases.
