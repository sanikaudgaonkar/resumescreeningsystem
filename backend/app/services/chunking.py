"""
Splits JD and resume text into meaningful chunks. Resume chunking injects
the nearest preceding heading as context into each bullet.
"""
import re

BULLET_CHARS_PATTERN = re.compile(r"[•●▪◦‣∙·]")
SENTENCE_END_PATTERN = re.compile(r"[.!?:]\s*$")

LOW_URGENCY_KEYWORDS = [
    "preferred", "nice to have", "nice-to-have", "a plus", "is a plus",
    "bonus", "desirable", "optional", "would be great",
]
CRITICAL_URGENCY_KEYWORDS = [
    "must have", "must-have", "required", "essential", "mandatory",
    "minimum of", "at least",
]
HIGH_URGENCY_KEYWORDS = [
    "strong", "proven", "extensive", "advanced", "deep understanding",
    "expert",
]


def classify_urgency(requirement_text: str) -> str:
    text_lower = requirement_text.lower()
    if any(kw in text_lower for kw in LOW_URGENCY_KEYWORDS):
        return "LOW"
    if any(kw in text_lower for kw in CRITICAL_URGENCY_KEYWORDS):
        return "CRITICAL"
    if any(kw in text_lower for kw in HIGH_URGENCY_KEYWORDS):
        return "HIGH"
    return "MEDIUM"


def merge_wrapped_lines(text: str) -> list[str]:
    normalized = BULLET_CHARS_PATTERN.sub("\n\u2022 ", text)
    raw_lines = [l.strip() for l in normalized.split("\n") if l.strip()]

    merged = []
    for line in raw_lines:
        if merged and not SENTENCE_END_PATTERN.search(merged[-1]) and not line.startswith("\u2022"):
            merged[-1] = f"{merged[-1]} {line}".strip()
        else:
            merged.append(line)
    return merged


def chunk_text(text: str, min_words: int = 4) -> list[str]:
    lines = merge_wrapped_lines(text)
    cleaned = [l.replace("\u2022", "").strip(" \t-*") for l in lines]
    return [l.strip() for l in cleaned if len(l.split()) >= min_words]


def chunk_resume(resume_text: str, min_words: int = 5) -> list[str]:
    lines = merge_wrapped_lines(resume_text)

    chunks = []
    context = None
    for line in lines:
        if line.startswith("\u2022"):
            bullet_text = line.replace("\u2022", "").strip()
            if len(bullet_text.split()) < min_words:
                continue
            chunks.append(f"{context}: {bullet_text}" if context else bullet_text)
        else:
            if len(line.split()) >= min_words:
                chunks.append(line)
            context = line

    return chunks


def extract_requirements_section(job_description: str) -> str:
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