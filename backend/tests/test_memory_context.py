import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository

class TestMemoryContext(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.db = SessionLocal()
        self.repo = InteractionRepository(self.db)
        self.created_ids = []

    def tearDown(self):
        for created_id in self.created_ids:
            self.repo.delete(created_id)
        self.db.close()

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_scenario_1_and_4_multi_turn_pronoun_preservation(self, mock_invoke):
        # 1. Log interaction
        # Mock classifier -> LOG_INTERACTION
        # Mock Log tool -> extract details
        mock_classifier_1 = MagicMock()
        mock_classifier_1.content = "LOG_INTERACTION"
        mock_log_1 = MagicMock()
        mock_log_1.content = '{"hcp_name": "Dr. House", "interaction_type": "Call", "sentiment": "Positive"}'
        mock_invoke.side_effect = [mock_classifier_1, mock_log_1]

        response_1 = self.client.post("/chat", json={
            "message": "Called Dr. House today. It went very well."
        })
        self.assertEqual(response_1.status_code, 200)
        data_1 = response_1.json()
        interaction_id = data_1.get("interaction_id")
        self.assertIsNotNone(interaction_id)
        self.created_ids.append(interaction_id)
        
        extracted_1 = data_1.get("extracted_data")
        self.assertEqual(extracted_1["hcp_name"], "Dr. House")
        self.assertEqual(extracted_1["sentiment"], "Positive")

        # 2. Edit doctor using pronoun ("Change his name to Dr. Gregory")
        # Mock classifier -> EDIT_INTERACTION
        # Mock Edit tool -> returns complete object with updated name
        mock_classifier_2 = MagicMock()
        mock_classifier_2.content = "EDIT_INTERACTION"
        mock_edit_2 = MagicMock()
        mock_edit_2.content = '{"hcp_name": "Dr. Gregory", "interaction_type": "Call", "sentiment": "Positive"}'
        mock_invoke.side_effect = [mock_classifier_2, mock_edit_2]

        response_2 = self.client.post("/chat", json={
            "message": "Change his name to Dr. Gregory.",
            "extracted_data": extracted_1,
            "interaction_id": interaction_id
        })
        self.assertEqual(response_2.status_code, 200)
        data_2 = response_2.json()
        self.assertEqual(data_2.get("interaction_id"), interaction_id)
        
        extracted_2 = data_2.get("extracted_data")
        self.assertEqual(extracted_2["hcp_name"], "Dr. Gregory")
        self.assertEqual(extracted_2["sentiment"], "Positive") # preserved

        # 3. Edit sentiment ("Change his sentiment to Negative.")
        # Mock classifier -> EDIT_INTERACTION
        # Mock Edit tool -> returns negative sentiment
        mock_classifier_3 = MagicMock()
        mock_classifier_3.content = "EDIT_INTERACTION"
        mock_edit_3 = MagicMock()
        mock_edit_3.content = '{"hcp_name": "Dr. Gregory", "interaction_type": "Call", "sentiment": "Negative"}'
        mock_invoke.side_effect = [mock_classifier_3, mock_edit_3]

        response_3 = self.client.post("/chat", json={
            "message": "Change his sentiment to Negative.",
            "extracted_data": extracted_2,
            "interaction_id": interaction_id
        })
        self.assertEqual(response_3.status_code, 200)
        data_3 = response_3.json()
        self.assertEqual(data_3.get("interaction_id"), interaction_id)
        
        extracted_3 = data_3.get("extracted_data")
        self.assertEqual(extracted_3["hcp_name"], "Dr. Gregory")
        self.assertEqual(extracted_3["sentiment"], "Negative")

        # 4. Add follow up using pronouns ("Schedule follow up for him next Tuesday.")
        # Mock classifier -> FOLLOW_UP
        # Mock Follow-up tool -> ADD operation
        mock_classifier_4 = MagicMock()
        mock_classifier_4.content = "FOLLOW_UP"
        mock_tool_4 = MagicMock()
        mock_tool_4.content = '{"operation": "ADD", "follow_up_action": "next Tuesday"}'
        mock_invoke.side_effect = [mock_classifier_4, mock_tool_4]

        response_4 = self.client.post("/chat", json={
            "message": "Schedule follow up for him next Tuesday.",
            "extracted_data": extracted_3,
            "interaction_id": interaction_id
        })
        self.assertEqual(response_4.status_code, 200)
        data_4 = response_4.json()
        self.assertEqual(data_4.get("interaction_id"), interaction_id)
        
        extracted_4 = data_4.get("extracted_data")
        self.assertEqual(extracted_4["hcp_name"], "Dr. Gregory")
        self.assertEqual(extracted_4["sentiment"], "Negative") # preserved
        self.assertEqual(extracted_4["follow_up_actions"], ["next Tuesday"])

        # Check DB to confirm only ONE record was created and updated throughout
        self.db.expire_all()
        db_records = self.repo.get_all()
        # Filter for our test records
        relevant_records = [r for r in db_records if r.id in self.created_ids]
        self.assertEqual(len(relevant_records), 1)
        self.assertEqual(relevant_records[0].hcp_name, "Dr. Gregory")
        self.assertEqual(relevant_records[0].sentiment, "Negative")
        self.assertEqual(relevant_records[0].follow_up_actions, ["next Tuesday"])

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_scenario_3_start_another_interaction_clears_context(self, mock_invoke):
        # 1. Log first interaction (Dr. Watson)
        mock_classifier_1 = MagicMock()
        mock_classifier_1.content = "LOG_INTERACTION"
        mock_log_1 = MagicMock()
        mock_log_1.content = '{"hcp_name": "Dr. Watson", "interaction_type": "Meeting"}'
        mock_invoke.side_effect = [mock_classifier_1, mock_log_1]

        response_1 = self.client.post("/chat", json={
            "message": "Met Dr. Watson today."
        })
        self.assertEqual(response_1.status_code, 200)
        data_1 = response_1.json()
        first_id = data_1.get("interaction_id")
        self.assertIsNotNone(first_id)
        self.created_ids.append(first_id)

        # 2. Log second interaction starting with trigger prefix ("Met Dr. Alice yesterday.")
        # This should trigger clearing the context, starting a new log.
        mock_classifier_2 = MagicMock()
        mock_classifier_2.content = "LOG_INTERACTION"
        mock_log_2 = MagicMock()
        mock_log_2.content = '{"hcp_name": "Dr. Alice", "interaction_type": "Meeting"}'
        mock_invoke.side_effect = [mock_classifier_2, mock_log_2]

        response_2 = self.client.post("/chat", json={
            "message": "Met Dr. Alice yesterday.",
            "extracted_data": data_1["extracted_data"],
            "interaction_id": first_id
        })
        self.assertEqual(response_2.status_code, 200)
        data_2 = response_2.json()
        second_id = data_2.get("interaction_id")
        
        # Verify a new interaction ID was generated (not reusing first_id)
        self.assertIsNotNone(second_id)
        self.assertNotEqual(first_id, second_id)
        self.created_ids.append(second_id)

        self.assertEqual(data_2["extracted_data"]["hcp_name"], "Dr. Alice")
        
        # Verify both records exist in DB independently
        self.db.expire_all()
        rec_1 = self.repo.get_by_id(first_id)
        rec_2 = self.repo.get_by_id(second_id)
        self.assertIsNotNone(rec_1)
        self.assertIsNotNone(rec_2)
        self.assertEqual(rec_1.hcp_name, "Dr. Watson")
        self.assertEqual(rec_2.hcp_name, "Dr. Alice")

    @patch("langchain_core.runnables.RunnableSequence.invoke")
    def test_scenario_5_many_turns_no_duplicates(self, mock_invoke):
        # Log first interaction
        mock_classifier = MagicMock()
        mock_classifier.content = "LOG_INTERACTION"
        mock_log = MagicMock()
        mock_log.content = '{"hcp_name": "Dr. Ten", "interaction_type": "Call"}'
        mock_invoke.side_effect = [mock_classifier, mock_log]

        response = self.client.post("/chat", json={"message": "Spoke to Dr. Ten on call."})
        data = response.json()
        interaction_id = data.get("interaction_id")
        self.created_ids.append(interaction_id)

        # Execute 10 subsequent edit turns on the SAME interaction
        current_data = data["extracted_data"]
        for i in range(10):
            mock_classifier_edit = MagicMock()
            mock_classifier_edit.content = "EDIT_INTERACTION"
            mock_edit = MagicMock()
            # Rotate outcomes text
            mock_edit.content = f'{{"hcp_name": "Dr. Ten", "interaction_type": "Call", "outcomes": "Turn {i}"}}'
            mock_invoke.side_effect = [mock_classifier_edit, mock_edit]

            response = self.client.post("/chat", json={
                "message": f"Change outcomes to Turn {i}",
                "extracted_data": current_data,
                "interaction_id": interaction_id
            })
            self.assertEqual(response.status_code, 200)
            current_data = response.json()["extracted_data"]

        # Verify only 1 row was created in DB for Dr. Ten
        self.db.expire_all()
        db_records = self.repo.get_all()
        relevant_records = [r for r in db_records if r.id == interaction_id]
        self.assertEqual(len(relevant_records), 1)
        self.assertEqual(relevant_records[0].outcomes, "Turn 9")

if __name__ == '__main__':
    unittest.main()
