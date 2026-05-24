from typing import TypedDict

class ResearchState(TypedDict):
    query : str
    search_results : list[dict]
    final_answer : str
    