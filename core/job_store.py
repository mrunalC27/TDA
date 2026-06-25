import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join("data", "scan_history.db")


def _get_connection():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def init_job_table():

    conn = _get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analysis_jobs (
            job_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            current_step TEXT,
            result_json TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_job_record(job_id):

    init_job_table()

    conn = _get_connection()

    now = datetime.now(timezone.utc).isoformat()

    conn.execute("""
        INSERT INTO analysis_jobs (job_id, status, current_step, result_json, error, created_at, updated_at)
        VALUES (?, 'running', 'Starting...', NULL, NULL, ?, ?)
    """, (job_id, now, now))

    conn.commit()
    conn.close()


def update_job_step_record(job_id, step_message):

    conn = _get_connection()

    conn.execute("""
        UPDATE analysis_jobs SET current_step = ?, updated_at = ?
        WHERE job_id = ?
    """, (step_message, datetime.now(timezone.utc).isoformat(), job_id))

    conn.commit()
    conn.close()


def complete_job_record(job_id, result):

    conn = _get_connection()

    conn.execute("""
        UPDATE analysis_jobs
        SET status = 'complete', current_step = 'Done', result_json = ?, updated_at = ?
        WHERE job_id = ?
    """, (json.dumps(result), datetime.now(timezone.utc).isoformat(), job_id))

    conn.commit()
    conn.close()


def fail_job_record(job_id, error_message):

    conn = _get_connection()

    conn.execute("""
        UPDATE analysis_jobs SET status = 'failed', error = ?, updated_at = ?
        WHERE job_id = ?
    """, (error_message, datetime.now(timezone.utc).isoformat(), job_id))

    conn.commit()
    conn.close()


def get_job_record(job_id):

    init_job_table()

    conn = _get_connection()

    row = conn.execute("""
        SELECT * FROM analysis_jobs WHERE job_id = ?
    """, (job_id,)).fetchone()

    conn.close()

    if not row:
        return None

    return {
        "status": row["status"],
        "current_step": row["current_step"],
        "result": json.loads(row["result_json"]) if row["result_json"] else None,
        "error": row["error"],
        "created_at": row["created_at"]
    }