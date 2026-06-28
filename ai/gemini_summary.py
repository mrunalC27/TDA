import json
import ollama

OLLAMA_MODEL = "mistral"


class GeminiSummary:

    def __init__(self):
        self.model = OLLAMA_MODEL

    def generate(self, report):

        prompt = f"""
You are a senior software architect.
Analyze the following repository report.
Generate:
1. Executive Summary
2. Strengths
3. Risks
4. Top 3 Recommendations
Important:
- Dead code findings are potential findings and may contain false positives.
- Dependency audit failures do not necessarily indicate vulnerabilities.
- Base conclusions only on the provided metrics.
- Avoid exaggeration.
Keep the response concise.
Report:
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

            return f"AI Summary Unavailable: {str(e)}"