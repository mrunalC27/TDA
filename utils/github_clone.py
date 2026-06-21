import os
import re
import shutil
import uuid

from git import Repo, GitCommandError

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


def cleanup_repository(repo_path):

    if repo_path and os.path.exists(repo_path) and CLONE_DIR in repo_path:
        shutil.rmtree(repo_path, ignore_errors=True)