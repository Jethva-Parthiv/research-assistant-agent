from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes.query_rewrite_node import query_rewrite_node
from app.graph.nodes.evidence_node import gather_evidence
from app.graph.nodes.planner_node import task_planner
from app.graph.nodes.synthesis_context import synthesis_context

graph = StateGraph(ResearchState)

graph.add_node("query_rewrite_node", query_rewrite_node)
graph.add_node("planner_node", task_planner)
graph.add_node("evidence_node", gather_evidence)
graph.add_node("synthesis_context", synthesis_context)

graph.set_entry_point("query_rewrite_node")
graph.add_edge("query_rewrite_node", "planner_node")
graph.add_edge("planner_node", "evidence_node")
graph.add_edge("evidence_node", "synthesis_context")
graph.add_edge("synthesis_context", END)

research_graph = graph.compile()