from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from app.core.llm import get_llm
from app.models.claims import ClaimResult
from langchain_core.runnables import RunnableConfig

class ClaimVerifierOutput(BaseModel):
    status: Literal["verified", "weak", "unverified", "conflicted"] = Field(
        ...,
        description="The verification status of the claim based strictly on the provided passages."
    )
    confidence: float = Field(
        ...,
        description="Confidence score of the verdict between 0.0 and 1.0."
    )
    source_url: Optional[str] = Field(
        None,
        description="The source URL of the best matching passage, or null if no matching passage exists."
    )
    source_passage: Optional[str] = Field(
        None,
        description="The specific sentence from the passage supporting/contradicting the claim (under 40 words), or null if no matching passage exists."
    )
    explanation: str = Field(
        ...,
        description="A one-sentence explanation of the verdict based on the provided passages."
    )

async def verify_claim(claim: str, passages: List[dict], config: RunnableConfig = None) -> ClaimResult:
    # Format the passages into a clear text reference block
    passages_text = ""
    for idx, passage in enumerate(passages):
        url = passage.get("url", "unknown_url")
        text = passage.get("text") or passage.get("raw_content") or passage.get("content") or ""
        passages_text += f"\nPassage [{idx}]:\nURL: {url}\nContent: {text}\n"

    prompt = f"""
    You are a fact-checking assistant. Your task is to verify the following factual claim using ONLY the provided list of source passages.
    Do NOT use any external search or outside knowledge.
    
    CLAIM:
    {claim}
    
    SOURCE PASSAGES:
    {passages_text}
    
    Instructions:
    1. Search through the source passages to find any passage that supports, weakens, or contradicts the claim.
    2. Determine the verification status:
       - "verified": The provided passages explicitly support the claim.
       - "weak": The provided passages suggest the claim might be true but do not explicitly verify it, or provide weak support.
       - "unverified": The passages contain no relevant information to verify or contradict the claim.
       - "conflicted": The passages contain conflicting statements about the claim, or some passages support it while others contradict it.
    3. Extract the `source_url` of the best matching passage. If no matching passage exists, return null.
    4. Extract `source_passage` as the specific sentence from that passage that directly supports/contradicts/relates to the claim (it must be under 40 words). If no matching passage exists, return null.
    5. Set `confidence` as a float between 0.0 and 1.0 indicating your confidence in the verdict.
    6. Provide a one-sentence `explanation` explaining the verdict.
    """

    try:
        model = get_llm()
        structured_llm = model.with_structured_output(ClaimVerifierOutput)
        result = await structured_llm.ainvoke(prompt, config=config)
        
        return ClaimResult(
            claim_text=claim,
            status=result.status,
            confidence=result.confidence,
            source_url=result.source_url,
            source_passage=result.source_passage,
            explanation=result.explanation
        )
    except Exception as err:
        return ClaimResult(
            claim_text=claim,
            status="unverified",
            confidence=0.0,
            source_url=None,
            source_passage=None,
            explanation=f"Error occurred during claim verification: {err}"
        )
