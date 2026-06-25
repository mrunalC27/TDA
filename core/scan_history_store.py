import sqlite3
import json
import os
from datetime import datetime, timezone

DB_PATH = os.path.join("data", "scan_history.db")


def _get_connection():

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = _get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo_url TEXT NOT NULL,
            scanned_at TEXT NOT NULL,
            primary_language TEXT,
            health_score INTEGER,
            health_status TEXT,
            average_complexity REAL,
            high_risk_functions INTEGER,
            average_maintainability REAL,
            total_dead_code INTEGER,
            security_high INTEGER,
            security_medium INTEGER,
            security_low INTEGER,
            dependency_vulnerabilities INTEGER,
            duplicate_blocks INTEGER,
            secrets_found INTEGER,
            backdoor_findings INTEGER,
            open_endpoints INTEGER,
            raw_snapshot TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_scan(repo_url, profile, health, complexity_summary,
              maint_summary, dead_summary, security_summary,
              dependency_summary, duplication_summary, secrets_summary,
              backdoor_summary, endpoint_summary, commit_hash=None):

    init_db()
    migrate_add_commit_hash_column()

    conn = _get_connection()

    raw_snapshot = json.dumps({
        "profile": profile,
        "health": health,
        "complexity": complexity_summary,
        "maintainability": maint_summary,
        "dead_code": dead_summary,
        "security": security_summary,
        "dependency": dependency_summary,
        "duplication": duplication_summary,
        "secrets": secrets_summary,
        "backdoor": backdoor_summary,
        "endpoint": endpoint_summary
    })

    health_score = health.get("health_score")

    if not isinstance(health_score, int):
        health_score = None

    conn.execute("""
        INSERT INTO scan_history (
            repo_url, scanned_at, primary_language,
            health_score, health_status,
            average_complexity, high_risk_functions,
            average_maintainability, total_dead_code,
            security_high, security_medium, security_low,
            dependency_vulnerabilities, duplicate_blocks,
            secrets_found, backdoor_findings, open_endpoints,
            raw_snapshot, commit_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        repo_url,
        datetime.now(timezone.utc).isoformat(),
        profile.get("primary_language", "Unknown"),
        health_score,
        health.get("status", "Unknown"),
        complexity_summary.get("average_complexity"),
        complexity_summary.get("high_risk_functions"),
        maint_summary.get("average_maintainability"),
        dead_summary.get("total_dead_code", 0),
        security_summary.get("high", 0),
        security_summary.get("medium", 0),
        security_summary.get("low", 0),
        dependency_summary.get("vulnerabilities", 0),
        duplication_summary.get("duplicate_blocks", 0),
        secrets_summary.get("total_findings", 0),
        backdoor_summary.get("backdoor_findings", 0),
        endpoint_summary.get("open_endpoints_found", 0),
        raw_snapshot,
        commit_hash
    ))

    conn.commit()
    conn.close()

def get_history_for_repo(repo_url, limit=20):

    init_db()

    conn = _get_connection()

    rows = conn.execute("""
        SELECT * FROM scan_history
        WHERE repo_url = ?
        ORDER BY scanned_at DESC
        LIMIT ?
    """, (repo_url, limit)).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_all_scans(limit=100):

    init_db()

    conn = _get_connection()

    rows = conn.execute("""
        SELECT id, repo_url, scanned_at, primary_language,
               health_score, health_status
        FROM scan_history
        ORDER BY scanned_at DESC
        LIMIT ?
    """, (limit,)).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def migrate_add_commit_hash_column():

    conn = _get_connection()

    try:

        conn.execute("ALTER TABLE scan_history ADD COLUMN commit_hash TEXT")
        conn.commit()

    except sqlite3.OperationalError:

        pass

    conn.close()


def get_cached_scan(repo_url, commit_hash):

    init_db()
    migrate_add_commit_hash_column()

    if not commit_hash:
        return None

    conn = _get_connection()

    row = conn.execute("""
        SELECT raw_snapshot FROM scan_history
        WHERE repo_url = ? AND commit_hash = ?
        ORDER BY scanned_at DESC
        LIMIT 1
    """, (repo_url, commit_hash)).fetchone()

    conn.close()

    if not row:
        return None

    return json.loads(row["raw_snapshot"])



def init_full_result_cache_table():

    conn = _get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS full_result_cache (
            repo_url TEXT NOT NULL,
            commit_hash TEXT NOT NULL,
            result_json TEXT NOT NULL,
            cached_at TEXT NOT NULL,
            PRIMARY KEY (repo_url, commit_hash)
        )
    """)

    conn.commit()
    conn.close()


def save_full_result_cache(repo_url, commit_hash, result):

    if not commit_hash:
        return

    init_full_result_cache_table()

    conn = _get_connection()

    conn.execute("""
        INSERT OR REPLACE INTO full_result_cache (repo_url, commit_hash, result_json, cached_at)
        VALUES (?, ?, ?, ?)
    """, (
        repo_url,
        commit_hash,
        json.dumps(result),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def get_full_result_cache(repo_url, commit_hash):

    if not commit_hash:
        return None

    init_full_result_cache_table()

    conn = _get_connection()

    row = conn.execute("""
        SELECT result_json FROM full_result_cache
        WHERE repo_url = ? AND commit_hash = ?
    """, (repo_url, commit_hash)).fetchone()

    conn.close()

    if not row:
        return None

    return json.loads(row["result_json"])