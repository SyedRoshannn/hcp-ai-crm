import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Append the app folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent

class TestVoiceSummaryEndToEnd(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_voice_summary_success(self, mock_invoke):
        # First call: router classification -> "VOICE_SUMMARY"
        # Second call: extraction LLM -> returns parsed JSON
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "VOICE_SUMMARY"
        
        mock_extraction_response = MagicMock()
        mock_extraction_response.content = '{"hcp_name": "Dr. Alice", "topics_discussed": ["Product Z"]}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_extraction_response]

        state: AgentState = {
            "user_input": "Met Dr. Alice yesterday. Discussed Product Z.",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": []
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.VOICE_SUMMARY)
        self.assertEqual(result["selected_tool"], "voice_summary_tool")
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Alice")
        self.assertEqual(result["extracted_data"]["topics_discussed"], ["Product Z"])
        self.assertEqual(result["response"], "✅ Voice note summarized successfully.")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_voice_summary_no_transcript(self, mock_invoke):
        # Empty voice summary command: "Summarize this voice note."
        # First call: router classification -> "VOICE_SUMMARY"
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "VOICE_SUMMARY"
        mock_invoke.return_value = mock_classifier_response

        state: AgentState = {
            "user_input": "Summarize this voice note.",
            "intent": None,
            "extracted_data": {"hcp_name": "Dr. Smith"},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": []
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.VOICE_SUMMARY)
        self.assertEqual(result["selected_tool"], "voice_summary_tool")
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith") # preserved
        self.assertIn("upload a voice note", result["response"])
        self.assertEqual(mock_invoke.call_count, 1)

if __name__ == '__main__':
    unittest.main()
