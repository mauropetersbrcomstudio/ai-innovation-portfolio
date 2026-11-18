import unittest

from security_governance import (
    ApprovalEvidence,
    Principal,
    SecurityPolicyEngine,
    SecurityPolicyError,
)


POLICY = {
    "agents": {
        "support-agent": {
            "roles": ["support_operator", "supervisor"],
            "tools": {
                "search_kb": {"risks": ["LOW", "MEDIUM"], "approval_required": False},
                "issue_refund": {"risks": ["HIGH"], "approval_required": True},
            },
        }
    }
}


class SecurityGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.verified = []
        self.engine = SecurityPolicyEngine(POLICY, lambda evidence: self.verified.append(evidence) or True)
        self.operator = Principal("user-17", ("support_operator",), True)

    def test_allowed_role_tool_and_risk(self):
        result = self.engine.authorize(self.operator, "support-agent", "search_kb", "LOW")
        self.assertTrue(result.allowed)
        self.assertEqual(result.reason, "AUTHORIZED")

    def test_unauthenticated_principal_is_denied(self):
        result = self.engine.authorize(Principal("user-17", ("support_operator",), False),
                                       "support-agent", "search_kb", "LOW")
        self.assertEqual(result.reason, "AUTHENTICATION_REQUIRED")

    def test_missing_role_is_denied(self):
        result = self.engine.authorize(Principal("user-18", ("analyst",), True),
                                       "support-agent", "search_kb", "LOW")
        self.assertEqual(result.reason, "ROLE_NOT_AUTHORIZED")

    def test_unknown_tool_and_risk_are_denied(self):
        self.assertEqual(self.engine.authorize(self.operator, "support-agent", "delete_all", "LOW").reason,
                         "TOOL_NOT_AUTHORIZED")
        self.assertEqual(self.engine.authorize(self.operator, "support-agent", "search_kb", "CRITICAL").reason,
                         "RISK_NOT_AUTHORIZED")

    def test_high_risk_requires_separate_verified_approval(self):
        missing = self.engine.authorize(self.operator, "support-agent", "issue_refund", "HIGH")
        self.assertEqual(missing.reason, "HUMAN_APPROVAL_REQUIRED")
        evidence = ApprovalEvidence("ap-1", "supervisor-2", "support-agent",
                                    "issue_refund", "HIGH", "user-17")
        accepted = self.engine.authorize(self.operator, "support-agent", "issue_refund", "HIGH", evidence)
        self.assertTrue(accepted.allowed)
        self.assertEqual(self.verified, [evidence])

    def test_approval_cannot_be_replayed_for_another_subject_or_tool(self):
        evidence = ApprovalEvidence("ap-1", "supervisor-2", "support-agent",
                                    "issue_refund", "HIGH", "someone-else")
        result = self.engine.authorize(self.operator, "support-agent", "issue_refund", "HIGH", evidence)
        self.assertEqual(result.reason, "APPROVAL_SCOPE_MISMATCH")
        self.assertEqual(self.verified, [])

    def test_approval_fails_closed_without_verifier(self):
        engine = SecurityPolicyEngine(POLICY)
        evidence = ApprovalEvidence("ap-1", "supervisor-2", "support-agent",
                                    "issue_refund", "HIGH", "user-17")
        result = engine.authorize(self.operator, "support-agent", "issue_refund", "HIGH", evidence)
        self.assertEqual(result.reason, "APPROVAL_VERIFIER_UNAVAILABLE")

    def test_invalid_policy_and_wildcards_are_rejected(self):
        with self.assertRaises(SecurityPolicyError):
            SecurityPolicyEngine({"agents": {"*": POLICY["agents"]["support-agent"]}})
        with self.assertRaises(SecurityPolicyError):
            SecurityPolicyEngine({"agents": {"support-agent": {
                "roles": ["*"], "tools": POLICY["agents"]["support-agent"]["tools"]
            }}})
        with self.assertRaises(SecurityPolicyError):
            SecurityPolicyEngine({"agents": {}})

    def test_denials_and_allowances_are_audited(self):
        self.engine.authorize(self.operator, "support-agent", "search_kb", "LOW")
        self.engine.authorize(self.operator, "support-agent", "unknown", "LOW")
        self.assertEqual(len(self.engine.audit_events), 2)
        self.assertEqual(self.engine.audit_events[0]["event"], "AUTHORIZATION_DECISION")
        self.assertTrue(self.engine.audit_events[0]["allowed"])
        self.assertFalse(self.engine.audit_events[1]["allowed"])


if __name__ == "__main__":
    unittest.main()
