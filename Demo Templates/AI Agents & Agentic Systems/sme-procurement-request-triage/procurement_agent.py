#!/usr/bin/env python3
"""Deterministic procurement request triage demo. No purchasing actions are performed."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "request_id", "requester", "item", "category", "amount",
    "currency", "supplier", "supplier_status", "urgency",
)


def is_positive_number(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and (not isinstance(value, float) or math.isfinite(value))
        and value > 0
    )


def validate_policy(policy: dict[str, Any]) -> None:
    if not isinstance(policy, dict):
        raise ValueError("Policy must be a JSON object.")
    currency = policy.get("currency")
    categories = policy.get("allowed_categories")
    manager_limit = policy.get("manager_review_limit")
    finance_limit = policy.get("finance_review_limit")
    if not isinstance(currency, str) or not currency.strip():
        raise ValueError("Policy currency must be a non-empty string.")
    if not isinstance(categories, list) or not categories or not all(
        isinstance(item, str) and item.strip() for item in categories
    ):
        raise ValueError("Policy allowed_categories must be a non-empty list of strings.")
    for name, value in (("manager_review_limit", manager_limit),
                        ("finance_review_limit", finance_limit)):
        if not is_positive_number(value):
            raise ValueError(f"Policy {name} must be a positive number.")
    if manager_limit > finance_limit:
        raise ValueError("manager_review_limit cannot exceed finance_review_limit.")


def _result(request_id: str | None, status: str, route: str,
            reason: str, trace: list[str], **extra: Any) -> dict[str, Any]:
    return {
        "request_id": request_id,
        "status": status,
        "review_route": route,
        "reason": reason,
        "trace": trace,
        "purchase_order_created": False,
        **extra,
    }


def assess_request(request: Any, policy: dict[str, Any],
                   duplicate_ids: set[str] | None = None) -> dict[str, Any]:
    """Assess one request and return a review recommendation, never an approval."""
    trace = ["request_received", "policy_loaded"]
    if not isinstance(request, dict):
        return _result(None, "rejected_input", "human_review",
                       "Each request must be a JSON object.",
                       trace + ["invalid_request_shape"])

    raw_id = request.get("request_id")
    request_id = raw_id.strip() if isinstance(raw_id, str) and raw_id.strip() else None
    missing = [
        field for field in REQUIRED_FIELDS
        if field not in request or request[field] is None
        or (isinstance(request[field], str) and not request[field].strip())
    ]
    if missing:
        return _result(request_id, "needs_information", "requester_follow_up",
                       "Required information is missing: " + ", ".join(missing) + ".",
                       trace + ["required_fields_checked", "missing_information_detected"],
                       missing_fields=missing)

    text_fields = ("request_id", "requester", "item", "category", "currency",
                   "supplier", "supplier_status", "urgency")
    invalid_text_fields = [
        field for field in text_fields
        if not isinstance(request[field], str) or not request[field].strip()
    ]
    if invalid_text_fields:
        return _result(request_id, "rejected_input", "human_review",
                       "These fields must be non-empty strings: " + ", ".join(invalid_text_fields) + ".",
                       trace + ["required_fields_checked", "invalid_text_fields"],
                       invalid_fields=invalid_text_fields)

    amount = request["amount"]
    if not is_positive_number(amount):
        return _result(request_id, "rejected_input", "human_review",
                       "Amount must be a finite positive number.",
                       trace + ["required_fields_checked", "invalid_amount"])

    if request["currency"].upper() != policy["currency"].upper():
        return _result(request_id, "rejected_input", "human_review",
                       f"Currency {request['currency']} does not match policy currency {policy['currency']}.",
                       trace + ["required_fields_checked", "currency_policy_mismatch"])

    if request["category"] not in policy["allowed_categories"]:
        return _result(request_id, "rejected_input", "human_review",
                       "Category is not included in the demonstration policy.",
                       trace + ["required_fields_checked", "category_not_allowed"])

    if request["supplier_status"] not in ("approved", "unverified"):
        return _result(request_id, "rejected_input", "human_review",
                       "supplier_status must be 'approved' or 'unverified'.",
                       trace + ["required_fields_checked", "invalid_supplier_status"])

    if request["urgency"] not in ("standard", "urgent"):
        return _result(request_id, "rejected_input", "human_review",
                       "urgency must be 'standard' or 'urgent'.",
                       trace + ["required_fields_checked", "invalid_urgency"])

    trace.extend(["required_fields_checked", "currency_checked", "category_checked"])
    if duplicate_ids and request_id in duplicate_ids:
        return _result(request_id, "duplicate_review", "human_review",
                       "The request ID appears more than once in this batch.",
                       trace + ["duplicate_request_detected"])

    if request["supplier_status"] == "unverified":
        return _result(request_id, "review_required", "supplier_due_diligence",
                       "Supplier status is unverified; complete supplier checks before approval.",
                       trace + ["supplier_status_checked", "supplier_due_diligence_required"],
                       amount=amount, currency=policy["currency"],
                       next_step="Verify supplier through the organization's approved process.")

    if request["urgency"] == "urgent":
        route = "priority_review"
        reason = "Urgent requests require human review regardless of amount."
        trace.extend(["urgency_checked", "priority_human_review_required"])
    elif amount <= policy["manager_review_limit"]:
        route = "manager_review"
        reason = "Amount falls within the manager review band."
        trace.extend(["approval_band_checked", "manager_review_required"])
    elif amount <= policy["finance_review_limit"]:
        route = "finance_review"
        reason = "Amount exceeds the manager band and falls within the finance review band."
        trace.extend(["approval_band_checked", "finance_review_required"])
    else:
        route = "executive_review"
        reason = "Amount exceeds the finance review limit."
        trace.extend(["approval_band_checked", "executive_review_required"])

    trace.append("no_purchase_order_created")
    return _result(request_id, "review_required", route, reason, trace,
                   amount=amount, currency=policy["currency"],
                   category=request["category"],
                   next_step="A designated approver must review the request outside this demo.")


def build_report(requests: Any, policy: dict[str, Any]) -> dict[str, Any]:
    validate_policy(policy)
    if not isinstance(requests, list):
        raise ValueError("Input must contain a JSON array of requests.")
    ids = [
        item.get("request_id").strip()
        for item in requests
        if isinstance(item, dict) and isinstance(item.get("request_id"), str)
        and item.get("request_id").strip()
    ]
    duplicate_ids = {item for item, count in Counter(ids).items() if count > 1}
    decisions = [assess_request(item, policy, duplicate_ids) for item in requests]
    return {
        "status": "TRIAGE_COMPLETE",
        "requests_processed": len(decisions),
        "review_required": sum(item["status"] in ("review_required", "duplicate_review") for item in decisions),
        "needs_information": sum(item["status"] == "needs_information" for item in decisions),
        "rejected_input": sum(item["status"] == "rejected_input" for item in decisions),
        "policy_summary": {
            "currency": policy["currency"],
            "manager_review_limit": policy["manager_review_limit"],
            "finance_review_limit": policy["finance_review_limit"],
            "allowed_categories": policy["allowed_categories"],
        },
        "decisions": decisions,
        "limitations": [
            "This demo applies explicit rules; it is not an LLM-powered system.",
            "All approval routes require a human decision.",
            "No purchase order, payment, supplier communication, or external system update is performed.",
            "Thresholds and categories are illustrative and must be replaced with an organization's approved policy.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("sample_requests.json"))
    parser.add_argument("--policy", type=Path, default=Path("policy.json"))
    parser.add_argument("--output", type=Path, default=Path("output/triage_report.json"))
    args = parser.parse_args()
    try:
        requests = json.loads(args.input.read_text(encoding="utf-8"))
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = build_report(requests, policy)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Processed {report['requests_processed']} request(s). Results: {args.output}")
    print("No requests were approved and no purchase orders were created.")


if __name__ == "__main__":
    main()
