from pydantic import BaseModel, Field
from typing import List
from app.core.llm import llm
from app.graph.state import ResearchState
from app.core.logging import logger

class GapFillingPlan(BaseModel):
    tasks: List[str] = Field(..., description="Exactly 2 focused research queries to fill information gaps in the current report.")

def gap_analysis_node(state: ResearchState):
    query = state.get("query")
    report = state.get("synthesis_context", "")
    retry_count = state.get("retry_count", 0)
    
    prompt = f"""
    You are an expert senior research planner. You are conducting deep research on: "{query}".
    A preliminary report was compiled, but it has content gaps, missing details, or insufficient source coverage.
    
    CURRENT REPORT:
    {report}
    
    Identify what key aspects of the original query "{query}" are missing, incomplete, or poorly cited.
    Then, formulate exactly 2 highly focused, concrete search queries (research sub-tasks) that target this missing information.
    """
    
    logger.info("Executing gap analysis to generate 2 new research tasks...")
    
    try:
        structured_llm = llm.with_structured_output(GapFillingPlan)
        plan = structured_llm.invoke(prompt)
        new_tasks = plan.tasks[:2]
        
        # Ensure we always have exactly 2 tasks
        while len(new_tasks) < 2:
            new_tasks.append(f"More facts about {query}")
    except Exception as err:
        logger.error(f"Failed to generate gap filling tasks: {err}", exc_info=True)
        new_tasks = [
            f"Factual details on {query}",
            f"Sources and context on {query}"
        ]
        
    logger.info(f"Generated gap-filling tasks: {new_tasks}")
    
    return {
        "research_tasks": new_tasks,
        "retry_count": retry_count + 1
    }
