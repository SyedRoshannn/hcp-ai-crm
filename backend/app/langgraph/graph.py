from langgraph.graph import StateGraph, START, END
from app.langgraph.state import AgentState
from app.langgraph.nodes import router_node, response_node
from app.langgraph.tools.log_interaction_tool import log_interaction_tool

# Define a StateGraph using the AgentState schema
workflow = StateGraph(AgentState)

# Add placeholder nodes
workflow.add_node("router_node", router_node)
workflow.add_node("log_interaction_tool", log_interaction_tool)
workflow.add_node("response_node", response_node)

# Construct sequential transitions (statically linked for step testing)
workflow.add_edge(START, "router_node")
workflow.add_edge("router_node", "log_interaction_tool")
workflow.add_edge("log_interaction_tool", "response_node")
workflow.add_edge("response_node", END)

# Compile the graph
app_graph = workflow.compile()
