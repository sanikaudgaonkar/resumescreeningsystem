import { useState } from "react";
import {
  uploadResume,
  uploadJobDescription,
  analyzeResume,
} from "./api";
import ProfileSummary from "./components/ProfileSummary";
import GapAnalysis from "./components/GapAnalysis";
import "./App.css";

export default function App() {
  const [step, setStep] = useState(1);

  const [file, setFile] = useState(null);
  const [jdFile, setJdFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // =========================
  // STEP 1 — JOB DESCRIPTION
  // =========================

  const handleJobDescriptionContinue = async () => {
    // -------------------------
    // OPTION 1 — Pasted JD
    // -------------------------
    if (jobDescription.trim()) {
      setStep(2);
      return;
    }

    // -------------------------
    // OPTION 2 — Uploaded JD
    // -------------------------
    if (jdFile) {
      try {
        setLoading(true);

        const response = await uploadJobDescription(jdFile);

        const extractedText = response.data.text;

        if (!extractedText || !extractedText.trim()) {
          alert(
            "Could not extract text from the job description."
          );
          return;
        }

        // Store extracted JD text
        setJobDescription(extractedText);

        // Move to resume step
        setStep(2);
      } catch (error) {
        console.error("JD upload failed:", error);

        alert(
          "Could not process the job description. Please try again."
        );
      } finally {
        setLoading(false);
      }

      return;
    }
  };

  const handleJDFileUpload = (e) => {
    const selectedFile = e.target.files[0];

    if (!selectedFile) return;

    // File selected → clear pasted JD
    setJdFile(selectedFile);
    setJobDescription("");
  };

  const handleJDTextChange = (e) => {
    const text = e.target.value;

    setJobDescription(text);

    // Text entered → remove uploaded file
    if (text.trim()) {
      setJdFile(null);
    }
  };

  const removeJDFile = () => {
    setJdFile(null);
    setJobDescription("");
  };

  // =========================
  // STEP 2 — RESUME
  // =========================

  const handleResumeUpload = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const removeResume = () => {
    setFile(null);
  };

  const handleAnalyze = async () => {
    if (!file || !jobDescription.trim()) return;

    setLoading(true);

    try {
      // Upload resume
      const uploadRes = await uploadResume(file);

      // Analyze resume against JD
      const analysisRes = await analyzeResume(
        uploadRes.data.resume_id,
        jobDescription
      );

      setResult(analysisRes.data);

      // Go to result page
      setStep(3);
    } catch (err) {
      console.error(err);
      alert(
        "Something went wrong — check the backend console."
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // HELPERS
  // =========================

  const getScore = () => {
    if (!result) return 0;

    return Math.round(
      result.match_score.overall_score * 100
    );
  };

  const getMatchLabel = () => {
    const score = getScore();

    if (score >= 80) return "Excellent Match";
    if (score >= 60) return "Good Match";
    if (score >= 40) return "Moderate Match";

    return "Needs Improvement";
  };

  // =========================
  // UI
  // =========================

  return (
    <div className="app">

      {/* =========================
          TOP NAVIGATION
      ========================= */}

      <header className="topbar">

        <div className="steps">

          <div className={`step ${step === 1 ? "active" : ""}`}>
            <span>1.</span>
            Job Description
          </div>

          <div className={`step ${step === 2 ? "active" : ""}`}>
            <span>2.</span>
            Resume
          </div>

          <div className={`step ${step === 3 ? "active" : ""}`}>
            <span>3.</span>
            Match Result
          </div>

        </div>

        <div className="brand">
          Semantic Candidate Matching
        </div>

      </header>


      {/* =====================================================
          STEP 1 — JOB DESCRIPTION
      ===================================================== */}

      {step === 1 && (

        <main className="page">

          <section className="hero">

            <h1>
              Find the right candidate beyond keywords.
            </h1>

            <p>
              Upload your job description to let our semantic
              engine deeply understand the required skills,
              experience context, and underlying intent to find
              the perfect match.
            </p>

          </section>


          {/* JD UPLOAD */}

          <div className="upload-card">

            <div className="upload-icon">
              ☁
            </div>

            <h2>
              Upload Job Description
            </h2>

            <p>
              Drag & drop your Job Description here
            </p>

            <label className="browse-button">

              Browse Files

              <input
                type="file"
                accept=".pdf,.docx,.txt"
                hidden
                onChange={handleJDFileUpload}
              />

            </label>

            <small>
              Supported formats: PDF, DOCX, TXT (Max 5MB)
            </small>

          </div>


          {/* SELECTED JD FILE */}

          {jdFile && (

            <div className="selected-jd-file">

              <div>

                <strong>
                  {jdFile.name}
                </strong>

                <small>
                  {(jdFile.size / 1024 / 1024).toFixed(2)} MB
                </small>

              </div>

              <button
                type="button"
                onClick={removeJDFile}
              >
                ×
              </button>

            </div>

          )}


          {/* OR */}

          <div className="divider">
            <span>OR</span>
          </div>


          {/* PASTE JD */}

          <p className="paste-label">
            Paste the job description instead
          </p>

          <textarea
            className="jd-textarea"
            placeholder="Paste the full job description text here..."
            value={jobDescription}
            onChange={handleJDTextChange}
          />


          {/* CONTINUE */}

          <div className="button-row">

            <button
              className="primary-button"
              disabled={
                (!jobDescription.trim() && !jdFile) ||
                loading
              }
              onClick={handleJobDescriptionContinue}
            >
              {loading
                ? "Reading Job Description..."
                : "Continue to Resume →"}
            </button>

          </div>

        </main>

      )}


      {/* =====================================================
          STEP 2 — RESUME
      ===================================================== */}

      {step === 2 && (

        <main className="page">

          <section className="hero">

            <h1>
              Now add the candidate resume
            </h1>

            <p>
              Upload a candidate resume to compare against the
              job description.
            </p>

          </section>


          {/* TARGET ROLE */}

          <div className="target-role">

            <div>

              <span className="label">
                TARGET ROLE
              </span>

              <h2>
                Candidate Resume
              </h2>

            </div>

          </div>


          {/* RESUME UPLOAD */}

          {!file && (

            <label className="resume-upload">

              <div className="upload-icon">
                ☁
              </div>

              <h2>
                Upload Candidate Resume
              </h2>

              <p>
                Drag and drop your resume here, or click to browse.
              </p>

              <span>
                Supported formats: PDF, DOCX (Max 5MB)
              </span>

              <div className="select-button">
                Select File
              </div>

              <input
                type="file"
                accept=".pdf,.docx"
                hidden
                onChange={handleResumeUpload}
              />

            </label>

          )}


          {/* SELECTED RESUME */}

          {file && (

            <div className="file-list">

              <h2>
                1 resume ready for analysis
              </h2>

              <div className="file-item">

                <div>

                  <strong>
                    {file.name}
                  </strong>

                  <small>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </small>

                </div>

                <button
                  type="button"
                  onClick={removeResume}
                >
                  ×
                </button>

              </div>

            </div>

          )}


          {/* BUTTONS */}

          <div className="button-row">

            <button
              className="secondary-button"
              onClick={() => setStep(1)}
            >
              ← Back
            </button>

            <button
              className="primary-button"
              disabled={!file || loading}
              onClick={handleAnalyze}
            >
              {loading
                ? "Analyzing..."
                : "Analyze Match →"}
            </button>

          </div>

        </main>

      )}


      {/* =====================================================
          STEP 3 — MATCH RESULT
      ===================================================== */}

      {step === 3 && result && (

        <main className="results-page">

          {/* HEADER */}

          <div className="results-header">

            <div>

              <h1>
                Candidate Match Results
              </h1>

              <p>
                AI-powered semantic analysis of the candidate
                against the job description.
              </p>

            </div>

            <button
              className="secondary-button"
              onClick={() => setStep(1)}
            >
              Start New Match
            </button>

          </div>


          {/* SCORE + METRICS */}

          <section className="metrics-grid">

            {/* OVERALL SCORE */}

            <div className="score-card">

              <span className="match-label">
                OVERALL MATCH
              </span>

              <div className="score-circle">

                <strong>
                  {getScore()}%
                </strong>

              </div>

              <h2>
                {getMatchLabel()}
              </h2>

            </div>


            {/* SEMANTIC SIMILARITY */}

            <div className="metric-card">

              <span>
                SEMANTIC SIMILARITY
              </span>

              <strong>
                {Math.round(
                  result.match_score.semantic_similarity * 100
                )}%
              </strong>

              <div className="progress">

                <div
                  style={{
                    width: `${
                      result.match_score.semantic_similarity * 100
                    }%`,
                  }}
                />

              </div>

            </div>


            {/* REQUIREMENTS */}

            <div className="metric-card">

              <span>
                REQUIREMENTS MATCHED
              </span>

              <strong>
                {
                  result.match_score.matched_requirements
                    ?.length || 0
                }
              </strong>

              <p className="metric-subtext">
                matched requirements
              </p>

            </div>

          </section>


          {/* AI SUMMARY */}

          <section className="ai-summary">

            <h2>
              ✦ AI Match Summary
            </h2>

            <p>
              {result.llm_feedback}
            </p>

          </section>


          {/* CANDIDATE PROFILE (skills / education / experience / tone) */}

          <ProfileSummary
            extractedInfo={result.extracted_info}
            sentiment={result.sentiment}
          />


          {/* GAP ANALYSIS + PRIORITIZED ROADMAP */}

          <GapAnalysis gapAnalysis={result.gap_analysis} />


          {/* REQUIREMENT BREAKDOWN */}

          <section className="requirements-section">

            <div className="section-title">

              <h2>
                Requirement Breakdown
              </h2>

              <span>
                {
                  result.match_score
                    .requirement_matches
                    ?.length || 0
                }{" "}
                requirements analyzed
              </span>

            </div>


            {
              result.match_score.requirement_matches?.map(
                (requirement, index) => {

                  const score =
                    Math.round(
                      requirement.score * 100
                    );

                  return (

                    <div
                      className="requirement-card"
                      key={index}
                    >

                      <div className="requirement-top">

                        <div>

                          <h3>
                            {requirement.requirement}
                          </h3>

                          {requirement.category && (
                            <span className="category-badge">
                              {requirement.category}
                            </span>
                          )}

                        </div>

                        <strong>
                          {score}%
                        </strong>

                      </div>


                      <div className="progress">

                        <div
                          style={{
                            width: `${score}%`,
                          }}
                        />

                      </div>


                      <div className="evidence">

                        <span>
                          RESUME EVIDENCE
                        </span>

                        <p>
                          {
                            requirement.evidence ||
                            "No supporting evidence found."
                          }
                        </p>

                        {requirement.supporting_evidence &&
                          requirement.supporting_evidence.length > 1 && (

                            <details className="more-evidence">

                              <summary>
                                +{requirement.supporting_evidence.length - 1}{" "}
                                more supporting snippet(s)
                              </summary>

                              <ul>
                                {requirement.supporting_evidence
                                  .slice(1)
                                  .map((snippet, i) => (
                                    <li key={i}>{snippet}</li>
                                  ))}
                              </ul>

                            </details>

                          )}

                      </div>

                    </div>

                  );
                }
              )
            }

          </section>


          {/* START AGAIN */}

          <div className="button-row">

            <button
              className="primary-button"
              onClick={() => {

                setStep(1);
                setFile(null);
                setJdFile(null);
                setJobDescription("");
                setResult(null);

              }}
            >
              Start New Match
            </button>

          </div>

        </main>

      )}

    </div>
  );
}