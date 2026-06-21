import os
from collections import Counter


class RepositoryProfiler:

    def __init__(self, repo_path):

        self.repo_path = repo_path

    EXTENSION_MAP = {

            ".py": "Python",

            ".js": "JavaScript",

            ".jsx": "JavaScript",

            ".ts": "TypeScript",

            ".tsx": "TypeScript",

            ".java": "Java",

            ".go": "Go",

            ".rs": "Rust",

            ".cpp": "C++",

            ".cc": "C++",

            ".c": "C",

            ".cs": "C#",

            ".php": "PHP",

            ".rb": "Ruby",

            ".kt": "Kotlin",

            ".swift": "Swift"
    }

    MARKUP_EXTENSION_MAP = {

        ".html": "HTML",

        ".css": "CSS",

        ".scss": "SCSS"
    }
        
    def detect_languages(self):

            counts = Counter()

            IGNORE_DIRS = {
                ".git",
                "node_modules",
                "venv",
                ".venv",
                "__pycache__",
                "dist",
                "build"
            }

            for root, dirs, files in os.walk(
                self.repo_path
            ):

                dirs[:] = [
                    d for d in dirs
                    if d not in IGNORE_DIRS
                ]

                for file in files:

                    ext = os.path.splitext(
                        file
                    )[1].lower()

                    language = (
                        self.EXTENSION_MAP.get(ext)
                    )

                    if language:

                        counts[language] += 1

            return counts
    
    def detect_framework(self):
        frameworks = {

            "requirements.txt": {
                "fastapi": "FastAPI",
                "django": "Django",
                "flask": "Flask"
            },

            "package.json": {
                "react": "React",
                "next": "Next.js",
                "vue": "Vue",
                "angular": "Angular"
            }
        }
        for root, dirs, files in os.walk(
        self.repo_path
        ):

            if "requirements.txt" in files:

                path = os.path.join(
                    root,
                    "requirements.txt"
                )

                with open(
                    path,
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    content = f.read().lower()

                for key, value in frameworks[
                    "requirements.txt"
                ].items():

                    if key in content:

                        return value

            if "package.json" in files:

                path = os.path.join(
                    root,
                    "package.json"
                )

                with open(
                    path,
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    content = f.read().lower()

                for key, value in frameworks[
                    "package.json"
                ].items():

                    if key in content:

                        return value

        return "Unknown"
    
    def detect_package_manager(self):
        for root, dirs, files in os.walk(
        self.repo_path
        ):

            if "requirements.txt" in files:

                return "pip"

            if "package.json" in files:

                return "npm"

            if "pom.xml" in files:

                return "maven"

            if "go.mod" in files:

                return "go modules"

        return "Unknown"
        
    def analyze(self):

            languages = self.detect_languages()

            if not languages:

                return {
                    "primary_language": "Unknown",
                    "secondary_languages": [],
                    "framework": "Unknown",
                    "package_manager": "Unknown"
                }

            primary_language = (
                languages.most_common(1)[0][0]
            )

            secondary = [

                lang

                for lang, count

                in languages.most_common()[1:]
            ]

            return {

                "primary_language":
                primary_language,

                "secondary_languages":
                secondary,

                "framework":
                self.detect_framework(),

                "package_manager":
                self.detect_package_manager()
            }