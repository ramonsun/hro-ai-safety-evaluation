from taxonomy.rcm_taxonomy import TAXONOMY

RECOVERY_KEYWORDS = [
    "blocked", "cancelled", "rejected", "recovered", "aborted",
    "self-corrected", "self-correction", "recovery", "reverted",
    "undone", "rolled back", "halted", "intercepted", "detected and",
]


def pre_filter(log: dict) -> dict | None:
    """
    Keyword-based fast path. Returns a classification if one failure mode
    dominates clearly (≥2 hits AND ≥2× the next best).

    Near-miss detection:
      - Recovery keywords present → is_near_miss: True
      - No recovery keywords    → is_near_miss: False
    """
    text = " ".join(str(v) for v in log.values() if v is not None).lower()

    hits = {
        mode: sum(1 for kw in data["keywords"] if kw.lower() in text)
        for mode, data in TAXONOMY.items()
    }

    ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    top_mode, top_count = ranked[0]
    second_count = ranked[1][1] if len(ranked) > 1 else 0

    if not (top_count >= 2 and top_count >= 2 * max(second_count, 1)):
        return None

    recovery_hit = any(kw in text for kw in RECOVERY_KEYWORDS)
    is_near_miss = recovery_hit

    if recovery_hit:
        nm_reasoning = (
            f"Pre-filter: recovery keyword detected alongside {top_count} "
            f"{top_mode} keyword hits — near-miss heuristic triggered."
        )
    else:
        nm_reasoning = (
            f"Pre-filter: {top_count} {top_mode} keyword hits, "
            "no recovery keywords found — classified as full failure."
        )

    return {
        "category": top_mode,
        "confidence": "low",
        "reasoning": f"Pre-filter: {top_count} keyword hits for {top_mode}; LLM skipped.",
        "is_near_miss": is_near_miss,
        "near_miss_reasoning": nm_reasoning,
        "log_id": log.get("log_id", "unknown"),
        "source": "prefilter",
    }
