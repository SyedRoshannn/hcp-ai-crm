from app.langgraph.state import AgentState
from app.services.interaction_service import extract_interaction_details

def log_interaction_tool(state: AgentState) -> dict:
    """Extracts structured interaction data from user input and updates the state."""
    user_input = state.get("user_input", "")
    
    # Run the extraction service to call the LLM structured parsing
    extracted_data = extract_interaction_details(user_input)
    
    # Return updates to merge into the state
    return {
        "extracted_data": extracted_data.model_dump()
    }
