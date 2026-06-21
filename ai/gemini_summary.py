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

class GeminiSummary:

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
            response = self.model.generate_content(
            prompt
            )
            return response.text
        except Exception as e:
            return(
                f"AI Summary Unavailable: {str(e)}"
            )
    
    
