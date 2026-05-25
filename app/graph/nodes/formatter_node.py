from app.services.formatter import format_extracted_content
from app.graph.state import ResearchState

def formatter_node(state: ResearchState):

    formatted_context = format_extracted_content(
        state["extracted_contents"]
    )

    return {
        "formatted_context": formatted_context
    }