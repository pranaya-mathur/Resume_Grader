import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")


def analyze_resume_with_llm(resume_text):

    # 🔒 Limit resume size (avoid token overflow)
    resume_text = resume_text[:8000]

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
Extract structured hiring intelligence from this resume.

Return STRICT JSON only with this structure:

{{
  "years_experience": number,
  "infra_stack": list,
  "ml_stack": list,
  "has_production_deployment": boolean,
  "ci_cd_used": boolean,
  "github_present": boolean,
  "project_depth_score": number,
  "exaggeration_score": number
}}

Resume:
{resume_text}
"""

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Always return valid JSON only. No explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.json()