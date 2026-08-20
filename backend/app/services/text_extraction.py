"""
STAGE 2: TEXT EXTRACTION
Pulls raw text out of an uploaded resume file (PDF or DOCX).
"""
import pdfplumber
import pymupdf  # formerly "fitz" — pymupdf is the current import name
from docx import Document
import os


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception:
        text = ""

    if len(text.strip()) < 30:  # pdfplumber likely failed — fall back
        text = ""
        doc = pymupdf.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()

    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    raise ValueError(f"Unsupported file type: {ext}. Use PDF or DOCX.")