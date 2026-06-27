from app.core.llm import llm
from app.graph.state import ResearchState
from pydantic import BaseModel, Field
from typing import List

class ResearchPlan(BaseModel):
    tasks: List[str] = Field(description="A list of 2 to 5 focused research sub-tasks derived from the user query.")
    task_count_rationale: str = Field(description="Reasoning explaining why this specific count of sub-tasks was chosen based on query complexity.")

def task_planner(state: ResearchState):
    query = state['rewritten_query']

    prompt = f"""
    You are a research planner.

    Break the user query into a list of focused research tasks.
    
    Query:
    {query}

    Instructions:
    - Analyze the complexity of the query.
    - Dynamically decide the number of sub-tasks (between 2 and 5) needed to answer it thoroughly.
    - Explain your reasoning for the chosen task count in the 'task_count_rationale' field.
    """

    structured_llm = llm.with_structured_output(ResearchPlan)
    result = structured_llm.invoke(prompt)

    return {
        'research_tasks': result.tasks
    }