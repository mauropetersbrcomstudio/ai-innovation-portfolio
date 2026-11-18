#!/usr/bin/env python3
"""Local approved-source retrieval demo with role filtering and human escalation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
STOP_WORDS = {"about", "after", "also", "and", "are", "can", "could", "does", "do", "for", "from", "how", "into", "is", "its", "please", "should", "that", "the", "their", "this", "what", "when", "where", "which", "who", "with", "would", "you", "your"}


def tokens(value: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(value.lower()) if token not in STOP_WORDS}


def load_sources(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ValueError("source file must contain a 'sources' array")
    seen: set[str] = set()
    sources = []
    for index, source in enumerate(data["sources"], start=1):
        if not isinstance(source, dict):
            raise ValueError(f"source {index} must be an object")
        source_id, title, content, roles = source.get("id"), source.get("title"), source.get("content"), source.get("allowed_roles")
        if not all(isinstance(x, str) and x.strip() for x in (source_id, title, content)):
            raise ValueError(f"source {index} requires non-empty id, title, and content")
        if source_id in seen:
            raise ValueError(f"duplicate source id: {source_id}")
        if not isinstance(roles, list) or not roles or not all(isinstance(role, str) and role.strip() for role in roles):
            raise ValueError(f"source {source_id} requires a non-empty allowed_roles list")
        seen.add(source_id)
        sources.append({"id": source_id, "title": title, "content": content, "allowed_roles": roles})
    return sources


def retrieve(question: str, user_role: str, sources: list[dict[str, Any]], threshold: float = 0.35) -> dict[str, Any]:
    if not isinstance(question, str) or not question.strip():
        return {"status": "ESCALATE", "reason": "empty_question", "results": [], "answer_policy": "source_excerpt_only"}
    if not isinstance(user_role, str) or not user_role.strip():
        return {"status": "ESCALATE", "reason": "missing_user_role", "results": [], "answer_policy": "source_excerpt_only"}
    query_terms = tokens(question)
    if not query_terms:
        return {"status": "ESCALATE", "reason": "no_searchable_terms", "results": [], "answer_policy": "source_excerpt_only"}
    matches = []
    for source in sources:
        if user_role not in source["allowed_roles"]:
            continue
        source_terms = tokens(source["title"] + " " + source["content"])
        overlap = query_terms & source_terms
        score = len(overlap) / len(query_terms)
        if overlap and score >= threshold:
            matches.append({
                "source_id": source["id"], "title": source["title"], "excerpt": source["content"],
                "matched_terms": sorted(overlap), "score": round(score, 3),
                "citation": f"[{source['id']}] {source['title']}",
            })
    matches.sort(key=lambda item: (-item["score"], item["source_id"]))
    if not matches:
        return {"status": "ESCALATE", "reason": "no_approved_source_match", "results": [], "answer_policy": "source_excerpt_only"}
    return {"status": "RETRIEVED", "reason": "approved_sources_found", "results": matches[:3], "answer_policy": "source_excerpt_only"}


def run(source_path: Path, request_path: Path, output_path: Path) -> dict[str, Any]:
    sources = load_sources(source_path)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if not isinstance(request, dict):
        raise ValueError("request file must contain a JSON object")
    result = retrieve(request.get("question"), request.get("user_role"), sources)
    result["request_id"] = request.get("request_id")
    result["disclaimer"] = "Retrieval only: excerpts are not generated answers. Verify the cited source and escalate when uncertain."
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=Path("approved_sources.json"))
    parser.add_argument("--request", type=Path, default=Path("sample_request.json"))
    parser.add_argument("--output", type=Path, default=Path("output/retrieval_result.json"))
    args = parser.parse_args()
    try:
        result = run(args.sources, args.request, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
