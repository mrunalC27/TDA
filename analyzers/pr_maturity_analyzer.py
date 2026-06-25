import os
import re
import requests

GITHUB_API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 10
MAX_PRS_TO_FETCH = 50


def parse_owner_repo(repo_url):

    match = re.search(
        r"github\.com/([\w.-]+)/([\w.-]+?)(\.git)?/?$",
        repo_url.strip()
    )

    if not match:
        return None, None

    return match.group(1), match.group(2)


class PRMaturityAnalyzer:
    """
    Computes PR Maturity Index using the GitHub API - requires
    network access and a GITHUB_TOKEN environment variable.
    Measures review coverage and merge timing across recent PRs.
    """

    def __init__(self, repo_url):

        self.repo_url = repo_url
        self._cache = None
        self.token = os.getenv("GITHUB_TOKEN")

    def _headers(self):

        headers = {"Accept": "application/vnd.github+json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def analyze(self):

        if self._cache is not None:
            return self._cache

        owner, repo = parse_owner_repo(self.repo_url)

        if not owner or not repo:

            self._cache = {"status": "Could Not Parse GitHub URL"}
            return self._cache

        try:

            response = requests.get(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls",
                params={"state": "closed", "per_page": MAX_PRS_TO_FETCH},
                headers=self._headers(),
                timeout=REQUEST_TIMEOUT
            )

        except requests.exceptions.RequestException as e:

            self._cache = {"status": "GitHub API Request Failed", "reason": str(e)}
            return self._cache

        if response.status_code == 403:

            self._cache = {
                "status": "GitHub API Rate Limited",
                "reason": "Add a GITHUB_TOKEN to .env to increase rate limits."
            }

            return self._cache

        if response.status_code != 200:

            self._cache = {
                "status": "GitHub API Error",
                "reason": f"HTTP {response.status_code}"
            }

            return self._cache

        prs = response.json()

        if not prs:

            self._cache = {"status": "No Pull Requests Found"}
            return self._cache

        pr_data = []

        for pr in prs:

            if not pr.get("merged_at"):
                continue

            try:

                review_response = requests.get(
                    pr["url"] + "/reviews",
                    headers=self._headers(),
                    timeout=REQUEST_TIMEOUT
                )

                review_count = (
                    len(review_response.json())
                    if review_response.status_code == 200
                    else 0
                )

            except requests.exceptions.RequestException:

                review_count = 0

            created = pr["created_at"]
            merged = pr["merged_at"]

            pr_data.append({
                "pr_number": pr["number"],
                "title": pr["title"][:60],
                "review_count": review_count,
                "merged_without_review": review_count == 0,
                "created_at": created,
                "merged_at": merged
            })

        self._cache = {"prs": pr_data}
        return self._cache

    def summary(self):

        result = self.analyze()

        if "status" in result:
            return result

        prs = result["prs"]

        if not prs:
            return {"status": "No Merged Pull Requests Found"}

        unreviewed = len([p for p in prs if p["merged_without_review"]])

        return {
            "merged_prs_analyzed": len(prs),
            "merged_without_review": unreviewed,
            "review_coverage_pct": round(
                ((len(prs) - unreviewed) / len(prs)) * 100, 1
            )
        }

    def top_findings(self, limit=20):

        result = self.analyze()

        if "status" in result:
            return []

        prs = list(result["prs"])

        prs.sort(key=lambda x: x["merged_without_review"], reverse=True)

        return prs[:limit]