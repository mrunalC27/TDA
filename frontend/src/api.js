import axios from "axios";

const API_BASE = "http://localhost:8000";

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