Readme file
# AI Resume Screening System
A hyper-personalized resume screening tool that uses semantic search (vector
embeddings + ChromaDB) to match resumes against job description requirements
— going beyond simple keyword matching. Breaks the JD into individual
requirements and finds the best supporting evidence for each one inside the
resume, producing an explainable, per-requirement match breakdown.
## Tech Stack
* *Backend:* FastAPI, SQLite, ChromaDB, Sentence Transformers, spaCy, Google Gemini
* *Frontend:* React (Vite)
## Prerequisites
* Python 3.11 or 3.12 (3.13 has packaging issues with some dependencies)
* Node.js 18+
* A free Gemini API key: https://aistudio.google.com/apikey
No separate database server needed — SQLite runs as a local file, created
automatically on first run.
## Setup
### 1. Clone the repo
bash
git clone https://github.com/sanikaudgaonkar/resumescreeningsystem.git
cd resumescreeningsystem
### 2. Backend setup
bash
cd backend
python -m venv venv
venv\Scripts\activate # Windows
# source venv/bin/activate # macOS/Linux
pip install -r requirements.txt
python -m spacy download en_core_web_sm
### 3. Configure environment variables
Copy the example file and fill in your own values:
bash
copy .env.example .env # Windows
# cp .env.example .env # macOS/Linux
Edit .env and set:
* GEMINI_API_KEY — your own key from the link above
DATABASE_URL and CHROMA_PERSIST_DIR can be left as-is — they default to
a local SQLite file and a local ChromaDB folder, both created automatically.
### 4. Run the backend
bash
uvicorn app.main:app --reload
API runs at http://localhost:8000 — interactive docs at http://localhost:8000/docs.
### 5. Frontend setup (in a new terminal)
bash
cd frontend
npm install
npm run dev
App runs at http://localhost:5173.
## Usage
1. Upload a resume (PDF or DOCX)
2. Paste a job description (works best with a clear "Requirements:" section)
3. Click "Upload & Analyze"
4. View the semantic match score and requirement-by-requirement breakdown
