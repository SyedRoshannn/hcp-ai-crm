import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Append the app folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent

class TestLogInteractionEndToEnd(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_log_interaction_success(self, mock_invoke):
        # Mock LLM to return valid JSON
        mock_response = MagicMock()
        mock_response.content = '{"hcp_name": "Dr. Smith", "interaction_type": "Meeting", "topics_discussed": ["Product X"]}'
        
        # In nodes.py, first chain.invoke classifies intent, second chain.invoke extracts details.
        # We need mock_invoke side effect to handle both:
        # First call: router_node classification ("LOG_INTERACTION")
        # Second call: extraction ("{"hcp_name": "Dr. Smith", ...}")
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "LOG_INTERACTION"
        
        mock_invoke.side_effect = [mock_classifier_response, mock_response]

        state: AgentState = {
            "user_input": "Met Dr. Smith to discuss Product X.",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": []
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.LOG_INTERACTION)
        self.assertEqual(result["selected_tool"], "log_interaction_tool")
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith")
        self.assertEqual(result["extracted_data"]["topics_discussed"], ["Product X"])
        self.assertEqual(result["response"], "✅ Interaction logged successfully.")

if __name__ == '__main__':
    unittest.main()
