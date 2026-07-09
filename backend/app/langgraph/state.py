from enum import Enum
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class Intent(str, Enum):
    LOG_INTERACTION = "LOG_INTERACTION"
    EDIT_INTERACTION = "EDIT_INTERACTION"
    VOICE_SUMMARY = "VOICE_SUMMARY"
    MATERIAL_RECOMMENDATION = "MATERIAL_RECOMMENDATION"
    FOLLOW_UP = "FOLLOW_UP"
    UNKNOWN = "UNKNOWN"

class AgentState(TypedDict):
    user_input: str
    intent: Optional[Intent]
    extracted_data: Dict[str, Any]
    selected_tool: Optional[str]
    response: str
    messages: Annotated[List[BaseMessage], add_messages]
    errors: List[str]
    recommended_materials: Optional[List[str]]
