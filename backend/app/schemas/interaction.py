from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict

class InteractionExtraction(BaseModel):
    """Schema representing structured details extracted from HCP interactions.
    Optimized for LLM structured output with flexible type normalization.
    """
    hcp_name: Optional[str] = Field(None, description="Name of the Healthcare Professional (HCP)")
    interaction_type: Optional[str] = Field(None, description="Type of interaction, e.g., Meeting, Call, Email, Seminar")
    date: Optional[str] = Field(None, description="Date of the interaction (preferably YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Time of the interaction (preferably HH:MM AM/PM)")
    attendees: List[str] = Field(default_factory=list, description="List of other attendees present during the interaction")
    topics_discussed: List[str] = Field(default_factory=list, description="List of discussion topics or therapeutic areas covered")
    materials_shared: List[str] = Field(default_factory=list, description="List of shared materials, brochures, or clinical publications")
    samples_distributed: List[str] = Field(default_factory=list, description="List of drug samples distributed to the HCP")
    sentiment: Optional[str] = Field(None, description="General sentiment of the HCP (Positive, Neutral, Negative)")
    outcomes: Optional[str] = Field(None, description="Agreed next steps or outcomes of the meeting")
    follow_up_actions: List[str] = Field(default_factory=list, description="List of scheduled follow-up actions")

    @field_validator('attendees', 'topics_discussed', 'materials_shared', 'samples_distributed', 'follow_up_actions', mode='before')
    @classmethod
    def normalize_list_fields(cls, v: Any) -> List[str]:
        """
        Normalizes list fields.
        - If input is null (None), returns an empty list [].
        - If input is a single string, returns it wrapped in a list.
        - If input is a list, converts elements to string, filtering out nulls.
        - Otherwise, returns an empty list.
        """
        if v is None:
            return []
        if isinstance(v, str):
            return [v.strip()] if v.strip() else []
        if isinstance(v, list):
            normalized = []
            for item in v:
                if item is not None:
                    s = str(item).strip()
                    if s:
                        normalized.append(s)
            return normalized
        return []

    @field_validator('hcp_name', 'interaction_type', 'date', 'time', 'sentiment', 'outcomes', mode='before')
    @classmethod
    def normalize_string_fields(cls, v: Any) -> Optional[str]:
        """
        Normalizes string fields.
        - If input is null (None), returns None.
        - If input is a list, extracts the first item or joins them.
        - Otherwise, returns the string representation.
        """
        if v is None:
            return None
        if isinstance(v, list):
            if len(v) > 0:
                first_item = v[0]
                return str(first_item).strip() if first_item is not None else None
            return None
        s = str(v).strip()
        return s if s else None

def normalize_interaction_output(data: Any) -> Dict[str, Any]:
    """
    Normalizes a dictionary representing interaction details before Pydantic schema validation.
    Guarantees:
    - Every schema field is present.
    - Missing string fields become None.
    - Missing list fields become [].
    - Empty strings for list fields become [].
    - A single string for a list field becomes [string].
    - None for list fields becomes [].
    - Unexpected types are safely converted.
    """
    if not isinstance(data, dict):
        data = {}
        
    string_fields = ['hcp_name', 'interaction_type', 'date', 'time', 'sentiment', 'outcomes']
    list_fields = ['attendees', 'topics_discussed', 'materials_shared', 'samples_distributed', 'follow_up_actions']
    
    normalized = {}
    
    # 1. Normalize string fields
    for field in string_fields:
        val = data.get(field)
        if val is None:
            normalized[field] = None
        elif isinstance(val, list):
            if len(val) > 0 and val[0] is not None:
                s = str(val[0]).strip()
                normalized[field] = s if s else None
            else:
                normalized[field] = None
        else:
            s = str(val).strip()
            normalized[field] = s if s else None
            
    # 2. Normalize list fields
    for field in list_fields:
        val = data.get(field)
        if val is None:
            normalized[field] = []
        elif isinstance(val, str):
            s = val.strip()
            normalized[field] = [s] if s else []
        elif isinstance(val, list):
            normalized_list = []
            for item in val:
                if item is not None:
                    s = str(item).strip()
                    if s:
                        normalized_list.append(s)
            normalized[field] = normalized_list
        else:
            normalized[field] = []
            
    return normalized
