import os
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from git import Repo, InvalidGitRepositoryError

GIT_LOG_TIMEOUT = 60
IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target"
}

RECENT_WINDOW_DAYS = 90
LARGE_COMMIT_LINE_THRESHOLD = 300

COMMIT_MARKER = "@@COMMIT@@"
LOG_FORMAT = f"{COMMIT_MARKER}%H|%an|%aI"


class ContributorAnalyzer:
    """
    Computes contributor and velocity metrics from local git history:
    Developer Efficiency, Knowledge Silos, Contributor Churn, and
    Code Impact Assessment. Debt Contribution Ratio is computed
    separately via cross_reference_debt().

    Uses a single batched `git log --numstat` call instead of
    per-commit `commit.stats` (GitPython's .stats spawns a separate
    git subprocess per commit - on repos with thousands of commits
    this can take many minutes or hang indefinitely. The batched
    approach runs one subprocess for the entire history).

    Requires full git history - shallow clones will show inaccurate
    or empty results.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def _is_ignored_path(self, file_path):

        parts = file_path.split("/")
        return any(p in IGNORE_DIRS for p in parts)

    def _parse_log(self, raw_output):

        commits = []

        blocks = raw_output.split(COMMIT_MARKER)

        for block in blocks:

            block = block.strip()

            if not block:
                continue

            lines = block.splitlines()

            header = lines[0]

            try:

                commit_hash, author, date_str = header.split("|", 2)

            except ValueError:

                continue

            try:

                commit_date = datetime.fromisoformat(date_str)

            except ValueError:

                continue

            total_lines = 0
            files_changed = []

            for line in lines[1:]:

                line = line.strip()

                if not line:
                    continue

                parts = line.split("\t")

                if len(parts) != 3:
                    continue

                additions, deletions, file_path = parts

                try:

                    add_count = int(additions) if additions != "-" else 0
                    del_count = int(deletions) if deletions != "-" else 0

                except ValueError:

                    add_count = 0
                    del_count = 0

                total_lines += add_count + del_count

                if not self._is_ignored_path(file_path):
                    files_changed.append(file_path)

            commits.append({
                "hash": commit_hash,
                "author": author,
                "date": commit_date,
                "total_lines": total_lines,
                "files_changed": files_changed
            })

        return commits

    def analyze(self):

        if self._cache is not None:
            return self._cache

        try:

            repo = Repo(self.repo_path)

        except InvalidGitRepositoryError:

            self._cache = {"status": "Not A Git Repository"}
            return self._cache
        
        try:

            result = subprocess.run(
                ["git", "log", f"--pretty=format:{LOG_FORMAT}", "--numstat"],
                cwd=self.repo_path,
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                timeout=GIT_LOG_TIMEOUT
            )

            raw_output = result.stdout


        except subprocess.TimeoutExpired:

            self._cache = {"status": "Contributor Analysis Timeout - Repository History Too Large"}
            return self._cache

        except Exception:

            self._cache = {"status": "No Commit History Available"}
            return self._cache
        
        commits = self._parse_log(raw_output)

        if not commits:

            self._cache = {"status": "No Commits Found"}
            return self._cache

        contributor_commits = defaultdict(int)
        contributor_lines = defaultdict(int)
        contributor_last_seen = {}
        contributor_first_seen = {}
        file_authors = defaultdict(set)
        large_commits = []

        now = datetime.now(timezone.utc)

        for commit in commits:

            author = commit["author"] or "Unknown"
            commit_date = commit["date"]

            contributor_commits[author] += 1
            contributor_lines[author] += commit["total_lines"]

            if author not in contributor_last_seen or commit_date > contributor_last_seen[author]:
                contributor_last_seen[author] = commit_date

            if author not in contributor_first_seen or commit_date < contributor_first_seen[author]:
                contributor_first_seen[author] = commit_date

            for file_path in commit["files_changed"]:
                file_authors[file_path].add(author)

            if commit["total_lines"] > LARGE_COMMIT_LINE_THRESHOLD:

                large_commits.append({
                    "commit": commit["hash"][:8],
                    "author": author,
                    "date": commit_date.strftime("%Y-%m-%d"),
                    "files_changed": len(commit["files_changed"]),
                    "lines_changed": commit["total_lines"]
                })

        knowledge_silos = [
            {"file": f, "sole_author": list(authors)[0]}
            for f, authors in file_authors.items()
            if len(authors) == 1
        ]

        recent_cutoff = now - timedelta(days=RECENT_WINDOW_DAYS)

        active_contributors = [
            a for a, last_seen in contributor_last_seen.items()
            if last_seen >= recent_cutoff
        ]

        churned_contributors = [
            a for a, last_seen in contributor_last_seen.items()
            if last_seen < recent_cutoff
        ]

        developer_efficiency = []

        for author, commit_count in contributor_commits.items():

            days_active = max(
                (contributor_last_seen[author] - contributor_first_seen[author]).days,
                1
            )

            developer_efficiency.append({
                "author": author,
                "commits": commit_count,
                "lines_changed": contributor_lines[author],
                "commits_per_week": round(commit_count / (days_active / 7), 2),
                "last_active": contributor_last_seen[author].strftime("%Y-%m-%d")
            })

        large_commits.sort(key=lambda x: x["lines_changed"], reverse=True)

        result = {
            "developer_efficiency": developer_efficiency,
            "knowledge_silos": knowledge_silos,
            "active_contributors": active_contributors,
            "churned_contributors": churned_contributors,
            "large_commits": large_commits,
            "file_authors": {k: list(v) for k, v in file_authors.items()}
        }

        self._cache = result
        return self._cache

    def summary(self):

        result = self.analyze()

        if "status" in result:
            return result

        return {
            "total_contributors": len(result["developer_efficiency"]),
            "active_contributors": len(result["active_contributors"]),
            "churned_contributors": len(result["churned_contributors"]),
            "knowledge_silo_files": len(result["knowledge_silos"]),
            "large_commits_found": len(result["large_commits"])
        }

    def developer_efficiency(self, limit=20):

        result = self.analyze()

        if "status" in result:
            return []

        data = list(result["developer_efficiency"])
        data.sort(key=lambda x: x["commits"], reverse=True)

        return data[:limit]

    def knowledge_silos(self, limit=30):

        result = self.analyze()

        if "status" in result:
            return []

        return result["knowledge_silos"][:limit]

    def large_commits(self, limit=20):

        result = self.analyze()

        if "status" in result:
            return []

        return result["large_commits"][:limit]

    def cross_reference_debt(self, high_risk_files):

        result = self.analyze()

        if "status" in result:
            return []

        high_risk_set = set(high_risk_files)

        contributor_total_files = defaultdict(set)
        contributor_debt_files = defaultdict(set)

        for file_path, authors in result["file_authors"].items():

            for author in authors:

                contributor_total_files[author].add(file_path)

                if file_path in high_risk_set:
                    contributor_debt_files[author].add(file_path)

        debt_ratios = []

        for author, total_files in contributor_total_files.items():

            debt_count = len(contributor_debt_files.get(author, set()))
            total_count = len(total_files)

            ratio = round(debt_count / total_count, 2) if total_count else 0

            debt_ratios.append({
                "author": author,
                "files_touched": total_count,
                "high_risk_files_touched": debt_count,
                "debt_contribution_ratio": ratio
            })

        debt_ratios.sort(
            key=lambda x: x["debt_contribution_ratio"], reverse=True
        )

        return debt_ratios