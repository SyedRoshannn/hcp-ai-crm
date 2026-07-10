import sys
import os
import unittest

# Append the app folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.structured_parser import parse_llm_json, normalize_dict, safe_interaction_parse

class TestStructuredParser(unittest.TestCase):
    def setUp(self):
        self.string_fields = ['hcp_name', 'interaction_type', 'date', 'time', 'sentiment', 'outcomes']
        self.list_fields = ['attendees', 'topics_discussed', 'materials_shared', 'samples_distributed', 'follow_up_actions']
        self.fallback = {
            "hcp_name": "Dr. Smith",
            "interaction_type": "Meeting",
            "date": "today",
            "attendees": ["Dr. Smith"]
        }

    def test_stage_1_plain_json(self):
        raw = '{"hcp_name": "Dr. House", "interaction_type": "Meeting"}'
        parsed = parse_llm_json(raw)
        self.assertEqual(parsed["hcp_name"], "Dr. House")
        self.assertEqual(parsed["interaction_type"], "Meeting")

    def test_stage_2_markdown_fenced(self):
        raw = 'Some text before\n```json\n{"hcp_name": "Dr. Lisa", "topics_discussed": ["Product X"]}\n```\nSome text after'
        parsed = parse_llm_json(raw)
        self.assertEqual(parsed["hcp_name"], "Dr. Lisa")
        self.assertEqual(parsed["topics_discussed"], ["Product X"])

    def test_stage_3_cleanup_trailing_commas_and_quotes(self):
        # Trailing commas and single quotes
        raw = "{'hcp_name': 'Dr. Alice', 'attendees': ['Dr. Bob',],}"
        parsed = parse_llm_json(raw)
        self.assertEqual(parsed["hcp_name"], "Dr. Alice")
        self.assertEqual(parsed["attendees"], ["Dr. Bob"])

    def test_normalization_empty_and_null_lists(self):
        raw_dict = {
            "hcp_name": "Dr. Watson",
            "topics_discussed": "",          # Empty string -> []
            "materials_shared": None,        # None -> []
            "samples_distributed": "Sample A" # Single string -> ["Sample A"]
        }
        normalized, performed = normalize_dict(raw_dict, self.string_fields, self.list_fields)
        self.assertTrue(performed)
        self.assertEqual(normalized["topics_discussed"], [])
        self.assertEqual(normalized["materials_shared"], [])
        self.assertEqual(normalized["samples_distributed"], ["Sample A"])
        self.assertEqual(normalized["hcp_name"], "Dr. Watson")

    def test_stage_4_fallback_handling(self):
        # Completely invalid JSON -> should trigger fallback without throwing exceptions
        invalid_raw = "This is not JSON at all."
        normalized, warning = safe_interaction_parse(invalid_raw, self.fallback, self.string_fields, self.list_fields)
        self.assertTrue("Failed to parse" in warning)
        self.assertEqual(normalized["hcp_name"], "Dr. Smith")
        self.assertEqual(normalized["interaction_type"], "Meeting")
        self.assertEqual(normalized["attendees"], ["Dr. Smith"])

if __name__ == '__main__':
    unittest.main()
