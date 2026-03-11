import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Multi-key pool: reads GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3 ... 
# Falls back to the legacy GROQ_API_KEY if no numbered keys are found.
# ─────────────────────────────────────────────────────────────────────────────
def _load_api_keys() -> list[str]:
    """
    Collect all configured Groq API keys from environment variables.
    Priority: GROQ_API_KEY_1, GROQ_API_KEY_2, GROQ_API_KEY_3 (numbered pool)
    Fallback:  GROQ_API_KEY (single legacy key)
    """
    keys = []
    for i in range(1, 11):                         # support up to 10 keys
        key = os.getenv(f"GROQ_API_KEY_{i}", "").strip()
        if key:
            keys.append(key)

    if not keys:                                    # legacy fallback
        legacy = os.getenv("GROQ_API_KEY", "").strip()
        if legacy:
            keys.append(legacy)

    return keys


GROQ_API_KEYS: list[str] = _load_api_keys()
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# Track which key index failed so we can rotate smartly across calls
_current_key_index: int = 0


def _next_key_index(current: int) -> int:
    """Rotate to the next key index, wrapping around."""
    return (current + 1) % len(GROQ_API_KEYS)


# ─────────────────────────────────────────────────────────────────────────────
# Core LLM call with multi-key fallover
# ─────────────────────────────────────────────────────────────────────────────
def analyze_resume_with_llm(resume_text: str) -> dict:
    """
    Call Groq API to extract structured hiring intelligence from a resume.

    Rotation strategy:
      - Tries every available API key in sequence.
      - On 429 (rate-limit) with a single key: sleeps briefly, then rotates.
      - On hard errors (500, timeout, etc.): rotates immediately.
      - Returns an error dict only if ALL keys are exhausted.
    """
    global _current_key_index

    if not GROQ_API_KEYS:
        return {"error": {"message": "No Groq API keys configured. Set GROQ_API_KEY_1 (or GROQ_API_KEY) in .env"}}

    # 🔒 Limit resume size to avoid token overflow
    resume_text = resume_text[:8000]

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

    num_keys = len(GROQ_API_KEYS)
    start_index = _current_key_index     # remember where we started

    for attempt in range(num_keys):
        key_index = (start_index + attempt) % num_keys
        api_key = GROQ_API_KEYS[key_index]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        key_label = f"Key #{key_index + 1}/{num_keys}"

        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)

            # ── Rate limited → wait a beat then try next key ──────────────
            if response.status_code == 429:
                print(f"⚠️  {key_label} rate-limited (429). Rotating to next key...")
                time.sleep(1)          # small courtesy sleep before rotating
                continue

            # ── Server errors → rotate immediately ────────────────────────
            if response.status_code >= 500:
                print(f"⚠️  {key_label} server error ({response.status_code}). Rotating...")
                continue

            # ── Auth / bad request errors → skip permanently ───────────────
            if response.status_code in (401, 403):
                print(f"❌  {key_label} auth error ({response.status_code}). Skipping this key.")
                continue

            response.raise_for_status()

            # ✅ Success — persist the winning key index for future calls
            _current_key_index = key_index
            print(f"✅  {key_label} succeeded.")
            return response.json()

        except requests.exceptions.Timeout:
            print(f"⏱️  {key_label} timed out. Rotating...")
            continue

        except requests.exceptions.RequestException as e:
            print(f"⚠️  {key_label} request error: {e}. Rotating...")
            continue

    # All keys exhausted
    return {
        "error": {
            "message": (
                f"All {num_keys} Groq API key(s) failed or are rate-limited. "
                "Add more keys (GROQ_API_KEY_2, GROQ_API_KEY_3 ...) or wait a moment."
            )
        }
    }