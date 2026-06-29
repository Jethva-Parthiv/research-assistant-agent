from typing import TypedDict, List, Dict, Optional
from app.models.claims import ClaimResult


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

    confidence_scores: Optional[Dict[str, float]]
    retry_count: int
    report_data: Optional[dict]
    claims: List[ClaimResult]
    verified_report: Optional[str]
    overall_confidence: Optional[float]

