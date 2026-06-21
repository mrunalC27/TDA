import os


class JSMaintainabilityAnalyzer:

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

        for file_path in self.get_js_files():

            try:

                with open(
                    file_path,
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    lines = f.readlines()

                total_lines = len(lines)
                long_lines = 0

                for line in lines:

                    if len(line) > 120:

                        long_lines += 1
                comment_lines = 0

                for line in lines:

                    stripped = line.strip()

                    if (
                        stripped.startswith("//")
                        or stripped.startswith("/*")
                        or stripped.startswith("*")
                    ):

                        comment_lines += 1

                comment_ratio = 0

                if total_lines > 0:

                    comment_ratio = round(
                        (
                            comment_lines
                            /
                            total_lines
                        ) * 100,
                        2
                    )

                score = 100
                if long_lines > 50:

                    score -= 10
                if total_lines > 500:

                    score -= 10

                if total_lines > 1000:

                    score -= 20

                if total_lines > 2000:

                    score -= 20

                if comment_ratio < 5:

                    score -= 10

                if comment_ratio < 2:

                    score -= 10

                score = max(
                    score,
                    0
                )

                findings.append({

                    "file":
                    os.path.basename(
                        file_path
                    ),

                    "lines":
                    total_lines,

                    "comment_ratio":
                    comment_ratio,

                    "maintainability":
                    score
                })

            except Exception:

                continue

        return findings

    def summary(self):

        findings = self.analyze()

        if not findings:

            return {}

        scores = [

            item["maintainability"]

            for item in findings
        ]

        average_score = round(

            sum(scores)
            /
            len(scores),

            2
        )

        if average_score >= 85:

            status = "Excellent"

        elif average_score >= 70:

            status = "Good"

        elif average_score >= 50:

            status = "Moderate"

        else:

            status = "Poor"

        return {

            "files_analyzed":
            len(findings),

            "average_maintainability":
            average_score,

            "status":
            status,

            "lowest_score":
            min(scores),

            "highest_score":
            max(scores)
        }

    def worst_files(
        self,
        limit=10
    ):

        findings = self.analyze()

        findings.sort(

            key=lambda x:
            x["maintainability"]
        )

        return findings[:limit]