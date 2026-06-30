# Refactr
 
**Debt doesn't ship. We find it before you do.**
 
An AI-driven code governance platform that audits any GitHub repository across four pillars — structural code quality, security, contributor velocity, and AI-synthesized insight — and produces an actionable health report, regardless of language.
 
## Live Demo

**[tda-green.vercel.app](https://tda-green.vercel.app)**

The deployed version runs the full pipeline (structural, security, contributor analysis, caching) against any public GitHub repository. AI-synthesized insights (executive summary, roadmap, architecture evaluation) require a local Ollama instance and are not available in the hosted version — see [Deployment](#deployment) below.

> First request after a period of inactivity may take 30-60 seconds while the free-tier backend wakes up.

## What it does
 
Paste a GitHub URL. Refactr clones the repository, detects its primary language, runs 20+ analyzers across structural, security, and contributor dimensions, and produces a single health score plus an AI-generated executive summary, remediation roadmap, and architecture evaluation. Repeat scans of an unchanged repository return instantly via commit-hash-based caching. AI synthesis runs on a local Ollama model when self-hosted; the hosted demo runs the full analysis pipeline without AI synthesis.
 
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
 
## Deployment

Refactr is deployed as two independent services:

- **Frontend** ([Vercel](https://vercel.com)) — static build of the React app. Root directory must be set to `frontend`. Requires a `VITE_API_BASE` environment variable pointing at the backend URL, set **before** the first production build (Vite inlines environment variables at build time — adding the variable after a deploy requires a fresh build, not just a redeploy, to take effect).
- **Backend** ([Render](https://render.com)) — deployed via the included `Dockerfile`, which installs Node.js and `jscpd` alongside the Python environment so duplication detection and `npm audit` work in production, not just locally.

### Deployment notes

- **The Dockerfile must be picked up at service creation, not added later.** Render does not reliably let you convert an existing native-runtime ("Python 3") service into a Docker-runtime service after the fact — pushing a `Dockerfile` to a repo connected to an already-existing native service may build successfully without ever being used to serve traffic. If a deployed service's `Dockerfile` changes don't appear to take effect, create a new service from scratch and explicitly select Docker as the environment during creation.
- **CORS origins must match exactly.** `backend/main.py`'s `allow_origins` list requires an exact string match against the browser's `Origin` header — no trailing slash, no leading/trailing whitespace, correct scheme (`https://`). A single stray character here fails silently as a generic network error in the browser rather than a clear CORS message in some cases.
- **Render's free tier has an ephemeral filesystem.** The SQLite database (scan history, job state, cache) resets on every redeploy. For persistent scan history across deploys, an external database (e.g. a managed Postgres instance) would be required.
- **Ollama does not run on the deployed backend.** AI-synthesized insights gracefully degrade to an explanatory message in production rather than failing or hanging.

## Known limitations
 
- **Test coverage is a static estimate, not real execution coverage.** Refactr does not install dependencies or run the target repository's test suite. It detects test-file presence by naming convention and reports an estimated file-level coverage signal, clearly labeled as such in the output.
- **Open Endpoints / RBAC detection is a proximity heuristic.** Repos using global auth middleware (rather than per-route decorators) will show false positives, since the analyzer checks for auth indicators near each route definition, not application-wide middleware registration.
- **Dead code detection is currently Python-only.**
- **Refactor ROI is not yet implemented.** It requires comparing complexity/maintainability trends across multiple historical scans of the same repository — the underlying scan history (SQLite) exists, but the ROI calculation itself is not built.
- **Trend Analysis and Debt Prediction require multiple prior scans of the same repository URL.** A single scan correctly reports "not enough data."
- **Shallow clone by default.** Repos are cloned with `depth=1` for speed; full commit history is fetched separately only when churn/contributor analysis needs it.
- **AI quality depends on the local model.** Refactr ships configured for `mistral` via Ollama. Larger or more specialized models will produce better-reasoned summaries at the cost of speed.
- **Single-threaded, synchronous analysis pipeline.** Each analysis runs all ~25 analyzers sequentially in a background thread per request. This is appropriate for local/single-user use, not concurrent multi-user production traffic.
- **AI features are local-only by default.** The hosted demo does not run Ollama; deploying with AI synthesis enabled requires either running Ollama on the same host as the backend, or swapping the AI provider for a hosted API.

## Tech stack

- **Backend**: FastAPI, Uvicorn, background-threaded job execution
- **Frontend**: React, Vite, Tailwind CSS, Recharts, react-markdown
- **Static analysis**: radon, vulture, bandit, lizard, jscpd
- **Dependency auditing**: pip-audit, npm audit
- **AI synthesis**: Ollama (local, no API key required)
- **Persistence**: SQLite (scan history, job state, full-result cache)
- **Version control integration**: GitPython, GitHub REST API
- **Deployment**: Docker, Render (backend), Vercel (frontend)