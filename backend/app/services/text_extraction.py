"""
STAGE 2: TEXT EXTRACTION

Extracts text from:
- PDF
- DOCX

Also extracts hyperlinks from both formats.

This is important for resumes because portfolio,
LinkedIn, GitHub and other links may appear as
clickable hyperlinks rather than normal text.
"""

import os
import re

import pdfplumber
import pymupdf

from docx import Document


# ============================================================
# URL REGEX
# ============================================================

URL_PATTERN = re.compile(
    r"https?://[^\s<>\"]+",
    re.IGNORECASE,
)


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(
    file_path: str,
) -> str:

    text = ""

    try:

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text() or ""

                if page_text.strip():
                    text += page_text + "\n"

    except Exception:
        text = ""

    # --------------------------------------------------------
    # Fallback to PyMuPDF
    # --------------------------------------------------------

    if len(text.strip()) < 30:

        text = ""

        doc = pymupdf.open(file_path)

        for page in doc:

            text += (
                page.get_text()
                + "\n"
            )

        doc.close()

    return text.strip()


# ============================================================
# PDF HYPERLINK EXTRACTION
# ============================================================

def extract_links_from_pdf(
    file_path: str,
) -> list[str]:

    links = []

    try:

        doc = pymupdf.open(file_path)

        for page in doc:

            page_links = page.get_links()

            for link in page_links:

                uri = link.get("uri")

                if uri:
                    links.append(
                        uri.strip()
                    )

        doc.close()

    except Exception as e:

        print(
            f"PDF link extraction failed: {e}"
        )

    return list(
        dict.fromkeys(links)
    )


# ============================================================
# DOCX TEXT EXTRACTION
# ============================================================

def extract_text_from_docx(
    file_path: str,
) -> str:

    doc = Document(file_path)

    text_parts = []

    # --------------------------------------------------------
    # Normal paragraphs
    # --------------------------------------------------------

    for paragraph in doc.paragraphs:

        text = paragraph.text.strip()

        if text:
            text_parts.append(text)

    # --------------------------------------------------------
    # Tables
    # --------------------------------------------------------

    for table in doc.tables:

        for row in table.rows:

            row_text = []

            for cell in row.cells:

                cell_text = cell.text.strip()

                if cell_text:
                    row_text.append(
                        cell_text
                    )

            if row_text:

                text_parts.append(
                    " | ".join(row_text)
                )

    return "\n".join(
        text_parts
    )


# ============================================================
# DOCX HYPERLINK EXTRACTION
# ============================================================

def extract_links_from_docx(
    file_path: str,
) -> list[str]:

    links = []

    try:

        doc = Document(file_path)

        # ----------------------------------------------------
        # DOCX hyperlinks are stored in relationships.
        # ----------------------------------------------------

        for relationship in (
            doc.part.rels.values()
        ):

            if (
                relationship.reltype
                == "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
            ):

                target = relationship.target_ref

                if target:
                    links.append(
                        target.strip()
                    )

    except Exception as e:

        print(
            f"DOCX link extraction failed: {e}"
        )

    return list(
        dict.fromkeys(links)
    )


# ============================================================
# EXTRACT URLs FROM NORMAL TEXT
# ============================================================

def extract_urls_from_text(
    text: str,
) -> list[str]:

    if not text:
        return []

    return list(
        dict.fromkeys(
            URL_PATTERN.findall(text)
        )
    )


# ============================================================
# CLASSIFY LINK
# ============================================================

def classify_link(
    url: str,
) -> str:

    url_lower = url.lower()

    if (
        "linkedin.com" in url_lower
    ):
        return "LinkedIn"

    if (
        "github.com" in url_lower
    ):
        return "GitHub"

    if (
        "behance.net" in url_lower
        or "behance.com" in url_lower
    ):
        return "Behance"

    if (
        "dribbble.com" in url_lower
    ):
        return "Dribbble"

    if (
        "portfolio" in url_lower
    ):
        return "Portfolio"

    return "Website"


# ============================================================
# BUILD LINK SECTION
# ============================================================

def build_link_section(
    links: list[str],
) -> str:

    if not links:
        return ""

    lines = [
        "",
        "RESUME LINKS",
        "The candidate has the following online profiles and websites:",
    ]

    for link in links:

        link_type = classify_link(
            link
        )

        lines.append(
            f"{link_type}: {link}"
        )

    return "\n".join(lines)


# ============================================================
# MAIN EXTRACTION
# ============================================================

def extract_text(
    file_path: str,
) -> str:

    ext = os.path.splitext(
        file_path
    )[1].lower()

    # ========================================================
    # PDF
    # ========================================================

    if ext == ".pdf":

        text = extract_text_from_pdf(
            file_path
        )

        links = (
            extract_links_from_pdf(
                file_path
            )
        )

    # ========================================================
    # DOCX
    # ========================================================

    elif ext == ".docx":

        text = extract_text_from_docx(
            file_path
        )

        links = (
            extract_links_from_docx(
                file_path
            )
        )

    else:

        raise ValueError(
            f"Unsupported file type: {ext}. "
            "Use PDF or DOCX."
        )

    # ========================================================
    # URLs visible as normal text
    # ========================================================

    text_urls = extract_urls_from_text(
        text
    )

    # Combine:
    # - clickable hyperlinks
    # - URLs visibly written in text
    all_links = list(
        dict.fromkeys(
            links + text_urls
        )
    )

    # ========================================================
    # Add links to extracted resume text
    # ========================================================

    link_section = build_link_section(
        all_links
    )

    if link_section:

        text = (
            text
            + "\n"
            + link_section
        )

    return text.strip()