from app.graph.state import ResearchState
from app.agents.researcher import research_task

def gather_evidence(state : ResearchState):

    evidence = []

    for task in state["research_tasks"]:

        evidence.extend(
            research_task(task)
        )

    return {
        "evidence": evidence
    }