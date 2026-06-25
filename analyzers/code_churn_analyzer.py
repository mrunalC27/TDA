import os
import subprocess
from collections import defaultdict
from git import Repo, InvalidGitRepositoryError

GIT_LOG_TIMEOUT = 60

IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "vendor",
    "target"
}

HIGH_CHURN_THRESHOLD = 10


class CodeChurnAnalyzer:
    """
    Measures how often each file has changed across commit history.
    High churn + high complexity (see UniversalComplexityAnalyzer /
    ComplexityAnalyzer) is a strong signal of an unstable, bug-prone file.
    Requires full git history - call fetch_full_history() on the repo
    before using this analyzer, otherwise results will be inaccurate
    (shallow clones only show 1 commit).
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def analyze(self):

            if self._cache is not None:
                return self._cache

            try:

                repo = Repo(self.repo_path)

            except InvalidGitRepositoryError:

                self._cache = []
                return self._cache

            churn_counts = defaultdict(int)


            try:
                
                result = subprocess.run(
                ["git", "log", "--name-only", "--pretty=format:"],
                cwd=self.repo_path,
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                timeout=GIT_LOG_TIMEOUT
                )

                raw_output = result.stdout

            except subprocess.TimeoutExpired:

                self._cache = [{
                    "file": "Churn Analysis Timeout",
                    "changes": 0
                }]

                return self._cache

            except Exception:

                self._cache = []
                return self._cache
    

            for line in raw_output.splitlines():

                file_path = line.strip()

                if not file_path:
                    continue

                parts = file_path.split("/")

                if any(p in IGNORE_DIRS for p in parts):
                    continue

                churn_counts[file_path] += 1

            findings = [
                {"file": file_path, "changes": count}
                for file_path, count in churn_counts.items()
            ]

            self._cache = findings
            return self._cache

    def summary(self):

        findings = self.analyze()

        if not findings:
            return {"status": "No History Available"}

        change_counts = [f["changes"] for f in findings]

        return {
            "files_tracked": len(findings),
            "average_changes": round(
                sum(change_counts) / len(change_counts), 2
            ),
            "high_churn_files": len(
                [c for c in change_counts if c > HIGH_CHURN_THRESHOLD]
            ),
            "max_changes": max(change_counts)
        }

    def hotspots(self, top_n=10):

        findings = list(self.analyze())

        findings.sort(
            key=lambda x: x["changes"],
            reverse=True
        )

        return findings[:top_n]