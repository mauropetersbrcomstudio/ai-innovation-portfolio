#!/usr/bin/env python3
"""Extract deterministic, traceable structure from plain-text documents."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
URL_RE = re.compile(r"(?i)\bhttps?://[^\s<>\]]+")
ISO_DATE_RE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")
CURRENCY_RE = re.compile(r"(?i)(?:\b(?:USD|EUR|GBP|BRL)\s*)?[$€£R]\s?\d[\d.,]*(?:\s?(?:USD|EUR|GBP|BRL))?")
KEY_VALUE_RE = re.compile(r"^\s*([^:=]{1,80}?)\s*[:=]\s*(.*?)\s*$")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def _unique_matches(pattern: re.Pattern[str], text: str) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for match in pattern.finditer(text):
        value = match.group(0).rstrip(".,;)")
        if value not in seen:
            seen.add(value)
            values.append(value)
    return values


def analyze_document(text: str, source_name: str = "inline.txt") -> dict[str, Any]:
    lines = text.splitlines()
    headings: list[dict[str, Any]] = []
    key_values: list[dict[str, Any]] = []

    for line_number, line in enumerate(lines, start=1):
        heading = HEADING_RE.match(line)
        if heading:
            headings.append({
                "line": line_number,
                "level": len(heading.group(1)),
                "text": heading.group(2).strip(),
            })
            continue

        pair = KEY_VALUE_RE.match(line)
        if pair and pair.group(1).strip():
            key_values.append({
                "line": line_number,
                "key": pair.group(1).strip(),
                "value": pair.group(2).strip(),
            })

    nonempty_lines = [line for line in lines if line.strip()]
    words = re.findall(r"\b[\w'-]+\b", text, flags=re.UNICODE)

    return {
        "source": source_name,
        "status": "empty" if not text.strip() else "analyzed",
        "statistics": {
            "character_count": len(text),
            "line_count": len(lines) if text else 0,
            "nonempty_line_count": len(nonempty_lines),
            "word_count": len(words),
        },
        "headings": headings,
        "key_value_pairs": key_values,
        "entities": {
            "emails": _unique_matches(EMAIL_RE, text),
            "urls": _unique_matches(URL_RE, text),
            "iso_dates": _unique_matches(ISO_DATE_RE, text),
            "currency_mentions": _unique_matches(CURRENCY_RE, text),
        },
        "limitations": [
            "Processes decoded plain text only; it does not read PDF, DOCX, image, or scanned documents.",
            "Extraction is pattern-based and does not establish whether a value is correct or authoritative.",
            "No semantic understanding, OCR, translation, summarization, or external lookup is performed.",
            "Extracted contact details and financial mentions may be sensitive; review the report before sharing it.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract traceable structure from a plain-text document.")
    parser.add_argument("input", help="Path to a UTF-8 .txt or .md file")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()

    source = Path(args.input)
    if source.suffix.lower() not in {".txt", ".md"}:
        parser.error("Only .txt and .md inputs are supported by this demo.")
    try:
        content = source.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        parser.error("Input must be valid UTF-8 text.")

    report = analyze_document(content, source.name)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
