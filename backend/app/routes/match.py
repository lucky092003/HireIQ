from fastapi import APIRouter, HTTPException
from app.schemas.match_schema import MatchRequest, MatchResponse
from app.services.langchain_service import match_candidates
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hireiq")


def _build_default_job_description(payload: MatchRequest) -> str:
    skills = payload.skills or []
    cleaned_skills = [skill.strip() for skill in skills if skill and skill.strip()]

    lines = [
        f"Role: {payload.job_title.strip()}" if payload.job_title and payload.job_title.strip() else "Role: General Software Engineer",
        f"Required experience: {payload.experience_years}+ years" if payload.experience_years is not None else "Required experience: Open",
        f"Location: {payload.location.strip()}" if payload.location and payload.location.strip() else "Location: Flexible",
    ]

    if cleaned_skills:
        lines.append("Key skills: " + ", ".join(cleaned_skills))
    else:
        lines.append("Key skills: To be evaluated based on overall profile relevance")

    lines.append("Responsibilities: Deliver production-ready features, collaborate with product and engineering teams, and maintain code quality.")
    return "\n".join(lines)


@router.post("/match", response_model=MatchResponse)
async def match_jd(payload: MatchRequest):
    """
    Find top 10 candidate matches for a job description.
    
    The LangChain agent:
    1. Extracts key requirements from the JD
    2. Generates embeddings
    3. Queries pgvector database for similar candidates
    4. Generates personalized match rationales
    5. Returns ranked results with HireIQ branding
    """
    
    supplied_jd = (payload.job_description or "").strip()
    has_quick_inputs = bool(payload.skills) or payload.experience_years is not None

    if len(supplied_jd) < 10 and not has_quick_inputs:
        raise HTTPException(
            status_code=400,
            detail="Provide a job description or quick inputs (skills/experience years)."
        )

    effective_job_description = supplied_jd if len(supplied_jd) >= 10 else _build_default_job_description(payload)
    
    try:
        logger.info(
            "Processing match request for title=%s location=%s input_mode=%s JD=%s...",
            (payload.job_title or "")[:50],
            (payload.location or "")[:50],
            "full_jd" if len(supplied_jd) >= 10 else "quick_input",
            effective_job_description[:50],
        )
        results = match_candidates(
            job_description=effective_job_description,
            job_title=payload.job_title,
            location=payload.location,
        )
        
        if not results:
            logger.warning("No candidates found in database")
        
        return {"candidates": results}
    
    except Exception as e:
        logger.error(f"Error in match_jd: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process match request. Please try again."
        )