from app.graph.state import ResearchState
from app.tools.web_search import extract_webpages

def extract_node(state: ResearchState):

    urls = [
        result["url"]
        for result in state["search_results"]
    ]

    extracted_contents = extract_webpages(urls)

    return {
        "extracted_contents": extracted_contents
    }