#!/usr/bin/env python3
"""Validate campaign launch metadata and build collision-safe UTM URLs."""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REQUIRED = (
    "campaign_id", "campaign_name", "destination_url", "utm_source",
    "utm_medium", "utm_campaign", "start_date", "end_date", "budget",
)
UTM_KEYS = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"}


def validate_row(row: dict[str, str], seen_ids: set[str]) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    cleaned = {key: (row.get(key) or "").strip() for key in REQUIRED}
    for key in REQUIRED:
        if not cleaned[key]:
            errors.append(f"{key} is required")

    campaign_id = cleaned["campaign_id"]
    if campaign_id and campaign_id in seen_ids:
        errors.append("campaign_id is duplicated")
    if campaign_id:
        seen_ids.add(campaign_id)

    try:
        parts = urlsplit(cleaned["destination_url"])
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            raise ValueError
        if parts.username or parts.password:
            raise ValueError
        existing_keys = {key.lower() for key, _ in parse_qsl(parts.query, keep_blank_values=True)}
        if existing_keys & UTM_KEYS:
            errors.append("destination_url already contains UTM parameters")
    except ValueError:
        errors.append("destination_url must be an absolute HTTP(S) URL without embedded credentials")

    parsed_dates: dict[str, date] = {}
    for field in ("start_date", "end_date"):
        try:
            parsed_dates[field] = date.fromisoformat(cleaned[field])
            if parsed_dates[field].isoformat() != cleaned[field]:
                raise ValueError
        except ValueError:
            errors.append(f"{field} must be a valid YYYY-MM-DD date")
    if len(parsed_dates) == 2 and parsed_dates["start_date"] > parsed_dates["end_date"]:
        errors.append("start_date must not be after end_date")

    try:
        budget = Decimal(cleaned["budget"])
        if not budget.is_finite() or budget < 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        errors.append("budget must be a finite non-negative decimal number")
        budget = None

    if errors:
        return None, errors

    query = parse_qsl(parts.query, keep_blank_values=True)
    query.extend([
        ("utm_source", cleaned["utm_source"]),
        ("utm_medium", cleaned["utm_medium"]),
        ("utm_campaign", cleaned["utm_campaign"]),
    ])
    if (row.get("utm_content") or "").strip():
        query.append(("utm_content", row["utm_content"].strip()))
    if (row.get("utm_term") or "").strip():
        query.append(("utm_term", row["utm_term"].strip()))
    result = dict(cleaned)
    result["budget"] = format(budget, "f")
    result["tracking_url"] = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    return result, []


def run(input_path: Path, output_dir: Path) -> dict[str, Any]:
    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        missing = [field for field in REQUIRED if field not in headers]
        if missing:
            raise ValueError("Missing required CSV columns: " + ", ".join(missing))
        rows = list(reader)

    # Detect duplicate IDs across the full file so both occurrences are flagged.
    id_counts: dict[str, int] = {}
    for row in rows:
        key = (row.get("campaign_id") or "").strip()
        if key:
            id_counts[key] = id_counts.get(key, 0) + 1

    approved: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    for line, row in enumerate(rows, start=2):
        # Duplicate identifiers are invalid on every occurrence, not only later rows.
        seen: set[str] = set()
        result, errors = validate_row(row, seen)
        campaign_id = (row.get("campaign_id") or "").strip()
        if campaign_id and id_counts[campaign_id] > 1 and "campaign_id is duplicated" not in errors:
            errors.append("campaign_id is duplicated")
        if errors:
            exceptions.append({"row": line, "campaign_id": campaign_id, "campaign_name": (row.get("campaign_name") or "").strip(), "reasons": errors})
        else:
            approved.append(result)

    output_dir.mkdir(parents=True, exist_ok=True)
    approved_fields = list(REQUIRED) + ["tracking_url"]
    with (output_dir / "approved_campaigns.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=approved_fields)
        writer.writeheader()
        writer.writerows(approved)
    with (output_dir / "exceptions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row", "campaign_id", "campaign_name", "reasons"])
        writer.writeheader()
        for item in exceptions:
            writer.writerow({**item, "reasons": " | ".join(item["reasons"])})
    summary = {
        "source_file": input_path.name,
        "status": "ready" if not exceptions else ("blocked" if not approved else "review"),
        "input_rows": len(rows),
        "approved_rows": len(approved),
        "exception_rows": len(exceptions),
        "source_modified": False,
        "limitations": [
            "This tool validates supplied metadata; it does not publish or activate campaigns.",
            "It does not verify destination ownership, consent, legal compliance, or analytics-platform configuration.",
            "UTM values are preserved as supplied; no taxonomy or naming convention is imposed.",
        ],
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_campaigns.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.input, args.output_dir), indent=2, ensure_ascii=False))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
