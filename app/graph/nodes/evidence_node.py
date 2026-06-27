from concurrent.futures import ThreadPoolExecutor
from app.graph.state import ResearchState
from app.agents.researcher import research_task
from app.core.logging import logger

def run_task_safely(task: str):
    """
    Run research_task safely with try-except to handle failures gracefully.
    """
    try:
        results = research_task(task)
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

def gather_evidence(state: ResearchState):
    tasks = state.get("research_tasks", [])
    
    # Run all search tasks concurrently in a thread pool
    with ThreadPoolExecutor(max_workers=max(1, len(tasks))) as executor:
        grouped_results = list(executor.map(run_task_safely, tasks))
        
    evidence = []
    # Flatten the results while preserving task order
    for results in grouped_results:
        evidence.extend(results)
        
    return {
        "evidence": evidence
    }