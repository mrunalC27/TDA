import os

from radon.metrics import mi_visit

IGNORE_DIRS = {
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build"
}

def get_maintainability_status(score):

    if score >= 85:
        return "Excellent"

    elif score >= 65:
        return "Good"

    elif score >= 40:
        return "Moderate"

    return "Poor"

def analyze_file(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            code = f.read()

        score = round(
            mi_visit(code, multi=True),
            2
        )

        return {
            "file": os.path.basename(file_path),
            "score": score,
            "status": get_maintainability_status(score)
        }

    except Exception:

        return None

class MaintainabilityAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        results = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if d not in IGNORE_DIRS
            ]

            for file in files:

                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(
                    root,
                    file
                )

                result = analyze_file(
                    file_path
                )

                if result:
                    results.append(result)

        self._cache = results
        return self._cache

    def summary(self):

        results = self.analyze()

        if not results:
            return {}

        scores = [
            r["score"]
            for r in results
        ]

        average_score = round(
            sum(scores) / len(scores),
            2
        )

        return {
            "files_analyzed": len(scores),
            "average_maintainability": average_score,
            "status": get_maintainability_status(
                average_score
            ),
            "lowest_score": min(scores),
            "highest_score": max(scores)
        }

    def worst_files(self, top_n=10):

        results = list(self.analyze())

        results.sort(
            key=lambda x: x["score"]
        )

        return results[:top_n]