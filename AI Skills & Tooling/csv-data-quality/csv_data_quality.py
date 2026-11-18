#!/usr/bin/env python3
"""Profile and validate CSV structure without modifying the source file."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def analyze_csv(path: str | Path, key_columns: list[str] | None = None) -> dict[str, Any]:
    source = Path(path)
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration:
            return {
                "file": source.name,
                "status": "invalid",
                "issues": ["empty_file"],
                "headers": [],
                "row_count": 0,
                "blank_rows": 0,
                "malformed_rows": [],
                "duplicate_rows": [],
                "duplicate_keys": [],
                "empty_cells_by_column": {},
            }

        normalized_headers = [header.strip() for header in headers]
        header_counts = Counter(normalized_headers)
        duplicate_headers = sorted(name for name, count in header_counts.items() if name and count > 1)
        empty_headers = [index for index, name in enumerate(normalized_headers) if not name]

        row_count = 0
        blank_rows = 0
        malformed_rows: list[int] = []
        duplicate_rows: list[int] = []
        seen_rows: set[tuple[str, ...]] = set()
        empty_cells = {name: 0 for name in normalized_headers if name}
        key_indexes: list[int] = []
        missing_key_columns: list[str] = []

        for key in key_columns or []:
            if key not in normalized_headers:
                missing_key_columns.append(key)
            else:
                key_indexes.append(normalized_headers.index(key))

        seen_keys: dict[tuple[str, ...], int] = {}
        duplicate_keys: list[dict[str, Any]] = []

        for line_number, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                blank_rows += 1
                continue
            row_count += 1
            if len(row) != len(headers):
                malformed_rows.append(line_number)
                continue

            row_tuple = tuple(row)
            if row_tuple in seen_rows:
                duplicate_rows.append(line_number)
            else:
                seen_rows.add(row_tuple)

            for index, header in enumerate(normalized_headers):
                if header and not row[index].strip():
                    empty_cells[header] += 1

            if key_indexes and not missing_key_columns:
                key_value = tuple(row[index].strip() for index in key_indexes)
                if any(value == "" for value in key_value):
                    continue
                if key_value in seen_keys:
                    duplicate_keys.append({
                        "line": line_number,
                        "first_seen_line": seen_keys[key_value],
                        "key": list(key_value),
                    })
                else:
                    seen_keys[key_value] = line_number

    issues = []
    if duplicate_headers:
        issues.append("duplicate_headers")
    if empty_headers:
        issues.append("empty_headers")
    if malformed_rows:
        issues.append("malformed_rows")
    if missing_key_columns:
        issues.append("missing_key_columns")

    return {
        "file": source.name,
        "status": "invalid" if issues else "review" if duplicate_rows or duplicate_keys or blank_rows or any(empty_cells.values()) else "ok",
        "issues": issues,
        "headers": headers,
        "duplicate_headers": duplicate_headers,
        "empty_header_positions": empty_headers,
        "row_count": row_count,
        "blank_rows": blank_rows,
        "malformed_rows": malformed_rows,
        "duplicate_rows": duplicate_rows,
        "key_columns": key_columns or [],
        "missing_key_columns": missing_key_columns,
        "duplicate_keys": duplicate_keys,
        "empty_cells_by_column": empty_cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile CSV structure and common data-quality issues.")
    parser.add_argument("input", help="Path to the source CSV file")
    parser.add_argument("--key-columns", nargs="*", default=[], help="Optional column names used to detect duplicate keys")
    parser.add_argument("--output", help="Optional path for a JSON report; stdout is used when omitted")
    args = parser.parse_args()

    report = analyze_csv(args.input, args.key_columns)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
