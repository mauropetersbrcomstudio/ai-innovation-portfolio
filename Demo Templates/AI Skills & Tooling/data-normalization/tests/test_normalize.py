import unittest

from normalize import normalize_rows


class NormalizeRowsTests(unittest.TestCase):
    def test_explicit_trim_rename_case_null_and_date_rules(self):
        rows = [{"full_name": " Ana Silva ", "email": " ANA@EXAMPLE.COM ", "signup_date": "17/11/2026", "notes": " n/a "}]
        config = {
            "trim_fields": ["full_name", "email", "signup_date", "notes"],
            "rename": {"full_name": "name"},
            "case": {"email": "lower"},
            "dates": {"signup_date": {"input_formats": ["%d/%m/%Y"], "output_format": "%Y-%m-%d"}},
        }
        result, report = normalize_rows(rows, config)
        self.assertEqual(result[0], {"name": "Ana Silva", "email": "ana@example.com", "signup_date": "2026-11-17", "notes": ""})
        self.assertEqual(report["rows_processed"], 1)
        self.assertEqual(report["changed_cells_by_field"]["email"], 1)

    def test_unconfigured_fields_are_preserved(self):
        rows = [{"code": " A-01 ", "description": "Mixed Case"}]
        result, _ = normalize_rows(rows, {})
        self.assertEqual(result, rows)

    def test_invalid_date_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Invalid date"):
            normalize_rows([{"date": "not-a-date"}], {"dates": {"date": {"input_formats": ["%Y-%m-%d"]}}})

    def test_unsupported_case_rule_fails(self):
        with self.assertRaisesRegex(ValueError, "Unsupported case rule"):
            normalize_rows([{"name": "Ana"}], {"case": {"name": "snake"}})

    def test_rename_collision_fails(self):
        with self.assertRaisesRegex(ValueError, "rename collision"):
            normalize_rows([{"first": "A", "last": "B"}], {"rename": {"first": "name", "last": "name"}})

    def test_null_matching_is_case_insensitive(self):
        result, _ = normalize_rows([{"value": " N/A "}], {"trim_fields": ["value"]})
        self.assertEqual(result[0]["value"], "")


if __name__ == "__main__":
    unittest.main()
