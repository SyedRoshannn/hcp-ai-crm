from app.langgraph.state import AgentState, Intent
from app.ai.llm import get_llm
from app.langgraph.prompts import INTENT_CLASSIFICATION_PROMPT
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

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
    """Evaluates the user request to classify intent and select the appropriate tool using LLM."""
    user_input = state.get("user_input", "")
    detected_intent = Intent.UNKNOWN
    
    try:
        # Retrieve the lazy-loaded LLM instance
        llm = get_llm()
        
        # Invoke the intent classification prompt
        prompt = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
        chain = prompt | llm
        
        response = chain.invoke({"user_input": user_input})
        raw_intent = response.content.strip()
        
        # Convert response into the Intent enum, falling back to UNKNOWN if invalid
        try:
            detected_intent = Intent(raw_intent)
        except ValueError:
            # Handle cases where LLM might return surrounding quotes or symbols
            clean_intent = raw_intent.replace('"', '').replace("'", "").strip().upper()
            try:
                detected_intent = Intent(clean_intent)
            except ValueError:
                logger.warning(f"Invalid LLM intent returned: '{raw_intent}'. Falling back to UNKNOWN.")
                detected_intent = Intent.UNKNOWN
                
    except Exception as e:
        logger.error(f"Error during intent classification: {e}. Falling back to UNKNOWN.")
        detected_intent = Intent.UNKNOWN
    
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
