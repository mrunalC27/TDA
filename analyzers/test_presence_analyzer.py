import os


IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    "vendor",
    "target"
}

SOURCE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".cc",
    ".c", ".cs", ".php", ".rb", ".kt", ".swift"
}

TEST_DIR_MARKERS = {"test", "tests", "__tests__", "spec", "specs"}


def is_test_file(filename):

    name = filename.lower()

    name_no_ext = os.path.splitext(name)[0]

    test_patterns = (
        name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.js")
        or name.endswith(".spec.js")
        or name.endswith(".test.ts")
        or name.endswith(".spec.ts")
        or name.endswith(".test.tsx")
        or name.endswith(".spec.tsx")
        or name.endswith("test.java")
        or name.endswith("tests.cs")
        or name.endswith("_test.go")
        or name.endswith("_spec.rb")
    )

    return test_patterns


def get_test_key(filename):
    """
    Strips test-related prefixes/suffixes to get the base name
    that should match a source file. e.g. 'test_app.py' -> 'app'
    """

    name = filename.lower()
    name_no_ext = os.path.splitext(name)[0]

    for prefix in ("test_",):
        if name_no_ext.startswith(prefix):
            name_no_ext = name_no_ext[len(prefix):]

    for suffix in (
        "_test", ".test", ".spec", "_spec", "test", "tests"
    ):
        if name_no_ext.endswith(suffix):
            name_no_ext = name_no_ext[: -len(suffix)]

    return name_no_ext


class TestPresenceAnalyzer:
    """
    Static proxy for test coverage - does NOT execute any code.
    Detects test files by naming convention and folder structure,
    then reports which source files appear to have no matching test.
    This is an estimate, not a measurement of actual line/branch coverage.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self._cache = None

    def analyze(self):

        if self._cache is not None:
            return self._cache

        source_files = []
        test_files = []

        for root, dirs, files in os.walk(self.repo_path):

            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            path_parts = {p.lower() for p in root.split(os.sep)}
            in_test_dir = bool(path_parts & TEST_DIR_MARKERS)

            for file in files:

                ext = os.path.splitext(file)[1].lower()

                if ext not in SOURCE_EXTENSIONS:
                    continue

                full_path = os.path.join(root, file)

                if in_test_dir or is_test_file(file):
                    test_files.append(full_path)
                else:
                    source_files.append(full_path)

        test_keys = {
            get_test_key(os.path.basename(t)) for t in test_files
        }

        untested = []

        for source_path in source_files:

            base_name = os.path.splitext(
                os.path.basename(source_path)
            )[0].lower()

            if base_name not in test_keys:

                untested.append({
                    "file": os.path.relpath(source_path, self.repo_path)
                })

        result = {
            "source_files": len(source_files),
            "test_files": len(test_files),
            "untested": untested
        }

        self._cache = result
        return self._cache

    def summary(self):

        result = self.analyze()

        source_count = result["source_files"]
        test_count = result["test_files"]
        untested_count = len(result["untested"])

        if source_count == 0:

            return {"status": "No Source Files Found"}

        tested_count = source_count - untested_count

        test_file_ratio = round(
            test_count / source_count, 2
        ) if source_count else 0

        estimated_coverage_pct = round(
            (tested_count / source_count) * 100, 1
        )

        return {
            "source_files": source_count,
            "test_files": test_count,
            "test_to_source_ratio": test_file_ratio,
            "files_with_no_test_found": untested_count,
            "estimated_file_coverage_pct": estimated_coverage_pct,
            "note": "Estimate based on file naming/structure, not actual code execution."
        }

    def untested_files(self, limit=50):

        result = self.analyze()
        return result["untested"][:limit]