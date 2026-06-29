import asyncio
from typing import List
from app.graph.state import ResearchState
from app.agents.claim_verifier import verify_claim
from app.models.claims import ClaimResult
from app.core.logging import logger

async def verification_node(state: ResearchState):
    claims: List[ClaimResult] = state.get("claims") or []
    extracted = state.get("extracted_contents") or []
    
    if not claims:
        logger.warning("No claims found in state to verify.")
        return {
            "claims": [],
            "overall_confidence": 0.0
        }
        
    # Convert extracted_contents into List[{"url": str, "text": str}]
    passages = []
    for item in extracted:
        passages.append({
            "url": item.get("url", ""),
            "text": item.get("raw_content", "")
        })
        
    # Helper wrapper to catch exceptions for individual claims
    async def verify_single_claim(claim_obj: ClaimResult) -> ClaimResult:
        try:
            result = await verify_claim(claim_obj.claim_text, passages)
            return result
        except Exception as err:
            logger.error(f"Error verifying claim '{claim_obj.claim_text}': {err}", exc_info=True)
            return ClaimResult(
                claim_text=claim_obj.claim_text,
                status="unverified",
                confidence=0.0,
                source_url=None,
                source_passage=None,
                explanation=f"Exception during verification: {err}"
            )
            
    # Run all verify_claim calls concurrently
    tasks = [verify_single_claim(c) for c in claims]
    verified_claims = await asyncio.gather(*tasks)
    
    # Compute overall_confidence as the mean of all claim confidence scores
    total_confidence = sum(c.confidence for c in verified_claims)
    overall_confidence = total_confidence / len(verified_claims) if verified_claims else 0.0
    
    # Log summary: how many verified / weak / unverified / conflicted
    summary = {
        "verified": 0,
        "weak": 0,
        "unverified": 0,
        "conflicted": 0
    }
    for c in verified_claims:
        status = c.status
        if status in summary:
            summary[status] += 1
        else:
            summary["unverified"] += 1
            
    logger.info(
        f"Claims verification batch complete. "
        f"Verified: {summary['verified']}, "
        f"Weak: {summary['weak']}, "
        f"Unverified: {summary['unverified']}, "
        f"Conflicted: {summary['conflicted']}. "
        f"Overall Confidence: {overall_confidence:.2f}"
    )
    
    return {
        "claims": verified_claims,
        "overall_confidence": overall_confidence
    }
