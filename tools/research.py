# blog_writer/tools/research.py
from typing import Dict, Any
from google.genai import Client

client = Client()

def research_topic(topic: str) -> Dict[str, Any]:
    """
    Uses the LLM to propose an outline and key points for the given topic.
    Returns a dict with: query, outline (list of H2 strings), facts (list of dicts).
    """
    topic = (topic or "").strip() or "General topic"
    prompt = f"""
You are helping plan a clear, structured blog post.

Topic: {topic}

1. Propose a refined one-line blog focus (query).
2. Propose 4–6 H2 section headings for a blog on this topic.
3. List 5–8 concise bullet points with key facts, tips, or arguments
   that the blog should cover.

Return STRICT JSON with keys:
- query: string
- outline: list of strings (H2 section titles)
- facts: list of objects with key 'fact' (string).
"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = getattr(resp, "text", "") or str(resp)

    # Best-effort JSON extraction
    import json
    try:
        s = raw.index("{")
        e = raw.rindex("}") + 1
        raw_json = raw[s:e]
    except Exception:
        raw_json = raw

    try:
        data = json.loads(raw_json)
    except Exception:
        # Fallback: minimal structure
        data = {
            "query": topic,
            "outline": [f"Introduction to {topic}", f"Key ideas about {topic}", f"How to apply {topic}", "Common mistakes", "Conclusion"],
            "facts": [{"fact": f"Overview of {topic}."}]
        }

    # Normalize shapes
    query = data.get("query", topic)
    outline = data.get("outline") or []
    facts = data.get("facts") or []

    # Ensure list-of-dicts for facts
    norm_facts = []
    for f in facts:
        if isinstance(f, dict) and "fact" in f:
            norm_facts.append({"fact": str(f["fact"])})
        else:
            norm_facts.append({"fact": str(f)})

    return {
        "query": str(query),
        "outline": [str(h) for h in outline],
        "facts": norm_facts,
    }
