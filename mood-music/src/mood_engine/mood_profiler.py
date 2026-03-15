import os
import json
import anthropic

# Manually load .env from project root
_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(_env_path):
    with open(_env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()  # always set, don't use setdefault

def _get_client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env")
    return anthropic.Anthropic(api_key=key)


SYSTEM_PROMPT = """You are a compassionate mood analyst for a music therapy platform.
Your job is to read what a user said and extract their emotional state.

Always respond with valid JSON only. No explanation, no markdown, just JSON.
"""

USER_PROMPT_TEMPLATE = """A user spoke the following (transcribed from voice):

\"{transcript}\"

Analyze their emotional state and return a JSON object with exactly these fields:

{{
  "primary_emotion": "one word (e.g. exhausted, anxious, sad, grief, angry, overwhelmed, hopeful)",
  "themes": ["list", "of", "themes", "mentioned"],
  "valence": <float 0.0 to 1.0, where 0=very sad, 1=very happy>,
  "arousal": <float 0.0 to 1.0, where 0=very calm/slow, 1=very energetic/tense>,
  "intensity": <float 0.0 to 1.0, how strongly they feel this>,
  "summary": "one sentence describing their state empathetically"
}}

Rules:
- valence and arousal must be numbers between 0.0 and 1.0
- primary_emotion must be a single lowercase word
- themes should reflect what they actually talked about
- Be generous in interpretation — assume the user is being honest
"""


def profile_mood(transcript: str) -> dict:
    """
    Takes a voice transcript and returns a mood profile dict.
    """
    client = _get_client()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(transcript=transcript)
            }
        ]
    )

    raw = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ─────────────────────────────────────────
# Quick test
# ─────────────────────────────────────────
if __name__ == "__main__":
    test_transcript = (
        "I've just had such a long day. Work was really stressful, "
        "I couldn't focus on anything and my mind keeps racing. "
        "I feel tense and I just can't seem to switch off."
    )

    print("Transcript:", test_transcript)
    print("\nAnalyzing mood...")

    profile = profile_mood(test_transcript)

    print("\nMood Profile:")
    print(json.dumps(profile, indent=2))
