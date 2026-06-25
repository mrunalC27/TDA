import os
import re


IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target",
    "test", "tests", "__tests__"
}

SCAN_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx"}

MAX_FILE_SIZE = 2_000_000

ROUTE_PATTERNS = [
    r"(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
    r"@app\.route\s*\(\s*['\"]([^'\"]+)['\"]",
    r"@(?:app)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
]

AUTH_INDICATORS = [
    r"login_required",
    r"jwt_required",
    r"requireAuth",
    r"isAuthenticated",
    r"authenticate",
    r"permission_classes",
    r"IsAuthenticated",
    r"Depends\s*\(\s*get_current_user",
    r"Depends\s*\(\s*require_",
    r"@auth",
    r"verifyToken",
    r"checkAuth",
    r"ensureLoggedIn",
]

SENSITIVE_PATH_KEYWORDS = [
    "admin", "delete", "remove", "user", "payment", "billing",
    "checkout", "settings", "config", "secret", "key", "token",
    "password", "credential", "internal", "debug"
]

AUTH_INDICATOR_REGEX = re.compile(
    "(" + "|".join(AUTH_INDICATORS) + ")", re.IGNORECASE
)

CONTEXT_WINDOW = 300


class EndpointSecurityAnalyzer:
    """
    Detects API route definitions and checks for nearby
    authentication/authorization indicators. Flags:
    1. Open endpoints - any route with no auth indicator nearby.
    2. RBAC risks - routes whose path suggests sensitive
       functionality (admin, delete, payment, etc.) but with no
       detected permission check.
    Pattern-based, line-proximity heuristic - not a guarantee of
    actual security status. Findings are candidates for review.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def _is_sensitive_path(self, path):

        path_lower = path.lower()

        return any(keyword in path_lower for keyword in SENSITIVE_PATH_KEYWORDS)

    def _has_nearby_auth(self, content, match_start, match_end):

        window_start = max(0, match_start - CONTEXT_WINDOW)
        window_end = min(len(content), match_end + CONTEXT_WINDOW)

        window = content[window_start:window_end]

        return bool(AUTH_INDICATOR_REGEX.search(window))

    def _scan_file(self, file_path, rel_path):

        findings = []

        try:

            if os.path.getsize(file_path) > MAX_FILE_SIZE:
                return findings

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        except Exception:

            return findings

        for pattern in ROUTE_PATTERNS:

            for match in re.finditer(pattern, content):

                groups = match.groups()

                path = groups[-1] if groups else "/"
                method = groups[0].upper() if len(groups) > 1 else "UNKNOWN"

                line_no = content[: match.start()].count("\n") + 1

                has_auth = self._has_nearby_auth(
                    content, match.start(), match.end()
                )

                is_sensitive = self._is_sensitive_path(path)

                if not has_auth:

                    findings.append({
                        "file": rel_path,
                        "line": line_no,
                        "method": method,
                        "path": path,
                        "auth_detected": False,
                        "sensitive_path": is_sensitive,
                        "risk": "HIGH" if is_sensitive else "MEDIUM"
                    })

        return findings

    def analyze(self):

        if self._cache is not None:
            return self._cache

        findings = []
        seen = set()

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d.lower() not in IGNORE_DIRS]

            for file in files:

                ext = os.path.splitext(file)[1].lower()

                if ext not in SCAN_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.repo_path)

                for finding in self._scan_file(full_path, rel_path):

                    key = (finding["file"], finding["line"], finding["path"])

                    if key not in seen:
                        seen.add(key)
                        findings.append(finding)

        self._cache = findings
        return self._cache

    def summary(self):

        findings = self.analyze()

        sensitive_unprotected = len(
            [f for f in findings if f["sensitive_path"]]
        )

        return {
            "open_endpoints_found": len(findings),
            "sensitive_endpoints_without_auth": sensitive_unprotected,
            "note": "Proximity-based heuristic - verify findings manually, framework-level auth (e.g. global middleware) may not be detected."
        }

    def top_findings(self, limit=30):

        findings = list(self.analyze())

        findings.sort(
            key=lambda x: x["sensitive_path"],
            reverse=True
        )

        return findings[:limit]