#!/usr/bin/env python3
"""Local, deterministic customer-support workflow demonstration."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)

def classify(message: str) -> tuple[str, str]:
    text = message.casefold()
    sensitive_terms = ("refund", "chargeback", "cancel my", "cancellation", "complaint", "lawyer", "legal", "safety", "data breach", "change my account", "delete my data")
    if any(term in text for term in sensitive_terms):
        return "human_review", "The request may require a policy decision or sensitive handling."
    rules = {
        "order_status": ("order", "delivery", "shipment", "tracking", "where is my package"),
        "billing": ("invoice", "payment", "billing", "charged", "receipt"),
        "product_information": ("product", "service", "feature", "specification", "how does it work"),
        "technical_support": ("error", "not working", "technical", "login", "cannot access", "can't access"),
        "returns": ("return", "exchange", "replacement"),
    }
    matches = [category for category, terms in rules.items() if any(term in text for term in terms)]
    if len(matches) == 1:
        return matches[0], "A single request category matched the demonstration rules."
    if len(matches) > 1:
        return "human_review", "The request matches more than one category."
    return "human_review", "No supported category could be identified confidently."

def handle_request(request: dict[str, Any], knowledge_base: dict[str, Any]) -> dict[str, Any]:
    request_id = str(request.get("request_id", "unknown"))
    message = request.get("message")
    if not isinstance(message, str) or not message.strip():
        return {"request_id": request_id, "category": "unknown", "route": "human_review",
                "status": "needs_information", "draft_response": None, "source": None,
                "reason": "The request message is missing or empty.", "message_sent": False}
    category, reason = classify(message)
    if category == "human_review":
        return {"request_id": request_id, "category": category, "route": "human_review",
                "status": "awaiting_human_review", "draft_response": None, "source": None,
                "reason": reason, "message_sent": False}
    entry = knowledge_base.get(category)
    if not isinstance(entry, dict) or not entry.get("draft_response") or not entry.get("source"):
        return {"request_id": request_id, "category": category, "route": "human_review",
                "status": "awaiting_human_review", "draft_response": None, "source": None,
                "reason": "No approved knowledge-base entry is available for this category.", "message_sent": False}
    return {"request_id": request_id, "category": category, "route": "agent_draft_for_review",
            "status": "draft_ready", "draft_response": entry["draft_response"],
            "source": entry["source"], "reason": reason, "message_sent": False}

def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local customer-support workflow demo.")
    parser.add_argument("--input", type=Path, default=Path("sample_requests.json"))
    parser.add_argument("--knowledge-base", type=Path, default=Path("knowledge_base.json"))
    parser.add_argument("--output", type=Path, default=Path("output/results.json"))
    args = parser.parse_args()
    requests = load_json(args.input)
    knowledge_base = load_json(args.knowledge_base)
    if not isinstance(requests, list):
        parser.error("Input JSON must contain a list of requests.")
    results = [handle_request(item, knowledge_base) for item in requests]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Processed {len(results)} request(s). Results: {args.output}")
    print("No customer messages were sent and no external systems were changed.")

if __name__ == "__main__":
    main()