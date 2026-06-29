from pydantic import BaseModel, Field
from typing import Optional, Literal

class ClaimResult(BaseModel):
    claim_text: str = Field(description="The atomic independently verifiable factual claim text")
    status: Literal["verified", "weak", "unverified", "conflicted"] = Field(
        default="unverified",
        description="The verification status of the claim"
    )
    confidence: float = Field(
        default=0.0,
        description="The verification confidence score between 0.0 and 1.0"
    )
    source_url: Optional[str] = Field(
        default=None,
        description="The URL of the best matching passage supporting or contradicting the claim, or null"
    )
    source_passage: Optional[str] = Field(
        default=None,
        description="The specific sentence from the passage supporting/contradicting the claim (under 40 words), or null"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="One sentence explaining the verdict"
    )
