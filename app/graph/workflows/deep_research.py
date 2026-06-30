from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes.query_rewrite_node import query_rewrite_node
from app.graph.nodes.evidence_node import gather_evidence
from app.graph.nodes.planner_node import task_planner
from app.graph.nodes.synthesis_context import synthesis_context
from app.graph.nodes.gap_analysis_node import gap_analysis_node
from app.graph.nodes.claim_splitter_node import claim_splitter_node
from app.graph.nodes.verification_node import verification_node
from app.graph.nodes.report_assembler_node import report_assembler_node

def route_evaluation(state: ResearchState):
    scores = state.get("confidence_scores") or {}
    retry_count = state.get("retry_count", 0)
    
    avg_score = 0.0
    if scores:
        avg_score = sum(scores.values()) / len(scores)
        
    if avg_score < 3.5 and retry_count < 1:
        return "gap_analysis_node"
    else:
        return "claim_splitter"

graph = StateGraph(ResearchState)

graph.add_node("query_rewrite_node", query_rewrite_node)
graph.add_node("planner_node", task_planner)
graph.add_node("evidence_node", gather_evidence)
graph.add_node("synthesis_context", synthesis_context)
graph.add_node("gap_analysis_node", gap_analysis_node)
graph.add_node("claim_splitter", claim_splitter_node)
graph.add_node("verification", verification_node)
graph.add_node("report_assembler", report_assembler_node)

graph.set_entry_point("query_rewrite_node")
graph.add_edge("query_rewrite_node", "planner_node")
graph.add_edge("planner_node", "evidence_node")
graph.add_edge("evidence_node", "synthesis_context")

# Conditional evaluation retry loop routing
graph.add_conditional_edges(
    "synthesis_context",
    route_evaluation,
    {
        "gap_analysis_node": "gap_analysis_node",
        "claim_splitter": "claim_splitter"
    }
)

# Connect gap analysis output back to evidence collection node
graph.add_edge("gap_analysis_node", "evidence_node")

# Claims splitting, verification, and report assembly nodes sequence
graph.add_edge("claim_splitter", "verification")
graph.add_edge("verification", "report_assembler")
graph.add_edge("report_assembler", END)

research_graph = graph.compile()