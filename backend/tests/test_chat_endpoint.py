import sys
import os
import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Append the app folder to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

class TestChatEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_chat_greeting_flow(self, mock_invoke):
        # Greetings should bypass LLM call and return a friendly greeting response immediately
        response = self.client.post("/chat", json={"message": "Hello"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "UNKNOWN")
        self.assertIn("help", data["response"].lower())
        mock_invoke.assert_not_called()

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_chat_invalid_payload_fallback(self, mock_invoke):
        # If LLM returns bad data, it should gracefully fall back (use non-trigger message)
        mock_response = MagicMock()
        mock_response.content = "Malformed response content"
        mock_invoke.return_value = mock_response

        response = self.client.post("/chat", json={
            "message": "Change outcomes to Turn 1.", 
            "extracted_data": {"hcp_name": "Dr. Smith"}
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Fallback preserves previous data
        self.assertEqual(data["extracted_data"]["hcp_name"], "Dr. Smith")

    def test_incomplete_edit_punctuation(self):
        # Incomplete edit ending with punctuation should return clarification question
        response = self.client.post("/chat", json={
            "message": "Change the doctor's name.",
            "extracted_data": {"hcp_name": "Dr. Smith"}
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["selected_tool"], "edit_interaction_tool")
        self.assertEqual(data["response"], "What would you like to change the doctor's name to?")
        self.assertEqual(data["extracted_data"]["hcp_name"], "Dr. Smith")

    def test_punctuation_only_help(self):
        # Punctuation-only messages should bypass LLM and return help response
        response = self.client.post("/chat", json={"message": "....."})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "UNKNOWN")
        self.assertIn("couldn't understand", data["response"].lower())
        self.assertIn("log an interaction", data["response"].lower())

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_capability_help(self, mock_invoke):
        # Capability question should trigger UNKNOWN and return help response
        mock_response = MagicMock()
        mock_response.content = "UNKNOWN"
        mock_invoke.return_value = mock_response

        response = self.client.post("/chat", json={"message": "What can you do?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["intent"], "UNKNOWN")
        self.assertIn("couldn't understand", data["response"].lower())
        self.assertIn("log an interaction", data["response"].lower())

if __name__ == '__main__':
    unittest.main()
