import unittest

from gateway import Session, ToolGateway, ToolSpec


SCHEMA = {
    "type": "object",
    "properties": {
        "ticket": {"type": "string", "minLength": 4, "maxLength": 40},
        "priority": {"type": "string", "enum": ["normal", "urgent"]},
    },
    "required": ["ticket", "priority"],
    "additionalProperties": False,
}


def make_gateway():
    gateway = ToolGateway()
    gateway.register(
        ToolSpec(
            name="create_ticket",
            description="Create a simulated support ticket",
            input_schema=SCHEMA,
            allowed_roles=("support", "manager"),
            requires_approval=True,
            max_calls_per_session=1,
        ),
        lambda args: {"ticket_ref": "SIM-001", "received": args["ticket"]},
    )
    return gateway


class ToolGatewayTests(unittest.TestCase):
    def test_allowlisted_approved_call_executes(self):
        gateway = make_gateway()
        session = Session("s1", "support", approved_tools=("create_ticket",))
        result = gateway.invoke("create_ticket", {"ticket": "Cannot login", "priority": "urgent"}, session)
        self.assertEqual(result["status"], "EXECUTED")
        self.assertEqual(result["output"]["ticket_ref"], "SIM-001")

    def test_unknown_tool_is_denied(self):
        gateway = make_gateway()
        result = gateway.invoke("shell", {}, Session("s1", "support"))
        self.assertEqual(result["reason"], "TOOL_NOT_ALLOWLISTED")

    def test_role_is_checked_before_execution(self):
        gateway = make_gateway()
        result = gateway.invoke("create_ticket", {"ticket": "Cannot login", "priority": "normal"}, Session("s1", "sales", approved_tools=("create_ticket",)))
        self.assertEqual(result["reason"], "ROLE_NOT_ALLOWED")

    def test_approval_required(self):
        gateway = make_gateway()
        result = gateway.invoke("create_ticket", {"ticket": "Cannot login", "priority": "normal"}, Session("s1", "support"))
        self.assertEqual(result["reason"], "HUMAN_APPROVAL_REQUIRED")

    def test_invalid_arguments_are_rejected(self):
        gateway = make_gateway()
        session = Session("s1", "support", approved_tools=("create_ticket",))
        result = gateway.invoke("create_ticket", {"ticket": "x", "priority": "critical", "extra": True}, session)
        self.assertEqual(result["reason"], "INVALID_ARGUMENTS")
        self.assertEqual(session.call_counts, {})

    def test_call_limit_enforced(self):
        gateway = make_gateway()
        session = Session("s1", "support", approved_tools=("create_ticket",))
        args = {"ticket": "Cannot login", "priority": "normal"}
        gateway.invoke("create_ticket", args, session)
        result = gateway.invoke("create_ticket", args, session)
        self.assertEqual(result["reason"], "SESSION_CALL_LIMIT_REACHED")

    def test_handler_failure_does_not_leak_exception(self):
        gateway = ToolGateway()
        gateway.register(ToolSpec("broken", "test", {"type": "object"}, ("support",)), lambda _: 1 / 0)
        result = gateway.invoke("broken", {}, Session("s1", "support"))
        self.assertEqual(result, {"status": "ERROR", "reason": "HANDLER_FAILED"})


    def test_audit_log_does_not_store_handler_output(self):
        gateway = ToolGateway()
        gateway.register(
            ToolSpec("read_secret", "return a synthetic value", {"type": "object"}, ("support",)),
            lambda _: {"api_token": "synthetic-secret-value"},
        )
        result = gateway.invoke("read_secret", {}, Session("s1", "support"))
        self.assertEqual(result["output"]["api_token"], "synthetic-secret-value")
        self.assertNotIn("output", gateway.audit_log[0])
        self.assertNotIn("synthetic-secret-value", repr(gateway.audit_log))

    def test_handler_failure_consumes_call_limit(self):
        gateway = ToolGateway()
        attempts = []

        def partially_failing_handler(_):
            attempts.append("called")
            raise RuntimeError("simulated failure after a possible side effect")

        gateway.register(
            ToolSpec("bounded_write", "bounded synthetic write", {"type": "object"},
                     ("support",), max_calls_per_session=1),
            partially_failing_handler,
        )
        session = Session("s1", "support")
        first = gateway.invoke("bounded_write", {}, session)
        second = gateway.invoke("bounded_write", {}, session)
        self.assertEqual(first, {"status": "ERROR", "reason": "HANDLER_FAILED"})
        self.assertEqual(second["reason"], "SESSION_CALL_LIMIT_REACHED")
        self.assertEqual(attempts, ["called"])
        self.assertEqual(session.call_counts["bounded_write"], 1)

    def test_audit_log_records_denials_and_execution(self):
        gateway = make_gateway()
        session = Session("s1", "support", approved_tools=("create_ticket",))
        args = {"ticket": "Cannot login", "priority": "normal"}
        gateway.invoke("create_ticket", args, session)
        self.assertEqual([item["status"] for item in gateway.audit_log], ["EXECUTED"])
        self.assertEqual(gateway.audit_log[0]["session_id"], "s1")


if __name__ == "__main__":
    unittest.main()
