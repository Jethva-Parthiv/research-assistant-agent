from typing import TypedDict, List


class SearchResult(TypedDict):
    title: str
    content: str
    url: str


class ResearchState(TypedDict):

    query: str

    rewrite_query: str

    search_results: List[SearchResult]

    formatted_context: str

    final_answer: str