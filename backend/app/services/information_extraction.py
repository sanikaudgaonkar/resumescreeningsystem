"""
STAGE 4: INFORMATION EXTRACTION

Extracts structured information from resumes:

- Skills
- Education
- Professional experience
- Experience duration
- Job titles

Important:
Experience duration is calculated from work/internship
date ranges only. Education and project dates are not
counted as professional experience.
"""

import re
from datetime import datetime


# ============================================================
# SKILLS
# ============================================================

SKILLS_DB = [

    # -------------------------
    # UI / UX
    # -------------------------

    "figma",
    "figjam",
    "adobe xd",
    "sketch",
    "photoshop",
    "illustrator",

    "ui design",
    "ux design",
    "ui/ux",
    "user experience",
    "user interface",

    "wireframing",
    "wireframes",
    "wireframe",

    "prototyping",
    "prototype",
    "prototypes",

    "user research",
    "ux research",
    "usability testing",

    "interaction design",
    "visual design",
    "design systems",
    "design system",

    "user flows",
    "user flow",

    "information architecture",

    "responsive design",
    "responsive web design",

    "usability",
    "accessibility",

    "design thinking",

    # -------------------------
    # Frontend
    # -------------------------

    "html",
    "css",
    "javascript",
    "typescript",
    "react",
    "next.js",
    "tailwind",
    "tailwind css",

    # -------------------------
    # Backend
    # -------------------------

    "node.js",
    "node",
    "express",
    "fastapi",
    "flask",
    "django",

    # -------------------------
    # Languages
    # -------------------------

    "python",
    "java",
    "c",
    "c++",
    "c#",

    # -------------------------
    # Databases
    # -------------------------

    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    # -------------------------
    # Tools
    # -------------------------

    "git",
    "github",
    "postman",

    # -------------------------
    # AI / ML
    # -------------------------

    "machine learning",
    "deep learning",
    "nlp",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch",
    "rag",
    "langchain",
    "chromadb",
    "llm",
    "generative ai",

    # -------------------------
    # Soft skills
    # -------------------------

    "communication",
    "leadership",
    "teamwork",
    "collaboration",
]


# ============================================================
# EDUCATION
# ============================================================

EDUCATION_KEYWORDS = [
    "bachelor",
    "master",
    "phd",
    "b.tech",
    "m.tech",
    "mba",
    "b.sc",
    "m.sc",
    "b.e",
    "bachelor of engineering",
    "bachelor's",
    "master's",
    "doctorate",
    "associate degree",
]


# ============================================================
# MONTHS
# ============================================================

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


# ============================================================
# EXPERIENCE SECTION DETECTION
# ============================================================

EXPERIENCE_HEADINGS = [
    "experience",
    "work experience",
    "professional experience",
    "internship",
    "internships",
    "employment",
    "work history",
    "career history",
]


NON_EXPERIENCE_HEADINGS = [
    "education",
    "projects",
    "academic projects",
    "certifications",
    "skills",
    "achievements",
    "awards",
    "activities",
    "extracurricular",
]


def get_experience_section(text: str) -> str:
    """
    Extract the experience section from a resume.

    Stops when another major resume section begins.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    inside_experience = False
    experience_lines = []

    for line in lines:

        normalized = line.lower().strip(" :")

        # Start experience section
        if any(
            heading == normalized
            for heading in EXPERIENCE_HEADINGS
        ):
            inside_experience = True
            continue

        # Stop at another major section
        if inside_experience and any(
            heading == normalized
            for heading in NON_EXPERIENCE_HEADINGS
        ):
            break

        if inside_experience:
            experience_lines.append(line)

    return "\n".join(experience_lines)


# ============================================================
# SKILL EXTRACTION
# ============================================================

def extract_skills(text: str) -> list[str]:
    """
    Extract skills from resume text.

    Used for structured information and later
    hybrid matching.
    """

    text_lower = text.lower()

    found = []

    for skill in SKILLS_DB:

        # Word-boundary matching prevents things such as
        # "c" accidentally matching every word containing c.
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text_lower):
            found.append(skill)

    return sorted(set(found))


# ============================================================
# EDUCATION EXTRACTION
# ============================================================

def extract_education(text: str) -> list[str]:
    """
    Extract education-related terms.
    """

    text_lower = text.lower()

    found = []

    for keyword in EDUCATION_KEYWORDS:

        if keyword in text_lower:
            found.append(keyword)

    return sorted(set(found))


# ============================================================
# DATE RANGE EXTRACTION
# ============================================================

DATE_RANGE_PATTERN = re.compile(
    r"""
    (?:
        (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)
        \.? \s*
    )?
    (\d{4})

    \s*
    [-–—]
    \s*

    (?:
        (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)
        \.? \s*
    )?

    (\d{4}|present|current)
    """,
    re.IGNORECASE | re.VERBOSE,
)


def parse_date_range(
    start_month,
    start_year,
    end_month,
    end_year,
):
    """
    Convert a date range into number of months.
    """

    start_year = int(start_year)

    start_month_num = (
        MONTHS.get(
            start_month[:3].lower(),
            1,
        )
        if start_month
        else 1
    )

    if end_year.lower() in (
        "present",
        "current",
    ):

        now = datetime.now()

        end_year_num = now.year
        end_month_num = now.month

    else:

        end_year_num = int(end_year)

        end_month_num = (
            MONTHS.get(
                end_month[:3].lower(),
                12,
            )
            if end_month
            else 12
        )

    months = (
        (end_year_num - start_year) * 12
        + (end_month_num - start_month_num)
    )

    if months <= 0:
        return None

    # Prevent obviously broken ranges
    if months > 120:
        return None

    return months


# ============================================================
# EXPERIENCE EXTRACTION
# ============================================================

def extract_experience_years(
    text: str
) -> float | None:
    """
    Calculate professional experience ONLY from the
    resume's experience section.

    Education and project dates are ignored.
    """

    experience_text = get_experience_section(
        text
    )

    if not experience_text:
        return None

    total_months = 0

    for match in DATE_RANGE_PATTERN.finditer(
        experience_text
    ):

        (
            start_month,
            start_year,
            end_month,
            end_year,
        ) = match.groups()

        months = parse_date_range(
            start_month,
            start_year,
            end_month,
            end_year,
        )

        if months:
            total_months += months

    if total_months == 0:
        return None

    return round(
        total_months / 12,
        1,
    )


# ============================================================
# JOB TITLE EXTRACTION
# ============================================================

JOB_TITLE_PATTERN = re.compile(
    r"""
    (?:
        ui/?ux
        |
        frontend
        |
        front-end
        |
        backend
        |
        back-end
        |
        full[- ]stack
        |
        software
        |
        product
        |
        graphic
        |
        web
        |
        data
        |
        machine learning
    )
    \s+
    (?:
        designer
        |
        developer
        engineer
        intern
        analyst
        researcher
        scientist
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def extract_job_titles(
    text: str
) -> list[str]:
    """
    Extract likely job titles using common
    role-title patterns.
    """

    titles = JOB_TITLE_PATTERN.findall(
        text
    )

    # The regex uses groups, so rebuild from
    # actual matching spans instead.
    matches = JOB_TITLE_PATTERN.finditer(
        text
    )

    result = [
        match.group(0).strip()
        for match in matches
    ]

    return sorted(
        set(result),
        key=str.lower,
    )


# ============================================================
# MAIN INFORMATION EXTRACTION
# ============================================================

def extract_information(
    cleaned_text: str
) -> dict:

    return {

        "skills": extract_skills(
            cleaned_text
        ),

        "education": extract_education(
            cleaned_text
        ),

        "experience_years":
            extract_experience_years(
                cleaned_text
            ),

        "job_titles":
            extract_job_titles(
                cleaned_text
            ),
    }