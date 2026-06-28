from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
from core.scan_history_store import get_all_scans
from backend.jobs import create_job, update_job_step, complete_job, fail_job, get_job
from backend.orchestrator import run_analysis
import os
app = FastAPI(title="Refactr API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repo_url: str


def _run_job(job_id, repo_url):

    def progress_callback(step_message):
        update_job_step(job_id, step_message)

    try:

        result = run_analysis(repo_url, progress_callback=progress_callback)
        complete_job(job_id, result)

    except Exception as e:

        fail_job(job_id, str(e))


@app.post("/api/analyze")
def start_analysis(request: AnalyzeRequest):

    if not request.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url is required")

    job_id = create_job()

    thread = threading.Thread(
        target=_run_job,
        args=(job_id, request.repo_url),
        daemon=True
    )
    thread.start()

    return {"job_id": job_id}


@app.get("/api/analyze/{job_id}")
def get_analysis_status(job_id: str):

    job = get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@app.get("/api/health")
def health_check():

    return {"status": "ok"}

@app.get("/api/recent-scans")
def recent_scans():

    scans = get_all_scans(limit=20)

    return {"scans": scans}


