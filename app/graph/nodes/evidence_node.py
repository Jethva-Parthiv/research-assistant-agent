from concurrent.futures import ThreadPoolExecutor
from app.graph.state import ResearchState
from app.services.researcher import research_task
from app.core.logging import logger
from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx
from langchain_core.runnables import RunnableConfig

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

def gather_evidence(state: ResearchState, config: RunnableConfig = None):
    tasks = state.get("research_tasks", [])
    
    # Retrieve main thread's Streamlit context forwarded via config or fallback to current
    ctx = None
    if config:
        ctx = config.get("configurable", {}).get("script_run_ctx")
    if ctx is None:
        ctx = get_script_run_ctx()
        
    def run_with_ctx(t: str):
        if ctx is not None:
            add_script_run_ctx(ctx)
        return run_task_safely(t)
        
    # Run all search tasks concurrently in a thread pool
    with ThreadPoolExecutor(max_workers=max(1, len(tasks))) as executor:
        grouped_results = list(executor.map(run_with_ctx, tasks))
        
    # Append results to existing evidence to support cumulative rounds
    evidence = list(state.get("evidence") or [])
    # Flatten the results while preserving task order
    for results in grouped_results:
        evidence.extend(results)
        
    return {
        "evidence": evidence
    }