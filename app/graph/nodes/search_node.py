from app.graph.state import ResearchState
from app.tools.tavily_search import tavily_search as web_search

def search_node(state: ResearchState):

    results = web_search(state["rewritten_query"])

    return {
        "search_results": results
    }