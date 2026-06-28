import json
import ollama

OLLAMA_MODEL = "mistral"


class RemediationRoadmap:

    def __init__(self):
        self.model = OLLAMA_MODEL

    def generate(self, report):

        prompt = f"""
You are a senior software architect.
Using the repository report below,
generate a remediation roadmap.
Rules:
- Prioritize by impact.
- Use Priority 1, Priority 2, Priority 3.
- Explain why each action matters.
- Keep the roadmap concise.
- Do not exaggerate risks.
Repository Report:
{json.dumps(report, indent=2)}
"""

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

            return f"Roadmap unavailable: {str(e)}"