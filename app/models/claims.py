from pydantic import BaseModel, Field

class ClaimResult(BaseModel):
    claim_text: str = Field(description="The atomic independently verifiable factual claim text")
    status: str = Field(default="unverified", description="The verification status of this claim")
    confidence: float = Field(default=0.0, description="The confidence score associated with this claim's verification")
