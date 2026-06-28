from app.graph.state import ResearchState
from app.services.researcher import generate_answer

def answer_node(state: ResearchState):

    answer = generate_answer(
        query=state["rewritten_query"],
        context=state["formatted_context"]
    )

    return {
        "final_answer": answer
    }
