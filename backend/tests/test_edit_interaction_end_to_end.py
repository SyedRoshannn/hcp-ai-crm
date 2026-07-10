import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Append the app folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent

class TestEditInteractionEndToEnd(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_valid_edit_flow(self, mock_invoke):
        # First call: router classification -> "EDIT_INTERACTION"
        # Second call: edit tool LLM -> returns updated object JSON
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "EDIT_INTERACTION"
        
        mock_edit_response = MagicMock()
        mock_edit_response.content = '{"hcp_name": "Dr. John", "interaction_type": "Meeting", "date": "today"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_edit_response]

        state: AgentState = {
            "user_input": "Change the doctor's name to Dr. John.",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "interaction_type": "Meeting",
                "date": "today"
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": []
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.EDIT_INTERACTION)
        self.assertEqual(result["selected_tool"], "edit_interaction_tool")
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. John")
        self.assertEqual(result["extracted_data"]["date"], "today") # preserved
        self.assertEqual(result["response"], "✅ Interaction updated successfully.")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_incomplete_edit_flow(self, mock_invoke):
        # Incomplete edit: "change the doctor's name"
        # First call: router classification -> "EDIT_INTERACTION"
        # Second call should NEVER happen because of validation check bypass
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "EDIT_INTERACTION"
        mock_invoke.return_value = mock_classifier_response

        state: AgentState = {
            "user_input": "change the doctor's name",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith"
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": []
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.EDIT_INTERACTION)
        self.assertEqual(result["selected_tool"], "edit_interaction_tool")
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith") # unchanged
        self.assertEqual(result["response"], "What would you like to change the doctor's name to?")
        # Verify that mock_invoke was only called once (for intent routing), bypassing edit LLM
        self.assertEqual(mock_invoke.call_count, 1)

if __name__ == '__main__':
    unittest.main()
