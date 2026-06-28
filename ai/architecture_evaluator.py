import os
import ollama

OLLAMA_MODEL = "mistral"

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv",
    "__pycache__", "dist", "build", "vendor", "target"
}

MAX_DEPTH = 4
MAX_ENTRIES_PER_DIR = 25


class ArchitectureEvaluator:
    """
    Uses a local Ollama model to evaluate the repository's
    architecture pattern based on its folder/file structure and
    detected framework. Does not read file contents - structure
    only, to keep the prompt small and avoid sending large amounts
    of source code.
    """

    def __init__(self, repo_path):

        self.repo_path = repo_path
        self.model = OLLAMA_MODEL

    def _build_tree(self, path, depth=0, prefix=""):

        if depth > MAX_DEPTH:
            return ""

        try:
            entries = sorted(os.listdir(path))
        except Exception:
            return ""

        entries = [e for e in entries if e not in IGNORE_DIRS]
        entries = entries[:MAX_ENTRIES_PER_DIR]

        lines = []

        for entry in entries:

            full_path = os.path.join(path, entry)

            lines.append(f"{prefix}{entry}")

            if os.path.isdir(full_path):

                lines.append(
                    self._build_tree(full_path, depth + 1, prefix + "  ")
                )

        return "\n".join(filter(None, lines))

    def evaluate(self, profile):

        tree = self._build_tree(self.repo_path)

        if not tree.strip():
            return "Could not generate folder structure for evaluation."

        prompt = f"""You are a senior software architect reviewing a codebase's folder structure.

Primary language: {profile.get('primary_language', 'Unknown')}
Framework detected: {profile.get('framework', 'Unknown')}

Folder/file structure (depth-limited, contents not included):
{tree}

Based on this structure alone, answer concisely:
1. What architecture pattern does this most resemble (MVC, layered, flat/no structure, feature-based, microservices-in-monorepo, etc.)?
2. Is there clear separation of concerns (routes/controllers, business logic, data access)?
3. Name up to 3 structural smells visible from the folder layout alone (e.g. no separation between routes and logic, no tests directory, configuration mixed with source).

Keep the response under 200 words, no preamble."""

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response["message"]["content"]

        except Exception as e:

            if "Failed to connect" in str(e) or "Connection refused" in str(e):

                return (
                    "AI insights run on a local model and are only available when running "
                    "Refactr on your own machine. The rest of this analysis is unaffected."
                )

            return f"Architecture evaluation unavailable: {str(e)}"