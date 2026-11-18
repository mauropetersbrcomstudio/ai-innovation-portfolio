#!/usr/bin/env python3
"""Heuristic scan of tracked public-repository files for selected credential patterns.

This is a narrow safety net, not a comprehensive secret scanner or privacy review.
It intentionally reports paths and rule IDs only; matched values are never printed.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 2_000_000
SAFE_ENV_SUFFIXES = {".example", ".sample", ".template"}

PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key-block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("stripe-live-secret", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}\b")),
    ("openai-project-key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b")),
    ("anthropic-api-key", re.compile(r"\bsk-ant-api03-[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("sendgrid-api-key", re.compile(r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    ("huggingface-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("jwt-like-token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("credential-url", re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")),
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    rule: str


@dataclass(frozen=True)
class ScanResult:
    findings: tuple[Finding, ...]
    scanned_files: int
    skipped_files: int


def is_environment_file(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    if name == ".env":
        return True
    if name.startswith(".env."):
        return PurePosixPath(name).suffix not in SAFE_ENV_SUFFIXES
    return False


def scan_text(path: str, content: str) -> list[Finding]:
    findings: list[Finding] = []
    if is_environment_file(path):
        findings.append(Finding(path, "environment-file"))
    for rule, pattern in PATTERNS:
        if pattern.search(content):
            findings.append(Finding(path, rule))
    return findings


def tracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    paths = [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]
    if not paths:
        raise RuntimeError("git ls-files returned no tracked files")
    return paths


def scan_repository(
    root: Path = ROOT,
    relative_paths: list[str] | None = None,
    max_file_bytes: int = MAX_FILE_BYTES,
) -> ScanResult:
    paths = relative_paths if relative_paths is not None else tracked_paths(root)
    findings: list[Finding] = []
    scanned = 0
    skipped = 0

    for raw_path in paths:
        relative = PurePosixPath(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Path is outside repository scope: {raw_path}")

        file_path = root.joinpath(*relative.parts)
        if is_environment_file(raw_path):
            findings.append(Finding(raw_path, "environment-file"))
        if not file_path.exists():
            raise FileNotFoundError(raw_path)
        if file_path.is_symlink() or not file_path.is_file():
            skipped += 1
            continue
        if file_path.stat().st_size > max_file_bytes:
            skipped += 1
            continue

        raw = file_path.read_bytes()
        if b"\0" in raw:
            skipped += 1
            continue
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            skipped += 1
            continue

        scanned += 1
        findings.extend(scan_text(raw_path, content))

    return ScanResult(tuple(sorted(set(findings))), scanned, skipped)


def format_findings(findings: tuple[Finding, ...] | list[Finding]) -> str:
    return "\n".join(f"{item.path}: {item.rule}" for item in sorted(set(findings)))


def main() -> int:
    try:
        result = scan_repository()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Public-content scan could not complete ({type(exc).__name__}).")
        return 2

    if result.findings:
        print("Potential public-content issues found; matched values are intentionally omitted:")
        print(format_findings(result.findings))
        print(f"Scanned {result.scanned_files} text files; skipped {result.skipped_files} files.")
        return 1

    print(
        "Public-content heuristic passed: "
        f"scanned {result.scanned_files} tracked UTF-8 text files; "
        f"skipped {result.skipped_files} binary, oversized, non-UTF-8, or symlink files. "
        "This check does not scan Git history or detect every secret or confidential-data type."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
