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

def is_greeting(text: str) -> bool:
    """Returns True if the input text is a greeting."""
    clean = text.strip().lower().rstrip(".!? ")
    greetings = {"hello", "hi", "hey", "yo", "greetings", "good morning", "good afternoon", "good evening"}
    return clean in greetings

def is_meaningless_or_greeting(text: str) -> bool:
    """Returns True if the input text is a greeting, acknowledgement, punctuation only, or meaningless."""
    if not text:
        return True
    clean = text.strip().lower().rstrip(".!? ")
    if not clean:
        return True
        
    # Check punctuation only
    if all(char in ".,!?@#$%^&*()_+-=[]{}|;:'\"<>/`~ thumbsup 👍 " for char in clean):
        return True
        
    # Check common greetings and acknowledgements
    greetings_and_acks = {
        "hello", "hi", "hey", "yo", "greetings", "good morning", "good afternoon", "good evening",
        "thanks", "thank you", "ok", "okay", "yes", "no", "yep", "nope", "sure", "fine", "thumbs up", "thumbsup",
        "please", "help", "test", "run", "go"
    }
    if clean in greetings_and_acks:
        return True
        
    return False

def router_node(state: AgentState) -> dict:
    """Evaluates the user request to classify intent and select the appropriate tool using LLM."""
    user_input = state.get("user_input", "")
    
    # 1. Run local pre-checks for greetings / meaningless text
    if is_meaningless_or_greeting(user_input):
        return {
            "intent": Intent.UNKNOWN,
            "selected_tool": None
        }
        
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
    """Formulates final conversational response if not already set by a tool."""
    response = state.get("response", "")
    intent = state.get("intent")
    user_input = state.get("user_input", "")
    
    if not response:
        if intent == Intent.UNKNOWN:
            if is_greeting(user_input):
                response = "Hello! I can help log interactions, edit existing records, summarize voice notes, recommend materials, and schedule follow-ups."
            else:
                response = (
                    "I couldn't understand your request.\n\n"
                    "You can:\n"
                    "• Log an interaction\n"
                    "• Edit an interaction\n"
                    "• Summarize a voice note\n"
                    "• Recommend materials\n"
                    "• Schedule follow-ups"
                )
        else:
            response = "Processing completed."
            
    return {
        "response": response
    }
