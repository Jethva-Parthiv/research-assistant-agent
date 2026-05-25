from typing import TypedDict, List


class SearchResult(TypedDict):
    title: str
    content: str
    url: str

class ExtractedContent(TypedDict):
    url: str
    raw_content: str

class ResearchState(TypedDict):

    query: str

    rewritten_query: str

    search_results: List[SearchResult]

    extracted_contents: List[ExtractedContent]

    formatted_context: str

    final_answer: str
