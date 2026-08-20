"""
Splits JD and resume text into meaningful chunks for per-requirement
semantic matching. Handles bullets both on their own line and mid-line
(some PDF extractions collapse bullets without real newlines).
"""
import re

BULLET_CHARS_PATTERN = re.compile(r"[•▪◦‣∙·]")


def chunk_text(text: str, min_words: int = 4) -> list[str]:
    normalized = BULLET_CHARS_PATTERN.sub("\n", text)
    lines = [l.strip(" \t-*") for l in normalized.split("\n")]
    return [l.strip() for l in lines if len(l.split()) >= min_words]


def extract_requirements_section(job_description: str) -> str:
    """Finds the 'Requirements'/'Qualifications'/etc. section of a JD.
    Falls back to the full JD if no such heading is found."""
    pattern = re.compile(
        r"(requirements|qualifications|what you.?ll need|"
        r"what we.?re looking for|must have)[:\s]*\n(.*?)(\n\s*\n|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(job_description)
    return match.group(2) if match else job_description


def chunk_job_description(job_description: str) -> list[str]:
    section = extract_requirements_section(job_description)
    chunks = chunk_text(section)
    return chunks if chunks else chunk_text(job_description)


def chunk_resume(resume_text: str) -> list[str]:
    return chunk_text(resume_text, min_words=5)