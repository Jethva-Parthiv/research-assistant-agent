from langgraph.graph import StateGraph, END
from app.graph.state import ResearchState
from app.tools.web_search import web_search
from app.agents.researcher import generate_answer


def search_node(state: ResearchState):

    results = web_search(state["query"])

    return {
        "search_results": results
    }


def answer_node(state: ResearchState):

    answer = generate_answer(
        query=state["query"],
        search_results=state["search_results"]
    )

    return {
        "final_answer": answer
    }


graph = StateGraph(ResearchState)

graph.add_node("search_node", search_node)
graph.add_node("answer_node", answer_node)

graph.set_entry_point("search_node")

graph.add_edge("search_node", "answer_node")
graph.add_edge("answer_node", END)

research_graph = graph.compile()