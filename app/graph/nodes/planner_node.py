from app.agents.planner import create_plan
from app.graph.state import ResearchState

def task_planner(state : ResearchState) : 
    query = state['rewritten_query']

    tasks = create_plan(query)

    return { 'research_tasks' : tasks }