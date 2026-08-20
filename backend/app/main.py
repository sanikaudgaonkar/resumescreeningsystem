from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine
from app.routers import upload, analysis, dashboard,job_description

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Resume Screening System",
    description="NLP + Vector DB + LLM powered resume screening API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(job_description.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Resume screening API is running."}