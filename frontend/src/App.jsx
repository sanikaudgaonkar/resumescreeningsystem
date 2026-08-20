import { useState } from "react";
import { uploadResume, analyzeResume } from "./api";

export default function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUploadAndAnalyze = async () => {
    if (!file || !jobDescription) return;
    setLoading(true);
    try {
      const uploadRes = await uploadResume(file);
      const analysisRes = await analyzeResume(uploadRes.data.resume_id, jobDescription);
      setResult(analysisRes.data);
    } catch (err) {
      console.error(err);
      alert("Something went wrong — check the backend console.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 720, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h1>AI Resume Screening System</h1>

      <input type="file" accept=".pdf,.docx" onChange={(e) => setFile(e.target.files[0])} />
      <br /><br />
      <textarea
        placeholder="Paste job description here..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />
      <br /><br />
      <button onClick={handleUploadAndAnalyze} disabled={loading}>
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>

      {result && (
        <div style={{ marginTop: 24 }}>
          <h2>Semantic Match Score: {(result.match_score.overall_score * 100).toFixed(0)}%</h2>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14, marginTop: 16 }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "4px 0" }}>Requirement</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "4px 8px" }}>Score</th>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: "4px 0" }}>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {result.match_score.requirement_matches.map((r, i) => (
                <tr key={i}>
                  <td style={{ padding: "6px 0", verticalAlign: "top" }}>{r.requirement}</td>
                  <td style={{ padding: "6px 8px", verticalAlign: "top" }}>{(r.score * 100).toFixed(0)}%</td>
                  <td style={{ padding: "6px 0", verticalAlign: "top", color: r.evidence ? "#1a1a1a" : "#999" }}>
                    {r.evidence || "No evidence found"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: 16 }}>
            <h3>LLM Feedback</h3>
            <p>{result.llm_feedback}</p>
          </div>
        </div>
      )}
    </div>
  );
}