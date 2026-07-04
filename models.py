from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResearchReport(BaseModel):
    title: str = Field(description="The final title of the research report.")
    introduction: str = Field(description="A concise executive summary of the topic.")
    key_findings: List[str] = Field(
        description="A list of findings. The agent found 4 great findings.",
        default_factory=list
    )
    conclusion: str = Field(description="A strategic wrap-up and future outlook.")
    sources: Optional[List[str]] = Field(default=None, description="Optional list of sources used.")
    research_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())