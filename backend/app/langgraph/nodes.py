from app.langgraph.state import AgentState, Intent

# Mapping between Intent enum values and future tool names
INTENT_TOOL_MAPPING = {
    Intent.LOG_INTERACTION: "log_interaction_tool",
    Intent.EDIT_INTERACTION: "edit_interaction_tool",
    Intent.VOICE_SUMMARY: "voice_summary_tool",
    Intent.MATERIAL_RECOMMENDATION: "material_recommendation_tool",
    Intent.FOLLOW_UP: "follow_up_tool",
    Intent.UNKNOWN: None
}

def router_node(state: AgentState) -> dict:
    """Evaluates the user request to classify intent and select the appropriate tool."""
    # TODO: Integrate Groq/LLM call to classify state["user_input"] into one of the Intent values.
    
    # Placeholder: Temporarily hardcode to LOG_INTERACTION to test the integration flow
    detected_intent = Intent.LOG_INTERACTION
    
    # Select appropriate tool based on intent mapping
    selected_tool = INTENT_TOOL_MAPPING.get(detected_intent)
    
    # Return updates to merge into the state
    return {
        "intent": detected_intent,
        "selected_tool": selected_tool
    }

def response_node(state: AgentState) -> dict:
    """Placeholder response node to formulate final conversational response."""
    # No business logic yet, just returning empty updates
    return {}
