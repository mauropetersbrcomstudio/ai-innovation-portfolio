import unittest

from document_intelligence import analyze_document


class DocumentIntelligenceTests(unittest.TestCase):
    def test_extracts_headings_key_values_and_entities(self):
        source = """# Service Agreement
Client: Example Ltd
Date: 2026-11-17
Contact: ops@example.test
Website: https://example.test/docs
Fee: USD 1,250.00
"""
        result = analyze_document(source, "agreement.md")
        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(result["headings"][0]["text"], "Service Agreement")
        self.assertEqual(result["headings"][0]["level"], 1)
        self.assertEqual(result["key_value_pairs"][0]["key"], "Client")
        self.assertEqual(result["entities"]["emails"], ["ops@example.test"])
        self.assertEqual(result["entities"]["iso_dates"], ["2026-11-17"])
        self.assertEqual(result["entities"]["urls"], ["https://example.test/docs"])
        self.assertEqual(result["entities"]["currency_mentions"], ["USD 1,250.00"])

    def test_deduplicates_entity_matches(self):
        result = analyze_document("a@example.test\na@example.test")
        self.assertEqual(result["entities"]["emails"], ["a@example.test"])

    def test_counts_lines_words_and_characters(self):
        text = "# Title\n\nHello world."
        stats = analyze_document(text)["statistics"]
        self.assertEqual(stats["character_count"], len(text))
        self.assertEqual(stats["line_count"], 3)
        self.assertEqual(stats["nonempty_line_count"], 2)
        self.assertEqual(stats["word_count"], 3)

    def test_empty_document(self):
        result = analyze_document("")
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["statistics"]["line_count"], 0)
        self.assertEqual(result["headings"], [])

    def test_ignores_non_key_value_and_non_heading_lines(self):
        result = analyze_document("Plain paragraph\n- list item\n## Heading")
        self.assertEqual(len(result["headings"]), 1)
        self.assertEqual(result["key_value_pairs"], [])

    def test_preserves_multiple_values_and_line_numbers(self):
        result = analyze_document("Intro\nOwner: Ana\nOwner: Bruno")
        self.assertEqual([item["line"] for item in result["key_value_pairs"]], [2, 3])
        self.assertEqual([item["value"] for item in result["key_value_pairs"]], ["Ana", "Bruno"])


if __name__ == "__main__":
    unittest.main()
