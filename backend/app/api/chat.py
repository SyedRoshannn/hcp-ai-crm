from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.langgraph.graph import app_graph
from app.langgraph.state import AgentState

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    extracted_data: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    intent: Optional[str]
    selected_tool: Optional[str]
    extracted_data: Dict[str, Any]
    response: Optional[str] = None
    recommended_materials: Optional[List[str]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    POST endpoint to process conversational messages using the LangGraph state graph.
    """
    try:
        # Create the initial state structure for the graph execution
        initial_state: AgentState = {
            "user_input": request.message,
            "intent": None,
            "extracted_data": request.extracted_data or {},
            "selected_tool": None,
            "response": "",
            "messages": [],
            "errors": [],
            "recommended_materials": None
        }
        
        # Invoke the compiled graph
        result = app_graph.invoke(initial_state)
        
        # Check if any errors occurred during the node execution pipeline
        if result.get("errors"):
            raise HTTPException(
                status_code=500,
                detail=f"Internal Graph Error: {', '.join(result['errors'])}"
            )
            
        # Return the response properties including response message and recommended materials list
        return ChatResponse(
            intent=result.get("intent"),
            selected_tool=result.get("selected_tool"),
            extracted_data=result.get("extracted_data", {}),
            response=result.get("response"),
            recommended_materials=result.get("recommended_materials")
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unhandled Server Error: {str(e)}"
        )
