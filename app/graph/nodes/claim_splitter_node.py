from pydantic import BaseModel, Field
from typing import List
from app.core.llm import llm
from app.core.logging import logger
from app.graph.state import ResearchState
from app.models.claims import ClaimResult

class ClaimsList(BaseModel):
    claims: List[str] = Field(
        ...,
        description="A list of at most 5 critical, atomic, independently verifiable factual claims extracted from the research report."
    )

def claim_splitter_node(state: ResearchState):
    final_answer = state.get("final_answer", "").strip()
    
    if not final_answer:
        logger.warning("final_answer is empty or missing in state. Returning empty claims list.")
        return {
            "claims": []
        }
        
    prompt = f"""
    You are a fact-checking assistant. Your task is to split the provided research report markdown string into a flat list of atomic, independently verifiable factual claims.

    Rules for splitting:
    - One claim = one verifiable fact (a number, a name, a date, a causal statement)
    - Select only the most critical, high-impact claims that actually require verification
    - Ignore transitional/summary sentences ("In conclusion...", "This shows that...")
    - Ignore opinion framing ("experts believe...", "it is argued that...")
    - Keep each claim under 30 words
    - Return at most 5 claims (or fewer if there are not enough critical factual statements)

    RESEARCH REPORT:
    {final_answer}
    """
    
    logger.info("Splitting final_answer into atomic verifiable claims...")
    
    try:
        structured_llm = llm.with_structured_output(ClaimsList)
        result = structured_llm.invoke(prompt)
        claims = result.claims[:5]
    except Exception as err:
        logger.error(f"Failed to split claims: {err}", exc_info=True)
        claims = []
        
    claim_results = [
        ClaimResult(claim_text=c, status="unverified", confidence=0.0)
        for c in claims
    ]
    
    logger.info(f"Split completed. Extracted {len(claim_results)} claims.")
    
    return {
        "claims": claim_results
    }
