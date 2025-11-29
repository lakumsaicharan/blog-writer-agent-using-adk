# blog_writer/tools/writer.py
from pathlib import Path
from typing import Dict, Any, List
from google.genai import Client

TEMPLATE_PATH = Path("prompts/writer_template.md")
template_text = TEMPLATE_PATH.read_text() if TEMPLATE_PATH.exists() else ""

client = Client()

def write_draft(
    topic: str,
    tone: str,
    audience: str,
    outline: List[str],
    facts: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Uses the LLM to create a JSON blog draft:
      { title, outline, intro, sections }
    sections is a dict mapping H2 -> text.
    """
    topic = (topic or "").strip() or "General topic"
    tone = tone or "conversational"
    audience = audience or "general readers"

    fact_lines = "\n".join(f"- {f.get('fact')}" for f in facts if isinstance(f, dict))
    outline_lines = "\n".join(f"- {h}" for h in outline)

    prompt = f"""
You are an expert blog writer.

Write a well-structured blog post based on:
Topic: {topic}
Audience: {audience}
Tone: {tone}

Planned outline (H2 headings):
{outline_lines}

Key points and facts to cover:
{fact_lines}

Template (use this for structure and style, but adapt to the topic):
{template_text}

Return STRICT JSON with keys:
- title: string
- outline: list of strings (H2 headings to use)
- intro: string
- sections: object mapping each H2 heading to a section body string.
"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = getattr(resp, "text", "") or str(resp)

    import json
    try:
        s = raw.index("{")
        e = raw.rindex("}") + 1
        raw_json = raw[s:e]
    except Exception:
        raw_json = raw

    try:
        draft = json.loads(raw_json)
    except Exception:
        # Very minimal fallback
        draft = {
            "title": f"{topic} – A Practical Guide",
            "outline": outline or [f"Introduction to {topic}", "Key ideas", "Conclusion"],
            "intro": f"This blog post introduces {topic} for {audience}.",
            "sections": {},
        }

    # Normalization
    title = draft.get("title") or f"{topic} – A Practical Guide"
    out = draft.get("outline") or outline or []
    intro = draft.get("intro") or ""
    sections = draft.get("sections") or {}

    # Ensure string keys and values
    norm_sections = {}
    for h in out:
        h_str = str(h)
        norm_sections[h_str] = str(sections.get(h_str, ""))

    return {
        "title": str(title),
        "outline": [str(h) for h in out],
        "intro": str(intro),
        "sections": norm_sections,
    }
