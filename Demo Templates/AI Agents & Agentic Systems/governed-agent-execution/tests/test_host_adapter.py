import unittest

from host_adapter import GovernedToolHost, run_demo
from gateway import ToolGateway, ToolSpec
from security_governance import ApprovalEvidence, Principal, SecurityPolicyEngine


POLICY = {
    "agents": {
        "support-agent": {
            "roles": ["support_operator", "supervisor"],
            "tools": {
                "create_review_task": {
                    "risks": ["MEDIUM"],
                    "approval_required": True,
                }
            },
        }
    }
}


def make_approval(approval_id="approval-1", subject_id="user-1"):
    return ApprovalEvidence(
        approval_id=approval_id,
        approver_id="supervisor-1",
        agent_id="support-agent",
        tool="create_review_task",
        risk="MEDIUM",
        subject_id=subject_id,
    )


class GovernedToolHostTests(unittest.TestCase):
    def setUp(self):
        self.verified_ids = {"approval-1", "approval-2", "approval-3"}

        def verify(evidence):
            return (
                evidence.approval_id in self.verified_ids
                and evidence.approver_id == "supervisor-1"
            )

        self.security = SecurityPolicyEngine(POLICY, approval_verifier=verify)
        self.side_effects = []
        self.gateway = ToolGateway()
        self.gateway.register(
            ToolSpec(
                name="create_review_task",
                description="Create a synthetic review task",
                input_schema={
                    "type": "object",
                    "properties": {
                        "request": {"type": "string", "minLength": 1, "maxLength": 100}
                    },
                    "required": ["request"],
                    "additionalProperties": False,
                },
                allowed_roles=("support_operator", "supervisor"),
                requires_approval=True,
                max_calls_per_session=1,
            ),
            lambda args: self.side_effects.append(args["request"])
            or {"queued": True, "marker": "synthetic-handler-output"},
        )
        self.host = GovernedToolHost(self.security, self.gateway)
        self.principal = Principal("user-1", ("support_operator",), True)

    def invoke(self, **overrides):
        values = {
            "session_id": "session-1",
            "principal": self.principal,
            "agent_id": "support-agent",
            "tool_name": "create_review_task",
            "risk": "MEDIUM",
            "arguments": {"request": "Review synthetic request"},
            "approval": make_approval(),
        }
        values.update(overrides)
        return self.host.invoke(**values)

    def test_verified_approval_is_required_before_dispatch(self):
        result = self.invoke(approval=None)
        self.assertEqual(result["status"], "DENIED")
        self.assertEqual(result["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertIsNone(result["dispatch"])
        self.assertEqual(self.side_effects, [])
        self.assertEqual(self.gateway.audit_log, [])

    def test_unauthenticated_principal_never_reaches_gateway(self):
        principal = Principal("user-1", ("support_operator",), False)
        result = self.invoke(principal=principal)
        self.assertEqual(result["reason"], "AUTHENTICATION_REQUIRED")
        self.assertEqual(self.gateway.audit_log, [])
        self.assertEqual(self.side_effects, [])

    def test_unverified_approval_fails_closed(self):
        result = self.invoke(approval=make_approval("untrusted-id"))
        self.assertEqual(result["reason"], "APPROVAL_NOT_VERIFIED")
        self.assertEqual(self.side_effects, [])

    def test_authorized_call_derives_gateway_approval_and_executes(self):
        result = self.invoke()
        self.assertEqual(result["status"], "EXECUTED")
        self.assertEqual(result["dispatch"]["output"]["queued"], True)
        self.assertEqual(self.side_effects, ["Review synthetic request"])
        self.assertEqual(self.gateway.audit_log[0]["status"], "EXECUTED")
        combined_audit = repr(
            self.host.audit_events + self.security.audit_events + self.gateway.audit_log
        )
        self.assertNotIn("synthetic-handler-output", combined_audit)
        self.assertNotIn("Review synthetic request", combined_audit)

    def test_approval_id_cannot_be_replayed_in_same_host_instance(self):
        first = self.invoke()
        second = self.invoke(session_id="session-2")
        self.assertEqual(first["status"], "EXECUTED")
        self.assertEqual(second["reason"], "APPROVAL_ALREADY_USED")
        self.assertEqual(len(self.side_effects), 1)

    def test_handler_error_consumes_approval_after_handler_entry(self):
        failing_gateway = ToolGateway()
        failing_gateway.register(
            ToolSpec(
                name="create_review_task",
                description="Fail after simulated handler entry",
                input_schema={"type": "object"},
                allowed_roles=("support_operator",),
                requires_approval=True,
            ),
            lambda _: (_ for _ in ()).throw(RuntimeError("synthetic failure")),
        )
        host = GovernedToolHost(self.security, failing_gateway)
        first = host.invoke(
            session_id="error-session",
            principal=self.principal,
            agent_id="support-agent",
            tool_name="create_review_task",
            risk="MEDIUM",
            arguments={},
            approval=make_approval("approval-2"),
        )
        second = host.invoke(
            session_id="error-session-2",
            principal=self.principal,
            agent_id="support-agent",
            tool_name="create_review_task",
            risk="MEDIUM",
            arguments={},
            approval=make_approval("approval-2"),
        )
        self.assertEqual(first["reason"], "HANDLER_FAILED")
        self.assertEqual(second["reason"], "APPROVAL_ALREADY_USED")

    def test_gateway_session_quota_persists_within_host_session(self):
        first = self.invoke()
        second = self.invoke(approval=make_approval("approval-2"))
        self.assertEqual(first["status"], "EXECUTED")
        self.assertEqual(second["reason"], "SESSION_CALL_LIMIT_REACHED")
        self.assertEqual(len(self.side_effects), 1)

    def test_session_id_cannot_be_reused_by_another_subject(self):
        self.invoke()
        other = Principal("user-2", ("support_operator",), True)
        result = self.invoke(
            principal=other,
            approval=make_approval("approval-2", subject_id="user-2"),
        )
        self.assertEqual(result["reason"], "SESSION_SUBJECT_MISMATCH")
        self.assertEqual(len(self.side_effects), 1)

    def test_session_role_cannot_change_mid_session(self):
        self.invoke()
        supervisor = Principal("user-1", ("supervisor",), True)
        result = self.invoke(
            principal=supervisor,
            approval=make_approval("approval-2"),
        )
        self.assertEqual(result["reason"], "SESSION_ROLE_MISMATCH")
        self.assertEqual(len(self.side_effects), 1)

    def test_gateway_role_mismatch_is_denied_before_dispatch(self):
        gateway = ToolGateway()
        gateway.register(
            ToolSpec(
                "create_review_task",
                "misconfigured role",
                {"type": "object"},
                ("finance_manager",),
                requires_approval=True,
            ),
            lambda _: self.side_effects.append("unexpected"),
        )
        host = GovernedToolHost(self.security, gateway)
        result = host.invoke(
            session_id="mismatch",
            principal=self.principal,
            agent_id="support-agent",
            tool_name="create_review_task",
            risk="MEDIUM",
            arguments={"request": "Review"},
            approval=make_approval(),
        )
        self.assertEqual(result["reason"], "GATEWAY_ROLE_MISMATCH")
        self.assertEqual(self.side_effects, [])

    def test_policy_and_gateway_approval_requirements_must_match(self):
        no_approval_policy = {
            "agents": {
                "support-agent": {
                    "roles": ["support_operator"],
                    "tools": {
                        "create_review_task": {
                            "risks": ["MEDIUM"],
                            "approval_required": False,
                        }
                    },
                }
            }
        }
        security = SecurityPolicyEngine(no_approval_policy)
        host = GovernedToolHost(security, self.gateway)
        result = host.invoke(
            session_id="config-mismatch",
            principal=self.principal,
            agent_id="support-agent",
            tool_name="create_review_task",
            risk="MEDIUM",
            arguments={"request": "Review"},
        )
        self.assertEqual(result["reason"], "APPROVAL_CONFIGURATION_MISMATCH")
        self.assertEqual(self.side_effects, [])

    def test_invalid_risk_and_session_are_denied(self):
        invalid_risk = self.invoke(risk=["MEDIUM"])
        invalid_session = self.invoke(session_id=" ")
        self.assertEqual(invalid_risk["reason"], "INVALID_RISK")
        self.assertEqual(invalid_session["reason"], "INVALID_SESSION_ID")
        self.assertEqual(self.side_effects, [])

    def test_invalid_arguments_do_not_consume_approval_or_call_quota(self):
        invalid = self.invoke(arguments={"unexpected": "field"})
        valid = self.invoke(arguments={"request": "Now valid"})
        self.assertEqual(invalid["reason"], "INVALID_ARGUMENTS")
        self.assertEqual(valid["status"], "EXECUTED")
        self.assertEqual(self.side_effects, ["Now valid"])

    def test_demo_runner_exposes_denied_and_approved_paths(self):
        denied = run_demo()
        approved = run_demo(approval_present=True)
        self.assertEqual(denied["invocation"]["reason"], "HUMAN_APPROVAL_REQUIRED")
        self.assertEqual(denied["side_effects"], [])
        self.assertEqual(approved["invocation"]["status"], "EXECUTED")
        self.assertEqual(len(approved["side_effects"]), 1)
        self.assertFalse(approved["side_effects"][0].get("external_action", False))


if __name__ == "__main__":
    unittest.main()
