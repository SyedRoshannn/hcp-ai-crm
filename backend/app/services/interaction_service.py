from app.schemas.interaction import InteractionExtraction
from app.utils.structured_parser import safe_llm_call

EXTRACTION_PROMPT = """You are an expert clinical CRM data extraction assistant.
Extract structured details from the following description of a Healthcare Professional (HCP) interaction.
Analyze the input text carefully and extract the fields.

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

def should_extract(user_input: str) -> bool:
    """
    Evaluates whether the user input contains enough meaningful context to perform extraction.
    Returns False for empty, punctuation, greetings, acknowledgements, or very short inputs.
    """
    if not user_input or not user_input.strip():
        return False
        
    # Clean text
    clean = user_input.strip().lower().rstrip(".!? ")
    
    # Check punctuation only
    if all(char in ".,!?@#$%^&*()_+-=[]{}|;:'\"<>/`~ thumbsup 👍 " for char in clean):
        return False
        
    # Common greetings and acknowledgements
    greetings_and_acks = {
        "hello", "hi", "hey", "yo", "greetings", "good morning", "good afternoon", "good evening",
        "thanks", "thank you", "ok", "okay", "yes", "no", "yep", "nope", "sure", "fine", "thumbs up", "thumbsup",
        "please", "help", "test", "run", "go"
    }
    if clean in greetings_and_acks:
        return False
        
    # Count meaningful words (excluding short words / stopwords / generic conversational tokens)
    words = [w for w in clean.split() if w not in ["a", "the", "an", "and", "or", "but", "is", "are", "am", "to", "of", "in", "on", "at", "for", "with"]]
    
    # Configure threshold (e.g. at least 2 meaningful words)
    if len(words) < 2:
        return False
        
    return True

def extract_interaction_details(user_input: str) -> InteractionExtraction:
    """Accepts unstructured user input and returns structured InteractionExtraction data using Groq LLM."""
    string_fields = ['hcp_name', 'interaction_type', 'date', 'time', 'sentiment', 'outcomes']
    list_fields = ['attendees', 'topics_discussed', 'materials_shared', 'samples_distributed', 'follow_up_actions']
    
    # Invoke structured parser's safe LLM execution pipeline
    normalized_dict, warning_msg = safe_llm_call(
        prompt_template=EXTRACTION_PROMPT,
        prompt_variables={"user_input": user_input},
        fallback_data={},
        string_fields=string_fields,
        list_fields=list_fields
    )
    
    # Instantiate InteractionExtraction in the caller service
    return InteractionExtraction(**normalized_dict)
