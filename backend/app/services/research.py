"""
Research grounding module.

Retrieves lightweight external context for a process before analysis, so
outputs are traceable to evidence rather than pure LLM opinion. Kept behind
its own function so a different search provider can be swapped in without
touching the analysis pipeline.
"""
import requests
import time
from app.config import SEARCH_API_KEY


def gather_evidence(process_name: str, category: str) -> list[dict]:
    """
    Returns a list of {title, url, snippet} dicts.
    Falls back to an empty list (not an error) if no search provider is
    configured - the LLM layer marks confidence as 'insufficient_evidence'
    in that case, which is surfaced honestly to the user rather than hidden.
    """
    if not SEARCH_API_KEY:
        return []

    try:
        time.sleep(3)  # avoid hitting free-tier rate limits
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": SEARCH_API_KEY,
                "query": f"{process_name} {category} best practices AI automation",
                "max_results": 3,
            },
            timeout=10,
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:500],
            }
            for r in results
        ]
    except Exception:
        return []


def evidence_to_text(evidence: list[dict]) -> str:
    if not evidence:
        return ""
    parts = []
    for e in evidence:
        parts.append(f"- {e['title']}: {e['snippet']}")
    return "\n".join(parts)
