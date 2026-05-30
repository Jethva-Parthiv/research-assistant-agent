from app.agents.synthesizer import synthesize_answer
from app.graph.state import ResearchState

def synthesis_context(state : ResearchState) : 
    query = state['rewritten_query']
    evidence = state['evidence']
    result = synthesize_answer(query,evidence)

    return { 'synthesis_context' : result, 'final_answer' : result }