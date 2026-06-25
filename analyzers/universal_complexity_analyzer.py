import os
import lizard


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

HIGH_RISK_THRESHOLD = 10


class UniversalComplexityAnalyzer:
    """
    Language-agnostic complexity analyzer using lizard.
    Supports Python, Java, JavaScript, TypeScript, C, C++, C#,
    Go, Rust, PHP, Ruby, Swift, Kotlin, Scala, Objective-C and more.
    Used as the fallback for any language not covered by a
    dedicated analyzer (radon for Python, custom regex for JS).
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def _collect_files(self):

        collected = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if d not in IGNORE_DIRS
            ]

            for file in files:

                collected.append(os.path.join(root, file))

        return collected

    def analyze(self):

        if self._cache is not None:
            return self._cache

        files = self._collect_files()

        findings = []

        try:

            analysis = lizard.analyze_files(files)

            for file_result in analysis:

                for function in file_result.function_list:

                    findings.append({
                        "file": os.path.relpath(file_result.filename, self.repo_path),
                        "function": function.name,
                        "complexity": function.cyclomatic_complexity,
                        "length": function.length,
                        "parameters": len(function.parameters)
                    })

        except Exception:

            findings = []

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        if not findings:
            return {}

        scores = [f["complexity"] for f in findings]

        return {
            "functions_analyzed": len(scores),
            "average_complexity": round(
                sum(scores) / len(scores), 2
            ),
            "high_risk_functions": len(
                [x for x in scores if x > HIGH_RISK_THRESHOLD]
            ),
            "max_complexity": max(scores)
        }

    def hotspots(self, top_n=10):

        findings = list(self.analyze())

        findings.sort(
            key=lambda x: x["complexity"],
            reverse=True
        )

        return findings[:top_n]