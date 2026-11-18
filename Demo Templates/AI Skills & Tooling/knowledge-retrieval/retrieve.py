"""Deterministic lexical retrieval over an explicitly supplied JSON knowledge base."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[\w'-]+", re.UNICODE)


def tokenize(value: str) -> list[str]:
    return [token.casefold() for token in TOKEN_RE.findall(value)]


def load_sources(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(sources, list):
        raise ValueError("Knowledge file must contain a 'sources' array")
    seen: set[str] = set()
    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            raise ValueError(f"Source {index} must be an object")
        for field in ("id", "title", "text"):
            if not isinstance(source.get(field), str) or not source[field].strip():
                raise ValueError(f"Source {index} requires non-empty string '{field}'")
        if source["id"] in seen:
            raise ValueError(f"Duplicate source id: {source['id']}")
        seen.add(source["id"])
        roles = source.get("allowed_roles", [])
        if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
            raise ValueError(f"Source {source['id']} allowed_roles must be a string array")
    return sources


def retrieve(query: str, role: str, sources: list[dict[str, Any]], *, min_score: int = 1, limit: int = 5) -> dict[str, Any]:
    if not query.strip():
        raise ValueError("Query must not be empty")
    if not role.strip():
        raise ValueError("Role must not be empty")
    if min_score < 1 or limit < 1:
        raise ValueError("min_score and limit must be positive integers")

    query_tokens = tokenize(query)
    query_terms = set(query_tokens)
    if not query_terms:
        raise ValueError("Query must contain at least one searchable token")

    ranked: list[dict[str, Any]] = []
    for source in sources:
        allowed_roles = source.get("allowed_roles", [])
        if allowed_roles and role not in allowed_roles:
            continue
        text = source["text"]
        searchable = " ".join([source["title"], text, " ".join(source.get("tags", []))])
        source_tokens = tokenize(searchable)
        source_terms = set(source_tokens)
        matched = sorted(query_terms & source_terms)
        score = sum(source_tokens.count(term) for term in matched)
        if query.strip().casefold() in searchable.casefold():
            score += 2
        if score >= min_score:
            ranked.append({
                "source_id": source["id"],
                "title": source["title"],
                "score": score,
                "matched_terms": matched,
                "excerpt": text[:280],
            })

    ranked.sort(key=lambda item: (-item["score"], item["source_id"]))
    results = ranked[:limit]
    return {
        "status": "MATCHES_FOUND" if results else "ESCALATE_NO_QUALIFYING_SOURCE",
        "query": query,
        "role": role,
        "results": results,
        "returned_count": len(results),
        "disclaimer": "Lexical matches only; results are source excerpts, not generated answers. Role filtering is not authentication.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve role-filtered source excerpts from a local JSON knowledge base.")
    parser.add_argument("--knowledge", required=True, type=Path)
    parser.add_argument("--query", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = retrieve(args.query, args.role, load_sources(args.knowledge), min_score=args.min_score, limit=args.limit)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
