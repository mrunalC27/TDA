import os
import re
import ast


IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target"
}

MAX_FILE_SIZE = 2_000_000

UNBOUNDED_QUERY_PATTERNS = [
    (r"\.objects\.all\(\)(?!.*\.limit)", "Django .objects.all() with no limit"),
    (r"\.query\.all\(\)(?!.*\.limit)", "SQLAlchemy .query.all() with no limit"),
    (r"\.find\(\s*\{?\s*\}?\s*\)(?!.*\.limit)", "Mongoose/MongoDB .find() with no limit"),
    (r"SELECT\s+\*\s+FROM\s+\w+(?!.*LIMIT)", "Raw SQL SELECT * with no LIMIT"),
]


class PythonLoopAnalyzer(ast.NodeVisitor):

    def __init__(self, filename):

        self.filename = filename
        self.findings = []

    def _loop_has_break(self, node):

        for child in ast.walk(node):

            if isinstance(child, ast.Break):
                return True

        return False

    def _get_loop_vars_modified(self, node, var_names):

        modified = set()

        for child in ast.walk(node):

            if isinstance(child, ast.Assign):

                for target in child.targets:

                    if isinstance(target, ast.Name) and target.id in var_names:
                        modified.add(target.id)

            if isinstance(child, ast.AugAssign):

                if isinstance(child.target, ast.Name) and child.target.id in var_names:
                    modified.add(child.target.id)

        return modified

    def visit_While(self, node):

        is_infinite_literal = (
            isinstance(node.test, ast.Constant) and node.test.value is True
        ) or (
            isinstance(node.test, ast.Num) and getattr(node.test, "n", None) == 1
        )

        if is_infinite_literal and not self._loop_has_break(node):

            self.findings.append({
                "file": os.path.basename(self.filename),
                "line": node.lineno,
                "issue": "while True/while(1) loop with no break - risk of infinite loop"
            })

        else:

            var_names = {
                n.id for n in ast.walk(node.test)
                if isinstance(n, ast.Name)
            }

            if var_names:

                modified = self._get_loop_vars_modified(node, var_names)

                if not modified and not self._loop_has_break(node):

                    self.findings.append({
                        "file": os.path.basename(self.filename),
                        "line": node.lineno,
                        "issue": "Loop condition variable never modified inside loop and no break - risk of infinite loop"
                    })

        self.generic_visit(node)


def analyze_python_file(file_path):

    try:

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return []

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        tree = ast.parse(source)

        analyzer = PythonLoopAnalyzer(file_path)
        analyzer.visit(tree)

        return analyzer.findings

    except SyntaxError:

        return []

    except Exception:

        return []


def analyze_generic_loops_regex(file_path):
    """
    Fallback for non-Python languages - simple regex for the most
    common infinite-loop pattern: while(true)/for(;;) with no break
    in a small surrounding window. Less precise than the AST version.
    """

    findings = []

    try:

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return findings

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    except Exception:

        return findings

    infinite_patterns = [
        r"while\s*\(\s*true\s*\)",
        r"while\s*\(\s*1\s*\)",
        r"for\s*\(\s*;\s*;\s*\)"
    ]

    for pattern in infinite_patterns:

        for match in re.finditer(pattern, content, re.IGNORECASE):

            start = match.start()
            end = min(start + 500, len(content))
            window = content[start:end]

            if "break" not in window:

                line_no = content[:start].count("\n") + 1

                findings.append({
                    "file": os.path.basename(file_path),
                    "line": line_no,
                    "issue": "Infinite loop pattern with no nearby break - risk of infinite loop"
                })

    return findings


def analyze_unbounded_queries(file_path):

    findings = []

    try:

        if os.path.getsize(file_path) > MAX_FILE_SIZE:
            return findings

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    except Exception:

        return findings

    for pattern, description in UNBOUNDED_QUERY_PATTERNS:

        for match in re.finditer(pattern, content, re.IGNORECASE):

            line_no = content[: match.start()].count("\n") + 1

            findings.append({
                "file": os.path.basename(file_path),
                "line": line_no,
                "issue": description
            })

    return findings


class LoopAndQueryAnalyzer:
    """
    Detects two distinct issues:
    1. Broken/risky loops - infinite loop risk via missing break or
       unmodified loop condition variables (AST-based for Python,
       regex-based for other languages).
    2. Unbounded queries - ORM/SQL patterns that fetch data with no
       row limit, a common source of performance/scaling issues.
    Pattern-based - findings are candidates for review, not
    definitive bugs.
    """

    SCAN_EXTENSIONS = {
        ".py", ".js", ".jsx", ".ts", ".tsx",
        ".java", ".go", ".rb", ".php", ".cs"
    }

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        loop_findings = []
        query_findings = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:

                ext = os.path.splitext(file)[1].lower()

                if ext not in self.SCAN_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)

                if ext == ".py":
                    loop_findings.extend(analyze_python_file(full_path))
                else:
                    loop_findings.extend(analyze_generic_loops_regex(full_path))

                query_findings.extend(analyze_unbounded_queries(full_path))

        self._cache = {
            "loops": loop_findings,
            "queries": query_findings
        }

        return self._cache

    def summary(self):

        result = self.analyze()

        return {
            "risky_loops_found": len(result["loops"]),
            "unbounded_queries_found": len(result["queries"]),
            "note": "Pattern-based detection - findings are candidates for manual review."
        }

    def loop_findings(self, limit=30):

        return self.analyze()["loops"][:limit]

    def query_findings(self, limit=30):

        return self.analyze()["queries"][:limit]