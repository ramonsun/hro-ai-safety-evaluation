from taxonomy.rcm_taxonomy import TAXONOMY


def pre_filter(log: dict) -> dict | None:
    """
    Keyword-based fast path. Returns a low-confidence classification if one
    failure mode dominates clearly (≥2 hits AND ≥2× the next best), skipping
    the LLM call. Returns None to fall through to LLM otherwise.

    Near-miss detection is always False on this path — that requires LLM analysis.
    """
    text = " ".join(str(v) for v in log.values() if v is not None).lower()

    hits = {
        mode: sum(1 for kw in data["keywords"] if kw.lower() in text)
        for mode, data in TAXONOMY.items()
    }

    ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    top_mode, top_count = ranked[0]
    second_count = ranked[1][1] if len(ranked) > 1 else 0

    if top_count >= 2 and top_count >= 2 * max(second_count, 1):
        return {
            "category": top_mode,
            "confidence": "low",
            "reasoning": f"Pre-filter: {top_count} keyword hits for {top_mode}; LLM skipped.",
            "is_near_miss": False,
            "near_miss_reasoning": "Pre-filter path; near-miss detection requires LLM analysis.",
            "log_id": log.get("log_id", "unknown"),
        }

    return None
