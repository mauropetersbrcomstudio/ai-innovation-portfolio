#!/usr/bin/env python3
"""Analyze campaign performance from a CSV using transparent arithmetic."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

NUMERIC_FIELDS = ("spend", "impressions", "clicks", "conversions", "revenue")
REQUIRED_FIELDS = ("campaign", "channel", *NUMERIC_FIELDS)


def parse_nonnegative_number(value: str, field: str, row_number: int) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"row {row_number}: {field} must be numeric") from None
    if not math.isfinite(number):
        raise ValueError(f"row {row_number}: {field} must be a finite number")
    if number < 0:
        raise ValueError(f"row {row_number}: {field} cannot be negative")
    return number


def safe_divide(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def calculate_metrics(record: dict[str, Any]) -> dict[str, Any]:
    spend = record["spend"]
    impressions = record["impressions"]
    clicks = record["clicks"]
    conversions = record["conversions"]
    revenue = record["revenue"]
    return {
        **record,
        "ctr": safe_divide(clicks, impressions),
        "conversion_rate": safe_divide(conversions, clicks),
        "cpc": safe_divide(spend, clicks),
        "cpa": safe_divide(spend, conversions),
        "roas": safe_divide(revenue, spend),
    }


def load_campaigns(input_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    campaigns: list[dict[str, Any]] = []
    exceptions: list[dict[str, str]] = []
    with input_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not set(REQUIRED_FIELDS).issubset(reader.fieldnames):
            raise ValueError("CSV must include: " + ", ".join(REQUIRED_FIELDS))
        for row_number, row in enumerate(reader, start=2):
            name = (row.get("campaign") or "").strip()
            channel = (row.get("channel") or "").strip()
            if not name or not channel:
                exceptions.append({"row": str(row_number), "campaign": name, "reason": "missing_campaign_or_channel"})
                continue
            try:
                values = {field: parse_nonnegative_number(row.get(field, ""), field, row_number)
                          for field in NUMERIC_FIELDS}
            except ValueError as exc:
                exceptions.append({"row": str(row_number), "campaign": name, "reason": str(exc)})
                continue
            if values["clicks"] > values["impressions"]:
                exceptions.append({"row": str(row_number), "campaign": name, "reason": f"row {row_number}: clicks cannot exceed impressions"})
                continue
            if values["conversions"] > values["clicks"]:
                exceptions.append({"row": str(row_number), "campaign": name, "reason": f"row {row_number}: conversions cannot exceed clicks"})
                continue
            campaigns.append(calculate_metrics({"campaign": name, "channel": channel, **values}))
    return campaigns, exceptions


def summarize(campaigns: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: sum(item[field] for item in campaigns) for field in NUMERIC_FIELDS}
    return {
        "campaign_count": len(campaigns),
        **totals,
        "ctr": safe_divide(totals["clicks"], totals["impressions"]),
        "conversion_rate": safe_divide(totals["conversions"], totals["clicks"]),
        "cpc": safe_divide(totals["spend"], totals["clicks"]),
        "cpa": safe_divide(totals["spend"], totals["conversions"]),
        "roas": safe_divide(totals["revenue"], totals["spend"]),
    }


def run(input_path: Path, output_dir: Path) -> dict[str, Any]:
    campaigns, exceptions = load_campaigns(input_path)
    summary = summarize(campaigns)
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = [*REQUIRED_FIELDS, "ctr", "conversion_rate", "cpc", "cpa", "roas"]
    with (output_dir / "campaign_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(campaigns)
    with (output_dir / "exceptions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row", "campaign", "reason"])
        writer.writeheader()
        writer.writerows(exceptions)
    result = {"summary": summary, "exception_count": len(exceptions)}
    (output_dir / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_campaigns.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        result = run(args.input, args.output_dir)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
