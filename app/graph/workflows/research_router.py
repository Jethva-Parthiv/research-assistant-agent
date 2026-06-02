from langgraph.graph import (
    StateGraph,
    END
)
from app.graph.state import ResearchState
from app.graph.nodes.router_node import (
    router_node,
    route_decision,
    simple_workflow_node,
    deep_workflow_node
)

graph = StateGraph(ResearchState)

graph.add_node(
    "router",
    router_node
)

graph.add_node(
    "simple",
    simple_workflow_node
)

graph.add_node(
    "deep",
    deep_workflow_node
)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "simple": "simple",
        "deep": "deep"
    }
)

graph.add_edge("simple", END)
graph.add_edge("deep", END)

research_router = graph.compile()