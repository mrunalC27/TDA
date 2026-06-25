import os
import json
import shutil
import subprocess
import tempfile

IGNORE_PATTERNS = [
    "**/node_modules/**",
    "**/.git/**",
    "**/venv/**",
    "**/.venv/**",
    "**/__pycache__/**",
    "**/dist/**",
    "**/build/**",
    "**/vendor/**",
    "**/target/**",
    "**/*.css",
    "**/*.scss",
    "**/*.min.js",
    "**/package-lock.json",
    "**/yarn.lock",
    "**/pnpm-lock.yaml",
    "**/Cargo.lock",
    "**/poetry.lock"
]

HIGH_DUPLICATION_THRESHOLD = 10


class DuplicationAnalyzer:
    """
    Detects copy-pasted code blocks across files using jscpd.
    Works across languages - not JS-specific despite the tool name.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        jscpd_path = shutil.which("jscpd")

        if not jscpd_path:

            self._cache = [{
                "status": "jscpd Not Found",
                "description": (
                    "jscpd is not installed. "
                    "Run: npm install -g jscpd"
                )
            }]

            return self._cache

        report_dir = tempfile.mkdtemp(prefix="jscpd_report_")

        try:

            ignore_value = ",".join(IGNORE_PATTERNS)

            result = subprocess.run(
                [
                    jscpd_path,
                    self.repo_path,
                    "--reporters", "json",
                    "--output", report_dir,
                    "--silent",
                    "--ignore", ignore_value
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            report_path = os.path.join(report_dir, "jscpd-report.json")

            if not os.path.exists(report_path):

                self._cache = []
                return self._cache

            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            findings = []

            for duplicate in data.get("duplicates", []):

                file_a = duplicate.get("firstFile", {}).get("name", "")
                file_b = duplicate.get("secondFile", {}).get("name", "")

                findings.append({
                    "file_a": file_a,
                    "file_b": file_b,
                    "same_file": file_a == file_b,
                    "lines_duplicated": duplicate.get("lines", 0),
                    "tokens_duplicated": duplicate.get("tokens", 0)
                })

            self._cache = findings
            return self._cache

        except subprocess.TimeoutExpired:

            self._cache = [{
                "status": "Duplication Scan Timeout",
                "description": "jscpd took too long and was stopped."
            }]

            return self._cache

        except Exception as e:

            self._cache = [{
                "status": "Duplication Scan Error",
                "description": str(e)
            }]

            return self._cache

        finally:

            shutil.rmtree(report_dir, ignore_errors=True)

    def summary(self):

        findings = self.analyze()

        error_statuses = {
            "jscpd Not Found",
            "Duplication Scan Timeout",
            "Duplication Scan Error"
        }

        if findings and findings[0].get("status") in error_statuses:

            return {
                "status": findings[0]["status"],
                "reason": findings[0]["description"]
            }

        if not findings:

            return {
                "duplicate_blocks": 0,
                "total_lines_duplicated": 0
            }

        total_lines = sum(f["lines_duplicated"] for f in findings)

        return {
            "duplicate_blocks": len(findings),
            "total_lines_duplicated": total_lines,
            "high_duplication": len(findings) > HIGH_DUPLICATION_THRESHOLD
        }

    def top_findings(self, limit=20):

        findings = list(self.analyze())

        error_statuses = {
            "jscpd Not Found",
            "Duplication Scan Timeout",
            "Duplication Scan Error"
        }

        if findings and findings[0].get("status") in error_statuses:
            return findings

        findings.sort(
            key=lambda x: x["lines_duplicated"],
            reverse=True
        )

        return findings[:limit]