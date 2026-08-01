"""
LLM Provider abstraction.

Why this exists: keeping the LLM call behind a single interface means the
rest of the app never imports Groq directly. Swapping providers (or adding
a local/open-source model later) only requires changing this file.
"""
import json
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SCHEMA_INSTRUCTIONS = """
You are an enterprise process analyst. Given a business process name,
description, and any supporting research evidence, produce a JSON object
with EXACTLY these fields (all strings unless noted):

- business_purpose: why this process exists
- key_activities: what happens in this process (2-4 sentences)
- current_challenges: typical problems with this process today
- ai_opportunity: how AI could change or improve it
- automation_potential: one of "Low", "Medium", "High"
- human_involvement: what humans will still be responsible for in future
- technologies: comma-separated relevant AI capabilities (e.g. "NLP, forecasting, computer vision")
- business_benefit: expected benefit category, e.g. "Cost reduction", "Revenue growth", "Customer experience", "Speed"
- risks: key AI/operational/regulatory risks
- rationale: 1-2 sentences explaining WHY you reached this conclusion, referencing the evidence if provided
- confidence: "grounded" if the evidence supported your answer, "insufficient_evidence" if you had to reason without solid support

Return ONLY valid JSON. No markdown, no preamble, no code fences.
"""


def analyze_process_with_llm(name: str, description: str, category: str, evidence_text: str) -> dict:
    """
    Calls the LLM to generate structured analysis for a single process.
    This is the ONE function every process — seeded or live-added — passes
    through. There is no per-process hard-coding anywhere in this path.
    """
    if _client is None:
        # No API key configured - return a clearly-marked placeholder so the
        # app remains demonstrable without live credentials.
        return _fallback_response(name, "No GROQ_API_KEY configured")

    user_prompt = f"""
Process name: {name}
Category: {category}
Description: {description}

Supporting research evidence:
{evidence_text if evidence_text else "(no external evidence retrieved)"}
"""

    try:
        completion = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SCHEMA_INSTRUCTIONS},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw = completion.choices[0].message.content
        data = json.loads(raw)
        return _validate_schema(data)
    except Exception as e:
        return _fallback_response(name, f"LLM call failed: {e}")


def _validate_schema(data: dict) -> dict:
    required = [
        "business_purpose", "key_activities", "current_challenges",
        "ai_opportunity", "automation_potential", "human_involvement",
        "technologies", "business_benefit", "risks", "rationale", "confidence",
    ]
    for field in required:
        if field not in data or not data[field]:
            data[field] = "insufficient_evidence"
    if data.get("automation_potential") not in ("Low", "Medium", "High"):
        data["automation_potential"] = "Medium"
    return data


def _fallback_response(name: str, reason: str) -> dict:
    return {
        "business_purpose": f"[Pending analysis for '{name}']",
        "key_activities": "insufficient_evidence",
        "current_challenges": "insufficient_evidence",
        "ai_opportunity": "insufficient_evidence",
        "automation_potential": "Medium",
        "human_involvement": "insufficient_evidence",
        "technologies": "insufficient_evidence",
        "business_benefit": "insufficient_evidence",
        "risks": "insufficient_evidence",
        "rationale": reason,
        "confidence": "insufficient_evidence",
    }
