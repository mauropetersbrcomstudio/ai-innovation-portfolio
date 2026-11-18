"""Configurable, local CRM lead qualification and routing demo."""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

REQUIRED = ("lead_id", "name", "email", "territory", "created_date")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def load_rules(path: Path) -> dict:
    rules = json.loads(path.read_text(encoding="utf-8"))
    threshold = rules.get("qualification_threshold")
    weights = rules.get("weights")
    teams = rules.get("territory_teams")
    sla = rules.get("follow_up_sla_calendar_days")
    if not isinstance(threshold, int) or not 0 <= threshold <= 100:
        raise ValueError("qualification_threshold must be an integer from 0 to 100")
    if not isinstance(weights, dict) or not weights or any(
        not isinstance(v, int) or v < 0 for v in weights.values()
    ):
        raise ValueError("weights must be a non-empty object of non-negative integers")
    if sum(weights.values()) > 100:
        raise ValueError("the sum of qualification weights cannot exceed 100")
    if not isinstance(teams, dict) or not teams:
        raise ValueError("territory_teams must be a non-empty object")
    if not isinstance(sla, int) or sla < 0:
        raise ValueError("follow_up_sla_calendar_days must be a non-negative integer")
    return rules


def score_lead(row: dict, rules: dict) -> int:
    weights = rules["weights"]
    score = 0
    if row.get("company", "").strip():
        score += weights.get("company_provided", 0)
    email = row.get("email", "").strip().lower()
    domain = email.rsplit("@", 1)[-1] if "@" in email else ""
    free_domains = {d.lower() for d in rules.get("free_email_domains", [])}
    if EMAIL_RE.fullmatch(email) and domain not in free_domains:
        score += weights.get("business_email", 0)
    if row.get("need", "").strip():
        score += weights.get("need_provided", 0)
    if row.get("budget_confirmed", "").strip().lower() == "true":
        score += weights.get("budget_confirmed", 0)
    if row.get("decision_role_confirmed", "").strip().lower() == "true":
        score += weights.get("decision_role_confirmed", 0)
    return score


def route_records(rows: list[dict], rules: dict) -> tuple[list[dict], list[dict]]:
    seen_ids: set[str] = set()
    seen_emails: set[str] = set()
    routed, review = [], []
    for line, original in enumerate(rows, start=2):
        row = {k: (v or "").strip() for k, v in original.items()}
        reasons = []
        for field in REQUIRED:
            if not row.get(field):
                reasons.append(f"missing_{field}")
        if row.get("email") and not EMAIL_RE.fullmatch(row["email"].lower()):
            reasons.append("invalid_email_format")
        created = None
        if row.get("created_date"):
            try:
                created = date.fromisoformat(row["created_date"])
            except ValueError:
                reasons.append("invalid_created_date")
        lead_id = row.get("lead_id", "")
        email = row.get("email", "").lower()
        if lead_id and lead_id in seen_ids:
            reasons.append("duplicate_lead_id")
        if email and email in seen_emails:
            reasons.append("duplicate_email")
        if lead_id:
            seen_ids.add(lead_id)
        if email:
            seen_emails.add(email)
        if reasons:
            review.append({**row, "source_line": str(line), "score": "",
                           "review_reasons": ";".join(reasons)})
            continue

        score = score_lead(row, rules)
        territory = row["territory"].lower()
        team = rules["territory_teams"].get(territory)
        if score >= rules["qualification_threshold"] and not team:
            review.append({**row, "source_line": str(line), "score": str(score),
                           "review_reasons": "unmapped_territory"})
            continue
        status = "sales_queue" if score >= rules["qualification_threshold"] else "nurture_queue"
        owner = team if status == "sales_queue" else "marketing_nurture"
        due = created + timedelta(days=rules["follow_up_sla_calendar_days"])
        routed.append({**row, "qualification_score": str(score), "route": status,
                       "assigned_team": owner, "follow_up_due_date": due.isoformat()})
    return routed, review


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--leads", type=Path, required=True)
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rules = load_rules(args.rules)
    with args.leads.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("input CSV must include a header row")
        rows = list(reader)
        fields = list(reader.fieldnames)
    routed, review = route_records(rows, rules)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "routed_leads.csv", routed,
              fields + ["qualification_score", "route", "assigned_team", "follow_up_due_date"])
    write_csv(args.output_dir / "review_queue.csv", review,
              fields + ["source_line", "score", "review_reasons"])
    summary = {
        "input_count": len(rows),
        "routed_count": len(routed),
        "review_count": len(review),
        "sales_queue_count": sum(r["route"] == "sales_queue" for r in routed),
        "nurture_queue_count": sum(r["route"] == "nurture_queue" for r in routed),
        "note": "Rule-based demonstration only; not a conversion prediction or live CRM action."
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
