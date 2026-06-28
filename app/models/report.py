from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime

class Citation(BaseModel):
    url: str = Field(description="The source URL of the citation")
    title: str = Field(description="The title of the cited source webpage")
    excerpt: str = Field(description="A brief factual snippet/excerpt from the source, under 30 words")

class ReportSection(BaseModel):
    heading: str = Field(description="The header/title of this report section")
    body: str = Field(description="The main markdown body content of this section")
    citations: List[Citation] = Field(default=[], description="List of source citations supporting the claims in this section")

class ReportSchema(BaseModel):
    title: str = Field(description="The title of the research report")
    summary: str = Field(description="A 2-3 sentence executive summary of the findings")
    sections: List[ReportSection] = Field(description="Detailed sections of the research report")
    confidence: Optional[Dict[str, float]] = Field(default=None, description="Quality/confidence scores from self-evaluation if available")
    route_used: Literal["SIMPLE", "DEEP"] = Field(description="The graph execution path used to compile the report")
    generated_at: datetime = Field(default_factory=datetime.now, description="The generation timestamp of the report")
