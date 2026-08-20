"""
STAGE 4: INFORMATION EXTRACTION
Pulls structured fields out of resume text: skills, education, experience,
job titles.

NOTE ON SCOPE: skill extraction here (SKILLS_DB keyword match) is used
ONLY to populate extracted_info.skills for display and LLM context — it
is NOT used for scoring/matching. Actual resume-to-JD matching is fully
semantic (see semantic_matching.py + skill_matching.py), so there's no
keyword list to maintain for that purpose. This function stays simple.

Experience-years extraction tries two strategies: explicit "X years"
phrasing, and (more commonly how resumes actually look) summing date
ranges like "November 2025 - January 2026" from work/project sections.
"""
import re
from datetime import datetime
import spacy

_nlp = spacy.load("en_core_web_sm")

# Used only for display/context (extracted_info.skills), not for scoring.
# TODO: expand as needed, or load from a file/DB instead of hardcoding.
SKILLS_DB = [
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    # Frontend
    "react", "html", "css", "node.js",
    # Backend / frameworks
    "fastapi", "django", "flask", "spring boot", "spring security",
    "rest api", "rest apis", "restful api", "restful apis",
    # Databases
    "sql", "postgresql", "mysql", "mongodb", "hibernate",
    # Cloud / infra
    "aws", "azure", "gcp", "docker", "kubernetes",
    # Tools
    "git", "github", "postman",
    # ML / AI
    "machine learning", "deep learning", "nlp", "pandas", "numpy",
    "tensorflow", "pytorch", "spacy", "random forest", "xgboost",
    "vector database", "vector databases", "embedding", "embeddings",
    "rag", "langchain", "pinecone", "chromadb", "sentence-transformers",
    "llm", "llm integration", "generative ai",
    # Auth / architecture
    "oauth2", "jwt", "role-based access control", "microservices",
    # Data / BI
    "excel", "tableau", "power bi",
    # Soft skills
    "communication", "leadership", "project management",
]

EDUCATION_KEYWORDS = [
    "bachelor", "master", "phd", "b.tech", "m.tech", "mba", "b.sc", "m.sc",
    "b.e", "bachelor of engineering", "bachelor's", "master's", "doctorate",
    "associate degree",
]

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def extract_skills(text: str) -> list[str]:
    """Simple keyword match — used only for display/context, not scoring."""
    text_lower = text.lower()
    found = [skill for skill in SKILLS_DB if skill in text_lower]
    return sorted(set(found))


def extract_education(text: str) -> list[str]:
    text_lower = text.lower()
    found = [kw for kw in EDUCATION_KEYWORDS if kw in text_lower]
    return sorted(set(found))


def extract_experience_years(text: str) -> float | None:
    """Two strategies, tried in order:
    1. Explicit statement — "5 years of experience", "3+ years"
    2. Date ranges — "November 2025 - January 2026", "2023 - 2027",
       "2022 - Present" — summed across all matches found. This is how
       most resumes actually present experience (internships, jobs,
       education duration), rather than stating a total up front.

    Note: this sums ALL date ranges found, including education duration —
    it's a rough signal, not a precise "years of professional experience"
    calculation. TODO: separate education date ranges from work-experience
    date ranges (e.g. by section) for a more accurate number.
    """
    text_lower = text.lower()

    explicit_matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text_lower)
    if explicit_matches:
        return max(float(m) for m in explicit_matches)

    range_pattern = re.compile(
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\.?\s*(\d{4})\s*"
        r"[-–—]\s*"
        r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\.?\s*(\d{4}|present|current)",
        re.IGNORECASE,
    )

    total_months = 0
    for start_mon, start_year, end_mon, end_year in range_pattern.findall(text_lower):
        start_m = MONTHS.get(start_mon[:3], 1) if start_mon else 1
        start_y = int(start_year)

        if end_year in ("present", "current"):
            end_y, end_m = datetime.now().year, datetime.now().month
        else:
            end_m = MONTHS.get(end_mon[:3], 12) if end_mon else 12
            end_y = int(end_year)

        months = (end_y - start_y) * 12 + (end_m - start_m)
        if 0 < months < 600:
            total_months += months

    return round(total_months / 12, 1) if total_months else None


def extract_job_titles(text: str) -> list[str]:
    """Placeholder — spaCy's default model doesn't know "job title" as an
    entity type, so this just returns short noun chunks as a rough guess.
    TODO: replace with a job-title gazetteer match or a fine-tuned NER
    model for real accuracy."""
    doc = _nlp(text)
    candidates = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) <= 4]
    return candidates[:5]


def extract_information(cleaned_text: str) -> dict:
    return {
        "skills": extract_skills(cleaned_text),
        "education": extract_education(cleaned_text),
        "experience_years": extract_experience_years(cleaned_text),
        "job_titles": extract_job_titles(cleaned_text),
    }