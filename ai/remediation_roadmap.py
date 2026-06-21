import os
import json
# from urllib import response

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)

class RemediationRoadmap:

    def __init__(self):

        self.model = genai.GenerativeModel(
            "gemini-2.5-pro"
        )


    def generate(
        self,
        report
    ):
        
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

            response = self.model.generate_content(
                prompt
            )

            return response.text

        except Exception as e:

            return f"Roadmap unavailable: {str(e)}"