from app.langgraph.state import AgentState
from app.utils.structured_parser import safe_llm_call
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository
import json
import logging

logger = logging.getLogger(__name__)

FOLLOW_UP_PROMPT = """You are a medical CRM follow-up scheduler assistant.
Your task is to analyze the user's follow-up request and extract the operation, date/action details, and follow-up string.

Supported Operations:
- ADD: User wants to add, schedule, or append a follow-up action (e.g., "Schedule a follow up next Monday", "Remind me to call Dr Smith tomorrow").
- UPDATE: User wants to change, modify, or update an existing follow-up (e.g., "Update follow up to next Wednesday").
- REMOVE: User wants to delete, remove, or clear follow-ups (e.g., "Remove follow up", "Delete follow up").
- VIEW: User wants to view, query, or check when their follow-up is (e.g., "What is my follow up?", "When is the follow up?").
- CLARIFY: Use this if the user wants to add or update a follow-up but has not specified any date, time, or action (e.g., "Schedule a follow up").

User Input:
{user_input}

Existing Follow-ups:
{existing_follow_ups}

Return ONLY a valid JSON object matching this schema:
{{
  "operation": "ADD" or "UPDATE" or "REMOVE" or "VIEW" or "CLARIFY",
  "follow_up_action": "description of the action or date, e.g., 'Next Monday' or 'Call Dr Smith tomorrow'"
}}
DO NOT wrap the JSON inside markdown.
DO NOT explain anything.
DO NOT include comments.
DO NOT include text before or after the JSON.
The first character of the response MUST be {{
The last character MUST be }}
If a value is unknown:
- use null for string fields
- use [] for list fields
Never invent extra keys.
Never omit schema keys.
"""

def check_follow_up_incomplete(instruction: str) -> str:
    """Checks if the user asks to schedule follow up but provides no details."""
    clean = instruction.lower().strip().rstrip(".!? ")
    if clean in ["schedule follow up", "schedule a follow up", "add follow up", "add a follow up", "remind me", "add reminder", "set reminder"]:
        return "Which date would you like to schedule the follow-up for?"
    return ""

def follow_up_tool(state: AgentState) -> dict:
    """Schedules, updates, removes, or views follow-up actions inside AgentState and persists updates in DB."""
    existing_data = state.get("extracted_data", {})
    user_input = state.get("user_input", "")
    interaction_id = state.get("interaction_id")
    
    # 1. Check for incomplete follow-up request
    clarification = check_follow_up_incomplete(user_input)
    if clarification:
        return {
            "extracted_data": existing_data,
            "response": clarification
        }
        
    string_fields = ["operation", "follow_up_action"]
    list_fields = []
    
    # Format existing follow-ups for LLM context
    existing_follow_ups = existing_data.get("follow_up_actions", [])
    
    # 2. Invoke LLM to classify operation and extract details
    normalized_dict, warning_msg = safe_llm_call(
        prompt_template=FOLLOW_UP_PROMPT,
        prompt_variables={
            "user_input": user_input,
            "existing_follow_ups": json.dumps(existing_follow_ups)
        },
        fallback_data={"operation": "VIEW", "follow_up_action": ""},
        string_fields=string_fields,
        list_fields=list_fields
    )
    
    operation = normalized_dict.get("operation", "VIEW").upper()
    action = normalized_dict.get("follow_up_action", "")
    
    # Make a copy of existing data to merge updates safely
    updated_data = existing_data.copy()
    current_follow_ups = list(updated_data.get("follow_up_actions", []))
    
    response_msg = ""
    
    if operation == "CLARIFY" or (operation in ["ADD", "UPDATE"] and not action):
        response_msg = "Which date would you like to schedule the follow-up for?"
        
    elif operation == "ADD":
        if not current_follow_ups:
            current_follow_ups.append(action)
            updated_data["follow_up_actions"] = current_follow_ups
            response_msg = f"✅ Follow-up scheduled successfully.\n\nNext follow-up:\n• {action}"
        else:
            current_follow_ups.append(action)
            updated_data["follow_up_actions"] = current_follow_ups
            response_msg = "✅ Follow-up added successfully.\n\nCurrent follow-ups:\n"
            for item in current_follow_ups:
                response_msg += f"\n• {item}"
                
    elif operation == "UPDATE":
        if current_follow_ups:
            current_follow_ups[-1] = action
        else:
            current_follow_ups = [action]
        updated_data["follow_up_actions"] = current_follow_ups
        response_msg = "✅ Follow-up updated successfully."
        
    elif operation == "REMOVE":
        updated_data["follow_up_actions"] = []
        response_msg = "✅ Follow-up removed successfully."
        
    elif operation == "VIEW":
        if current_follow_ups:
            response_msg = "Current follow-up:\n"
            for item in current_follow_ups:
                response_msg += f"\n• {item}"
        else:
            response_msg = "No follow-up has been scheduled yet."
            
    else:
        response_msg = "No follow-up has been scheduled yet."
        
    # 3. Persist update in DB if interaction_id exists
    if interaction_id:
        with SessionLocal() as db:
            repo = InteractionRepository(db)
            repo.update(interaction_id, updated_data)
    else:
        logger.info("follow_up_tool: No interaction_id present in state. DB update skipped.")
            
    return {
        "extracted_data": updated_data,
        "response": response_msg
    }
