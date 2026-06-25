import os
import re


IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target",
    "migrations", "seeds", "seed", "fixtures"
}

SCAN_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".cc",
    ".c", ".cs", ".php", ".rb"
}

MAX_FILE_SIZE = 2_000_000

BACKDOOR_PATTERNS = [
    (
        r"""(?i)(username|user)\s*==\s*['"]admin['"]\s*(\|\||or)\s*(password|pass)\s*==\s*['"][^'"]+['"]""",
        "Hardcoded admin/password bypass condition",
        "HIGH"
    ),
    (
        r"(?i)\bDEBUG\s*=\s*True\b",
        "DEBUG mode hardcoded to True",
        "MEDIUM"
    ),
    (
        r"(?i)\.debug\s*=\s*true\b",
        "Debug mode hardcoded to true",
        "MEDIUM"
    ),
    (
        r"(?i)(skip|bypass|disable)[_-]?auth",
        "Auth skip/bypass flag found",
        "HIGH"
    ),
    (
        r"(?i)if\s*\(?\s*(true|1)\s*\)?\s*(:|{)?\s*(#|//)?\s*(skip|bypass).{0,40}(auth|login|permission)",
        "Conditional bypass of auth/login/permission check",
        "HIGH"
    ),
    (
        r"(?i)(#|//)\s*(if\s+not\s+authenticated|if\s*\(?\s*!?\s*authenticated)",
        "Commented-out authentication check",
        "MEDIUM"
    ),
]

DANGEROUS_PATTERNS = [
    (r"\bos\.system\s*\(", "Python: os.system() - command injection risk", "HIGH"),
    (r"\bsubprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True", "Python: subprocess with shell=True", "HIGH"),
    (r"\beval\s*\(", "eval() - arbitrary code execution risk", "HIGH"),
    (r"\bexec\s*\(", "exec() - arbitrary code execution risk", "HIGH"),
    (r"\bpickle\.loads?\s*\(", "Python: pickle deserialization - unsafe with untrusted input", "HIGH"),
    (r"child_process\.exec\s*\(", "Node.js: child_process.exec() - command injection risk", "HIGH"),
    (r"Runtime\.getRuntime\(\)\.exec\s*\(", "Java: Runtime.exec() - command injection risk", "HIGH"),
    (r"ObjectInputStream", "Java: ObjectInputStream - unsafe deserialization risk", "MEDIUM"),
    (r"\bexec\.Command\s*\(", "Go: exec.Command() - verify input is not user-controlled", "MEDIUM"),
    (r"unserialize\s*\(", "PHP: unserialize() - unsafe deserialization risk", "HIGH"),
    (r"\bsystem\s*\(", "Command execution via system() - verify input is not user-controlled", "MEDIUM"),
    (r"Marshal\.load\s*\(", "Ruby: Marshal.load() - unsafe deserialization risk", "HIGH"),
]


class BackdoorPatternAnalyzer:
    """
    Multi-language detector for two categories:
    1. Backdoor/trapdoor patterns - hardcoded bypass conditions,
       debug flags left on, commented-out auth checks.
    2. Dangerous code patterns beyond what Bandit (Python-only) and
       the JS security analyzer already cover - command injection
       and unsafe deserialization across Java, Go, PHP, Ruby, etc.
    Pattern-based - findings are candidates for manual review.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def _scan_file(self, file_path, rel_path):

        findings = []

        try:

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                return findings

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        except Exception:

            return findings

        for pattern, label, severity in BACKDOOR_PATTERNS:

            for match in re.finditer(pattern, content):

                line_no = content[: match.start()].count("\n") + 1

                findings.append({
                    "file": rel_path,
                    "line": line_no,
                    "category": "backdoor",
                    "issue": label,
                    "severity": severity
                })

        for pattern, label, severity in DANGEROUS_PATTERNS:

            for match in re.finditer(pattern, content):

                line_no = content[: match.start()].count("\n") + 1

                findings.append({
                    "file": rel_path,
                    "line": line_no,
                    "category": "dangerous_pattern",
                    "issue": label,
                    "severity": severity
                })

        return findings

    def analyze(self):

        if self._cache is not None:
            return self._cache

        findings = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]

            for file in files:

                ext = os.path.splitext(file)[1].lower()

                if ext not in SCAN_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.repo_path)

                findings.extend(self._scan_file(full_path, rel_path))

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        backdoors = [f for f in findings if f["category"] == "backdoor"]
        dangerous = [f for f in findings if f["category"] == "dangerous_pattern"]

        return {
            "backdoor_findings": len(backdoors),
            "dangerous_pattern_findings": len(dangerous),
            "high_severity_total": len(
                [f for f in findings if f["severity"] == "HIGH"]
            )
        }

    def top_findings(self, limit=30):

        findings = list(self.analyze())

        severity_rank = {"HIGH": 2, "MEDIUM": 1}

        findings.sort(
            key=lambda x: severity_rank.get(x["severity"], 0),
            reverse=True
        )

        return findings[:limit]