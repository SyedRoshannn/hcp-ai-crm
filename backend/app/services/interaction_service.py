from app.ai.llm import get_llm
from app.schemas.interaction import InteractionExtraction
from langchain_core.prompts import ChatPromptTemplate

EXTRACTION_PROMPT = """You are an expert clinical CRM data extraction assistant.
Extract structured details from the following description of a Healthcare Professional (HCP) interaction.
Analyze the input text carefully and extract the fields.

CRITICAL FORMATTING RULES:
1. Every List[str] field (attendees, topics_discussed, materials_shared, samples_distributed, follow_up_actions) MUST ALWAYS return an array (list of strings).
2. NEVER return null or None for array/list fields. Use [] if the information is unavailable.
3. NEVER return a single string where an array is expected. (e.g., topics_discussed: ["Product X"] is correct; topics_discussed: "Product X" is INCORRECT).
4. NEVER return an array where a string is expected. (e.g., hcp_name: "Dr. Smith" is correct; hcp_name: ["Dr. Smith"] is INCORRECT).

JSON Schema Guidance:
- attendees: Array of strings. Use [] if not mentioned.
- topics_discussed: Array of strings. Use [] if not mentioned.
- materials_shared: Array of strings. Use [] if not mentioned.
- samples_distributed: Array of strings. Use [] if not mentioned.
- follow_up_actions: Array of strings. Use [] if not mentioned.
- hcp_name: String or null.
- interaction_type: String or null.
- date: String or null.
- time: String or null.
- sentiment: String or null.
- outcomes: String or null.

---
FEW-SHOT EXAMPLES:

Example 1:
Input: "Met Dr. Smith to discuss Prodo-X."
Output JSON:
{{
  "hcp_name": "Dr. Smith",
  "interaction_type": "Meeting",
  "date": null,
  "time": null,
  "attendees": [],
  "topics_discussed": ["Prodo-X"],
  "materials_shared": [],
  "samples_distributed": [],
  "sentiment": "Neutral",
  "outcomes": "Discussed product",
  "follow_up_actions": []
}}

Example 2:
Input: "Yesterday at 3 PM, I called Dr. Alice Johnson. Shared the new efficacy brochure. She had positive sentiment. Follow-up: send clinical trial links next week."
Output JSON:
{{
  "hcp_name": "Dr. Alice Johnson",
  "interaction_type": "Call",
  "date": "Yesterday",
  "time": "03:00 PM",
  "attendees": ["Dr. Alice Johnson"],
  "topics_discussed": [],
  "materials_shared": ["efficacy brochure"],
  "samples_distributed": [],
  "sentiment": "Positive",
  "outcomes": "Shared brochure",
  "follow_up_actions": ["send clinical trial links next week"]
}}

---
Input text to extract:
{user_input}
"""

def extract_interaction_details(user_input: str) -> InteractionExtraction:
    """Accepts unstructured user input and returns structured InteractionExtraction data using Groq LLM."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(InteractionExtraction)
    
    prompt = ChatPromptTemplate.from_template(EXTRACTION_PROMPT)
    chain = prompt | structured_llm
    
    # Execute extraction
    result = chain.invoke({"user_input": user_input})
    return result
