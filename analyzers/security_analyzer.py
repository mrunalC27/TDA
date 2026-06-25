import json
import subprocess
class SecurityAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path

    def analyze(self):

        try:

            result = subprocess.run(
                [
                    "bandit",
                    "-r",
                    self.repo_path,
                    "-f",
                    "json"
                ],
                capture_output=True,
                text=True
            )

            data = json.loads(
                result.stdout
            )

            findings = []

            for item in data.get(
                "results",
                []
            ):

                findings.append({
                    "file": item.get("filename"),
                    "line": item.get("line_number"),
                    "issue": item.get("issue_text"),
                    "severity": item.get("issue_severity"),
                    "confidence": item.get("issue_confidence")
                })

            return findings

        except Exception as e:

            print(e)

            return []
    
    def summary(self):

        findings = self.analyze()

        high_confidence_findings = [
            f for f in findings
            if f.get("confidence", "").upper() in ("HIGH", "MEDIUM")
        ]

        high = 0
        medium = 0
        low = 0

        for item in high_confidence_findings:

            severity = item[
                "severity"
            ].upper()

            if severity == "HIGH":
                high += 1

            elif severity == "MEDIUM":
                medium += 1

            else:
                low += 1

        return {
            "total_issues": len(findings),
            "high_confidence_issues": len(high_confidence_findings),
            "high": high,
            "medium": medium,
            "low": low
        }
    
    def top_findings(
    self,
    limit=20
    ):

        findings = self.analyze()

        severity_order = {
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1
        }

        findings.sort(
            key=lambda x:
            severity_order.get(
                x["severity"].upper(),
                0
            ),
            reverse=True
        )

        return findings[:limit]