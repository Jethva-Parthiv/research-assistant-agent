from app.graph.state import ResearchState
from app.agents.classifier import classify_query
from app.graph.workflows import deep_research
from app.graph.workflows import simple_research
from app.core.logging import logger

def router_node(state):

    route = classify_query(
        state["query"]
    )

    return {
        "route": route
    }


def route_decision(state):

    route = state["route"]

    if route in ["DEEP","deep"]:
        return "deep"

    return "simple"


def simple_workflow_node(state):

    logger.info(
        "Simple Workflow Initiated !!"
    )

    result = simple_research.research_graph.invoke(
        {
            "query": state["query"]
        }
    )


    
    return result


def deep_workflow_node(state):

    logger.info(
        "Deep Workflow Initiated !!"
    )
    
    result = deep_research.research_graph.invoke(
        {
            "query": state["query"]
        }
    )


    return result