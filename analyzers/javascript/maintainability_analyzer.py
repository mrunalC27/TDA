import os

MAX_FILE_SIZE = 2_000_000


def get_maintainability_status(score):

    if score >= 85:
        return "Excellent"

    elif score >= 65:
        return "Good"

    elif score >= 40:
        return "Moderate"

    return "Poor"


class JSMaintainabilityAnalyzer:

    def __init__(
        self,
        repo_path
    ):

        self.repo_path = repo_path
        self._cache = None

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

        if self._cache is not None:
            return self._cache

        findings = []

        for file_path in self.get_js_files():

            try:

                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    continue

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

                    "score":
                    score,

                    "status":
                    get_maintainability_status(score)
                })

            except Exception:

                continue

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        if not findings:

            return {}

        scores = [

            item["score"]

            for item in findings
        ]

        average_score = round(

            sum(scores)
            /
            len(scores),

            2
        )

        return {

            "files_analyzed":
            len(findings),

            "average_maintainability":
            average_score,

            "status":
            get_maintainability_status(average_score),

            "lowest_score":
            min(scores),

            "highest_score":
            max(scores)
        }

    def worst_files(
        self,
        limit=10
    ):

        findings = list(self.analyze())

        findings.sort(

            key=lambda x:
            x["score"]
        )

        return findings[:limit]