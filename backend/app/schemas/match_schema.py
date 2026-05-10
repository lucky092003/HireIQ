from pydantic import BaseModel
from typing import List, Optional

class MatchRequest(BaseModel):
    job_description: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None

class CandidateResponse(BaseModel):
    id: int
    name: str
    title: str
    match_score: float
    rationale: str
    location: Optional[str] = None
    matched_skills: List[str] = []
    location_match: bool = False

class MatchResponse(BaseModel):
    candidates: List[CandidateResponse]