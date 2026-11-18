import unittest

from json_contract_validator import validate_json


class JsonContractValidatorTests(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "type": "object",
            "required": ["request_id", "priority", "active", "tags"],
            "additionalProperties": False,
            "properties": {
                "request_id": {"type": "string", "minLength": 3},
                "priority": {"type": "integer", "minimum": 1, "maximum": 5},
                "active": {"type": "boolean"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
        }

    def test_valid_object(self):
        report = validate_json(
            {"request_id": "REQ-1", "priority": 3, "active": True, "tags": ["ops"]},
            self.schema,
        )
        self.assertTrue(report["valid"])
        self.assertEqual(report["error_count"], 0)

    def test_required_and_additional_properties(self):
        report = validate_json(
            {"priority": 6, "active": False, "tags": [], "extra": "no"},
            self.schema,
        )
        self.assertFalse(report["valid"])
        codes = {error["code"] for error in report["errors"]}
        self.assertIn("required", codes)
        self.assertIn("additional_property", codes)
        self.assertIn("maximum", codes)

    def test_boolean_is_not_integer(self):
        report = validate_json(
            {"request_id": "REQ", "priority": True, "active": True, "tags": []},
            self.schema,
        )
        self.assertIn("type_mismatch", {error["code"] for error in report["errors"]})

    def test_nested_array_item_path(self):
        report = validate_json(
            {"request_id": "REQ", "priority": 2, "active": True, "tags": ["ok", 7]},
            self.schema,
        )
        self.assertIn("$.tags[1]", [error["path"] for error in report["errors"]])

    def test_enum_and_string_length(self):
        schema = {"type": "string", "minLength": 2, "enum": ["open", "closed"]}
        report = validate_json("x", schema)
        codes = {error["code"] for error in report["errors"]}
        self.assertIn("min_length", codes)
        self.assertIn("enum_mismatch", codes)

    def test_root_type_mismatch(self):
        report = validate_json([], {"type": "object"})
        self.assertEqual(report["errors"][0]["code"], "type_mismatch")

    def test_invalid_schema_root(self):
        with self.assertRaises(ValueError):
            validate_json({}, {})


if __name__ == "__main__":
    unittest.main()
