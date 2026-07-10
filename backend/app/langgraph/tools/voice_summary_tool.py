from app.langgraph.state import AgentState
from app.services.interaction_service import extract_interaction_details, should_extract
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository
import logging

logger = logging.getLogger(__name__)

def check_voice_empty(user_input: str) -> bool:
    """Returns True if the input contains only commands but no transcript content."""
    input_clean = user_input.lower().strip().rstrip(".! ")
    commands = [
        "summarize this voice note",
        "summarize the voice note",
        "summarize voice note",
        "summarize this voice",
        "summarize voice",
        "summarize",
        "process voice note",
        "process voice"
    ]
    return input_clean in commands

def voice_summary_tool(state: AgentState) -> dict:
    """Processes speech-to-text transcript from user_input, extracts structured data, persists to DB, and updates state."""
    existing_data = state.get("extracted_data", {})
    user_input = state.get("user_input", "")
    interaction_id = state.get("interaction_id")
    
    # 1. Prevent extraction on meaningless input or empty commands
    if not should_extract(user_input) or check_voice_empty(user_input):
        return {
            "extracted_data": existing_data,
            "response": "Please upload a voice note or paste the transcript content so I can summarize it."
        }
        
    try:
        extracted_data = extract_interaction_details(user_input)
        extracted_dict = extracted_data.model_dump()
        
        # 2. Guard against meaningless/empty extractions
        has_data = any(val for key, val in extracted_dict.items() if val not in [None, [], ""])
        if not has_data:
            return {
                "extracted_data": existing_data,
                "response": "Please upload a voice note or paste the transcript content so I can summarize it."
            }
            
        # 3. Persist to SQLite Database
        with SessionLocal() as db:
            repo = InteractionRepository(db)
            db_interaction = repo.create_interaction(extracted_dict)
            interaction_id = db_interaction.id

            
        # 4. Standardized tool response including interaction_id
        return {
            "extracted_data": extracted_dict,
            "interaction_id": interaction_id,
            "response": "✅ Voice note summarized successfully."
        }
    except Exception as e:
        return {
            "extracted_data": existing_data,
            "response": f"⚠️ Failed to summarize voice note: {str(e)}"
        }
