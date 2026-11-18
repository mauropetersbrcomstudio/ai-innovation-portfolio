"""Config-driven CSV normalization. Source files are never modified."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def normalize_rows(rows: list[dict[str, str]], config: dict[str, Any]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    trim_fields = set(config.get("trim_fields", []))
    null_values = {str(v).casefold() for v in config.get("null_values", ["null", "n/a", "na"])}
    case_rules = config.get("case", {})
    date_rules = config.get("dates", {})
    rename = config.get("rename", {})
    if not all(isinstance(k, str) and isinstance(v, str) and v for k, v in rename.items()):
        raise ValueError("'rename' must map field names to non-empty field names")

    normalized: list[dict[str, str]] = []
    changes: dict[str, int] = {}
    for row_number, row in enumerate(rows, start=1):
        result: dict[str, str] = {}
        for original, raw in row.items():
            target = rename.get(original, original)
            if target in result:
                raise ValueError(f"Column rename collision at row {row_number}: {target}")
            value = raw if raw is not None else ""
            before = value
            if original in trim_fields or target in trim_fields:
                value = value.strip()
            if value.casefold() in null_values:
                value = ""
            rule = case_rules.get(original, case_rules.get(target))
            if value and rule:
                if rule == "lower":
                    value = value.lower()
                elif rule == "upper":
                    value = value.upper()
                elif rule == "title":
                    value = value.title()
                else:
                    raise ValueError(f"Unsupported case rule for {original}: {rule}")
            date_rule = date_rules.get(original, date_rules.get(target))
            if value and date_rule:
                formats = date_rule.get("input_formats", [])
                output_format = date_rule.get("output_format", "%Y-%m-%d")
                parsed = None
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue
                if parsed is None:
                    raise ValueError(f"Invalid date at row {row_number}, field '{original}': {value}")
                value = parsed.strftime(output_format)
            if value != before:
                changes[target] = changes.get(target, 0) + 1
            result[target] = value
        normalized.append(result)
    report = {"rows_processed": len(rows), "changed_cells_by_field": dict(sorted(changes.items()))}
    return normalized, report


def normalize_file(input_path: Path, config_path: Path, output_path: Path, report_path: Path | None = None) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("Input CSV must include a header row")
        rows = list(reader)
        fieldnames = reader.fieldnames
    normalized, report = normalize_rows(rows, config)
    output_fields = [config.get("rename", {}).get(name, name) for name in fieldnames]
    if len(output_fields) != len(set(output_fields)):
        raise ValueError("Column rename creates duplicate output headers")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(normalized)
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize CSV fields using an explicit JSON configuration.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = normalize_file(args.input, args.config, args.output, args.report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
