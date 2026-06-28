from pydantic import BaseModel, Field
from app.core.llm import llm
from app.services.synthesizer import synthesize_answer
from app.graph.state import ResearchState
from app.core.logging import logger

class ReportEvaluation(BaseModel):
    source_coverage: float = Field(..., description="Grade 1.0 to 5.0 for source coverage")
    claim_support: float = Field(..., description="Grade 1.0 to 5.0 for claim support")
    completeness: float = Field(..., description="Grade 1.0 to 5.0 for completeness")

def synthesis_context(state: ResearchState): 
    query = state['rewritten_query']
    evidence = state['evidence']
    result = synthesize_answer(query, evidence)
    
    # Self-evaluation loop step
    eval_prompt = f"""
    You are an expert research evaluator. Assess the following research report compiled for the original user query: "{state['query']}".
    
    REPORT:
    {result}
    
    Score the report on a scale of 1.0 to 5.0 for each of the following parameters:
    - source_coverage: Are there enough distinct sources and viewpoints represented?
    - claim_support: Are all major claims and factual statements supported by explicit citations (e.g. [1], [2])?
    - completeness: Does the report fully answer and address all aspects of the user query?
    """
    
    try:
        structured_llm = llm.with_structured_output(ReportEvaluation)
        eval_result = structured_llm.invoke(eval_prompt)
        
        scores = {
            "source_coverage": float(eval_result.source_coverage),
            "claim_support": float(eval_result.claim_support),
            "completeness": float(eval_result.completeness)
        }
        avg_score = sum(scores.values()) / 3.0
        logger.info(f"Self-evaluation complete. Scores: {scores} (Average: {avg_score:.2f})")
    except Exception as err:
        logger.error(f"Failed to perform self-evaluation: {err}", exc_info=True)
        scores = {
            "source_coverage": 3.0,
            "claim_support": 3.0,
            "completeness": 3.0
        }
        
    return {
        'synthesis_context': result,
        'final_answer': result,
        'confidence_scores': scores
    }