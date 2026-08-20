"""
STAGE 9/10: HYBRID SCORING

Combines:
- Semantic requirement matching
- Structured skill matching
- Candidate previous-experience matching

IMPORTANT:
"Internship Duration: 6 months"
means the duration of the offered internship.

It does NOT mean:
"Candidate has 6 months of previous experience."

Only explicit previous-experience requirements are used
for the experience component.
"""

import re


# ============================================================
# WEIGHTS
# ============================================================

SEMANTIC_WEIGHT = 0.60
SKILL_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.15


# ============================================================
# SKILL ALIASES
# ============================================================

SKILL_ALIASES = {

    # --------------------------------------------------------
    # UI / UX
    # --------------------------------------------------------

    "figma": {
        "figma",
    },

    "ux research": {
        "ux research",
        "user research",
    },

    "wireframing": {
        "wireframe",
        "wireframes",
        "wireframing",
    },

    "prototyping": {
        "prototype",
        "prototypes",
        "prototyping",
    },

    "design systems": {
        "design system",
        "design systems",
    },

    "interaction design": {
        "interaction design",
    },

    "responsive design": {
        "responsive design",
        "responsive web design",
    },

    "ui design": {
        "ui design",
        "user interface design",
    },

    "ux design": {
        "ux design",
        "user experience design",
    },

    "usability testing": {
        "usability testing",
    },

    "information architecture": {
        "information architecture",
    },

    "accessibility": {
        "accessibility",
        "accessible design",
        "web accessibility",
    },

    "user centered design": {
        "user centered design",
        "user-centered design",
        "user centred design",
        "user-centred design",
    },

    "user flows": {
        "user flow",
        "user flows",
    },

    "wireframes": {
        "wireframe",
        "wireframes",
    },

    "auto layout": {
        "auto layout",
    },

    "components": {
        "components",
        "component design",
    },

    "design thinking": {
        "design thinking",
    },


    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    "html": {
        "html",
    },

    "css": {
        "css",
    },

    "javascript": {
        "javascript",
        "js",
    },

    "typescript": {
        "typescript",
    },

    "react": {
        "react",
        "react.js",
        "reactjs",
    },

    "next.js": {
        "next.js",
        "nextjs",
        "next js",
    },

    "tailwind css": {
        "tailwind",
        "tailwind css",
    },


    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    "node.js": {
        "node.js",
        "nodejs",
        "node js",
    },

    "express": {
        "express",
        "express.js",
    },

    "fastapi": {
        "fastapi",
    },

    "flask": {
        "flask",
    },

    "django": {
        "django",
    },


    # --------------------------------------------------------
    # Languages
    # --------------------------------------------------------

    "python": {
        "python",
    },

    "java": {
        "java",
    },

    "c": {
        "c",
    },

    "c++": {
        "c++",
    },

    "c#": {
        "c#",
        "c sharp",
    },


    # --------------------------------------------------------
    # Databases
    # --------------------------------------------------------

    "sql": {
        "sql",
    },

    "mysql": {
        "mysql",
    },

    "postgresql": {
        "postgresql",
        "postgres",
    },

    "mongodb": {
        "mongodb",
        "mongo db",
    },


    # --------------------------------------------------------
    # Tools
    # --------------------------------------------------------

    "git": {
        "git",
    },

    "github": {
        "github",
        "github.com",
    },

    "postman": {
        "postman",
    },


    # --------------------------------------------------------
    # AI / ML
    # --------------------------------------------------------

    "machine learning": {
        "machine learning",
    },

    "deep learning": {
        "deep learning",
    },

    "nlp": {
        "nlp",
        "natural language processing",
    },

    "pandas": {
        "pandas",
    },

    "numpy": {
        "numpy",
    },

    "tensorflow": {
        "tensorflow",
    },

    "pytorch": {
        "pytorch",
    },

    "rag": {
        "rag",
        "retrieval augmented generation",
    },

    "langchain": {
        "langchain",
    },

    "chromadb": {
        "chromadb",
        "chroma db",
    },

    "llm": {
        "llm",
        "large language model",
    },

    "generative ai": {
        "generative ai",
        "generative artificial intelligence",
    },
}


# ============================================================
# NORMALIZE SKILL
# ============================================================

def normalize_skill(skill: str) -> str:
    """
    Converts a skill or alias into its canonical name.
    """

    skill = skill.lower().strip()

    for canonical, aliases in SKILL_ALIASES.items():

        if skill == canonical:
            return canonical

        if skill in aliases:
            return canonical

    return skill


# ============================================================
# EXTRACT REQUIRED SKILLS FROM JD
# ============================================================

def extract_required_skills(
    job_description: str,
) -> list[str]:
    """
    Extract known skills from the job description.

    This is a structured signal used alongside
    semantic matching.

    It does NOT replace semantic matching.
    """

    if not job_description:
        return []

    text = job_description.lower()

    found = set()

    for canonical, aliases in SKILL_ALIASES.items():

        names_to_check = set(aliases)
        names_to_check.add(canonical)

        for skill in names_to_check:

            pattern = (
                r"(?<!\w)"
                + re.escape(skill.lower())
                + r"(?!\w)"
            )

            if re.search(pattern, text):

                found.add(canonical)

                break

    return sorted(found)


# ============================================================
# COMPUTE SKILL MATCH
# ============================================================

def compute_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
) -> float | None:
    """
    Computes structured skill overlap.

    Returns:
        None -> JD does not contain recognizable skills
        0.0  -> JD has skills but resume has none of them
        1.0  -> all required skills are present
    """

    if not required_skills:
        return None

    resume_normalized = {
        normalize_skill(skill)
        for skill in resume_skills
    }

    required_normalized = {
        normalize_skill(skill)
        for skill in required_skills
    }

    if not required_normalized:
        return None

    matched = (
        resume_normalized
        & required_normalized
    )

    return len(matched) / len(required_normalized)


# ============================================================
# EXTRACT CANDIDATE EXPERIENCE REQUIREMENT
# ============================================================

def extract_required_experience(
    job_description: str,
) -> float | None:
    """
    Extract ONLY previous candidate experience requirements.

    Examples:

    "Minimum 6 months of relevant experience"
        -> 0.5

    "At least 1 year of UI/UX experience"
        -> 1.0

    "2 years of professional experience"
        -> 2.0

    IMPORTANT:

    "Internship Duration: 6 months"
        -> None

    "Internship period: 6 months"
        -> None

    "This internship is for 6 months"
        -> None

    "6-month internship"
        -> None

    This prevents the system from incorrectly treating
    the offered internship duration as candidate experience.
    """

    if not job_description:
        return None

    text = job_description.lower()

    # --------------------------------------------------------
    # Remove offered-role duration statements
    # --------------------------------------------------------

    duration_patterns = [

        # Internship duration: 6 months
        r"\binternship\s+duration\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Internship period: 6 months
        r"\binternship\s+period\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Program duration: 6 months
        r"\bprogram\s+duration\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Role duration: 6 months
        r"\brole\s+duration\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Duration: 6 months
        r"\bduration\s*[:\-]?\s*"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Duration of 6 months
        r"\bduration\s+of\s+"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # This internship is for 6 months
        r"\bthis\s+internship\s+is\s+for\s+"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # Internship is for 6 months
        r"\binternship\s+is\s+for\s+"
        r"\d+(?:\.\d+)?\s*(?:months?|years?)",

        # 6-month internship
        r"\b\d+(?:\.\d+)?\s*[-–—]\s*"
        r"(?:month|months|year|years)\s+internship",

        # 6 month internship
        r"\b\d+(?:\.\d+)?\s+"
        r"(?:month|months|year|years)\s+internship",
    ]

    for pattern in duration_patterns:

        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE,
        )

    # --------------------------------------------------------
    # Candidate experience: YEARS
    # --------------------------------------------------------

    year_pattern = re.compile(
        r"""
        (?:
            minimum\s+
            |
            minimum\s+of\s+
            |
            at\s+least\s+
            |
            required\s+
            |
            preferably\s+
            |
            preferred\s+
        )?

        (\d+(?:\.\d+)?)

        \s*\+?\s*

        years?

        \s*

        (?:of\s+)?

        (?:
            relevant\s+
            |
            professional\s+
            |
            industry\s+
        )?

        experience
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    year_matches = year_pattern.findall(text)

    if year_matches:

        values = [
            float(value)
            for value in year_matches
        ]

        return min(values)

    # --------------------------------------------------------
    # Candidate experience: MONTHS
    # --------------------------------------------------------

    month_pattern = re.compile(
        r"""
        (?:
            minimum\s+
            |
            minimum\s+of\s+
            |
            at\s+least\s+
            |
            required\s+
            |
            preferably\s+
            |
            preferred\s+
        )?

        (\d+)

        \s*

        months?

        \s*

        (?:of\s+)?

        (?:
            relevant\s+
            |
            professional\s+
            |
            industry\s+
        )?

        experience
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    month_matches = month_pattern.findall(text)

    if month_matches:

        values = [
            int(value) / 12
            for value in month_matches
        ]

        return min(values)

    return None


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def compute_experience_match(
    resume_experience_years: float | None,
    required_experience_years: float | None,
) -> float | None:
    """
    Compare candidate's previous experience against
    the JD's required previous experience.

    If JD has no previous-experience requirement,
    return None so experience does not affect the score.
    """

    # No previous experience requirement
    if required_experience_years is None:
        return None

    # JD requires experience but resume has no usable value
    if resume_experience_years is None:
        return 0.0

    if required_experience_years <= 0:
        return 1.0

    ratio = (
        resume_experience_years
        / required_experience_years
    )

    return max(
        0.0,
        min(1.0, ratio),
    )


# ============================================================
# FINAL MATCH SCORE
# ============================================================

def compute_match_score(
    semantic_similarity: float,
    requirement_matches: list[dict],
    resume_skills: list[str] | None = None,
    resume_experience_years: float | None = None,
    job_description: str = "",
) -> dict:
    """
    Calculate the final candidate score.

    Base weights:

        Semantic     = 60%
        Skills       = 25%
        Experience   = 15%

    However, if the JD does not contain a skill requirement
    or previous-experience requirement, that component is
    excluded and the remaining weights are normalized.

    Example:

        JD has only semantic requirements

        semantic = 0.60

        final =
            semantic / 0.60

        This prevents missing/irrelevant categories from
        artificially lowering the candidate's score.
    """

    resume_skills = resume_skills or []

    # ========================================================
    # 1. SEMANTIC SCORE
    # ========================================================

    semantic_score = max(
        0.0,
        min(
            1.0,
            semantic_similarity,
        ),
    )

    # ========================================================
    # 2. SKILL SCORE
    # ========================================================

    required_skills = extract_required_skills(
        job_description
    )

    skill_score = compute_skill_match(
        resume_skills,
        required_skills,
    )

    # ========================================================
    # 3. PREVIOUS EXPERIENCE SCORE
    # ========================================================

    required_experience_years = (
        extract_required_experience(
            job_description
        )
    )

    experience_score = compute_experience_match(
        resume_experience_years,
        required_experience_years,
    )

    # ========================================================
    # 4. DYNAMIC WEIGHTING
    # ========================================================

    components = [
        (
            "semantic",
            semantic_score,
            SEMANTIC_WEIGHT,
        )
    ]

    # Only include skill score when the JD actually
    # contains recognizable skill requirements.
    if skill_score is not None:

        components.append(
            (
                "skills",
                skill_score,
                SKILL_WEIGHT,
            )
        )

    # Only include experience when the JD explicitly
    # asks for previous candidate experience.
    if experience_score is not None:

        components.append(
            (
                "experience",
                experience_score,
                EXPERIENCE_WEIGHT,
            )
        )

    # ========================================================
    # Normalize active weights
    # ========================================================

    total_weight = sum(
        weight
        for _, _, weight in components
    )

    overall_score = sum(
        score * weight
        for _, score, weight in components
    ) / total_weight

    overall_score = max(
        0.0,
        min(
            1.0,
            overall_score,
        ),
    )

    # ========================================================
    # 5. MATCHED / MISSING REQUIREMENTS
    # ========================================================

    matched = [
        r["requirement"]
        for r in requirement_matches
        if r.get("evidence")
    ]

    missing = [
        r["requirement"]
        for r in requirement_matches
        if not r.get("evidence")
    ]

    # ========================================================
    # 6. RESULT
    # ========================================================

    return {

        "overall_score": round(
            overall_score,
            2,
        ),

        "semantic_similarity": round(
            semantic_score,
            2,
        ),

        "skill_score": (
            round(skill_score, 2)
            if skill_score is not None
            else None
        ),

        "experience_score": (
            round(experience_score, 2)
            if experience_score is not None
            else None
        ),

        "matched_requirements": matched,

        "missing_requirements": missing,

        "requirement_matches":
            requirement_matches,
    }