# blog_writer/tools/seo_checker.py
def keyword_density(text: str, keyword: str):
    words = text.split()
    total = max(1, len(words))
    count = sum(1 for w in words if w.lower().strip(".,!?()[]\"'") == keyword.lower())
    density = count / total
    return {"keyword": keyword, "count": count, "total_words": total, "density": density}

def simple_seo_check(draft: dict, keywords: list):
    results = []
    text_blocks = [draft.get("intro","")] + list(draft.get("sections",{}).values())
    full_text = " ".join(text_blocks)
    for k in keywords:
        results.append(keyword_density(full_text, k))
    return results

def edit_post(draft: dict, keywords: list) -> dict:
    """
    Lightly annotates the draft with SEO hints; does NOT call the LLM.
    Adds an 'seo_notes' field with suggestions based on keyword density.
    """
    seo_results = simple_seo_check(draft, keywords or [])
    notes = []
    for r in seo_results:
        k = r["keyword"]
        density = r["density"]
        if density == 0:
            notes.append(f"Consider mentioning '{k}' at least once in the post.")
        elif density < 0.01:
            notes.append(f"Consider using '{k}' a bit more often for SEO (current density ~{density:.2%}).")
    edited = dict(draft)
    if notes:
        edited["seo_notes"] = notes
    return edited
