import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent

class TestFollowUpEndToEnd(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_add_follow_up(self, mock_invoke):
        # 1) Add follow-up (when list is empty)
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "ADD", "follow_up_action": "next Monday"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Schedule a follow up next Monday.",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "sentiment": "Positive",
                "topics_discussed": ["Product X"],
                "materials_shared": ["Brochure Y"],
                "follow_up_actions": []
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.FOLLOW_UP)
        self.assertEqual(result["selected_tool"], "follow_up_tool")
        # Assert action is added
        self.assertEqual(result["extracted_data"]["follow_up_actions"], ["next Monday"])
        # Assert response is scheduled successfully
        self.assertIn("scheduled successfully", result["response"])
        self.assertIn("next Monday", result["response"])
        # Assert baseline fields preserved
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith")
        self.assertEqual(result["extracted_data"]["sentiment"], "Positive")
        self.assertEqual(result["extracted_data"]["topics_discussed"], ["Product X"])
        self.assertEqual(result["extracted_data"]["materials_shared"], ["Brochure Y"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_append_follow_up(self, mock_invoke):
        # 2) Append follow-up
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "ADD", "follow_up_action": "Call Dr Smith next Friday"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Remind me to call Dr Smith next Friday.",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": ["Next Monday"]
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["extracted_data"]["follow_up_actions"], ["Next Monday", "Call Dr Smith next Friday"])
        self.assertIn("added successfully", result["response"])
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_update_follow_up(self, mock_invoke):
        # 3) Update follow-up
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "UPDATE", "follow_up_action": "next Wednesday"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Update follow up to next Wednesday.",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": ["next Monday"]
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["extracted_data"]["follow_up_actions"], ["next Wednesday"])
        self.assertIn("updated successfully", result["response"])
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_remove_follow_up(self, mock_invoke):
        # 4) Remove follow-up
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "REMOVE", "follow_up_action": ""}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Remove follow up.",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": ["next Monday"]
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["extracted_data"]["follow_up_actions"], [])
        self.assertIn("removed successfully", result["response"])
        self.assertEqual(result["extracted_data"]["hcp_name"], "Dr. Smith")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_view_follow_up(self, mock_invoke):
        # 5) View follow-up
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "VIEW", "follow_up_action": ""}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "What is my follow up?",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": ["next Monday"]
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["extracted_data"]["follow_up_actions"], ["next Monday"])
        self.assertIn("Current follow-up", result["response"])
        self.assertIn("next Monday", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_empty_view_follow_up(self, mock_invoke):
        # 6) Empty follow-up view
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"operation": "VIEW", "follow_up_action": ""}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "When is the follow up?",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": []
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["extracted_data"]["follow_up_actions"], [])
        self.assertIn("No follow-up has been scheduled yet", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_invalid_date_or_incomplete(self, mock_invoke):
        # 7) Incomplete/invalid date -> triggers clarification question
        state: AgentState = {
            "user_input": "Schedule a follow up",
            "intent": None,
            "extracted_data": {
                "hcp_name": "Dr. Smith"
            },
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "FOLLOW_UP"
        mock_invoke.return_value = mock_classifier_response

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.FOLLOW_UP)
        self.assertEqual(result["selected_tool"], "follow_up_tool")
        self.assertEqual(result["response"], "Which date would you like to schedule the follow-up for?")
        self.assertEqual(mock_invoke.call_count, 1)

if __name__ == '__main__':
    unittest.main()
