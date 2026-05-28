from collections import Counter


def analyze_session(results: list[dict]) -> dict:
    if not results:
        return {}

    n = len(results)
    near_misses = [r for r in results if r.get("is_near_miss")]
    scores = [r["deception_risk_score"] for r in results if "deception_risk_score" in r]
    categories = [r.get("category", "unknown") for r in results]

    # Risk trajectory: deception risk score per log in order, smoothed as cumulative average
    trajectory = []
    for i, r in enumerate(results):
        window = scores[: i + 1]
        trajectory.append({
            "log_id": r.get("log_id", f"log_{i}"),
            "deception_risk_score": r.get("deception_risk_score", 0),
            "cumulative_avg": round(sum(window) / len(window), 1),
        })

    return {
        "total_logs": n,
        "near_miss_count": len(near_misses),
        "near_miss_rate_per_100": round(len(near_misses) / n * 100, 1),
        "mode_distribution": dict(Counter(categories)),
        "top_failure_mode": Counter(categories).most_common(1)[0][0] if categories else None,
        "avg_rpn": round(sum(scores) / len(scores), 1) if scores else 0,
        "max_rpn": max(scores) if scores else 0,
        "risk_trajectory": trajectory,
    }
