import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository

class TestPersistenceIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        self.repo = InteractionRepository(self.db)
        self.created_ids = []

    def tearDown(self):
        # Clean up database records created during integration tests
        for created_id in self.created_ids:
            self.repo.delete(created_id)
        self.db.close()

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_log_persists_to_db(self, mock_invoke):
        # Router intent classification -> LOG_INTERACTION
        mock_classifier = MagicMock()
        mock_classifier.content = "LOG_INTERACTION"
        
        mock_log = MagicMock()
        mock_log.content = '{"hcp_name": "Dr. Persistence Log", "interaction_type": "Meeting"}'
        
        mock_invoke.side_effect = [mock_classifier, mock_log]

        response = self.client.post("/chat", json={
            "message": "Met Dr. Persistence Log today."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        interaction_id = data.get("interaction_id")
        self.assertIsNotNone(interaction_id)
        self.created_ids.append(interaction_id)

        # Retrieve row from DB and verify creation
        db_record = self.repo.get_by_id(interaction_id)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.hcp_name, "Dr. Persistence Log")
        self.assertEqual(db_record.interaction_type, "Meeting")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_edit_persists_to_db(self, mock_invoke):
        # First manually create a database record
        hcp_data = {
            "hcp_name": "Dr. Original Name",
            "interaction_type": "Meeting"
        }
        db_interaction = self.repo.create_interaction(hcp_data)
        interaction_id = db_interaction.id
        self.created_ids.append(interaction_id)

        # Mock LLM calls
        mock_classifier = MagicMock()
        mock_classifier.content = "EDIT_INTERACTION"
        
        mock_edit = MagicMock()
        mock_edit.content = '{"hcp_name": "Dr. Updated Name", "interaction_type": "Meeting"}'
        
        mock_invoke.side_effect = [mock_classifier, mock_edit]

        response = self.client.post("/chat", json={
            "message": "Change the doctor's name to Dr. Updated Name.",
            "extracted_data": {
                "hcp_name": "Dr. Original Name",
                "interaction_type": "Meeting"
            },
            "interaction_id": interaction_id
        })
        self.assertEqual(response.status_code, 200)

        # Expire session cache to force reload from DB
        self.db.expire_all()

        # Retrieve row and verify update in database
        db_record = self.repo.get_by_id(interaction_id)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.hcp_name, "Dr. Updated Name")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_follow_up_persists_to_db(self, mock_invoke):
        # First manually create a database record
        hcp_data = {
            "hcp_name": "Dr. Smith",
            "follow_up_actions": []
        }
        db_interaction = self.repo.create_interaction(hcp_data)
        interaction_id = db_interaction.id
        self.created_ids.append(interaction_id)

        # Classifier -> FOLLOW_UP
        mock_classifier = MagicMock()
        mock_classifier.content = "FOLLOW_UP"
        
        mock_tool = MagicMock()
        mock_tool.content = '{"operation": "ADD", "follow_up_action": "next Wednesday"}'
        
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        response = self.client.post("/chat", json={
            "message": "Schedule a follow up next Wednesday.",
            "extracted_data": {
                "hcp_name": "Dr. Smith",
                "follow_up_actions": []
            },
            "interaction_id": interaction_id
        })
        self.assertEqual(response.status_code, 200)

        # Expire session cache to force reload from DB
        self.db.expire_all()

        # Retrieve row and verify update in database
        db_record = self.repo.get_by_id(interaction_id)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.follow_up_actions, ["next Wednesday"])
        self.assertEqual(db_record.hcp_name, "Dr. Smith") # preserved

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_voice_summary_persists_to_db(self, mock_invoke):
        # Classifier -> VOICE_SUMMARY
        mock_classifier = MagicMock()
        mock_classifier.content = "VOICE_SUMMARY"
        
        mock_tool = MagicMock()
        mock_tool.content = '{"hcp_name": "Dr. Alice Voice", "topics_discussed": ["Product Z"]}'
        
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        response = self.client.post("/chat", json={
            "message": "Summarize this voice note: Met Dr. Alice yesterday and discussed Product Z."
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()

        interaction_id = data.get("interaction_id")
        self.assertIsNotNone(interaction_id)
        self.created_ids.append(interaction_id)

        # Retrieve row and verify creation in database
        db_record = self.repo.get_by_id(interaction_id)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record.hcp_name, "Dr. Alice Voice")
        self.assertEqual(db_record.topics_discussed, ["Product Z"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_material_recommendation_does_not_persist_to_db(self, mock_invoke):
        # Get baseline row count
        initial_count = len(self.repo.get_all())

        # Classifier -> MATERIAL_RECOMMENDATION
        mock_classifier = MagicMock()
        mock_classifier.content = "MATERIAL_RECOMMENDATION"
        
        mock_tool = MagicMock()
        mock_tool.content = '{"query": "diabetes"}'
        
        mock_invoke.side_effect = [mock_classifier, mock_tool]

        response = self.client.post("/chat", json={
            "message": "Recommend brochure for diabetes"
        })
        self.assertEqual(response.status_code, 200)

        # Verify database row count remains unchanged
        post_count = len(self.repo.get_all())
        self.assertEqual(initial_count, post_count)

if __name__ == '__main__':
    unittest.main()
