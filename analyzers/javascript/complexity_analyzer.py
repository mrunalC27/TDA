import os 

class JSComplexityAnalyzer:

    def __init__(
        self,
        repo_path
    ):

        self.repo_path = repo_path

    def get_js_files(self):

        js_files = []

        for root, dirs, files in os.walk(
            self.repo_path
        ):

            dirs[:] = [

                d for d in dirs

                if d not in {
                    ".git",
                    "node_modules"
                }
            ]

            for file in files:

                if file.endswith(
                    (
                        ".js",
                        ".jsx"
                    )
                ):

                    js_files.append(
                        os.path.join(
                            root,
                            file
                        )
                    )

        return js_files
    def analyze(self):

        findings = []

        js_files = self.get_js_files()

        print("JS FILES FOUND:", len(js_files))

        for file_path in js_files:

            with open(
                file_path,
                encoding="utf-8",
                errors="ignore"
            ) as f:

                content = f.read()

            complexity = 1

            keywords = [

                "if",
                "else if",
                "for",
                "while",
                "switch",
                "case",
                "catch",
                "&&",
                "||"
            ]

            for keyword in keywords:

                complexity += content.count(
                    keyword
                )

            findings.append({

                "file":
                os.path.basename(
                    file_path
                ),

                "complexity":
                complexity
            })

        print(
            "TOTAL FINDINGS:",
            len(findings)
        )

        return findings
    
    def summary(self):

        findings = self.analyze()

        if not findings:

            return {}

        scores = [

            item["complexity"]

            for item in findings
        ]

        return {

            "files_analyzed":
            len(findings),

            "average_complexity":
            round(
                sum(scores)
                /
                len(scores),
                2
            ),

            "max_complexity":
            max(scores),

            "high_risk_files":
            len(
                [
                    s
                    for s in scores
                    if s > 15
                ]
            )
        }
    def hotspots(
        self,
        limit=10
    ):

        findings = self.analyze()

        findings.sort(

            key=lambda x:
            x["complexity"],

            reverse=True
        )

        return findings[:limit]