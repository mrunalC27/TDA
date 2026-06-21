import os
import re


class JSDeadCodeAnalyzer:

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

        for file_path in self.get_js_files():

            with open(
                file_path,
                encoding="utf-8",
                errors="ignore"
            ) as f:

                content = f.read()

            functions = re.findall(
                r'function\s+(\w+)',
                content
            )

            for fn in functions:

                count = content.count(fn)

                if count == 1:

                    findings.append({

                        "name": fn,

                        "type": "function",

                        "file":
                        os.path.basename(
                            file_path
                        )
                    })

        return findings

    def summary(self):

        findings = self.analyze()

        return {

            "total_dead_code":
            len(findings),

            "functions":
            len(findings)
        }

    def top_findings(
        self,
        limit=20
    ):

        return self.analyze()[:limit]