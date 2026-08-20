"""
STAGE 3: TEXT PREPROCESSING
IMPORTANT: clean_text() must preserve line breaks — chunking.py depends
on newlines to split resume text into individual bullets/lines for
semantic matching. Collapsing all whitespace (including \n) into single
spaces here silently breaks chunking downstream: the whole resume ends
up as one giant "chunk" instead of one chunk per line, which tanks
semantic match scores across the board.
"""
import re
import spacy

_nlp = spacy.load("en_core_web_sm")


def clean_text(raw_text: str) -> str:
    text = re.sub(r"[\u2022\u25cf\u2023\u2043]", " ", raw_text)  # bullet glyphs
    text = re.sub(r"[^\x00-\x7F\n]+", " ", text)                  # non-ASCII junk, KEEP \n
    text = re.sub(r"[ \t]+", " ", text)                           # collapse spaces/tabs only
    text = re.sub(r"\n{3,}", "\n\n", text)                        # collapse excessive blank lines
    text = "\n".join(line.strip() for line in text.split("\n"))   # trim each line
    return text.strip()


def lemmatize_and_remove_stopwords(text: str) -> str:
    doc = _nlp(text)
    tokens = [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    return " ".join(tokens)


def preprocess(raw_text: str) -> dict:
    cleaned = clean_text(raw_text)
    normalized = lemmatize_and_remove_stopwords(cleaned)
    return {"cleaned_text": cleaned, "normalized_text": normalized}