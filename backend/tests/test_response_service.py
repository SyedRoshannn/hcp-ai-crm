import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.response_service import generate_ai_response

class TestResponseService(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_generate_ai_response_log(self, mock_invoke):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.content = "I've successfully logged your interaction with Dr. Smith."
        mock_invoke.return_value = mock_response

        user_input = "Met Dr. Smith today."
        intent = "LOG_INTERACTION"
        extracted_data = {"hcp_name": "Dr. Smith", "interaction_type": "Meeting"}
        tool_response = "✅ Interaction logged successfully."

        result = generate_ai_response(
            user_input=user_input,
            intent=intent,
            extracted_data=extracted_data,
            tool_response=tool_response
        )

        self.assertEqual(result, "I've successfully logged your interaction with Dr. Smith.")
        mock_invoke.assert_called_once()

    def test_generate_ai_response_clarification_bypass(self):
        # Clarification questions ending with ? should be returned directly without calling LLM
        user_input = "Change doctor's name"
        intent = "EDIT_INTERACTION"
        extracted_data = {}
        tool_response = "What would you like to change the doctor's name to?"

        result = generate_ai_response(
            user_input=user_input,
            intent=intent,
            extracted_data=extracted_data,
            tool_response=tool_response
        )

        self.assertEqual(result, tool_response)

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_generate_ai_response_failure_fallback(self, mock_invoke):
        # On LLM exception, fallback should return the raw tool_response
        mock_invoke.side_effect = Exception("LLM connection error")

        user_input = "Met Dr. Smith."
        intent = "LOG_INTERACTION"
        extracted_data = {}
        tool_response = "✅ Interaction logged successfully."

        result = generate_ai_response(
            user_input=user_input,
            intent=intent,
            extracted_data=extracted_data,
            tool_response=tool_response
        )

        self.assertEqual(result, tool_response)

if __name__ == '__main__':
    unittest.main()
