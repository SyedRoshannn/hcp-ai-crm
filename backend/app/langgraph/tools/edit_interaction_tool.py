from app.langgraph.state import AgentState
from app.schemas.interaction import InteractionExtraction
from app.utils.structured_parser import safe_llm_call
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository
import json
import logging

logger = logging.getLogger(__name__)

EDIT_PROMPT = """You are an expert clinical CRM data editing assistant.
You are given the existing extracted details of a Healthcare Professional (HCP) interaction, and a new edit instruction from the user.

Your task is to output the COMPLETE InteractionExtraction object.
CRITICAL INSTRUCTIONS:
1. Start with the existing interaction data as your base template.
2. Apply ONLY the specific changes requested by the user's edit instruction.
3. For all other fields that are NOT mentioned in the edit instruction, you MUST preserve their existing values EXACTLY as they are. DO NOT clear them, DO NOT make them null, and DO NOT ignore them. Copy them over to the output.
4. Every List field (attendees, topics_discussed, materials_shared, samples_distributed, follow_up_actions) must ALWAYS return a JSON array (list of strings). Use [] if empty. Never return null.
5. NEVER return a partial JSON object containing only the changed fields. You must fill out and return the entire, complete InteractionExtraction object structure.

Existing extracted data:
{existing_data}

User Edit Instruction:
{user_input}

Return ONLY a valid JSON object.
DO NOT wrap the JSON inside markdown.
DO NOT explain anything.
DO NOT include comments.
DO NOT include text before the JSON.
DO NOT include text after the JSON.
The first character of the response MUST be {{
The last character MUST be }}
If a value is unknown:
- use null for string fields
- use [] for list fields
Never invent extra keys.
Never omit schema keys.
"""

def check_edit_incomplete(instruction: str) -> str:
    """Checks if the edit instruction is missing a target value and returns a clarification question, or empty string."""
    # Clean trailing punctuation
    instr_lower = instruction.lower().strip().rstrip(".!? ")
    
    # Common incomplete patterns
    if instr_lower in [
        "change the doctor's name", "change doctor's name", "change doctor name", "edit doctor's name", "change hcp name", "change name",
        "update doctor's name", "update the doctor's name", "modify doctor's name", "edit name"
    ] or instr_lower.endswith("change the doctor's name to") or instr_lower.endswith("change doctor's name to"):
        return "What would you like to change the doctor's name to?"
        
    if instr_lower in [
        "change the date", "change date", "edit date", "change meeting date", "change interaction date", "edit the meeting date", "update date", "update the meeting date"
    ] or instr_lower.endswith("change the date to") or instr_lower.endswith("change date to"):
        return "What date would you like me to set for the interaction?"
        
    if instr_lower in [
        "change sentiment", "change the sentiment", "edit sentiment", "update sentiment", "update the sentiment"
    ] or instr_lower.endswith("change sentiment to") or instr_lower.endswith("change the sentiment to"):
        return "What sentiment (Positive, Neutral, Negative) would you like to set?"
        
    if instr_lower in [
        "add attendee", "add attendees", "change attendees", "modify attendees", "edit attendees"
    ] or instr_lower.endswith("add attendee") or instr_lower.endswith("add attendees"):
        return "Which attendee would you like to add?"
        
    if instr_lower in [
        "remove brochure", "remove brochures", "delete brochure", "delete brochures", "edit brochures"
    ]:
        return "Which material/brochure would you like to remove?"
        
    if instr_lower in [
        "remove follow up", "remove follow-up", "delete follow up", "delete follow-up", "edit follow up"
    ]:
        return "Which follow-up action would you like to remove?"
        
    return ""

def edit_interaction_tool(state: AgentState) -> dict:
    """Edits the existing extracted data based on user edit instruction, updates database row, and returns the updated state."""
    existing_data = state.get("extracted_data", {})
    user_input = state.get("user_input", "")
    interaction_id = state.get("interaction_id")
    
    # 1. Check for incomplete edit requests
    clarification = check_edit_incomplete(user_input)
    if clarification:
        return {
            "extracted_data": existing_data,
            "response": clarification
        }
        
    string_fields = ['hcp_name', 'interaction_type', 'date', 'time', 'sentiment', 'outcomes']
    list_fields = ['attendees', 'topics_discussed', 'materials_shared', 'samples_distributed', 'follow_up_actions']
    
    try:
        existing_json = json.dumps(existing_data)
        
        # Invoke structured parser's safe LLM execution pipeline
        normalized_output, warning_msg = safe_llm_call(
            prompt_template=EDIT_PROMPT,
            prompt_variables={
                "existing_data": existing_json,
                "user_input": user_input
            },
            fallback_data=existing_data,
            string_fields=string_fields,
            list_fields=list_fields
        )
        
        # 3. Harden edit merging logic:
        # Preserve existing values for any field the LLM omitted or cleared incorrectly.
        user_wants_deletion = any(word in user_input.lower() for word in ["delete", "remove", "clear", "wipe", "erase"])
        
        merged_data = {}
        for key in InteractionExtraction.model_fields.keys():
            old_val = existing_data.get(key)
            new_val = normalized_output.get(key)
            
            # Check if new value is empty
            is_empty = new_val in [None, "", []]
            
            if is_empty:
                if old_val not in [None, "", []]:
                    # Unless user explicitly requested deletion, preserve the old value!
                    if user_wants_deletion:
                        merged_data[key] = new_val
                    else:
                        merged_data[key] = old_val
                else:
                    merged_data[key] = new_val
            else:
                merged_data[key] = new_val
                
        # Validate and instantiate final merged object in the caller
        validated = InteractionExtraction(**merged_data)
        final_dict = validated.model_dump()
        
        if interaction_id:
            with SessionLocal() as db:
                repo = InteractionRepository(db)
                repo.update(interaction_id, final_dict)
        else:
            logger.info("edit_interaction_tool: No interaction_id present in state. DB update skipped.")
        
        # 5. Return standardized response
        return {
            "extracted_data": final_dict,
            "response": "✅ Interaction updated successfully."
        }
        
    except Exception as e:
        return {
            "extracted_data": existing_data,
            "response": f"⚠️ Failed to apply edit: {str(e)}"
        }
