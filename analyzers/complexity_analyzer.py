import os
from radon.complexity import cc_visit

IGNORE_DIRS = {
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build"
}


def get_risk_level(score):

    if score <= 5:
        return "Low"

    elif score <= 10:
        return "Medium"

    elif score <= 20:
        return "High"

    return "Critical"


def analyze_file(file_path):

    findings = []

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            code = f.read()

        results = cc_visit(code)

        for item in results:

            findings.append({
                "function": item.name,
                "line": item.lineno,
                "complexity": item.complexity,
                "risk": get_risk_level(item.complexity)
            })

    except Exception:
        pass

    return findings


class ComplexityAnalyzer:

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def analyze(self):

        findings = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if d not in IGNORE_DIRS
            ]

            for file in files:

                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)

                file_findings = analyze_file(file_path)

                for item in file_findings:

                    item["file"] = file

                    findings.append(item)

        return findings

    def summary(self):

        findings = self.analyze()

        if not findings:
            return {}

        scores = [
            f["complexity"]
            for f in findings
        ]

        return {
            "functions_analyzed": len(scores),
            "average_complexity": round(
                sum(scores) / len(scores),
                2
            ),
            "high_risk_functions": len(
                [x for x in scores if x > 10]
            ),
            "max_complexity": max(scores)
        }

    def hotspots(self, top_n=10):

        findings = self.analyze()

        findings.sort(
            key=lambda x: x["complexity"],
            reverse=True
        )

        return findings[:top_n]