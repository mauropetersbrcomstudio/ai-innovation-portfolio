#!/usr/bin/env python3
"""Run a quality preflight before calculating campaign performance metrics."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
QUALITY_TOOL = ROOT / "AI Skills & Tooling" / "csv-data-quality"
ANALYZER_TOOL = ROOT / "Marketing Intelligence & Business Automation" / "campaign-performance-analyzer"
sys.path.insert(0, str(QUALITY_TOOL))
sys.path.insert(0, str(ANALYZER_TOOL))

from csv_data_quality import analyze_csv
from analyzer import run as run_campaign_analysis


class PreflightBlocked(ValueError):
    """Raised when quality findings require review before analysis."""


def run_pipeline(input_path: Path, output_dir: Path, allow_review: bool = False) -> dict[str, Any]:
    quality = analyze_csv(input_path)
    if quality["status"] == "invalid":
        raise PreflightBlocked("CSV failed structural validation; inspect quality_report.json")
    if quality["status"] == "review" and not allow_review:
        raise PreflightBlocked("CSV requires human review; rerun with --allow-review only after inspection")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "quality_report.json").write_text(
        json.dumps(quality, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    analysis = run_campaign_analysis(input_path, output_dir)
    return {"preflight_status": quality["status"], **analysis}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_campaigns.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument(
        "--allow-review", action="store_true",
        help="Continue after a review-level report; use only after inspecting the source and report.",
    )
    args = parser.parse_args()
    try:
        result = run_pipeline(args.input, args.output_dir, args.allow_review)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
