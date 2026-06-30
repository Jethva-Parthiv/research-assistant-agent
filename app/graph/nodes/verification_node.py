import asyncio
import threading
import queue
from typing import List
from app.graph.state import ResearchState
from app.agents.claim_verifier import verify_claim
from app.models.claims import ClaimResult
from app.core.logging import logger

def run_async_synchronously(coro):
    """
    Run an async coroutine synchronously in a separate thread to avoid event loop conflicts 
    under environments with pre-existing event loops (such as Streamlit).
    """
    res_queue = queue.Queue()
    
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(coro)
            res_queue.put((True, res))
        except Exception as e:
            res_queue.put((False, e))
        finally:
            loop.close()
            
    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()
    
    success, val = res_queue.get()
    if success:
        return val
    else:
        raise val

def verification_node(state: ResearchState):
    claims: List[ClaimResult] = state.get("claims") or []
    extracted = state.get("extracted_contents") or []
    evidence = state.get("evidence") or []
    
    if not claims:
        logger.warning("No claims found in state to verify.")
        return {
            "claims": [],
            "overall_confidence": 0.0
        }
        
    # Convert extracted_contents and evidence into List[{"url": str, "text": str}]
    passages = []
    for item in extracted:
        passages.append({
            "url": item.get("url", ""),
            "text": item.get("raw_content", "")
        })
    for item in evidence:
        passages.append({
            "url": item.get("source", ""),
            "text": item.get("content", "")
        })
        
    # Helper wrapper to catch exceptions for individual claims with rate-limit pacing
    async def verify_single_claim(claim_obj: ClaimResult, idx: int) -> ClaimResult:
        delay = idx * 3.5
        if delay > 0:
            await asyncio.sleep(delay)
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
            
    # Run the batch verification concurrently in the helper async closure
    async def run_batch():
        tasks = [verify_single_claim(c, idx) for idx, c in enumerate(claims)]
        return await asyncio.gather(*tasks)
        
    try:
        verified_claims = run_async_synchronously(run_batch())
    except Exception as batch_err:
        logger.error(f"Batch claim verification loop failed: {batch_err}", exc_info=True)
        # Safe fallback: keep existing claims unverified
        verified_claims = [
            ClaimResult(
                claim_text=c.claim_text,
                status="unverified",
                confidence=0.0,
                explanation=f"Batch verification failed: {batch_err}"
            )
            for c in claims
        ]
        
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
