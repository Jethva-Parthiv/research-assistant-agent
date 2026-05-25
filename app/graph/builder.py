from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.graph.nodes.query_rewrite_node import query_rewrite_node
from app.graph.nodes.search_node import search_node
from app.graph.nodes.formatter_node import formatter_node
from app.graph.nodes.answer_node import answer_node
from app.graph.nodes.extract_node import extract_node

graph = StateGraph(ResearchState)

graph.add_node("query_rewrite_node", query_rewrite_node)
graph.add_node("search_node", search_node)
graph.add_node("extract_node", extract_node)
graph.add_node("formatter_node", formatter_node)
graph.add_node("answer_node", answer_node)

graph.set_entry_point("query_rewrite_node")
graph.add_edge("query_rewrite_node", "search_node")
graph.add_edge("search_node", "extract_node")
graph.add_edge("extract_node", "formatter_node")
graph.add_edge("formatter_node", "answer_node")
graph.add_edge("answer_node", END)

research_graph = graph.compile()