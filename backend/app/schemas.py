from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProcessCreate(BaseModel):
    organization_id: int
    name: str
    category: str
    description: Optional[str] = ""


class EvidenceOut(BaseModel):
    source_title: Optional[str]
    source_url: Optional[str]
    snippet: Optional[str]

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    business_purpose: Optional[str]
    key_activities: Optional[str]
    current_challenges: Optional[str]
    ai_opportunity: Optional[str]
    automation_potential: Optional[str]
    human_involvement: Optional[str]
    technologies: Optional[str]
    business_benefit: Optional[str]
    risks: Optional[str]
    rationale: Optional[str]
    confidence: Optional[str]

    class Config:
        from_attributes = True


class ProcessOut(BaseModel):
    id: int
    organization_id: int
    name: str
    category: str
    description: Optional[str]
    status: str
    analysis: Optional[AnalysisOut] = None
    evidence: List[EvidenceOut] = []

    class Config:
        from_attributes = True


class OrganizationCreate(BaseModel):
    name: str
    industry: str


class OrganizationOut(BaseModel):
    id: int
    name: str
    industry: str

    class Config:
        from_attributes = True
