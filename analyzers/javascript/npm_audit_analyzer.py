import os
import json
import shutil
import subprocess


class NPMAuditAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cached_findings = None

    def find_package_json(self):

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [
                d for d in dirs
                if d not in {".git", "node_modules"}
            ]

            if "package.json" in files:

                return root

        return None

    def analyze(self):

        if self._cached_findings is not None:
            return self._cached_findings

        npm_path = shutil.which("npm")

        if not npm_path:

            self._cached_findings = [{
                "package": "npm Not Found",
                "severity": "unknown",
                "fix_available": False,
                "description": (
                    "npm is not installed on this machine. "
                    "Install Node.js to enable dependency scanning."
                )
            }]

            return self._cached_findings

        repo_root = self.find_package_json()

        if not repo_root:

            self._cached_findings = []
            return self._cached_findings

        try:

            install_result = subprocess.run(
                [
                    npm_path,
                    "install",
                    "--package-lock-only",
                    "--no-audit",
                    "--ignore-scripts"
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=120
            )

            if install_result.returncode != 0:

                self._cached_findings = [{
                    "package": "Dependency Resolution Error",
                    "severity": "unknown",
                    "fix_available": False,
                    "description": install_result.stderr[:500]
                }]

                return self._cached_findings

            audit_result = subprocess.run(
                [npm_path, "audit", "--json"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            data = json.loads(audit_result.stdout)

            findings = []

            vulnerabilities = data.get("vulnerabilities", {})

            for name, vuln in vulnerabilities.items():

                findings.append({
                    "package": name,
                    "severity": vuln.get("severity", "unknown"),
                    "fix_available": vuln.get("fixAvailable", False)
                })

            self._cached_findings = findings
            return self._cached_findings

        except subprocess.TimeoutExpired:

            self._cached_findings = [{
                "package": "Audit Timeout",
                "severity": "unknown",
                "fix_available": False,
                "description": "npm install/audit took too long and was stopped."
            }]

            return self._cached_findings

        except Exception as e:

            self._cached_findings = [{
                "package": "Dependency Resolution Error",
                "severity": "unknown",
                "fix_available": False,
                "description": str(e)
            }]

            return self._cached_findings

    def summary(self):

        findings = self.analyze()

        error_types = {
            "npm Not Found",
            "Dependency Resolution Error",
            "Audit Timeout"
        }

        if findings and findings[0]["package"] in error_types:

            return {
                "status": "Audit Failed",
                "reason": findings[0]["description"]
            }

        return {
            "vulnerabilities": len(findings),
            "affected_packages": len(
                set(item["package"] for item in findings)
            )
        }

    def top_findings(self, limit=20):

        return self.analyze()[:limit]