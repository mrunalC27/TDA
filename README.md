# Refactr
 
**Debt doesn't ship. We find it before you do.**
 
An AI-driven code governance platform that audits any GitHub repository across four pillars — structural code quality, security, contributor velocity, and AI-synthesized insight — and produces an actionable health report, regardless of language.
 
## What it does
 
Paste a GitHub URL. Refactr clones the repository, detects its primary language, runs 20+ analyzers across structural, security, and contributor dimensions, and produces a single health score plus a locally-generated executive summary, remediation roadmap, and architecture evaluation. Repeat scans of an unchanged repository return instantly via commit-hash-based caching.
 
## Four Pillars
 
### Pillar 1: Structural Code Intelligence
- Cyclomatic Complexity (dedicated Python/JS analyzers + `lizard` fallback for 10+ other languages)
- Maintainability Index (Python/JS, shared scoring convention)
- Dead Code Detection (Python)
- Code Churn (commit frequency per file, via batched `git log`)
- Logic Duplication (cross-file and within-file, via `jscpd`)
- Broken Loops (infinite-loop risk via AST analysis for Python, pattern-based for others)
- Unbounded Queries (ORM/SQL calls missing row limits)
- Dependency Rot (version staleness vs. PyPI/npm latest, separate from vulnerability scanning)
- Untested Functions (static test-file-presence proxy — not executed coverage)
### Pillar 2: Security & Vulnerability Fortification
- Leaked API Secrets & Hardcoded Credentials (universal signature + pattern scanner, all languages)
- Dangerous Code Patterns (Bandit for Python, pattern-based for JS/Java/Go/PHP/Ruby)
- Backdoor/Trapdoor Detection (hardcoded bypass conditions, debug flags, disabled auth checks)
- Open Endpoints & RBAC Mapping (route detection + auth-proximity heuristic)
### Pillar 3: Contributor & Velocity Metrics
- Developer Efficiency (commits, lines changed, commit velocity per contributor)
- Debt Contribution Ratio (cross-references contributor activity against high-risk files)
- Knowledge Silos (files touched by exactly one contributor)
- Contributor Churn (active vs. inactive contributors over a rolling window)
- Code Impact Assessment (unusually large/high-risk commits)
- PR Maturity Index (review coverage on merged PRs, via authenticated GitHub API)
### Pillar 4: AI-Synthesized Insight
- Automated Executive Summary
- Actionable Remediation Roadmap
- Architecture Pattern Evaluation (folder-structure-based)
- Trend Analysis & Debt Prediction (requires multiple historical scans of the same repo)
All AI features run on a local Ollama model — no API key, no quota, no cost.
 
## Architecture
 
```
TDA/
├── backend/                        # FastAPI application
│   ├── main.py                       # Routes, CORS, job lifecycle
│   ├── orchestrator.py               # Runs the full analyzer pipeline, caching
│   └── jobs.py                       # Job state (backed by SQLite)
├── frontend/                       # React + Vite + Tailwind dashboard
│   └── src/
│       ├── Dashboard.jsx              # 5-tab results view
│       ├── components/                # Cards, tables, charts, badges
│       └── useAnalysis.js             # Polling hook for async job status
├── analyzers/                      # Pillar 1 & 2 analyzers
│   ├── javascript/                   # JS-specific analyzers
│   ├── complexity_analyzer.py        # Python (radon)
│   ├── universal_complexity_analyzer.py  # Any language (lizard)
│   ├── duplication_analyzer.py       # jscpd wrapper
│   ├── secrets_analyzer.py           # Universal secrets scanner
│   ├── backdoor_pattern_analyzer.py
│   ├── endpoint_security_analyzer.py
│   ├── code_churn_analyzer.py
│   ├── contributor_analyzer.py       # Pillar 3
│   ├── pr_maturity_analyzer.py        # Pillar 3, GitHub API
│   ├── dependency_rot_analyzer.py
│   ├── loop_and_query_analyzer.py
│   └── test_presence_analyzer.py
├── ai/                              # Pillar 4, Ollama-powered
│   ├── gemini_summary.py              # Executive summary (name retained, runs on Ollama)
│   ├── remediation_roadmap.py
│   └── architecture_evaluator.py
├── core/
│   ├── repository_profiler.py        # Language/framework detection
│   ├── coverage_engine.py
│   ├── job_store.py                  # Async job persistence (SQLite)
│   └── scan_history_store.py         # Scan history, trend data, full-result cache
├── scoring/
│   └── health_score.py               # Composite health score, per-category breakdown
├── utils/
│   └── github_clone.py               # Clone, shallow/full history, commit lookup, cleanup
└── app.py                           # Original Streamlit prototype (retained, superseded)
```
 
## Setup
 
### Prerequisites
- Python 3.10+
- Node.js (for the frontend, `npm audit`, and `jscpd`)
- Git
- [Ollama](https://ollama.com/download), with a model pulled (e.g. `ollama pull mistral`)
### Backend
 
```bash
cd TDA
python -m venv venv
.\venv\Scripts\Activate    # Windows
# source venv/bin/activate # macOS/Linux
 
pip install -r requirements.txt
npm install -g jscpd
```
 
### Frontend
 
```bash
cd frontend
npm install
```
 
### Environment variables
 
Create a `.env` file in the project root:
 
```
GITHUB_TOKEN=your_github_personal_access_token
```
 
`GITHUB_TOKEN` needs only `public_repo` scope. It's used for PR Maturity Index and commit-hash cache lookups. Without it, both fall back to GitHub's unauthenticated rate limit (60 requests/hour).
 
### Run
 
Two processes, in separate terminals:
 
```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload --port 8000 --reload-dir backend --reload-dir analyzers --reload-dir ai --reload-dir core --reload-dir scoring --reload-dir utils
 
# Terminal 2 — frontend
cd frontend
npm run dev
```
 
Open the URL Vite prints (typically `http://localhost:5173`).
 
> The `--reload-dir` flags are required on Windows — `--reload-exclude` does not reliably exclude `cloned_repos/`, and watching it directly causes uvicorn to restart mid-analysis every time a repo is cloned.
 
## Caching
 
Refactr checks the latest commit hash on a repository's default branch before cloning. If a complete result already exists for that exact commit, it's returned instantly with no clone, no re-analysis, and no AI calls. A new commit, or a repository scanned for the first time, runs the full pipeline and caches the result for next time.
 
## Known limitations
 
- **Test coverage is a static estimate, not real execution coverage.** Refactr does not install dependencies or run the target repository's test suite. It detects test-file presence by naming convention and reports an estimated file-level coverage signal, clearly labeled as such in the output.
- **Open Endpoints / RBAC detection is a proximity heuristic.** Repos using global auth middleware (rather than per-route decorators) will show false positives, since the analyzer checks for auth indicators near each route definition, not application-wide middleware registration.
- **Dead code detection is currently Python-only.**
- **Refactor ROI is not yet implemented.** It requires comparing complexity/maintainability trends across multiple historical scans of the same repository — the underlying scan history (SQLite) exists, but the ROI calculation itself is not built.
- **Trend Analysis and Debt Prediction require multiple prior scans of the same repository URL.** A single scan correctly reports "not enough data."
- **Shallow clone by default.** Repos are cloned with `depth=1` for speed; full commit history is fetched separately only when churn/contributor analysis needs it.
- **AI quality depends on the local model.** Refactr ships configured for `mistral` via Ollama. Larger or more specialized models will produce better-reasoned summaries at the cost of speed.
- **Single-threaded, synchronous analysis pipeline.** Each analysis runs all ~25 analyzers sequentially in a background thread per request. This is appropriate for local/single-user use, not concurrent multi-user production traffic.
## Tech stack
 
- **Backend**: FastAPI, Uvicorn, background-threaded job execution
- **Frontend**: React, Vite, Tailwind CSS, Recharts, react-markdown
- **Static analysis**: radon, vulture, bandit, lizard, jscpd
- **Dependency auditing**: pip-audit, npm audit
- **AI synthesis**: Ollama (local, no API key required)
- **Persistence**: SQLite (scan history, job state, full-result cache)
- **Version control integration**: GitPython, GitHub REST API