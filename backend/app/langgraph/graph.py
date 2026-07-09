from langgraph.graph import StateGraph, START, END
from app.langgraph.state import AgentState
from app.langgraph.nodes import router_node, response_node
from app.langgraph.tools.log_interaction_tool import log_interaction_tool
from app.langgraph.tools.edit_interaction_tool import edit_interaction_tool

def route_after_router(state: AgentState) -> str:
    """
    Evaluates the selected_tool in the state to determine the next graph node transition.
    Returns the node name to transition to.
    """
    selected_tool = state.get("selected_tool")
    if selected_tool == "log_interaction_tool":
        return "log_interaction_tool"
    if selected_tool == "edit_interaction_tool":
        return "edit_interaction_tool"
    
    # Placeholder routing paths for future tool nodes:
    # if selected_tool == "voice_summary_tool":
    #     return "voice_summary_tool"
    # if selected_tool == "material_recommendation_tool":
    #     return "material_recommendation_tool"
    # if selected_tool == "follow_up_tool":
    #     return "follow_up_tool"
        
    return "response_node"

# Define a StateGraph using the AgentState schema
workflow = StateGraph(AgentState)

# Add placeholder nodes
workflow.add_node("router_node", router_node)
workflow.add_node("log_interaction_tool", log_interaction_tool)
workflow.add_node("edit_interaction_tool", edit_interaction_tool)
workflow.add_node("response_node", response_node)

# Construct sequential transitions and conditional routing
workflow.add_edge(START, "router_node")

# Conditional edges from router_node based on selected_tool classification
workflow.add_conditional_edges(
    "router_node",
    route_after_router,
    {
        "log_interaction_tool": "log_interaction_tool",
        "edit_interaction_tool": "edit_interaction_tool",
        "response_node": "response_node"
        # Future mappings:
        # "voice_summary_tool": "voice_summary_tool",
        # "material_recommendation_tool": "material_recommendation_tool",
        # "follow_up_tool": "follow_up_tool",
    }
)

# Edges from tools back to response_node
workflow.add_edge("log_interaction_tool", "response_node")
workflow.add_edge("edit_interaction_tool", "response_node")

# Edge from response_node to the end of workflow
workflow.add_edge("response_node", END)

# Compile the graph
app_graph = workflow.compile()
