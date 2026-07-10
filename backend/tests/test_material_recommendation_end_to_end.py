import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState, Intent

class TestMaterialRecommendationEndToEnd(unittest.TestCase):

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_recommendation_diabetes(self, mock_invoke):
        # 1) "Recommend brochure for diabetes" -> Intent.MATERIAL_RECOMMENDATION -> material_recommendation_tool
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"query": "diabetes"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Recommend brochure for diabetes",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.MATERIAL_RECOMMENDATION)
        self.assertEqual(result["selected_tool"], "material_recommendation_tool")
        self.assertIn("Diabetes Clinical Brochure", result["recommended_materials"])
        self.assertIn("Diabetes Patient Education Guide", result["recommended_materials"])
        self.assertIn("Latest Diabetes Study", result["recommended_materials"])
        self.assertIn("Diabetes Clinical Brochure", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_recommendation_product_x(self, mock_invoke):
        # 2) "Need Product X brochure"
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"query": "product x"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Need Product X brochure",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.MATERIAL_RECOMMENDATION)
        self.assertEqual(result["selected_tool"], "material_recommendation_tool")
        self.assertIn("Product X Brochure", result["recommended_materials"])
        self.assertIn("Product X Clinical Trial Summary", result["recommended_materials"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_recommendation_hypertension(self, mock_invoke):
        # 3) "Show hypertension publications"
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"query": "hypertension"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Show hypertension publications",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.MATERIAL_RECOMMENDATION)
        self.assertEqual(result["selected_tool"], "material_recommendation_tool")
        self.assertIn("Hypertension Guideline", result["recommended_materials"])
        self.assertIn("Blood Pressure Management Guide", result["recommended_materials"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_recommendation_unknown(self, mock_invoke):
        # 4) "Unknown product" -> no match found response
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"query": "unknown product"}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Recommend brochure for unknown product",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.MATERIAL_RECOMMENDATION)
        self.assertEqual(result["selected_tool"], "material_recommendation_tool")
        self.assertEqual(result["recommended_materials"], [])
        self.assertIn("I couldn't find matching materials", result["response"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_recommendation_general(self, mock_invoke):
        # 5) "Recommend brochure" (General recommendation request)
        mock_classifier_response = MagicMock()
        mock_classifier_response.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool_response = MagicMock()
        mock_tool_response.content = '{"query": ""}'
        
        mock_invoke.side_effect = [mock_classifier_response, mock_tool_response]

        state: AgentState = {
            "user_input": "Recommend brochure",
            "intent": None,
            "extracted_data": {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }

        result = app_graph.invoke(state)
        self.assertEqual(result["intent"], Intent.MATERIAL_RECOMMENDATION)
        self.assertEqual(result["selected_tool"], "material_recommendation_tool")
        self.assertEqual(result["recommended_materials"], [])
        self.assertIn("I couldn't find matching materials", result["response"])

if __name__ == '__main__':
    unittest.main()
