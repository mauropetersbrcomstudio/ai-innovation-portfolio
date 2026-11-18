import unittest

from validate_policy import validate_policy


class PolicyValidatorTests(unittest.TestCase):
    def test_valid_low_risk_policy(self):
        result = validate_policy({"agents": [{
            "name": "classifier", "risk": "LOW", "allowed_tools": ["classify"], "max_steps": 5
        }]})
        self.assertTrue(result["valid"])

    def test_high_risk_requires_approval(self):
        result = validate_policy({"agents": [{
            "name": "operator", "risk": "HIGH", "allowed_tools": ["update"], "approval_required_for": [],
            "max_steps": 5
        }]})
        self.assertFalse(result["valid"])
        self.assertTrue(any("must require approval" in error for error in result["errors"]))

    def test_wildcard_tools_rejected(self):
        result = validate_policy({"agents": [{
            "name": "agent", "risk": "LOW", "allowed_tools": ["*"], "max_steps": 5
        }]})
        self.assertFalse(result["valid"])

    def test_approval_tool_must_be_allowlisted(self):
        result = validate_policy({"agents": [{
            "name": "agent", "risk": "LOW", "allowed_tools": ["read"],
            "approval_required_for": ["delete"], "max_steps": 5
        }]})
        self.assertFalse(result["valid"])

    def test_duplicate_agent_names_rejected(self):
        item = {"name": "same", "risk": "LOW", "allowed_tools": [], "max_steps": 1}
        result = validate_policy({"agents": [item, item]})
        self.assertTrue(any("Duplicate agent name" in error for error in result["errors"]))

    def test_step_limit_enforced(self):
        result = validate_policy({"agents": [{
            "name": "agent", "risk": "LOW", "allowed_tools": [], "max_steps": 1000
        }]})
        self.assertFalse(result["valid"])

    def test_non_object_policy_rejected(self):
        self.assertFalse(validate_policy([])["valid"])


if __name__ == "__main__":
    unittest.main()
