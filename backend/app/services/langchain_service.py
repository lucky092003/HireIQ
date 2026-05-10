import os
import json
import psycopg2
import re
from typing import Optional
from openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client with OpenRouter support
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

# Initialize LLM with LangChain
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
    temperature=0.7
)


class JDExtraction(BaseModel):
    """Extracted JD details"""
    role: str = Field(..., description="Job title/role")
    key_skills: list = Field(..., description="List of required technical skills")
    experience_years: Optional[int] = Field(None, description="Years of experience required")
    experience_level: str = Field(..., description="Experience level (junior/mid/senior)")
    location: Optional[str] = Field(None, description="Location requirement")
    other_requirements: Optional[str] = Field(None, description="Other important requirements")


COMMON_SKILLS = [
    "react", "node.js", "node", "mongodb", "postgresql", "python", "fastapi",
    "django", "java", "spring", "aws", "azure", "gcp", "docker", "kubernetes",
    "typescript", "javascript", "next.js", "sql", "redis", "graphql", "vue", "angular"
]


def _fallback_extract_jd_details(job_description: str, job_title: Optional[str] = None) -> dict:
    combined_text = f"{job_title or ''}\n{job_description}".strip()
    lower = combined_text.lower()
    found_skills = [skill for skill in COMMON_SKILLS if skill in lower]

    years_match = re.search(r"(\d+)\s*\+?\s*(?:years|yrs)", lower)
    years = int(years_match.group(1)) if years_match else None

    if years is None:
        experience_level = "mid"
    elif years <= 2:
        experience_level = "junior"
    elif years <= 5:
        experience_level = "mid"
    else:
        experience_level = "senior"

    return {
        "role": (job_title or job_description[:80]),
        "key_skills": found_skills,
        "experience_years": years,
        "experience_level": experience_level,
        "location": None,
        "other_requirements": None,
    }


def extract_jd_details(job_description: str, job_title: Optional[str] = None) -> dict:
    """Extract structured information from job description using LLM"""
    jd_input = (
        f"Job Title: {job_title}\n\nJob Description:\n{job_description}"
        if job_title
        else job_description
    )
    
    prompt_template = PromptTemplate(
        input_variables=["job_description"],
        template="""You are an expert recruiter. Extract key information from the job description.

Return ONLY valid JSON (no markdown, no backticks) matching this structure:
{{
    "role": "job title",
    "key_skills": ["skill1", "skill2"],
    "experience_years": 2,
    "experience_level": "junior/mid/senior",
    "location": "location or null",
    "other_requirements": "any other requirements"
}}

Job Description:
{job_description}"""
    )
    
    try:
        # Use modern LangChain syntax: prompt | llm
        chain = prompt_template | llm
        response = chain.invoke({"job_description": jd_input})

        # Extract text from response
        if hasattr(response, "content"):
            text = response.content
        else:
            text = str(response)

        # Clean response if wrapped in markdown
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()

        extracted = json.loads(cleaned)
        return extracted
    except Exception:
        # Graceful fallback when LLM is unavailable or output is malformed
        return _fallback_extract_jd_details(job_description, job_title)


def get_embedding(text: str) -> Optional[list]:
    """Generate embedding for text using OpenAI"""
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception:
        return None


def generate_match_rationale(job_description: str, candidate_data: dict) -> str:
    """Generate detailed matching rationale using LLM"""
    
    prompt_template = PromptTemplate(
        input_variables=["job_description", "candidate_data"],
        template="""You are an expert recruiter. Generate a brief matching rationale (2-3 sentences).

Job Description: {job_description}

Candidate: {candidate_data}

Provide a concise rationale explaining why this candidate is a good match."""
    )
    
    try:
        # Use modern LangChain syntax: prompt | llm
        chain = prompt_template | llm
        response = chain.invoke({
            "job_description": job_description,
            "candidate_data": json.dumps(candidate_data)
        })

        # Extract text from response
        if hasattr(response, "content"):
            rationale = response.content
        else:
            rationale = str(response)

        rationale = rationale.strip()

        # Smart truncate: prefer sentence boundary before max_len, otherwise last space
        def _smart_truncate(text: str, max_len: int = 200) -> str:
            if len(text) <= max_len:
                return text
            # look for sentence-ending punctuation before max_len
            cut = text.rfind('.', 0, max_len)
            if cut == -1:
                cut = text.rfind('!', 0, max_len)
            if cut == -1:
                cut = text.rfind('?', 0, max_len)
            if cut != -1 and cut > int(max_len * 0.5):
                return text[: cut + 1]
            # fallback to last space to avoid cutting words
            cut = text.rfind(' ', 0, max_len)
            if cut != -1 and cut > int(max_len * 0.4):
                return text[:cut] + '...'
            # as a last resort, hard cut
            return text[:max_len].rstrip() + '...'

        return _smart_truncate(rationale, 200)
    except Exception:
        skills = str(candidate_data.get("skills") or "").strip()
        experience = candidate_data.get("experience")
        parts = ["Matched by Mike based on profile relevance"]
        if skills:
            parts.append(f"skills: {skills[:80]}")
        if experience is not None:
            parts.append(f"experience: {experience} years")
        return ". ".join(parts) + "."


def _build_candidate_filters(jd_extraction: dict) -> tuple[list[str], dict]:
    where_clauses = []
    params = {}

    location = jd_extraction.get("location")
    if location:
        where_clauses.append("location ILIKE %(location)s")
        params["location"] = f"%{str(location).strip()}%"

    experience_years = jd_extraction.get("experience_years")
    try:
        if experience_years is not None and experience_years != "":
            experience_years = int(float(experience_years))
            min_years = max(0, experience_years - 2)
            max_years = experience_years + 2
            where_clauses.append("experience_years BETWEEN %(min_years)s AND %(max_years)s")
            params["min_years"] = min_years
            params["max_years"] = max_years
    except (TypeError, ValueError):
        pass

    key_skills = [skill for skill in jd_extraction.get("key_skills", []) if skill]
    if key_skills:
        skill_conditions = []
        for index, skill in enumerate(key_skills):
            param_name = f"skill_{index}"
            skill_conditions.append(f"array_to_string(skills, ' ') ILIKE %({param_name})s")
            params[param_name] = f"%{skill}%"
        where_clauses.append("(" + " OR ".join(skill_conditions) + ")")

    return where_clauses, params


def _normalize_skills(skills) -> list[str]:
    if skills is None:
        return []
    if isinstance(skills, str):
        return [item.strip() for item in skills.split(",") if item.strip()]
    if isinstance(skills, (list, tuple)):
        return [str(item).strip() for item in skills if str(item).strip()]
    return [str(skills).strip()]


def _extract_match_details(jd_extraction: dict, skills, location) -> tuple[list[str], bool]:
    jd_skills = [s.lower() for s in jd_extraction.get("key_skills", []) if s]
    candidate_skills = _normalize_skills(skills)
    matched_skills = [skill for skill in candidate_skills if skill.lower() in jd_skills]
    location_match = False

    if jd_extraction.get("location") and location:
        location_match = jd_extraction["location"].lower() in str(location).lower()

    return matched_skills, location_match


def _score_candidate(jd_extraction: dict, candidate: dict, similarity: float) -> float:
    jd_skills = [s.lower() for s in jd_extraction.get("key_skills", []) if s]
    matched_skills = [s.lower() for s in candidate.get("matched_skills", []) if s]

    skill_score = min(20, (len(matched_skills) / max(len(jd_skills), 1)) * 20) if jd_skills else 10

    experience_score = 0
    required_years = jd_extraction.get("experience_years")
    candidate_years = candidate.get("experience")
    if required_years is None or candidate_years is None:
        experience_score = 10
    else:
        gap = abs(candidate_years - required_years)
        experience_score = max(0, 20 - gap * 5)

    location_score = 10 if candidate.get("location_match") else 0

    total = min(100, round(similarity * 70 + skill_score + experience_score + location_score, 2))
    return total


def _fallback_match_without_embeddings(cur, jd_extraction: dict) -> list:
    where_clauses, params = _build_candidate_filters(jd_extraction)
    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

    query = f"""
        SELECT id, name, title, skills, experience_years, location
        FROM candidates
        WHERE {where_sql}
        LIMIT 200;
    """
    cur.execute(query, params)
    rows = cur.fetchall()

    ranked = []
    for row in rows:
        candidate_id, name, title, skills, exp_years, location = row
        candidate_data = {
            "name": name,
            "title": title,
            "skills": skills,
            "experience": exp_years,
            "location": location,
        }

        matched_skills, location_match = _extract_match_details(jd_extraction, skills, location)
        candidate_score = _score_candidate(jd_extraction, {
            "title": title,
            "skills": skills,
            "location": location,
            "experience": exp_years,
            "matched_skills": matched_skills,
            "location_match": location_match,
        }, similarity=0.5)

        ranked.append({
            "id": candidate_id,
            "name": name,
            "title": title,
            "match_score": candidate_score,
            "rationale": generate_match_rationale("", candidate_data),
            "location": location,
            "matched_skills": matched_skills,
            "location_match": location_match,
        })

    ranked.sort(key=lambda item: item["match_score"], reverse=True)
    return ranked[:10]


def match_candidates(
    job_description: str,
    job_title: Optional[str] = None,
    location: Optional[str] = None,
) -> list:
    """
    LangChain agent: Extract JD → Get embedding → Query pgvector → Rank → Generate rationales
    """
    
    # Step 1: Extract JD details
    jd_extraction = extract_jd_details(job_description, job_title)
    if job_title and not jd_extraction.get("role"):
        jd_extraction["role"] = job_title
    if location:
        jd_extraction["location"] = location

    search_text = "\n".join(
        part for part in [job_title, job_description, location] if part and str(part).strip()
    )
    
    # Step 2: Get embedding for full JD
    embedding = get_embedding(search_text)

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()

        if embedding is None:
            return _fallback_match_without_embeddings(cur, jd_extraction)

        vector_literal = "[" + ",".join(str(x) for x in embedding) + "]"
        where_clauses, params = _build_candidate_filters(jd_extraction)
        where_clauses.insert(0, "embedding IS NOT NULL")
        where_sql = " AND ".join(where_clauses)

        query = f'''
        SELECT id, name, title, skills, experience_years, location,
               1 - (embedding <=> %(embedding)s::vector) AS similarity
        FROM candidates
        WHERE {where_sql}
        ORDER BY embedding <=> %(embedding_order)s::vector
        LIMIT 25;
        '''

        query_params = dict(params)
        query_params["embedding"] = vector_literal
        query_params["embedding_order"] = vector_literal

        try:
            cur.execute(query, query_params)
            rows = cur.fetchall()
        except Exception as query_error:
            # Fall back to a simpler SQL path if the vector query fails for any reason.
            print(f"Vector match query failed: {query_error}")
            conn.rollback()
            return _fallback_match_without_embeddings(cur, jd_extraction)

        results = []

        for row in rows:
            candidate_id, name, title, skills, exp_years, location, similarity = row

            candidate_data = {
                "name": name,
                "title": title,
                "skills": skills,
                "experience": exp_years,
                "location": location
            }

            matched_skills, location_match = _extract_match_details(jd_extraction, skills, location)
            match_score = _score_candidate(jd_extraction, {
                "title": title,
                "skills": skills,
                "location": location,
                "experience": exp_years,
                "matched_skills": matched_skills,
                "location_match": location_match,
            }, similarity=similarity)

            rationale = generate_match_rationale(search_text, candidate_data)

            results.append({
                "id": candidate_id,
                "name": name,
                "title": title,
                "match_score": match_score,
                "rationale": rationale,
                "location": location,
                "matched_skills": matched_skills,
                "location_match": location_match,
            })

        results.sort(key=lambda item: item["match_score"], reverse=True)
        return results[:10]

    except Exception as error:
        print(f"match_candidates failed: {error}")
        return []
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()