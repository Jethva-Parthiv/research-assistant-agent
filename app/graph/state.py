from typing import TypedDict, List


class SearchResult(TypedDict):
    title: str
    content: str
    url: str


class ExtractedContent(TypedDict):
    url: str
    raw_content: str


class Evidence(TypedDict):
    task: str
    source: str
    content: str


class ResearchState(TypedDict):

    query: str

    route: str

    rewritten_query: str

    research_tasks: List[str]

    search_results: List[SearchResult]

    extracted_contents: List[ExtractedContent]

    evidence: List[Evidence]
    synthesis_context: str

    formatted_context: str

    final_answer: str


# class ResearchState(TypedDict):

#     query: str

#     rewritten_query: str

#     search_results: List[SearchResult]

#     extracted_contents: List[ExtractedContent]

#     formatted_context: str

#     final_answer: str