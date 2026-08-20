import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume_screening.db")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

settings = Settings()

# Silences ChromaDB's harmless "Failed to send telemetry event" warnings
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")