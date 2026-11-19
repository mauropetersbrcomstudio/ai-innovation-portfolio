from __future__ import annotations

import re
import sys
from pathlib import Path

BLOCKED_WORKFLOW_MARKERS = (
    "actions/configure-pages",
    "actions/upload-pages-artifact",
    "actions/deploy-pages",
    "pages: write",
    "vercel/action",
    "netlify/actions",
    "cloudflare/pages-action",
    "peaceiris/actions-gh-pages",
    "wrangler deploy",
    "firebase deploy",
    "azure/static-web-apps-deploy",
)
BLOCKED_ROOT_MANIFESTS = (
    "vercel.json",
    "netlify.toml",
    "wrangler.toml",
    "firebase.json",
    "amplify.yml",
    "render.yaml",
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.is_dir():
        errors.append("Missing .github/workflows directory.")
    else:
        workflow_files = sorted(
            path
            for path in workflows_dir.iterdir()
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
        )
        for workflow in workflow_files:
            content = workflow.read_text(encoding="utf-8").lower()
            for marker in BLOCKED_WORKFLOW_MARKERS:
                if marker in content:
                    errors.append(f"{workflow.relative_to(root)} contains prohibited deployment marker: {marker}")
            if re.search(r"(?m)^\s*id-token\s*:\s*write\b", content):
                errors.append(f"{workflow.relative_to(root)} grants id-token write permission.")

    for manifest in BLOCKED_ROOT_MANIFESTS:
        if (root / manifest).exists():
            errors.append(f"Prohibited root hosting manifest exists: {manifest}")

    root_readme = root / "README.md"
    if not root_readme.is_file():
        errors.append("Missing root README.md.")
    else:
        readme_text = root_readme.read_text(encoding="utf-8").lower()
        for phrase in ("github-only", "no github pages", "no web deployment"):
            if phrase not in readme_text:
                errors.append(f"Root README must document the repository boundary: {phrase}")

    cases_root = root / "Client Case Studies"
    if not cases_root.is_dir():
        errors.append("Missing Client Case Studies directory.")
    else:
        case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
        for case_dir in case_dirs:
            if not case_dir.name.startswith("anonymized-"):
                errors.append(f"Public case directory must be anonymized: {case_dir.relative_to(root)}")
            readme = case_dir / "README.md"
            if not readme.is_file():
                errors.append(f"Missing case README: {case_dir.relative_to(root)}")
                continue
            text = readme.read_text(encoding="utf-8").lower()
            status_match = re.search(
                r"(?im)^\s*\*\*status:\s*(concept|demo|prototype|implemented)\s*\*\*",
                text,
            )
            if not status_match:
                errors.append(f"Case README must contain one exact maturity label: {readme.relative_to(root)}")
            has_identity = "identity" in text or "identidade" in text
            has_withheld = "withheld" in text or "omitid" in text or "retirad" in text
            if not (has_identity and has_withheld):
                errors.append(f"Case README must state that client identity is withheld: {readme.relative_to(root)}")
            if not any(token in text for token in ("synthetic", "sintétic", "sintetic")):
                errors.append(f"Case README must identify synthetic data: {readme.relative_to(root)}")
            for asset in case_dir.rglob("*"):
                if asset.is_file() and asset.suffix.lower() in IMAGE_SUFFIXES:
                    errors.append(f"Image/brand asset must not be public in anonymized case: {asset.relative_to(root)}")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_repository(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    workflow_count = len(
        [
            path
            for path in (root / ".github" / "workflows").iterdir()
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
        ]
    )
    case_count = len([path for path in (root / "Client Case Studies").iterdir() if path.is_dir()])
    print(f"Repository publication scope passed: {workflow_count} workflow files and {case_count} anonymized case directories inspected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
