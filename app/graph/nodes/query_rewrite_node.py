from app.graph.state import ResearchState
from app.services.query_rewriter import rewrite_query


def query_rewrite_node(state: ResearchState):

    results = rewrite_query(state["query"])
    print(results)
    return {
        "rewritten_query": results
    }
