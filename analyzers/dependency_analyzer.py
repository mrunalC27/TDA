import os
import json
import subprocess

class DependencyAnalyzer:

    def __init__(self, repo_path):

        self.repo_path = repo_path

    def find_requirements(self):

        for root, dirs, files in os.walk(
            self.repo_path
        ):
        # for root, dirs, files in os.walk(self.repo_path):

        #     print("ROOT:", root)
        #     print("FILES:", files)

        #     if "requirements.txt" in files:

        #         return os.path.join(
        #             root,
        #             "requirements.txt"
        #         )

            if "requirements.txt" in files:

                return os.path.join(
                    root,
                    "requirements.txt"
                )

        return None
    
    def analyze(self):



        print("DEPENDENCY ANALYZER STARTED")

        requirements = self.find_requirements()

        print("FOUND FILE:", requirements)

        requirements = (
            self.find_requirements()
        )

        if not requirements:

            return []

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
                text=True
            )
            print("FILE:", requirements)
            print("RETURN CODE:", result.returncode)
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)

            # data = json.loads(
            #     result.stdout
            # )
            if result.returncode != 0:

                return [{
                    "package": "Dependency Resolution Error",
                    "version": "-",
                    "id": "N/A",
                    "description": result.stderr
                }]

            data = json.loads(result.stdout)
            print("RAW JSON:")
            print(data)

            findings = []

            for package in data.get(
                "dependencies",
                []
            ):

                vulnerabilities = package.get(
                    "vulns",
                    []
                )

                for vuln in vulnerabilities:

                    findings.append({
                        "package":
                        package["name"],

                        "version":
                        package["version"],

                        "id":
                        vuln["id"],

                        "description":
                        vuln.get(
                            "description",
                            ""
                        )
                    })

            return findings

        except Exception as e:

            print("ERROR:", e)

            return []
        
    def summary(self):

        findings = self.analyze()

        unique_packages = len(
            set(
                item["package"]
                for item in findings
            )
        )

        if findings and findings[0]["package"] == "Dependency Resolution Error":

            return {
                "status": "Audit Failed",
                "reason": "Dependency conflicts detected"
            }

        return {
            "vulnerabilities": len(findings),
            "affected_packages": unique_packages
        }
    
    def top_findings(
        self,
        limit=20
    ):

        return self.analyze()[:limit]