import os

def count_files(repo_path):
    total = 0

    for root, dirs, files in os.walk(repo_path):
        IGNORE_DIRS = {
            ".git",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build"
        }
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]
        total += len(files)

    return total


from collections import Counter
import os


def get_extensions(repo_path):
    extensions = Counter()

    for root, dirs, files in os.walk(repo_path):
        IGNORE_DIRS = {
            ".git",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build"
        }
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]
        for file in files:

            ext = os.path.splitext(file)[1]

            if ext:
                extensions[ext] += 1

    return dict(extensions)


import os


def count_lines(repo_path):

    total_lines = 0

    for root, dirs, files in os.walk(repo_path):
        IGNORE_DIRS = {
            ".git",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build"
        }
        dirs[:] = [
            d for d in dirs
            if d not in IGNORE_DIRS
        ]
        for file in files:

            file_path = os.path.join(root, file)

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    total_lines += len(f.readlines())

            except:
                pass

    return total_lines


import os
from collections import Counter


class RepositoryAnalyzer:

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def analyze(self):

        total_files = count_files(self.repo_path)

        extensions = get_extensions(self.repo_path)

        total_lines = count_lines(self.repo_path)

        return {
            "repository_name": os.path.basename(self.repo_path),
            "total_files": total_files,
            "total_lines": total_lines,
            "extensions": extensions
        }