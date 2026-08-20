# app/database/models.py
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database.db import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    raw_text = Column(String)
    skills = Column(JSON, default=list)
    education = Column(JSON, default=list)
    experience_years = Column(Float, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())