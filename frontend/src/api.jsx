import axios from "axios";

const API_BASE = "http://localhost:8000/api";

export const uploadResume = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_BASE}/resumes/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const analyzeResume = (resumeId, jobDescription) =>
  axios.post(`${API_BASE}/analysis/`, {
    resume_id: resumeId,
    job_description: jobDescription,
  });

export const listResumes = () => axios.get(`${API_BASE}/dashboard/resumes`);