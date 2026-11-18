#!/usr/bin/env python3
"""Convert a structured business brief into a traceable task plan.

This is a deterministic transformation utility, not an LLM. It does not infer
missing business facts: unresolved fields are surfaced as open questions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FIELDS = (
    "objective", "context", "deliverables", "constraints", "stakeholders",
    "deadline", "success_criteria",
)


def clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError("List fields must be strings or arrays of strings.")
    if any(not isinstance(item, str) for item in value):
        raise ValueError("List fields may contain only strings.")
    return [item.strip() for item in value if item.strip()]


def normalize_brief(brief: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(brief, dict):
        raise ValueError("The brief root must be a JSON object.")
    title = brief.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("A non-empty title is required.")

    normalized: dict[str, Any] = {"title": title.strip()}
    for field in FIELDS:
        value = brief.get(field)
        if field in ("objective", "context", "deadline"):
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{field} must be a string.")
            normalized[field] = value.strip() if isinstance(value, str) else ""
        else:
            normalized[field] = clean_list(value)

    # Explicit assumptions remain separate from confirmed brief content.
    normalized["assumptions"] = clean_list(brief.get("assumptions"))
    return normalized


def build_plan(brief: dict[str, Any]) -> dict[str, Any]:
    source = normalize_brief(brief)
    open_questions: list[str] = []
    for field, question in (
        ("objective", "What specific outcome should this work achieve?"),
        ("deliverables", "Which concrete deliverables are required?"),
        ("success_criteria", "How will completion and quality be accepted?"),
        ("deadline", "What is the required deadline or target date?"),
    ):
        if not source[field]:
            open_questions.append(question)

    tasks = []
    for index, deliverable in enumerate(source["deliverables"], start=1):
        tasks.append({
            "id": f"T{index:02d}",
            "title": f"Deliver: {deliverable}",
            "deliverable": deliverable,
            "acceptance_criteria": list(source["success_criteria"]),
            "acceptance_status": "provided" if source["success_criteria"] else "unresolved",
            "dependencies": [],
            "owner": None,
            "due_date": None,
        })

    return {
        "title": source["title"],
        "status": "READY_FOR_REVIEW" if not open_questions else "NEEDS_CLARIFICATION",
        "source_brief": source,
        "task_breakdown": tasks,
        "confirmed_requirements": {
            "objective": source["objective"],
            "context": source["context"],
            "deliverables": source["deliverables"],
            "constraints": source["constraints"],
            "stakeholders": source["stakeholders"],
            "deadline": source["deadline"],
            "success_criteria": source["success_criteria"],
        },
        "assumptions": source["assumptions"],
        "open_questions": open_questions,
        "guardrails": [
            "No missing dates, owners, budgets, or requirements have been invented.",
            "Assumptions are user-supplied and kept separate from confirmed requirements.",
            "Tasks are a direct breakdown of supplied deliverables; sequencing is not inferred.",
        ],
    }


def render_markdown(plan: dict[str, Any]) -> str:
    brief = plan["source_brief"]
    lines = [
        f"# {plan['title']}", "",
        f"**Status:** {plan['status']}", "",
        "## Objective", brief["objective"] or "_Not provided._", "",
        "## Context", brief["context"] or "_Not provided._", "",
        "## Confirmed requirements",
    ]
    for field in ("deliverables", "constraints", "stakeholders", "success_criteria"):
        lines.extend([f"### {field.replace('_', ' ').title()}"])
        values = brief[field]
        lines.extend([f"- {item}" for item in values] if values else ["- _Not provided._"])
        lines.append("")
    lines.extend(["### Deadline", brief["deadline"] or "_Not provided._", "", "## Task breakdown"])
    if plan["task_breakdown"]:
        for task in plan["task_breakdown"]:
            lines.extend([f"### {task['id']} — {task['title']}",
                          f"- Acceptance status: {task['acceptance_status']}"])
            if task["acceptance_criteria"]:
                lines.extend([f"- Acceptance: {item}" for item in task["acceptance_criteria"]])
            else:
                lines.append("- Acceptance: _Needs definition._")
            lines.append("")
    else:
        lines.extend(["No tasks generated: deliverables are missing.", ""])
    lines.extend(["## Assumptions"])
    lines.extend([f"- {item}" for item in plan["assumptions"]] or ["- None supplied."])
    lines.extend(["", "## Open questions"])
    lines.extend([f"- {item}" for item in plan["open_questions"]] or ["- None identified by required-field checks."])
    lines.extend(["", "## Guardrails"])
    lines.extend([f"- {item}" for item in plan["guardrails"]])
    return "\n".join(lines) + "\n"


def run(input_path: Path, output_dir: Path) -> dict[str, Any]:
    brief = json.loads(input_path.read_text(encoding="utf-8"))
    plan = build_plan(brief)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "task_plan.json").write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (output_dir / "task_plan.md").write_text(render_markdown(plan), encoding="utf-8")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_brief.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    try:
        plan = run(args.input, args.output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({
        "status": plan["status"],
        "tasks_created": len(plan["task_breakdown"]),
        "open_questions": len(plan["open_questions"]),
        "output_dir": str(args.output_dir),
    }, indent=2))


if __name__ == "__main__":
    main()
