#!/usr/bin/env python3
"""Check project status/docs and keep the root/category indexes aligned with the tree."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = (
    "client-demos",
    "demo-templates",
    "AI Agents & Agentic Systems",
    "AI Automation & Workflows",
    "AI Skills & Tooling",
    "AI Product Development",
    "Web Applications & SaaS",
    "Marketing Intelligence & Business Automation",
)
ALLOWED_STATUSES = {"CONCEPT", "DEMO", "PROTOTYPE", "IMPLEMENTED"}
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")


def project_directories() -> set[str]:
    found: set[str] = set()
    for category in CATEGORIES:
        folder = ROOT / category
        if not folder.is_dir():
            raise RuntimeError(f"Missing agreed category folder: {category}")
        for readme in folder.glob("*/README.md"):
            found.add(readme.parent.relative_to(ROOT).as_posix())
    return found


def resolve_local_link(source: Path, raw_target: str) -> Path | None:
    raw_target = raw_target.strip()
    if not raw_target:
        return None
    target = raw_target.split()[0].split("#", 1)[0].split("?", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    candidate = (source.parent / unquote(target)).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Link escapes repository: {source.relative_to(ROOT)} -> {raw_target}") from exc
    return candidate


def local_links(markdown: str, source: Path) -> list[Path]:
    links: list[Path] = []
    for match in LINK_PATTERN.finditer(markdown):
        candidate = resolve_local_link(source, match.group(1))
        if candidate is not None:
            links.append(candidate)
    return links


def project_targets(markdown: str, source: Path, projects: set[str]) -> set[str]:
    targets: set[str] = set()
    for candidate in local_links(markdown, source):
        if candidate.is_dir():
            relative = candidate.relative_to(ROOT).as_posix()
            if relative in projects:
                targets.add(relative)
        elif candidate.name == "README.md":
            relative = candidate.parent.relative_to(ROOT).as_posix()
            if relative in projects:
                targets.add(relative)
    return targets


def validate_project_readme(project: str) -> list[str]:
    path = ROOT / project / "README.md"
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    status_match = re.search(
        r"(?im)^\s*\*\*Status:\s*(CONCEPT|DEMO|PROTOTYPE|IMPLEMENTED)\*\*",
        "\n".join(text.splitlines()[:15]),
    )
    if not status_match:
        errors.append(f"{project}: missing or non-standard status label")

    has_run = bool(re.search(
        r"(?im)^#{1,6}\s*(run|run locally|run it|usage|quick start|get started|getting started|execution)\b",
        text,
    )) or bool(re.search(r"(?im)^\s*(python|node|npm|pytest)\s+", text))
    if not has_run:
        errors.append(f"{project}: missing run instructions")

    if not re.search(r"(?i)(Python\s*\d|Node\.js|standard library|requirements|dependencies)", text):
        errors.append(f"{project}: missing runtime/dependency information")

    has_tests = bool(re.search(r"(?im)^#{1,6}\s*(tests?|run tests|verification)\b", text)) or bool(
        re.search(r"(?i)(unittest discover|npm test|node --test|pytest)", text)
    )
    if not has_tests:
        errors.append(f"{project}: missing test instructions or an explicit test reference")

    has_limits = bool(re.search(
        r"(?im)^#{1,6}\s*(limitations?|boundaries|trust|data and limitations|scope and limitations|non-goals?)\b",
        text,
    ))
    has_limits = has_limits or bool(re.search(
        r"(?i)(does not|do not|not a production|not production|no authentication|no external)",
        text,
    ))
    if not has_limits:
        errors.append(f"{project}: missing limitations or boundary section")
    return errors


def main() -> int:
    errors: list[str] = []
    projects = project_directories()
    root_readme = ROOT / "README.md"
    root_text = root_readme.read_text(encoding="utf-8")

    if "\\n" in root_text:
        errors.append("Root README contains a literal backslash-n sequence; check table formatting.")

    explore = root_text.split("## Explore working demos", 1)
    if len(explore) != 2:
        errors.append("Root README is missing the Explore working demos section.")
        root_section = ""
    else:
        root_section = explore[1].split("## Portfolio", 1)[0]
        rows = [line for line in root_section.splitlines() if line.startswith("| [")]
        if len(rows) != len(projects):
            errors.append(
                f"Root demo table has {len(rows)} project rows; repository contains {len(projects)} project folders."
            )

    root_targets = project_targets(root_section, root_readme, projects)
    if root_targets != projects:
        missing = sorted(projects - root_targets)
        extra = sorted(root_targets - projects)
        errors.append(f"Root project index mismatch; missing={missing}; extra={extra}")

    for category in CATEGORIES:
        index = ROOT / category / "README.md"
        if not index.is_file():
            errors.append(f"Missing category index: {category}/README.md")
            continue
        text = index.read_text(encoding="utf-8")
        expected = {project for project in projects if project.startswith(category + "/")}
        actual = project_targets(text, index, projects)
        if actual != expected:
            errors.append(
                f"{category}: index mismatch; missing={sorted(expected - actual)}; extra={sorted(actual - expected)}"
            )
        for candidate in local_links(text, index):
            if not candidate.exists():
                errors.append(f"Broken category link in {index.relative_to(ROOT)}: {candidate}")

    for candidate in local_links(root_text, root_readme):
        if not candidate.exists():
            errors.append(f"Broken root link: {candidate}")

    for project in sorted(projects):
        errors.extend(validate_project_readme(project))

    if errors:
        print("Portfolio validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Portfolio validation passed: {len(projects)} project READMEs, "
        f"{len(CATEGORIES)} category indexes, root index coverage, local links, "
        "status labels, run/dependency/test/limitation documentation."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
