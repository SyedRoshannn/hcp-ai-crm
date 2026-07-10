import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository

class TestHistorySearchEndToEnd(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        self.repo = InteractionRepository(self.db)
        self.created_ids = []
        
        # Populate mock interaction records
        self.rec1 = self.repo.create_interaction({
            "hcp_name": "Dr. Alice",
            "interaction_type": "Meeting",
            "date": "today",
            "sentiment": "Positive",
            "topics_discussed": ["Product X"],
            "materials_shared": ["Brochure A"],
            "follow_up_actions": ["Call next week"]
        })
        self.created_ids.append(self.rec1.id)
        
        self.rec2 = self.repo.create_interaction({
            "hcp_name": "Dr. Bob",
            "interaction_type": "Call",
            "date": "yesterday",
            "sentiment": "Neutral",
            "topics_discussed": ["Product Y"],
            "materials_shared": [],
            "follow_up_actions": []
        })
        self.created_ids.append(self.rec2.id)

    def tearDown(self):
        for cid in self.created_ids:
            self.repo.delete(cid)
        self.db.close()

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_show_all_interactions(self, mock_invoke):
        # 1. Show all interactions
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"all": "true"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show all interactions",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.HISTORY_SEARCH)
        self.assertEqual(result["selected_tool"], "history_search_tool")
        self.assertIn("Dr. Alice", result["response"])
        self.assertIn("Dr. Bob", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_doctor_search(self, mock_invoke):
        # 2. Doctor search
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"doctor_name": "Alice"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show meetings with Dr. Alice",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("Dr. Alice", result["response"])
        self.assertNotIn("Dr. Bob", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_date_search(self, mock_invoke):
        # 3. Date search
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"date": "yesterday"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show interactions from yesterday",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("Dr. Bob", result["response"])
        self.assertNotIn("Dr. Alice", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_sentiment_search(self, mock_invoke):
        # 4. Sentiment search
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"sentiment": "Positive"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show positive interactions",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("Dr. Alice", result["response"])
        self.assertNotIn("Dr. Bob", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_latest_interaction(self, mock_invoke):
        # 5. Latest interaction
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"latest": "true"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show the latest interaction",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        # Latest should be rec2 because it was created last
        self.assertIn("Dr. Bob", result["response"])
        self.assertNotIn("Dr. Alice", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_product_search(self, mock_invoke):
        # 6. Product search
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"topic": "Product X"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show interactions containing Product X",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("Dr. Alice", result["response"])
        self.assertNotIn("Dr. Bob", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_followup_search(self, mock_invoke):
        # 7. Follow-up search
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"has_followup": "true"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show interactions with follow-ups",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("Dr. Alice", result["response"])
        self.assertNotIn("Dr. Bob", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_empty_search(self, mock_invoke):
        # 8. Invalid search / no results
        mock_classifier = MagicMock()
        mock_classifier.content = "HISTORY_SEARCH"
        mock_tool = MagicMock()
        mock_tool.content = '{"doctor_name": "Unknown"}'
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        state: AgentState = {
            "user_input": "Show meetings with Dr. Unknown",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertIn("I couldn't find any interaction logs matching", result["response"])

if __name__ == '__main__':
    unittest.main()
