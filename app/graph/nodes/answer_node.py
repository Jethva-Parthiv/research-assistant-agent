from app.graph.state import ResearchState
from app.services.researcher import generate_answer
from app.services.report_parser import parse_markdown_to_report

def answer_node(state: ResearchState):
    answer = generate_answer(
        query=state["rewritten_query"],
        context=state["formatted_context"]
    )

    # Convert answer to structured JSON format
    report_dict = parse_markdown_to_report(
        query=state["query"],
        markdown_report=answer,
        route_used="SIMPLE"
    )

    return {
        "final_answer": answer,
        "report_data": report_dict
    }
