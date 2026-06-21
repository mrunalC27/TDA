import os
import re


class JSSecurityAnalyzer:

    def __init__(
        self,
        repo_path
    ):

        self.repo_path = repo_path

    def get_js_files(self):

        files = []

        for root, dirs, filenames in os.walk(
            self.repo_path
        ):

            dirs[:] = [

                d for d in dirs

                if d not in {
                    ".git",
                    "node_modules"
                }
            ]

            for file in filenames:

                if file.endswith(
                    (
                        ".js",
                        ".jsx"
                    )
                ):

                    files.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

        return files

    def analyze(self):

        findings = []

        patterns = [

            (
                r"password\s*=",
                "Possible hardcoded password",
                "HIGH"
            ),

            (
                r"secret\s*=",
                "Possible hardcoded secret",
                "HIGH"
            ),

            (
                r"api[_-]?key\s*=",
                "Possible API key",
                "HIGH"
            ),

            (
                r"eval\s*\(",
                "Use of eval()",
                "MEDIUM"
            ),

            (
                r"innerHTML\s*=",
                "Direct innerHTML assignment",
                "MEDIUM"
            ),

            (
                r"document\.write\s*\(",
                "Use of document.write()",
                "LOW"
            )
        ]

        for file_path in self.get_js_files():

            try:

                with open(
                    file_path,
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    lines = f.readlines()

                for line_no, line in enumerate(
                    lines,
                    start=1
                ):

                    for pattern, issue, severity in patterns:

                        if re.search(
                            pattern,
                            line,
                            re.IGNORECASE
                        ):

                            findings.append({

                                "file":
                                os.path.basename(
                                    file_path
                                ),

                                "line":
                                line_no,

                                "issue":
                                issue,

                                "severity":
                                severity
                            })

            except Exception:

                continue

        return findings

    def summary(self):

        findings = self.analyze()

        return {

            "total_issues":
            len(findings),

            "high":
            len([
                x for x in findings
                if x["severity"] == "HIGH"
            ]),

            "medium":
            len([
                x for x in findings
                if x["severity"] == "MEDIUM"
            ]),

            "low":
            len([
                x for x in findings
                if x["severity"] == "LOW"
            ])
        }

    def top_findings(
        self,
        limit=20
    ):

        return self.analyze()[:limit]