import asyncio
from app.graph.state import ResearchState
from app.agents.researcher import research_task
from app.core.logging import logger

async def run_task_safely(task: str):
    """
    Run research_task in a separate thread to support parallel execution.
    Gracefully handles failure by inserting an empty Evidence object.
    """
    try:
        results = await asyncio.to_thread(research_task, task)
        # If Tavily search returned no results, insert an empty Evidence structure
        if not results:
            return [
                {
                    "task": task,
                    "source": "",
                    "content": ""
                }
            ]
        return results
    except Exception as error:
        logger.error(f"Error researching task '{task}': {error}", exc_info=True)
        return [
            {
                "task": task,
                "source": "",
                "content": ""
            }
        ]

async def gather_evidence(state: ResearchState):
    tasks = state.get("research_tasks", [])
    
    # Schedule all Tavily API calls concurrently
    jobs = [run_task_safely(task) for task in tasks]
    grouped_results = await asyncio.gather(*jobs)
    
    evidence = []
    # Flatten the results while preserving task order
    for results in grouped_results:
        evidence.extend(results)
        
    return {
        "evidence": evidence
    }