"""Resumable composition of the portfolio's lead and invoice intake demos."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Automation & Workflows" / "lead-intake-pipeline"))
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Automation & Workflows" / "invoice-intake-exception-routing"))
sys.path.insert(0, str(ROOT / "Demo Templates" / "AI Agents & Agentic Systems" / "durable-workflow-runner"))
from pipeline import process_rows
from invoice_workflow import process_invoices
from durable_runner import run_durable_workflow

def build_handlers() -> dict[str, Any]:
    def lead_intake(request):
        rows = request["context"].get("lead_records", [])
        if not isinstance(rows, list):
            raise ValueError("lead_records must be a list")
        processed, exceptions = process_rows(rows)
        return {"processed": processed, "exceptions": exceptions}

    def invoice_intake(request):
        context = request["context"]
        return process_invoices(context.get("invoice_records", []),
                                context.get("approval_threshold", "5000.00"))

    def prepare_human_review(request):
        outputs = request["previous_outputs"]
        lead_result, invoice_result = outputs["lead_intake"], outputs["invoice_intake"]
        lead_items = [
            {"item_id": f"lead_intake:{item['row']}", "source": "lead_intake", "reference": item.get("email") or f"row:{item['row']}",
             "reason": item["reason"], "row": int(item["row"])}
            for item in lead_result["exceptions"]
        ]
        invoice_items = [
            {"item_id": f"invoice_intake:{item['row']}", "source": "invoice_intake", "reference": item.get("invoice_id") or f"row:{item['row']}",
             "reason": item["status"], "row": item["row"], "details": item["reasons"]}
            for item in invoice_result["results"] if item["status"] != "AP_REVIEW"
        ]
        return {
            "status": "PENDING_HUMAN_REVIEW" if lead_items or invoice_items else "NO_REVIEW_REQUIRED",
            "lead_exception_count": len(lead_items), "invoice_review_count": len(invoice_items),
            "items": lead_items + invoice_items,
            "note": "Queue preparation only; no approval, payment, outreach, or external action is performed."
        }
    return {"lead_intake": lead_intake, "invoice_intake": invoice_intake,
            "prepare_human_review": prepare_human_review}

def run_intake_workflow(workflow_id, lead_records, invoice_records, database, event_log,
                        approval_threshold="5000.00"):
    context = {"lead_records": lead_records, "invoice_records": invoice_records,
               "approval_threshold": approval_threshold}
    return run_durable_workflow(
        workflow_id, ["lead_intake", "invoice_intake", "prepare_human_review"],
        build_handlers(), context, database, event_log)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leads", required=True)
    parser.add_argument("--invoices", required=True)
    parser.add_argument("--database", default="output/intake-workflows.sqlite")
    parser.add_argument("--events", default="output/intake-workflows.jsonl")
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--approval-threshold", default="5000.00")
    args = parser.parse_args()
    try:
        leads = json.loads(Path(args.leads).read_text(encoding="utf-8"))
        invoices = json.loads(Path(args.invoices).read_text(encoding="utf-8"))
        if not isinstance(leads, list) or not isinstance(invoices, list):
            raise ValueError("Both input files must contain JSON arrays")
        result = run_intake_workflow(args.workflow_id, leads, invoices, args.database,
                                     args.events, args.approval_threshold)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    workflow = result["workflow"]
    print(json.dumps({"workflow_id": workflow["workflow_id"], "status": workflow["status"],
                      "completed_steps": workflow["state"]["completed_steps"],
                      "human_review": workflow["state"]["outputs"].get("prepare_human_review"),
                      "resumed": result["resumed"]}, indent=2))
    return 0 if workflow["status"] == "COMPLETED" else 1

if __name__ == "__main__":
    raise SystemExit(main())
