"""Deterministic invoice intake and exception-routing demonstration.

No payments, approvals, ERP writes, or external messages are performed.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


SUPPORTED_CURRENCIES = {"BRL", "EUR", "GBP", "USD"}
STATUSES = (
    "AP_REVIEW",
    "MANAGER_APPROVAL",
    "NEEDS_INFORMATION",
    "DUPLICATE_REVIEW",
    "POLICY_HOLD",
)


def _clean_text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _parse_amount(value: Any) -> Decimal | None:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not amount.is_finite() or amount <= 0:
        return None
    return amount


def process_invoices(
    records: list[Any],
    approval_threshold: Any = "5000.00",
) -> dict[str, Any]:
    """Validate invoice records and assign review routes without external side effects."""
    if not isinstance(records, list):
        raise ValueError("Invoice input must be a JSON array")

    threshold = _parse_amount(approval_threshold)
    if threshold is None:
        raise ValueError("Approval threshold must be a positive finite amount")

    prepared: list[dict[str, Any]] = []
    duplicate_counts: Counter[tuple[str, str]] = Counter()

    for row_number, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            prepared.append({
                "row": row_number,
                "record_valid": False,
                "invoice_id": None,
                "supplier_id": None,
                "invoice_date": None,
                "due_date": None,
                "amount": None,
                "currency": None,
                "purchase_order": None,
                "duplicate_key": None,
            })
            continue

        invoice_id = _clean_text(record.get("invoice_id"))
        supplier_id = _clean_text(record.get("supplier_id"))
        invoice_date_text = _clean_text(record.get("invoice_date"))
        due_date_text = _clean_text(record.get("due_date"))
        currency = _clean_text(record.get("currency")).upper()
        purchase_order = _clean_text(record.get("purchase_order"))
        amount = _parse_amount(record.get("amount"))
        invoice_date = _parse_date(invoice_date_text) if invoice_date_text else None
        due_date = _parse_date(due_date_text) if due_date_text else None
        duplicate_key = (
            (supplier_id.casefold(), invoice_id.casefold())
            if supplier_id and invoice_id else None
        )
        if duplicate_key:
            duplicate_counts[duplicate_key] += 1

        prepared.append({
            "row": row_number,
            "record_valid": True,
            "invoice_id": invoice_id or None,
            "supplier_id": supplier_id or None,
            "invoice_date": invoice_date.isoformat() if invoice_date else invoice_date_text or None,
            "due_date": due_date.isoformat() if due_date else due_date_text or None,
            "invoice_date_parsed": invoice_date,
            "due_date_parsed": due_date,
            "amount": format(amount, "f") if amount is not None else None,
            "amount_present": record.get("amount") is not None and not (isinstance(record.get("amount"), str) and not record.get("amount").strip()),
            "amount_parsed": amount,
            "currency": currency or None,
            "purchase_order": purchase_order or None,
            "duplicate_key": duplicate_key,
        })

    results: list[dict[str, Any]] = []
    for item in prepared:
        reasons: list[str] = []
        missing_fields: list[str] = []

        if not item["record_valid"]:
            status = "POLICY_HOLD"
            reasons.append("RECORD_MUST_BE_OBJECT")
        elif item["duplicate_key"] and duplicate_counts[item["duplicate_key"]] > 1:
            status = "DUPLICATE_REVIEW"
            reasons.append("DUPLICATE_SUPPLIER_INVOICE_PAIR")
        else:
            required_values = {
                "invoice_id": item["invoice_id"],
                "supplier_id": item["supplier_id"],
                "invoice_date": item["invoice_date"],
                "due_date": item["due_date"],
                "amount": item["amount_present"],
                "currency": item["currency"],
                "purchase_order": item["purchase_order"],
            }
            missing_fields = [name for name, value in required_values.items() if not value]

            if missing_fields:
                status = "NEEDS_INFORMATION"
                reasons.append("MISSING_REQUIRED_FIELDS")
            elif item["invoice_date_parsed"] is None:
                status = "POLICY_HOLD"
                reasons.append("INVALID_INVOICE_DATE")
            elif item["due_date_parsed"] is None:
                status = "POLICY_HOLD"
                reasons.append("INVALID_DUE_DATE")
            elif item["due_date_parsed"] < item["invoice_date_parsed"]:
                status = "POLICY_HOLD"
                reasons.append("DUE_DATE_BEFORE_INVOICE_DATE")
            elif item["amount_parsed"] is None:
                status = "POLICY_HOLD"
                reasons.append("INVALID_AMOUNT")
            elif item["currency"] not in SUPPORTED_CURRENCIES:
                status = "POLICY_HOLD"
                reasons.append("UNSUPPORTED_CURRENCY")
            elif item["amount_parsed"] > threshold:
                status = "MANAGER_APPROVAL"
                reasons.append("AMOUNT_ABOVE_APPROVAL_THRESHOLD")
            else:
                status = "AP_REVIEW"
                reasons.append("READY_FOR_ACCOUNTS_PAYABLE_REVIEW")

        results.append({
            "row": item["row"],
            "invoice_id": item["invoice_id"],
            "supplier_id": item["supplier_id"],
            "invoice_date": item["invoice_date"],
            "due_date": item["due_date"],
            "amount": item["amount"],
            "currency": item["currency"],
            "purchase_order": item["purchase_order"],
            "status": status,
            "reasons": reasons,
            "missing_fields": missing_fields,
        })

    status_counts = {
        status: sum(1 for item in results if item["status"] == status)
        for status in STATUSES
    }
    return {
        "processed_count": len(results),
        "approval_threshold": format(threshold, "f"),
        "status_counts": status_counts,
        "results": results,
    }


def run(input_path: str | Path, output_path: str | Path,
        approval_threshold: Any = "5000.00") -> dict[str, Any]:
    source = Path(input_path)
    destination = Path(output_path)
    records = json.loads(source.read_text(encoding="utf-8"))
    result = process_invoices(records, approval_threshold)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and route synthetic invoice records.")
    parser.add_argument("--input", required=True, help="Path to a JSON array of invoice records")
    parser.add_argument("--output", required=True, help="Path for the JSON review report")
    parser.add_argument("--approval-threshold", default="5000.00",
                        help="Amount above which manager approval is recommended")
    args = parser.parse_args(argv)

    try:
        result = run(args.input, args.output, args.approval_threshold)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Invoice workflow failed: {exc}", file=sys.stderr)
        return 2

    print(
        f"Processed {result['processed_count']} invoices; "
        f"routes: {result['status_counts']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
