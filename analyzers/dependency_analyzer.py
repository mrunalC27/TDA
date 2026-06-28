import os
import json
import subprocess

DEPENDENCY_TIMEOUT = 120


class DependencyAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def find_requirements(self):

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if d not in {".git", "venv", ".venv", "node_modules", "__pycache__"}
            ]

            if "requirements.txt" in files:

                return os.path.join(root, "requirements.txt")

        return None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        requirements = self.find_requirements()

        if not requirements:

            self._cache = []
            return self._cache

        try:

            result = subprocess.run(
                [
                    "pip-audit",
                    "-r",
                    requirements,
                    "--format",
                    "json"
                ],
                capture_output=True,
                text=True,
                timeout=DEPENDENCY_TIMEOUT
            )

            if result.returncode != 0:

                self._cache = [{
                    "package": "Dependency Resolution Error",
                    "version": "-",
                    "id": "N/A",
                    "description": result.stderr[:500]
                }]

                return self._cache

            data = json.loads(result.stdout)

            findings = []

            for package in data.get("dependencies", []):

                vulnerabilities = package.get("vulns", [])

                for vuln in vulnerabilities:

                    findings.append({
                        "package": package["name"],
                        "version": package["version"],
                        "id": vuln["id"],
                        "description": vuln.get("description", "")
                    })

            self._cache = findings
            return self._cache

        except subprocess.TimeoutExpired:

            self._cache = [{
                "package": "Dependency Resolution Error",
                "version": "-",
                "id": "N/A",
                "description": "pip-audit took too long and was stopped."
            }]

            return self._cache

        except Exception as e:

            self._cache = [{
                "package": "Dependency Resolution Error",
                "version": "-",
                "id": "N/A",
                "description": str(e)
            }]

            return self._cache

    def summary(self):

        findings = self.analyze()

        if findings and findings[0]["package"] == "Dependency Resolution Error":

            return {
                "status": "Audit Failed",
                "reason": findings[0]["description"]
            }

        unique_packages = len(
            set(item["package"] for item in findings)
        )

        return {
            "vulnerabilities": len(findings),
            "affected_packages": unique_packages
        }

    def top_findings(self, limit=20):

        return self.analyze()[:limit]