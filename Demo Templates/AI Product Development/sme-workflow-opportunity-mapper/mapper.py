#!/usr/bin/env python3
"""Rank workflow automation opportunities using a transparent user-supplied rubric."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCORES = ("frequency", "time_burden", "standardization", "data_readiness", "user_impact", "risk")
POSITIVE = ("frequency", "time_burden", "standardization", "data_readiness", "user_impact")


def validate_opportunity(item: dict[str, Any], index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise ValueError(f"opportunity {index}: expected an object")
    name = item.get("name")
    problem = item.get("problem")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"opportunity {index}: name is required")
    if not isinstance(problem, str) or not problem.strip():
        raise ValueError(f"{name}: problem description is required")
    result = {"name": name.strip(), "problem": problem.strip()}
    for field in SCORES:
        value = item.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 5:
            raise ValueError(f"{name}: {field} must be an integer from 1 to 5")
        result[field] = value
    return result


def classify(score: float) -> str:
    if score >= 4.0:
        return "PRIORITIZE_FOR_DISCOVERY"
    if score >= 3.0:
        return "INVESTIGATE"
    return "DEFER_OR_REDESIGN"


def assess(item: dict[str, Any]) -> dict[str, Any]:
    validated = validate_opportunity(item, 1)
    positive_total = sum(validated[field] for field in POSITIVE)
    risk_adjusted = 6 - validated["risk"]
    score = (positive_total + risk_adjusted) / 6
    return {
        **validated,
        "risk_adjusted_score": risk_adjusted,
        "rubric_score": round(score, 2),
        "recommendation": classify(score),
        "score_explanation": (
            "Mean of five positive 1–5 ratings and the inverse risk rating (6 − risk). "
            "Higher scores indicate a stronger candidate for further discovery, not proof of ROI."
        ),
    }


def build_report(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Input root must be a JSON object")
    items = payload.get("opportunities")
    if not isinstance(items, list) or not items:
        raise ValueError("Input must contain a non-empty opportunities array")
    assessments = [assess(item) for item in items]
    assessments.sort(key=lambda item: (-item["rubric_score"], item["name"].casefold()))
    return {
        "title": str(payload.get("title") or "Workflow Opportunity Assessment"),
        "status": "RUBRIC_ASSESSMENT",
        "method": {
            "scale": "1 = low/unfavorable; 5 = high/favorable",
            "risk_direction": "Risk is reverse-scored: 6 − supplied risk rating.",
            "formula": "(frequency + time_burden + standardization + data_readiness + user_impact + (6 − risk)) ÷ 6",
            "thresholds": {
                "4.00–5.00": "PRIORITIZE_FOR_DISCOVERY",
                "3.00–3.99": "INVESTIGATE",
                "1.00–2.99": "DEFER_OR_REDESIGN",
            },
            "warning": "Weights and ratings are illustrative decision-support inputs, not empirical predictions.",
        },
        "assessments": assessments,
        "limitations": [
            "Ratings are supplied by the user and are not independently verified.",
            "The score is a screening aid, not a financial business case or an implementation recommendation.",
            "Security, privacy, compliance, change impact, and technical architecture require separate review.",
            "No workflow is connected, changed, or automated by this tool.",
        ],
    }


def run(input_path: Path, output_path: Path) -> dict[str, Any]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    report = build_report(payload)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_opportunities.json"))
    parser.add_argument("--output", type=Path, default=Path("output/opportunity_report.json"))
    args = parser.parse_args()
    try:
        report = run(args.input, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "status": report["status"],
        "opportunities_assessed": len(report["assessments"]),
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
