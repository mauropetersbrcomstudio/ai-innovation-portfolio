#!/usr/bin/env python3
"""Deterministic CSV lead-intake demonstration; Python standard library only."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

REQUIRED = ("name", "email")
FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "proton.me", "protonmail.com",
}
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def normalize(value: str | None) -> str:
    return " ".join((value or "").strip().split())


def score_lead(record: dict[str, str]) -> int:
    email_domain = record["email"].rsplit("@", 1)[-1].lower()
    score = 0
    score += 30 if record.get("company") else 0
    score += 25 if email_domain not in FREE_EMAIL_DOMAINS else 0
    score += 25 if record.get("service") else 0
    score += 20 if record.get("source") else 0
    return score


def route_lead(score: int) -> str:
    if score >= 70:
        return "priority"
    if score >= 40:
        return "standard"
    return "review"


def process_rows(rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    processed: list[dict[str, Any]] = []
    exceptions: list[dict[str, str]] = []
    seen_emails: set[str] = set()

    for row_number, raw in enumerate(rows, start=2):
        row = {key: normalize(value) for key, value in raw.items() if key}
        row["email"] = row.get("email", "").lower()
        errors = [f"missing_{field}" for field in REQUIRED if not row.get(field)]
        if row.get("email") and not EMAIL_RE.match(row["email"]):
            errors.append("invalid_email")
        if errors:
            exceptions.append({"row": str(row_number), "email": row.get("email", ""), "reason": ";".join(errors)})
            continue

        email = row["email"]
        if email in seen_emails:
            exceptions.append({"row": str(row_number), "email": email, "reason": "duplicate_email"})
            continue
        seen_emails.add(email)

        score = score_lead(row)
        processed.append({
            **row,
            "score": score,
            "route": route_lead(score),
        })
    return processed, exceptions


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(input_path: Path, output_dir: Path) -> dict[str, Any]:
    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError("Input CSV must include name and email columns.")
        rows = list(reader)

    processed, exceptions = process_rows(rows)
    output_dir.mkdir(parents=True, exist_ok=True)
    lead_fields = list(dict.fromkeys(
        [key for row in processed for key in row.keys()]
        or ["name", "email", "company", "service", "source", "score", "route"]
    ))
    write_csv(output_dir / "processed_leads.csv", processed, lead_fields)
    write_csv(output_dir / "exceptions.csv", exceptions, ["row", "email", "reason"])

    summary = {
        "input_rows": len(rows),
        "processed_rows": len(processed),
        "exception_rows": len(exceptions),
        "routes": {
            route: sum(1 for item in processed if item["route"] == route)
            for route in ("priority", "standard", "review")
        },
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_leads.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        summary = run(args.input, args.output_dir)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
