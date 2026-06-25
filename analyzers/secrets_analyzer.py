import os
import re


IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target"
}

IGNORE_FILES = {"package-lock.json", "yarn.lock", "poetry.lock"}

MAX_FILE_SIZE = 2_000_000

SIGNATURE_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", "HIGH"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API Key", "HIGH"),
    (r"gh[pousr]_[0-9A-Za-z]{36,}", "GitHub Token", "HIGH"),
    (r"xox[baprs]-[0-9A-Za-z\-]{10,}", "Slack Token", "HIGH"),
    (r"sk_live_[0-9A-Za-z]{24,}", "Stripe Live Secret Key", "HIGH"),
    (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "Private Key Block", "HIGH"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "JWT-like Token", "MEDIUM"),
]

GENERIC_CREDENTIAL_PATTERN = re.compile(
    r"""(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['"]([^'"\s]{6,})['"]"""
)

PLACEHOLDER_VALUES = {
    "changeme", "your_api_key", "your-api-key", "xxx", "todo",
    "placeholder", "example", "test", "password", "secret",
    "your_secret_here", "<your-key-here>", "insert_key_here"
}


class SecretsAnalyzer:
    """
    Language-agnostic secrets/credentials scanner. Reads any text
    file regardless of extension and checks for known secret
    signatures plus generic credential-assignment patterns.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def _scan_file(self, file_path):

        findings = []

        try:

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                return findings

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        except Exception:

            return findings

        rel_path = os.path.relpath(file_path, self.repo_path)

        for pattern, label, severity in SIGNATURE_PATTERNS:

            for match in re.finditer(pattern, content):

                line_no = content[: match.start()].count("\n") + 1

                findings.append({
                    "file": rel_path,
                    "line": line_no,
                    "type": label,
                    "severity": severity,
                    "match_preview": match.group(0)[:10] + "..."
                })

        for match in GENERIC_CREDENTIAL_PATTERN.finditer(content):

            value = match.group(2).strip().lower()

            if value in PLACEHOLDER_VALUES:
                continue

            if len(set(value)) <= 2:
                continue

            line_no = content[: match.start()].count("\n") + 1

            findings.append({
                "file": rel_path,
                "line": line_no,
                "type": f"Hardcoded {match.group(1)}",
                "severity": "MEDIUM",
                "match_preview": match.group(2)[:4] + "..."
            })

        return findings

    def analyze(self):

        if self._cache is not None:
            return self._cache

        findings = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:

                if file in IGNORE_FILES:
                    continue

                if file == ".env":

                    findings.append({
                        "file": os.path.relpath(
                            os.path.join(root, file), self.repo_path
                        ),
                        "line": 0,
                        "type": ".env file committed to repository",
                        "severity": "HIGH",
                        "match_preview": "N/A"
                    })

                    continue

                full_path = os.path.join(root, file)

                findings.extend(self._scan_file(full_path))

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        high = len([f for f in findings if f["severity"] == "HIGH"])
        medium = len([f for f in findings if f["severity"] == "MEDIUM"])

        return {
            "total_findings": len(findings),
            "high_severity": high,
            "medium_severity": medium
        }

    def top_findings(self, limit=30):

        findings = list(self.analyze())

        severity_rank = {"HIGH": 2, "MEDIUM": 1}

        findings.sort(
            key=lambda x: severity_rank.get(x["severity"], 0),
            reverse=True
        )

        return findings[:limit]