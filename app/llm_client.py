"""
LLM stub for the LLM-FREE option.
If in future you want to enable an LLM, replace/extend this module.
"""

def chat_completion(system: str, user: str, model: str = "none") -> str:
    """
    Return a stable JSON-like notice so callers expecting JSON can handle it.
    """
    # Keep this as a JSON string to match older callers that json.loads() it.
    return '{"note": "LLM not configured; using heuristic parsing."}'
