from collections import Counter


def analyze_session(results: list[dict]) -> dict:
    if not results:
        return {}

    n = len(results)
    near_misses = [r for r in results if r.get("is_near_miss")]
    rpns = [r["rpn"] for r in results if "rpn" in r]
    categories = [r.get("category", "unknown") for r in results]

    # Risk trajectory: RPN per log in order, smoothed as cumulative average
    trajectory = []
    for i, r in enumerate(results):
        window = rpns[: i + 1]
        trajectory.append({
            "log_id": r.get("log_id", f"log_{i}"),
            "rpn": r.get("rpn", 0),
            "cumulative_avg_rpn": round(sum(window) / len(window), 1),
        })

    return {
        "total_logs": n,
        "near_miss_count": len(near_misses),
        "near_miss_rate_per_100": round(len(near_misses) / n * 100, 1),
        "mode_distribution": dict(Counter(categories)),
        "top_failure_mode": Counter(categories).most_common(1)[0][0] if categories else None,
        "avg_rpn": round(sum(rpns) / len(rpns), 1) if rpns else 0,
        "max_rpn": max(rpns) if rpns else 0,
        "risk_trajectory": trajectory,
    }
