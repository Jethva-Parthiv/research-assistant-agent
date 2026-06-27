from app.core.llm import llm
from pydantic import BaseModel
from typing import List

class ResearchPlan(BaseModel):
    tasks: List[str]


def create_plan(query: str):

    prompt = f"""
    You are a research planner.

    Break the user query into research tasks.

    Query:
    {query}

    Return 2 focused research tasks.
    """

    structured_llm = llm.with_structured_output(
        ResearchPlan
    )

    result = structured_llm.invoke(prompt)

    return result.tasks


