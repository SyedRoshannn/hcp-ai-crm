from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    extracted_data: Optional[Dict[str, Any]] = None
    interaction_id: Optional[str] = None

class ChatResponse(BaseModel):
    intent: Optional[str]
    selected_tool: Optional[str]
    extracted_data: Dict[str, Any]
    response: Optional[str] = None
    recommended_materials: Optional[List[str]] = None
    interaction_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    POST endpoint to process conversational messages using the LangGraph state graph.
    """
    try:
        # Debug Logging for interaction_id received by API
        logger.info(f"[DEBUG LOG] API received interaction_id: {request.interaction_id}")
        
        # Create the initial state structure for the graph execution
        initial_state: AgentState = {
            "user_input": request.message,
            "intent": None,
            "extracted_data": request.extracted_data or {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None,
            "interaction_id": request.interaction_id
        }
        
        # Debug Logging for interaction_id entering LangGraph
        logger.info(f"[DEBUG LOG] Entering LangGraph with interaction_id: {initial_state['interaction_id']}")
        
        # Invoke the compiled graph
        result = app_graph.invoke(initial_state)
        
        # Check if any errors occurred during the node execution pipeline
        if result.get("errors"):
            raise HTTPException(
                status_code=500,
                detail=f"Internal Graph Error: {', '.join(result['errors'])}"
            )
            
        # Return the response properties including response message, recommended materials, and interaction_id
        return ChatResponse(
            intent=result.get("intent"),
            selected_tool=result.get("selected_tool"),
            extracted_data=result.get("extracted_data", {}),
            response=result.get("response"),
            recommended_materials=result.get("recommended_materials"),
            interaction_id=result.get("interaction_id")
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unhandled Server Error: {str(e)}"
        )
