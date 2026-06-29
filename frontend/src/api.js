import axios from "axios";
console.log("VITE_API_BASE =", import.meta.env.VITE_API_BASE);
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
console.log("API_BASE =", API_BASE);
export async function startAnalysis(repoUrl) {
    const response = await axios.post(`${API_BASE}/api/analyze`, {
        repo_url: repoUrl,
    });
    return response.data.job_id;
}

export async function getAnalysisStatus(jobId) {
    const response = await axios.get(`${API_BASE}/api/analyze/${jobId}`);
    return response.data;
}

export async function getRecentScans() {
    const response = await axios.get(`${API_BASE}/api/recent-scans`);
    return response.data.scans;
  }