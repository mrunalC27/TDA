import os
import re
import shutil
import stat
import uuid
import requests

from git import Repo, GitCommandError
from dotenv import load_dotenv

load_dotenv()
CLONE_DIR = "cloned_repos"

GITHUB_URL_PATTERN = re.compile(
    r"^https://github\.com/[\w.-]+/[\w.-]+(\.git)?/?$"
)


def validate_repo_url(repo_url):

    if not repo_url or not GITHUB_URL_PATTERN.match(repo_url.strip()):

        raise ValueError(
            "Invalid GitHub URL. Expected format: "
            "https://github.com/owner/repo"
        )


def clone_repository(repo_url):

    repo_url = repo_url.strip()

    validate_repo_url(repo_url)

    os.makedirs(CLONE_DIR, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")

    unique_suffix = uuid.uuid4().hex[:8]

    repo_path = os.path.join(
        CLONE_DIR,
        f"{repo_name}_{unique_suffix}"
    )

    try:

        Repo.clone_from(
            repo_url,
            repo_path,
            depth=1,
            single_branch=True
        )

    except GitCommandError as e:

        if os.path.exists(repo_path):
            shutil.rmtree(repo_path, ignore_errors=True)

        raise ValueError(
            f"Failed to clone repository. Check the URL and that the "
            f"repository is public. Details: {str(e)[:300]}"
        )

    return repo_path


def fetch_full_history(repo_path):

    try:

        repo = Repo(repo_path)

        if repo.git.rev_parse("--is-shallow-repository") == "true":

            repo.git.fetch("--unshallow")

        return True

    except Exception:

        return False


def _remove_readonly(func, path, exc_info):

    os.chmod(path, stat.S_IWRITE)
    func(path)


def cleanup_repository(repo_path):

    if not repo_path or not os.path.exists(repo_path) or CLONE_DIR not in repo_path:
        return

    try:

        shutil.rmtree(repo_path, onerror=_remove_readonly)

    except Exception as e:

        print(f"Cleanup failed for {repo_path}: {e}")



def get_latest_commit_hash(repo_url):

    owner_repo_match = re.search(
        r"github\.com/([\w.-]+)/([\w.-]+?)(\.git)?/?$",
        repo_url.strip()
    )

    if not owner_repo_match:
        print(f"COMMIT HASH: URL regex did not match for {repo_url}")
        return None

    owner = owner_repo_match.group(1)
    repo = owner_repo_match.group(2)

    headers = {"Accept": "application/vnd.github+json"}

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:

        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            params={"per_page": 1},
            headers=headers,
            timeout=10
        )

        print(f"COMMIT HASH: status={response.status_code} owner={owner} repo={repo}")

        if response.status_code != 200:
            print(f"COMMIT HASH: response body={response.text[:300]}")
            return None

        commits = response.json()

        if not commits:
            print("COMMIT HASH: empty commits list")
            return None

        return commits[0]["sha"]

    except Exception as e:

        print(f"COMMIT HASH EXCEPTION: {e}")
        return None