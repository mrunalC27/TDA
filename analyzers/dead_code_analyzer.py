import os
from vulture import Vulture

IGNORE_DIRS = {
    ".git",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build"
}

class DeadCodeAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path

    def analyze(self):

        v = Vulture()

        v.scavenge(
            [self.repo_path]
        )

        findings = []

        for item in v.get_unused_code():

            findings.append({
                "name": item.name,
                "type": item.typ,
                "file": os.path.basename(
                    item.filename
                ),
                "line": item.first_lineno
            })

        return findings
    def summary(self):

        findings = self.analyze()

        type_counts = {}

        for item in findings:

            code_type = item["type"]

            type_counts[code_type] = (
                type_counts.get(code_type, 0) + 1
            )

        return {
            "total_dead_code": len(findings),
            "breakdown": type_counts
        }
    
    def top_findings(self, limit=20):

        findings = self.analyze()

        return findings[:limit]