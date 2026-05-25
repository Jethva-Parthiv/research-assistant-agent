from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.tools.web_search import web_search
from app.agents.researcher import generate_answer
from app.services.formatter import format_search_results
from app.services.query_rewriter import rewrite_query


def query_rewrite_node(state: ResearchState):

    results = rewrite_query(state["query"])
    print(results)
    return {
        "rewrite_query": results
    }


def search_node(state: ResearchState):

    results = web_search(state["rewrite_query"])

    return {
        "search_results": results
    }


def formatter_node(state: ResearchState):

    formatted_context = format_search_results(
        state["search_results"]
    )

    return {
        "formatted_context": formatted_context
    }


def answer_node(state: ResearchState):

    answer = generate_answer(
        query=state["rewrite_query"],
        context=state["formatted_context"]
    )

    return {
        "final_answer": answer
    }


graph = StateGraph(ResearchState)

graph.add_node("query_rewrite_node", query_rewrite_node)
graph.add_node("search_node", search_node)
graph.add_node("formatter_node", formatter_node)
graph.add_node("answer_node", answer_node)

graph.set_entry_point("query_rewrite_node")
graph.add_edge("query_rewrite_node", "search_node")
graph.add_edge("search_node", "formatter_node")
graph.add_edge("formatter_node", "answer_node")
graph.add_edge("answer_node", END)

research_graph = graph.compile()