"""
TEXT CHUNKING

Splits job descriptions and resumes into meaningful chunks
for semantic matching.

JD handling:
- Detects common JD sections
- Includes candidate-related sections
- Excludes salary, benefits, PPO, company information
- Excludes job/internship metadata such as internship duration
- Handles bullets, numbered lists, and collapsed PDF bullets
- Removes duplicate/empty chunks

Resume handling:
- Splits resume text into meaningful evidence chunks
"""

import re


# ============================================================
# BULLETS
# ============================================================

BULLET_CHARS_PATTERN = re.compile(
    r"[•▪◦‣∙·●○]"
)


# ============================================================
# JD SECTION HEADINGS
# ============================================================

JD_SECTION_PATTERN = re.compile(
    r"^\s*(?:"
    r"requirements?|"
    r"qualifications?|"
    r"responsibilities?|"
    r"what you.?ll do|"
    r"what you.?ll need|"
    r"what we.?re looking for|"
    r"must have|"
    r"preferred qualifications?|"
    r"preferred skills?|"
    r"nice to have|"
    r"skills?|"
    r"experience|"
    r"education|"
    r"about the role|"
    r"role overview|"
    r"job responsibilities?|"
    r"key responsibilities?|"
    r"candidate profile|"
    r"who you are|"
    r"who we are looking for"
    r")\s*:?\s*$",
    re.IGNORECASE,
)


# ============================================================
# JD SECTIONS
# ============================================================

INCLUDED_SECTIONS = {
    "requirements",
    "qualifications",
    "responsibilities",
    "preferred",
    "skills",
    "experience",
    "education",
    "general",
}


# ============================================================
# EXCLUDED SECTIONS
# ============================================================

EXCLUDED_SECTION_KEYWORDS = [
    "what we offer",
    "what you get",
    "benefits",
    "perks",
    "salary",
    "compensation",
    "stipend",
    "pay",
    "package",
    "employee benefits",
    "why join us",
    "about us",
    "about the company",
    "company overview",
    "our company",
    "company culture",
    "work location",
    "job location",
    "location",
    "ppo",
    "what happens next",
    "application process",
    "how to apply",
    "how to apply?",
]


# ============================================================
# NON-MATCHING JD INFORMATION
# ============================================================

NON_REQUIREMENT_PATTERNS = [

    # --------------------------------------------------------
    # Internship / program duration
    # --------------------------------------------------------

    r"^internship\s+duration\b",
    r"^internship\s+period\b",
    r"^internship\s+length\b",
    r"^program\s+duration\b",
    r"^program\s+length\b",
    r"^role\s+duration\b",

    r"^duration\s*[:\-]",
    r"^duration\s+of\s+the\s+internship\b",

    r"^internship\s*[:\-]\s*\d+",
    r"^internship\s+is\s+for\b",
    r"^this\s+internship\s+is\s+for\b",

    # Examples:
    # "6-month internship"
    # "6 months internship"
    # "6 month internship"
    r"^\d+\s*[-]?\s*months?\s+internship\b",
    r"^\d+\s*[-]?\s*month\s+intern\b",

    # Examples:
    # "Internship - 6 months"
    # "Internship: 6 months"
    r"^internship\s*[-:]\s*\d+\s*months?\b",

    # --------------------------------------------------------
    # Job metadata
    # --------------------------------------------------------

    r"^employment\s+type\s*[:\-]",
    r"^job\s+type\s*[:\-]",
    r"^work\s+mode\s*[:\-]",
    r"^work\s+type\s*[:\-]",
    r"^joining\s+date\s*[:\-]",
    r"^start\s+date\s*[:\-]",
    r"^application\s+deadline\s*[:\-]",

    # --------------------------------------------------------
    # Salary / compensation
    # --------------------------------------------------------

    r"^salary\s*[:\-]",
    r"^stipend\s*[:\-]",
    r"^compensation\s*[:\-]",
    r"^pay\s*[:\-]",

]


# ============================================================
# NON-REQUIREMENT KEYWORDS
# ============================================================

NON_REQUIREMENT_KEYWORDS = [
    "internship duration",
    "internship period",
    "internship length",
    "program duration",
    "program length",
    "role duration",
    "duration of the internship",
    "employment type",
    "job type",
    "work mode",
    "work type",
    "joining date",
    "start date",
    "application deadline",
]


# ============================================================
# CHECK NON-REQUIREMENT
# ============================================================

def is_non_requirement(text: str) -> bool:
    """
    Determines whether a JD chunk is job metadata rather than
    an actual candidate requirement.

    Example:

        Internship Duration: 6 Months
        -> True

        Strong proficiency in Figma
        -> False
    """

    if not text:
        return True

    normalized = re.sub(
        r"\s+",
        " ",
        text.lower().strip(),
    )

    # --------------------------------------------------------
    # Pattern-based checks
    # --------------------------------------------------------

    for pattern in NON_REQUIREMENT_PATTERNS:

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        ):
            return True

    # --------------------------------------------------------
    # Keyword-based checks
    # --------------------------------------------------------

    for keyword in NON_REQUIREMENT_KEYWORDS:

        if normalized.startswith(keyword):
            return True

    # --------------------------------------------------------
    # Duration-only metadata
    # --------------------------------------------------------

    duration_patterns = [

        # "6 months internship"
        r"^\d+\s*months?\s+internship\b",

        # "6-month internship"
        r"^\d+\s*-\s*month\s+internship\b",

        # "6 months of internship"
        r"^\d+\s*months?\s+of\s+internship\b",

        # "6 month internship duration"
        r"^\d+\s*months?\s+internship\s+duration\b",
    ]

    for pattern in duration_patterns:

        if re.search(
            pattern,
            normalized,
            re.IGNORECASE,
        ):
            return True

    return False


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text: str) -> str:
    """
    Basic cleanup of extracted PDF/DOCX text.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Tabs -> spaces
    text = text.replace("\t", " ")

    # Normalize spaces
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text,
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


# ============================================================
# SECTION CLASSIFICATION
# ============================================================

def classify_section_heading(
    heading: str
) -> str:
    """
    Converts a JD heading into a normalized section type.

    Returns:

        requirements
        responsibilities
        preferred
        skills
        experience
        education
        excluded
        general
    """

    normalized = re.sub(
        r"\s+",
        " ",
        heading.lower().strip().rstrip(":"),
    )

    # --------------------------------------------------------
    # EXCLUDED
    # --------------------------------------------------------

    for keyword in EXCLUDED_SECTION_KEYWORDS:

        if keyword in normalized:
            return "excluded"

    # --------------------------------------------------------
    # RESPONSIBILITIES
    # --------------------------------------------------------

    if (
        "responsib" in normalized
        or "what you'll do" in normalized
        or "what you will do" in normalized
        or "what you do" in normalized
        or "job duties" in normalized
        or "key duties" in normalized
    ):
        return "responsibilities"

    # --------------------------------------------------------
    # PREFERRED
    # --------------------------------------------------------

    if (
        "preferred" in normalized
        or "nice to have" in normalized
        or "bonus" in normalized
    ):
        return "preferred"

    # --------------------------------------------------------
    # REQUIREMENTS
    # --------------------------------------------------------

    if (
        "requirement" in normalized
        or "qualification" in normalized
        or "must have" in normalized
        or "what you'll need" in normalized
        or "what you will need" in normalized
        or "candidate profile" in normalized
        or "who you are" in normalized
        or "who we're looking for" in normalized
    ):
        return "requirements"

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    if "skill" in normalized:
        return "skills"

    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    if "experience" in normalized:
        return "experience"

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    if "education" in normalized:
        return "education"

    # --------------------------------------------------------
    # ROLE INFORMATION
    # --------------------------------------------------------

    if (
        "about the role" in normalized
        or "role overview" in normalized
    ):
        return "responsibilities"

    return "general"


# ============================================================
# BULLET SPLITTING
# ============================================================

def split_bullets(text: str) -> list[str]:
    """
    Splits text using:

    - bullet characters
    - numbered lists
    - dash bullets
    - line breaks

    Handles PDF extraction where bullets appear
    in the middle of a line.
    """

    text = clean_text(text)

    # Convert bullet characters to line breaks
    text = BULLET_CHARS_PATTERN.sub(
        "\n",
        text,
    )

    # Numbered lists
    text = re.sub(
        r"(?<!^)\s+(?=\d+[\.\)]\s+)",
        "\n",
        text,
    )

    # Dash bullets
    text = re.sub(
        r"(?<!^)\s+(?=-\s+)",
        "\n",
        text,
    )

    lines = text.split("\n")

    chunks = []

    for line in lines:

        line = line.strip()

        # Remove bullet / numbering markers
        line = re.sub(
            r"^(?:[-*•▪◦‣∙·●○]|\d+[\.\)])\s*",
            "",
            line,
        )

        line = line.strip()

        if line:
            chunks.append(line)

    return chunks


# ============================================================
# GENERIC TEXT CHUNKING
# ============================================================

def chunk_text(
    text: str,
    min_words: int = 4
) -> list[str]:
    """
    Generic text chunking.
    """

    chunks = split_bullets(text)

    return [
        chunk
        for chunk in chunks
        if len(chunk.split()) >= min_words
    ]


# ============================================================
# JD SECTION EXTRACTION
# ============================================================

def extract_jd_sections(
    job_description: str
) -> dict[str, str]:
    """
    Extract sections from a job description.

    Excluded sections such as:

        What We Offer
        Benefits
        Salary
        PPO
        Company Information

    are ignored.
    """

    text = clean_text(
        job_description
    )

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    sections = {}

    current_section = "general"

    sections[current_section] = []

    for line in lines:

        section_type = classify_section_heading(
            line
        )

        # ----------------------------------------------------
        # Section heading
        # ----------------------------------------------------

        if section_type != "general":

            current_section = section_type

            if current_section != "excluded":

                sections.setdefault(
                    current_section,
                    [],
                )

            continue

        # ----------------------------------------------------
        # Ignore excluded sections
        # ----------------------------------------------------

        if current_section == "excluded":
            continue

        sections.setdefault(
            current_section,
            [],
        )

        sections[current_section].append(
            line
        )

    return {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if value
    }


# ============================================================
# EXTRACT RELEVANT JD CONTENT
# ============================================================

def extract_requirements_section(
    job_description: str
) -> str:
    """
    Extract candidate-related content.

    Included:

    - responsibilities
    - requirements
    - qualifications
    - skills
    - experience
    - education
    - preferred qualifications

    Excluded:

    - salary
    - stipend
    - benefits
    - PPO
    - company information
    - application process
    """

    sections = extract_jd_sections(
        job_description
    )

    relevant_sections = []

    structured_sections = [
        "requirements",
        "responsibilities",
        "preferred",
        "skills",
        "experience",
        "education",
    ]

    for section_name in structured_sections:

        if section_name in sections:

            content = sections[
                section_name
            ].strip()

            if content:
                relevant_sections.append(
                    content
                )

    # If structured sections exist,
    # use only those.
    if relevant_sections:

        return "\n".join(
            relevant_sections
        )

    # Otherwise use full JD.
    return job_description


# ============================================================
# DUPLICATE REMOVAL
# ============================================================

def remove_duplicates(
    chunks: list[str]
) -> list[str]:
    """
    Remove duplicate chunks while
    preserving order.
    """

    seen = set()

    unique = []

    for chunk in chunks:

        normalized = re.sub(
            r"\s+",
            " ",
            chunk.lower(),
        ).strip()

        if not normalized:
            continue

        if normalized not in seen:

            seen.add(normalized)

            unique.append(
                chunk
            )

    return unique


# ============================================================
# JD REQUIREMENT CHUNKING
# ============================================================

def chunk_job_description(
    job_description: str
) -> list[str]:
    """
    Converts a complete JD into individual
    candidate requirements.

    IMPORTANT:

    Job metadata is removed before semantic
    embeddings are generated.

    Example:

        Internship Duration: 6 Months

    will NOT become a semantic requirement.
    """

    if not job_description:
        return []

    # --------------------------------------------------------
    # Extract candidate-related sections
    # --------------------------------------------------------

    relevant_text = extract_requirements_section(
        job_description
    )

    # --------------------------------------------------------
    # Split into chunks
    # --------------------------------------------------------

    chunks = chunk_text(
        relevant_text,
        min_words=3,
    )

    # --------------------------------------------------------
    # Remove section headings
    # --------------------------------------------------------

    chunks = [
        chunk
        for chunk in chunks
        if not JD_SECTION_PATTERN.match(
            chunk
        )
    ]

    # --------------------------------------------------------
    # Remove job metadata
    # --------------------------------------------------------

    filtered_chunks = []

    for chunk in chunks:

        if is_non_requirement(
            chunk
        ):
            continue

        filtered_chunks.append(
            chunk
        )

    # --------------------------------------------------------
    # Remove accidental offer/benefit
    # content that slipped into a line
    # --------------------------------------------------------

    excluded_content_keywords = [
        "₹",
        "stipend",
        "salary",
        "compensation",
        "ppo",
        "perks",
        "benefits",
        "what we offer",
        "remote working opportunity",
        "work from home opportunity",
    ]

    final_chunks = []

    for chunk in filtered_chunks:

        normalized = chunk.lower()

        should_exclude = any(
            keyword in normalized
            for keyword
            in excluded_content_keywords
        )

        if not should_exclude:

            final_chunks.append(
                chunk
            )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    final_chunks = remove_duplicates(
        final_chunks
    )

    return final_chunks


# ============================================================
# RESUME CHUNKING
# ============================================================

def chunk_resume(
    resume_text: str
) -> list[str]:
    """
    Split resume into meaningful evidence chunks.

    Portfolio / LinkedIn / GitHub links are preserved
    even if they contain very few words.
    """

    if not resume_text:
        return []

    chunks = split_bullets(
        resume_text
    )

    final_chunks = []

    for chunk in chunks:

        chunk = chunk.strip()

        if not chunk:
            continue

        # ----------------------------------------------------
        # Always preserve URLs
        # ----------------------------------------------------

        if re.search(
            r"https?://",
            chunk,
            re.IGNORECASE,
        ):

            final_chunks.append(
                chunk
            )

            continue

        # ----------------------------------------------------
        # Normal resume chunks
        # ----------------------------------------------------

        if len(chunk.split()) >= 5:

            final_chunks.append(
                chunk
            )

    return remove_duplicates(
        final_chunks
    )