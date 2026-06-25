import os
import json
import re
import requests
from packaging.version import Version, InvalidVersion

PYPI_URL = "https://pypi.org/pypi/{package}/json"
NPM_URL = "https://registry.npmjs.org/{package}"

REQUEST_TIMEOUT = 5

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build"
}


def clean_version(raw):

    match = re.search(r"[\d]+\.[\d]+(\.[\d]+)?", raw)
    return match.group(0) if match else None


def classify_staleness(current, latest):

    try:

        current_v = Version(current)
        latest_v = Version(latest)

    except InvalidVersion:

        return "unknown"

    if current_v >= latest_v:
        return "up_to_date"

    if current_v.major != latest_v.major:
        return "major_behind"

    if current_v.minor != latest_v.minor:
        return "minor_behind"

    return "patch_behind"


class DependencyRotAnalyzer:
    """
    Checks how far each dependency is behind its latest published
    version. Complements vulnerability scanning (DependencyAnalyzer /
    NPMAuditAnalyzer) - a package can be rot-free of vulnerabilities
    but still dangerously outdated.
    """

    def __init__(self, repo_path, language):

        self.repo_path = repo_path
        self.language = language
        self._cache = None

    def _find_file(self, filename):

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            if filename in files:
                return os.path.join(root, filename)

        return None

    def _parse_python_requirements(self, path):

        deps = {}

        with open(path, "r", encoding="utf-8", errors="ignore") as f:

            for line in f:

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                match = re.match(
                    r"^([A-Za-z0-9_\-\.]+)\s*==\s*([0-9.]+)", line
                )

                if match:
                    deps[match.group(1)] = match.group(2)

        return deps

    def _parse_package_json(self, path):

        deps = {}

        try:

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)

        except Exception:

            return deps

        for section in ("dependencies", "devDependencies"):

            for name, version_raw in data.get(section, {}).items():

                cleaned = clean_version(version_raw)

                if cleaned:
                    deps[name] = cleaned

        return deps

    def _fetch_latest_pypi(self, package):

        try:

            response = requests.get(
                PYPI_URL.format(package=package),
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                return None

            return response.json()["info"]["version"]

        except Exception:

            return None

    def _fetch_latest_npm(self, package):

        try:

            response = requests.get(
                NPM_URL.format(package=package),
                timeout=REQUEST_TIMEOUT
            )

            if response.status_code != 200:
                return None

            return response.json().get("dist-tags", {}).get("latest")

        except Exception:

            return None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        findings = []

        if self.language == "Python":

            req_path = self._find_file("requirements.txt")

            if req_path:

                deps = self._parse_python_requirements(req_path)

                for name, current_version in deps.items():

                    latest = self._fetch_latest_pypi(name)

                    if not latest:
                        continue

                    findings.append({
                        "package": name,
                        "current_version": current_version,
                        "latest_version": latest,
                        "status": classify_staleness(current_version, latest)
                    })

        elif self.language == "JavaScript":

            pkg_path = self._find_file("package.json")

            if pkg_path:

                deps = self._parse_package_json(pkg_path)

                for name, current_version in deps.items():

                    latest = self._fetch_latest_npm(name)

                    if not latest:
                        continue

                    findings.append({
                        "package": name,
                        "current_version": current_version,
                        "latest_version": latest,
                        "status": classify_staleness(current_version, latest)
                    })

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        if not findings:
            return {"status": "No Dependency File Found Or Unsupported Language"}

        major = len([f for f in findings if f["status"] == "major_behind"])
        minor = len([f for f in findings if f["status"] == "minor_behind"])
        patch = len([f for f in findings if f["status"] == "patch_behind"])
        current = len([f for f in findings if f["status"] == "up_to_date"])

        return {
            "packages_checked": len(findings),
            "up_to_date": current,
            "patch_behind": patch,
            "minor_behind": minor,
            "major_behind": major
        }

    def top_findings(self, limit=30):

        findings = list(self.analyze())

        severity_rank = {
            "major_behind": 3,
            "minor_behind": 2,
            "patch_behind": 1,
            "up_to_date": 0,
            "unknown": 0
        }

        findings.sort(
            key=lambda x: severity_rank.get(x["status"], 0),
            reverse=True
        )

        return findings[:limit]