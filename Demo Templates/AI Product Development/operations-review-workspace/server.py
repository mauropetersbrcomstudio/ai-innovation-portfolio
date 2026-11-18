"""Loopback-only HTTP adapter for the Operations Review Workspace demo."""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[3]
HUB = ROOT / "Demo Templates" / "AI Automation & Workflows" / "intake-operations-hub"
sys.path.insert(0, str(HUB))
from workflow_hub import run_intake_workflow
from review_decisions import ReviewDecisionStore

STATIC_DIR = Path(__file__).resolve().parent
STATIC_FILES = {"index.html", "app.js", "styles.css"}
DEMO_WORKFLOW_ID = "operations-review-demo"
DEMO_LEADS = [
    {"name": "Alex Morgan", "email": "alex@example.test", "company": "Northstar Studio"},
    {"name": "Taylor Reed", "email": "not-an-email", "company": ""},
    {"name": "Jordan Lee", "email": "alex@example.test", "company": "Duplicate Example"},
]
DEMO_INVOICES = [
    {"invoice_id": "INV-DEMO-001", "supplier_id": "SUP-01", "invoice_date": "2026-01-10",
     "due_date": "2026-02-10", "amount": "7200.00", "currency": "BRL", "purchase_order": ""},
    {"invoice_id": "INV-DEMO-002", "supplier_id": "SUP-02", "invoice_date": "2026-01-12",
     "due_date": "2026-02-12", "amount": "240.00", "currency": "BRL", "purchase_order": "PO-02"},
]


def seed_demo(database: Path, event_log: Path) -> None:
    """Create one deterministic sample workflow only when it does not exist."""
    from state_store import StateStore
    store = StateStore(database)
    if store.get(DEMO_WORKFLOW_ID) is None:
        run_intake_workflow(DEMO_WORKFLOW_ID, DEMO_LEADS, DEMO_INVOICES,
                            database, event_log, "5000.00")


def workflow_payload(database: Path, workflow_id: str) -> dict:
    from state_store import StateStore
    workflow = StateStore(database).get(workflow_id)
    if workflow is None:
        raise KeyError("Workflow not found")
    state = workflow["state"]
    queue = state.get("outputs", {}).get("prepare_human_review", {})
    decisions = ReviewDecisionStore(database).list_for_workflow(workflow_id)
    decision_by_item = {row["item_id"]: row for row in decisions}
    items = []
    for item in queue.get("items", []):
        items.append({**item, "decision": decision_by_item.get(item["item_id"])})
    return {
        "workflow_id": workflow_id,
        "status": workflow["status"],
        "completed_steps": state.get("completed_steps", []),
        "queue_status": queue.get("status", "NO_REVIEW_REQUIRED"),
        "items": items,
        "decisions": decisions,
        "events": StateStore(database).events(workflow_id),
    }


def make_handler(database: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = "OperationsReviewDemo/1.0"

        def _send(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            raw_length = self.headers.get("Content-Length", "")
            if not raw_length.isdigit() or int(raw_length) > 16384:
                raise ValueError("Request body must be valid JSON and no larger than 16 KB")
            raw = self.rfile.read(int(raw_length))
            try:
                value = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Request body must be valid JSON") from exc
            if not isinstance(value, dict):
                raise ValueError("Request body must be a JSON object")
            return value

        def _send_static(self, filename: str) -> None:
            if filename not in STATIC_FILES:
                return self._send(404, {"error": "Not found"})
            content = (STATIC_DIR / filename).read_bytes()
            content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/":
                return self._send_static("index.html")
            if path in {"/app.js", "/styles.css"}:
                return self._send_static(path.lstrip("/"))
            if path == "/api/health":
                return self._send(200, {"status": "ok", "mode": "local-demo"})
            prefix = "/api/workflows/"
            if path.startswith(prefix):
                workflow_id = unquote(path[len(prefix):])
                if not workflow_id or "/" in workflow_id:
                    return self._send(400, {"error": "Invalid workflow ID"})
                try:
                    return self._send(200, workflow_payload(database, workflow_id))
                except KeyError as exc:
                    return self._send(404, {"error": str(exc).strip("'")})
                except Exception:
                    return self._send(500, {"error": "Unable to read workflow data"})
            return self._send(404, {"error": "Not found"})

        def do_POST(self):
            if urlparse(self.path).path != "/api/decisions":
                return self._send(404, {"error": "Not found"})
            try:
                data = self._read_json()
                required = ("workflow_id", "item_id", "reviewer_id", "outcome", "reason")
                if any(not isinstance(data.get(key), str) for key in required):
                    raise ValueError("All decision fields must be strings")
                result = ReviewDecisionStore(database).record(*(data[key] for key in required))
                return self._send(201, {"decision": result})
            except ValueError as exc:
                return self._send(409 if "already exists" in str(exc) else 400, {"error": str(exc)})
            except KeyError as exc:
                return self._send(404, {"error": str(exc).strip("'")})
            except Exception:
                return self._send(500, {"error": "Unable to persist decision"})

        def log_message(self, fmt, *args):
            return

    return Handler


def create_server(database: Path, host: str = "127.0.0.1", port: int = 8765):
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("This demo server may bind only to loopback")
    return ThreadingHTTPServer((host, port), make_handler(database))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("output/operations-review-demo.sqlite"))
    parser.add_argument("--events", type=Path, default=Path("output/operations-review-demo.jsonl"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        parser.error("This demo server may bind only to loopback")
    args.database.parent.mkdir(parents=True, exist_ok=True)
    seed_demo(args.database, args.events)
    server = create_server(args.database, args.host, args.port)
    print(f"Operations Review Workspace: http://127.0.0.1:{server.server_port}")
    print("DEMO ONLY — synthetic data; reviewer identity is not authenticated.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
