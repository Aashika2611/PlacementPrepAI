"""
Thin wrapper around the Anthropic Messages API.

Every function here returns `None` (instead of raising) when the API key is
missing or the request fails for any reason, so callers can fall back to the
local, non-AI logic instead of breaking the feature.
"""
import json
import re
import requests
from flask import current_app

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _call_claude(system_prompt, user_prompt, max_tokens=1024):
    api_key = current_app.config.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    model = current_app.config.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    try:
        response = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        blocks = data.get("content", [])
        text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
        return text.strip() or None
    except Exception as exc:
        current_app.logger.warning(f"Anthropic API call failed: {exc}")
        return None


def _extract_json(text):
    """Pull the first JSON object out of a model response, tolerating stray text."""
    if not text:
        return None
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def analyze_resume_with_ai(resume_text):
    """Return a dict with score/skills/strengths/weaknesses/suggestions, or None on failure."""
    system_prompt = (
        "You are a career coach helping students improve their resumes. "
        "Respond ONLY with a single JSON object, no markdown, no commentary."
    )
    user_prompt = (
        "Analyze the following resume text. Respond with a JSON object with these exact keys:\n"
        '- "score": integer 0-100 (an app-generated quality score, not an official ATS score)\n'
        '- "skills_detected": array of strings\n'
        '- "strengths": array of short strings\n'
        '- "weaknesses": array of short strings\n'
        '- "suggestions": array of short, actionable strings\n'
        '- "sections_detected": array of section names found (e.g. "Education", "Experience")\n\n'
        f"Resume text:\n{resume_text[:8000]}"
    )
    raw = _call_claude(system_prompt, user_prompt, max_tokens=1200)
    parsed = _extract_json(raw)
    if not parsed or "score" not in parsed:
        return None
    return parsed


def generate_interview_question_with_ai(role, topic, difficulty):
    system_prompt = (
        "You are an interview question generator for a student career-prep app. "
        "Respond ONLY with a single JSON object, no markdown, no commentary."
    )
    user_prompt = (
        f"Generate one {difficulty.lower()} difficulty interview question for a "
        f"'{role}' candidate on the topic '{topic}'. "
        'Respond with JSON: {"question": "..."}'
    )
    raw = _call_claude(system_prompt, user_prompt, max_tokens=300)
    parsed = _extract_json(raw)
    if not parsed or "question" not in parsed:
        return None
    return parsed["question"]


def evaluate_answer_with_ai(role, topic, question, answer):
    system_prompt = (
        "You are an interview coach giving constructive feedback to a student. "
        "Respond ONLY with a single JSON object, no markdown, no commentary."
    )
    user_prompt = (
        f"Role: {role}\nTopic: {topic}\nQuestion: {question}\nCandidate's answer: {answer}\n\n"
        "Evaluate the answer. Respond with a JSON object with these exact keys:\n"
        '- "score": integer 0-100\n'
        '- "strengths": array of short strings\n'
        '- "improvements": array of short, actionable strings'
    )
    raw = _call_claude(system_prompt, user_prompt, max_tokens=600)
    parsed = _extract_json(raw)
    if not parsed or "score" not in parsed:
        return None
    return parsed
