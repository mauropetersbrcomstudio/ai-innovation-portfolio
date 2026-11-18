# JSON Contract Validator

**Status: DEMO**

A local Python utility that checks JSON data against a small, explicitly documented schema subset. It is intended as a reusable input/output contract check for skills, tools, and agent workflows.

## Supported rules

- Types: object, array, string, number, integer, boolean, null.
- Object required properties and optional rejection of additional properties.
- Nested object properties and array item validation.
- String minimum/maximum length.
- Numeric minimum/maximum.
- Enumerated allowed values.
- Error reports with JSON-style paths such as `$.items[0].name`.

## Run

Requirements: Python 3.10+; standard library only.

```bash
python json_contract_validator.py examples/request.json examples/request.schema.json
```

Save a report:

```bash
python json_contract_validator.py examples/request.json examples/request.schema.json --output report.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Limitations

This is not a complete JSON Schema implementation. It does not support references, combinators, formats, pattern constraints, conditional schemas, custom keywords, or schema draft compatibility. It assumes schema structures are authored correctly; malformed schema definitions may raise errors or behave outside the supported contract.

The validator reports structural contract violations only. It does not establish business correctness, authorization, or data truth. It makes no network calls and does not modify input files.
