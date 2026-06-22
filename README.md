# Technical Debt Analyzer (TDA)

An AI-driven code governance platform that audits vibe-coded software across four pillars — structural code quality, security, contributor velocity, and AI-synthesized remediation guidance — and produces an actionable health report for any GitHub repository, regardless of language.

## What it does

Paste a GitHub URL. TDA clones the repository, detects its primary language, runs 15+ analyzers across structural, security, and contributor dimensions, and produces a single health score plus a Gemini-generated executive summary and remediation roadmap.

## Four Pillars

### Pillar 1: Structural Code Intelligence
- Cyclomatic Complexity (dedicated Python/JS analyzers + `lizard` fallback for 10+ other languages)
- Maintainability Index (Python/JS)
- Dead Code Detection (Python)
- Code Churn (commit frequency per file)
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
- PR Maturity Index (review coverage on merged PRs, via GitHub API)

### Pillar 4: Gemini-Powered AI Synthesis
- Automated Executive Summary
- Actionable Remediation Roadmap
- Architecture Pattern Evaluation (folder-structure-based, via Gemini)
- Trend Analysis & Debt Prediction (requires multiple historical scans of the same repo)

## Architecture

```
TDA/
├── app.py                          # Streamlit entrypoint, orchestrates all analyzers
├── analyzers/                      # Pillar 1 & 2 analyzers
│   ├── javascript/                 # JS-specific analyzers
│   ├── complexity_analyzer.py      # Python (radon)
│   ├── universal_complexity_analyzer.py  # Any language (lizard)
│   ├── duplication_analyzer.py     # jscpd wrapper
│   ├── secrets_analyzer.py         # Universal secrets scanner
│   ├── backdoor_pattern_analyzer.py
│   ├── endpoint_security_analyzer.py
│   ├── code_churn_analyzer.py
│   ├── contributor_analyzer.py     # Pillar 3
│   ├── pr_maturity_analyzer.py     # Pillar 3, GitHub API
│   ├── dependency_rot_analyzer.py
│   ├── loop_and_query_analyzer.py
│   └── test_presence_analyzer.py
├── ai/                             # Pillar 4, Gemini-powered
│   ├── gemini_summary.py
│   ├── remediation_roadmap.py
│   └── architecture_evaluator.py
├── core/
│   ├── repository_profiler.py      # Language/framework detection
│   ├── coverage_engine.py
│   └── scan_history_store.py       # SQLite persistence for trend analysis
├── scoring/
│   └── health_score.py             # Composite health score calculation
└── utils/
    └── github_clone.py             # Clone, shallow/full history fetch, cleanup
```

## Setup

### Prerequisites
- Python 3.10+
- Node.js (for `npm audit` and `jscpd` duplication scanning)
- Git

### Installation

```bash
git clone <this-repo-url>
cd TDA
python -m venv venv
.\venv\Scripts\Activate    # Windows
# source venv/bin/activate # macOS/Linux

pip install -r requirements.txt
npm install -g jscpd
```

### Environment variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
```

`GITHUB_TOKEN` only needs `public_repo` scope. Without it, PR Maturity Index falls back to GitHub's unauthenticated rate limit (60 requests/hour).

### Run

```bash
streamlit run app.py
```

## Known limitations

- **Test coverage is a static estimate, not real execution coverage.** TDA does not install dependencies or run the target repository's test suite. It detects test-file presence by naming convention and reports an estimated file-level coverage signal, clearly labeled as such in the output.
- **Open Endpoints / RBAC detection is a proximity heuristic.** Repos using global auth middleware (rather than per-route decorators) will show false positives, since the analyzer checks for auth indicators near each route definition, not application-wide middleware registration.
- **Dead code detection is currently Python-only.**
- **Refactor ROI is not yet implemented.** It requires comparing complexity/maintainability trends across multiple historical scans of the same repository — the underlying scan history (SQLite) now exists, but the ROI calculation itself is not built.
- **Trend Analysis and Debt Prediction require multiple prior scans of the same repository URL.** A single scan will correctly report "not enough data."
- **Shallow clone by default.** Repos are cloned with `depth=1` for speed; full commit history is fetched separately only when churn/contributor analysis needs it.
- **Gemini-powered features (Pillar 4) require a working Gemini API quota.** Free-tier access varies by model; `gemini-2.5-pro` currently has no free-tier allocation — the project uses `gemini-2.5-flash` instead.

## Tech stack

- **Frontend**: Streamlit
- **Static analysis**: radon, vulture, bandit, lizard, jscpd
- **Dependency auditing**: pip-audit, npm audit
- **AI synthesis**: Google Gemini API
- **Persistence**: SQLite
- **Version control integration**: GitPython, GitHub REST API