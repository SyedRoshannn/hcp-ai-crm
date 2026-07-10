from app.langgraph.state import AgentState
from app.utils.structured_parser import safe_llm_call
from app.db.database import SessionLocal
from app.repositories.interaction_repository import InteractionRepository
import logging

logger = logging.getLogger(__name__)

HISTORY_SEARCH_PROMPT = """You are a medical CRM search filter extraction assistant.
Given a user query requesting to search or view past interaction logs, extract the relevant structured search filters.

Therapeutic/Product keywords like "Product X" or "diabetes" should be mapped to the target "topic" filter.

Return ONLY a valid JSON object matching this schema:
{{
  "doctor_name": null or string,
  "date": null or string,
  "date_from": null or string,
  "date_to": null or string,
  "sentiment": null or string,
  "interaction_type": null or string,
  "material": null or string,
  "topic": null or string,
  "latest": "false" or "true",
  "all": "false" or "true",
  "has_followup": "false" or "true"
}}

DO NOT wrap the JSON inside markdown.
DO NOT explain anything.
DO NOT include comments.
DO NOT include text before or after the JSON.
The first character of the response MUST be {{
The last character MUST be }}

User Query:
{user_input}
"""

def clean_str_filter(val) -> str or None:
    """Cleans string filters, returning None if they represent a null/empty filter value."""
    if val is None:
        return None
    s = str(val).strip()
    if s.lower() in ["null", "none", "undefined", ""]:
        return None
    return s

def history_search_tool(state: AgentState) -> dict:
    """Extracts structured search parameters from user input, queries SQLite DB, and returns formatted history list."""
    user_input = state.get("user_input", "")
    
    string_fields = [
        "doctor_name", "date", "date_from", "date_to", "sentiment", 
        "interaction_type", "material", "topic", "latest", "all", "has_followup"
    ]
    list_fields = []
    
    # 1. Invoke safe_llm_call to extract structured search filters
    normalized_dict, warning_msg = safe_llm_call(
        prompt_template=HISTORY_SEARCH_PROMPT,
        prompt_variables={"user_input": user_input},
        fallback_data={
            "doctor_name": None, "date": None, "date_from": None, "date_to": None,
            "sentiment": None, "interaction_type": None, "material": None, "topic": None,
            "latest": "false", "all": "true", "has_followup": "false"
        },
        string_fields=string_fields,
        list_fields=list_fields
    )
    
    # Clean boolean and string parameters
    filters = {
        "doctor_name": clean_str_filter(normalized_dict.get("doctor_name")),
        "date": clean_str_filter(normalized_dict.get("date")),
        "date_from": clean_str_filter(normalized_dict.get("date_from")),
        "date_to": clean_str_filter(normalized_dict.get("date_to")),
        "sentiment": clean_str_filter(normalized_dict.get("sentiment")),
        "interaction_type": clean_str_filter(normalized_dict.get("interaction_type")),
        "material": clean_str_filter(normalized_dict.get("material")),
        "topic": clean_str_filter(normalized_dict.get("topic")),
        "latest": str(normalized_dict.get("latest", "")).lower() in ["true", "1", "yes"],
        "all": str(normalized_dict.get("all", "")).lower() in ["true", "1", "yes"],
        "has_followup": str(normalized_dict.get("has_followup", "")).lower() in ["true", "1", "yes"]
    }
    
    # 2. Query Database Repository
    results = []
    try:
        with SessionLocal() as db:
            repo = InteractionRepository(db)
            results = repo.search(filters)
    except Exception as e:
        return {
            "response": f"⚠️ Failed to query interaction history: {str(e)}"
        }
        
    # 3. Format results into human-readable chat message response
    if not results:
        # Fallback if no matching records
        query_subject = filters["doctor_name"] or filters["topic"] or user_input
        response_msg = f"I couldn't find any interaction logs matching \"{query_subject}\".\n\nTry another doctor name or search criteria."
    else:
        count = len(results)
        response_msg = f"I found {count} interaction{'s' if count > 1 else ''}.\n\n"
        for i, item in enumerate(results, 1):
            response_msg += f"{i}.\n"
            response_msg += f"Doctor: {item.hcp_name or 'N/A'}\n"
            response_msg += f"Date: {item.date or 'N/A'}\n"
            response_msg += f"Sentiment: {item.sentiment or 'N/A'}\n"
            
            # Format list fields nicely if present
            topics = item.topics_discussed or []
            if topics:
                response_msg += "Topics:\n"
                for topic in topics:
                    response_msg += f"• {topic}\n"
                    
            materials = item.materials_shared or []
            if materials:
                response_msg += "Materials Shared:\n"
                for mat in materials:
                    response_msg += f"• {mat}\n"
                    
            followups = item.follow_up_actions or []
            if followups:
                response_msg += "Follow-up Actions:\n"
                for fup in followups:
                    response_msg += f"• {fup}\n"
                    
            response_msg += "\n"
            
    return {
        "response": response_msg.strip()
    }
