from app.langgraph.state import AgentState
from app.utils.structured_parser import safe_llm_call

MOCK_CATALOGUE = [
    {"id": "MAT001", "title": "Diabetes Clinical Brochure", "category": "diabetes", "type": "brochure"},
    {"id": "MAT002", "title": "Diabetes Patient Education Guide", "category": "diabetes", "type": "guide"},
    {"id": "MAT003", "title": "Latest Diabetes Study", "category": "diabetes", "type": "study"},
    {"id": "MAT004", "title": "Product X Brochure", "category": "product x", "type": "brochure"},
    {"id": "MAT005", "title": "Product X Clinical Trial Summary", "category": "product x", "type": "study"},
    {"id": "MAT006", "title": "Product X Safety Guide", "category": "product x", "type": "guide"},
    {"id": "MAT007", "title": "Hypertension Guideline", "category": "hypertension", "type": "guideline"},
    {"id": "MAT008", "title": "Blood Pressure Management Guide", "category": "hypertension", "type": "guide"},
    {"id": "MAT009", "title": "Cardiovascular Study Report", "category": "cardiovascular", "type": "report"},
    {"id": "MAT010", "title": "Product Y Patient Leaflet", "category": "product y", "type": "leaflet"}
]

MATERIAL_RECOMMENDATION_PROMPT = """You are a medical CRM search extraction assistant.
Given a user query requesting materials, extract the primary target therapeutic area, product name, or subject.
Example: "Recommend brochure for diabetes" -> "diabetes"
Example: "Need Product X brochure" -> "product x"
Example: "Show hypertension publications" -> "hypertension"

User Input:
{user_input}

Return ONLY a valid JSON object matching this schema:
{{
  "query": "extracted category or product name here"
}}
DO NOT wrap the JSON inside markdown.
DO NOT explain anything.
DO NOT include comments.
DO NOT include text before the JSON.
DO NOT include text after the JSON.
The first character of the response MUST be {{
The last character MUST be }}
"""

def material_recommendation_tool(state: AgentState) -> dict:
    """Recommends relevant materials from the catalogue based on search extraction from user input."""
    user_input = state.get("user_input", "")
    
    # 1. Extract search query key terms from user input
    normalized_dict, warning_msg = safe_llm_call(
        prompt_template=MATERIAL_RECOMMENDATION_PROMPT,
        prompt_variables={"user_input": user_input},
        fallback_data={"query": ""},
        string_fields=["query"],
        list_fields=[]
    )
    
    query = normalized_dict.get("query", "")
    query_clean = query.strip().lower() if query else ""
    
    # 2. Match search term against mock catalogue
    matches = []
    if query_clean:
        for item in MOCK_CATALOGUE:
            if query_clean in item["category"].lower() or query_clean in item["title"].lower():
                matches.append(item["title"])
                
    # 3. Format response and recommended list
    if matches:
        response_msg = "✅ I found the following materials:\n\n"
        for title in matches:
            response_msg += f"• {title}\n\n"
        response_msg += "Would you like to attach one to this interaction?"
    else:
        # No match found format
        query_val = query or user_input
        response_msg = f"I couldn't find matching materials for \"{query_val}\".\n\nTry another disease area or product name."
        
    return {
        "recommended_materials": matches,
        "response": response_msg
    }
