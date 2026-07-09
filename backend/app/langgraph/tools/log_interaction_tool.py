from app.langgraph.state import AgentState
from app.services.interaction_service import extract_interaction_details, should_extract
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository
import logging

logger = logging.getLogger(__name__)

def log_interaction_tool(state: AgentState) -> dict:
    """Extracts structured interaction data from user input, persists it to DB, and updates the state."""
    existing_data = state.get("extracted_data", {})
    user_input = state.get("user_input", "")
    interaction_id = state.get("interaction_id")
    
    # Debug Logging for entering tool
    logger.info(f"[DEBUG LOG] log_interaction_tool entering with interaction_id: {interaction_id}")
    
    # 1. Prevent extraction on meaningless input
    if not should_extract(user_input):
        return {
            "extracted_data": existing_data,
            "response": "I couldn't extract any interaction details from your message. Existing form details have been preserved."
        }
        
    try:
        extracted_data = extract_interaction_details(user_input)
        extracted_dict = extracted_data.model_dump()
        
        # 2. Guard against meaningless/empty extractions
        has_data = any(val for key, val in extracted_dict.items() if val not in [None, [], ""])
        if not has_data:
            return {
                "extracted_data": existing_data,
                "response": "I couldn't extract any interaction details from your message. Existing form details have been preserved."
            }
            
        # 3. Persist to SQLite Database
        with SessionLocal() as db:
            repo = InteractionRepository(db)
            db_interaction = repo.create_interaction(extracted_dict)
            interaction_id = db_interaction.id
            # Debug Logging for DB creation
            logger.info(f"[DEBUG LOG] Log tool created DB record. Commit succeeded. Affected row ID: {interaction_id}")
            
        # 4. Standardized tool response including interaction_id
        return {
            "extracted_data": extracted_dict,
            "interaction_id": interaction_id,
            "response": "✅ Interaction logged successfully."
        }
    except Exception as e:
        return {
            "extracted_data": existing_data,
            "response": f"⚠️ Failed to process interaction: {str(e)}"
        }
