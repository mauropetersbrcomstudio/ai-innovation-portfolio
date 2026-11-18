"""Deterministic, side-effect-free SME operations assistant demo.

This baseline intentionally simulates actions. It does not connect to external
systems, send messages, modify records, or execute business operations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


ALLOWED_ACTIONS = {
    "billing_status": "Retrieve a simulated billing status",
    "order_status": "Retrieve a simulated order status",
    "support_triage": "Create a simulated support triage record",
}

KEYWORDS = {
    "billing_status": ("invoice", "billing", "payment", "fatura", "pagamento"),
    "order_status": ("order", "delivery", "shipment", "pedido", "entrega"),
    "support_triage": ("support", "issue", "problem", "help", "suporte", "problema"),
}


@dataclass(frozen=True)
class AgentResult:
    status: str
    category: str | None
    proposed_action: str | None
    action_description: str | None
    trace: tuple[str, ...]
    escalation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def classify_request(request: str) -> str | None:
    """Classify only when exactly one intent is detected."""
    normalized = request.casefold()
    matches = [
        action
        for action, terms in KEYWORDS.items()
        if any(term in normalized for term in terms)
    ]
    return matches[0] if len(matches) == 1 else None


def handle_request(request: str, requested_action: str | None = None) -> AgentResult:
    """Return an auditable proposal; never perform the proposed action."""
    trace = ["received_request", "checked_allowlist"]

    if not isinstance(request, str) or not request.strip():
        return AgentResult(
            status="escalated",
            category=None,
            proposed_action=None,
            action_description=None,
            trace=tuple(trace + ["rejected_empty_request"]),
            escalation_reason="Request must be a non-empty string.",
        )

    action = requested_action or classify_request(request)
    trace.append("classified_request" if requested_action is None else "read_requested_action")

    if action is None:
        return AgentResult(
            status="escalated",
            category=None,
            proposed_action=None,
            action_description=None,
            trace=tuple(trace + ["escalated_ambiguous_or_unclassified"]),
            escalation_reason="Intent is ambiguous or not recognized; human review is required.",
        )

    if action not in ALLOWED_ACTIONS:
        return AgentResult(
            status="rejected",
            category=None,
            proposed_action=None,
            action_description=None,
            trace=tuple(trace + ["rejected_unknown_action"]),
            escalation_reason="Requested action is not on the allowlist.",
        )

    trace.extend(["validated_action", "simulated_no_side_effects"])
    return AgentResult(
        status="proposal_only",
        category=action,
        proposed_action=action,
        action_description=ALLOWED_ACTIONS[action],
        trace=tuple(trace),
    )


if __name__ == "__main__":
    examples = [
        "Can you check the status of my invoice?",
        "Where is my order delivery?",
        "I need help with a problem.",
        "Please do something with this.",
    ]
    for example in examples:
        print({"request": example, "result": handle_request(example).to_dict()})
