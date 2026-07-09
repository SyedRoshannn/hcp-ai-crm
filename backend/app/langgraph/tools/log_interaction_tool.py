from app.langgraph.state import AgentState
from app.services.interaction_service import extract_interaction_details, should_extract

def log_interaction_tool(state: AgentState) -> dict:
    """Extracts structured interaction data from user input and updates the state."""
    existing_data = state.get("extracted_data", {})
    user_input = state.get("user_input", "")
    
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
            
        # 3. Standardized tool response
        return {
            "extracted_data": extracted_dict,
            "response": "✅ Interaction logged successfully."
        }
    except Exception as e:
        return {
            "extracted_data": existing_data,
            "response": f"⚠️ Failed to process interaction: {str(e)}"
        }
