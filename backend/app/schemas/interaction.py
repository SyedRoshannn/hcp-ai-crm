from pydantic import BaseModel, Field
from typing import List, Optional

class InteractionExtraction(BaseModel):
    """Schema representing structured details extracted from HCP interactions."""
    hcp_name: Optional[str] = Field(None, description="Name of the Healthcare Professional (HCP)")
    interaction_type: Optional[str] = Field(None, description="Type of interaction, e.g., Meeting, Call, Email, Seminar")
    date: Optional[str] = Field(None, description="Date of the interaction (preferably YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Time of the interaction (preferably HH:MM AM/PM)")
    attendees: List[str] = Field(default_factory=list, description="List of other attendees present during the interaction")
    topics_discussed: Optional[str] = Field(None, description="Summary of key discussion topics or therapeutic areas covered")
    materials_shared: List[str] = Field(default_factory=list, description="List of shared materials, brochures, or clinical publications")
    samples_distributed: List[str] = Field(default_factory=list, description="List of drug samples distributed to the HCP")
    sentiment: Optional[str] = Field(None, description="General sentiment of the HCP (Positive, Neutral, Negative)")
    outcomes: Optional[str] = Field(None, description="Agreed next steps or outcomes of the meeting")
    follow_up_actions: List[str] = Field(default_factory=list, description="List of scheduled follow-up actions")
