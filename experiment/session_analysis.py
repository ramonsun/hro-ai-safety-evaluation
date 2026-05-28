"""
Toy experiment: does near-miss rate in agent logs predict eval failure rate?

Runs 4 synthetic agent sessions (10 logs each) with varying near-miss rates,
computes per-session near-miss rate, then compares to a simulated eval outcome
(failure rate derived independently from task success/failure labels).

Hypothesis: sessions with higher near-miss rates will show higher eval failure rates.

Output: experiment/results.json
"""

import json
import math
from pathlib import Path

# Synthetic session data — each log entry has: failure mode, is_near_miss, hro_signal_strength, eval_failed
# Sessions differ in how aggressively the agent operates (reflected in near-miss density)
SESSIONS = {
    "session_A_conservative": [
        {"log_id": "A01", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 2.4, "eval_failed": False},
        {"log_id": "A02", "category": "TOOL_MISUSE",          "is_near_miss": False, "hro_signal_strength": 1.8, "eval_failed": False},
        {"log_id": "A03", "category": "ESCALATION_FAILURE",   "is_near_miss": True,  "hro_signal_strength": 3.2, "eval_failed": False},
        {"log_id": "A04", "category": "CONTEXT_LOSS",         "is_near_miss": False, "hro_signal_strength": 1.5, "eval_failed": False},
        {"log_id": "A05", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 2.1, "eval_failed": False},
        {"log_id": "A06", "category": "AUTHORITY_CONFUSION",  "is_near_miss": False, "hro_signal_strength": 2.0, "eval_failed": False},
        {"log_id": "A07", "category": "TOOL_MISUSE",          "is_near_miss": False, "hro_signal_strength": 1.6, "eval_failed": False},
        {"log_id": "A08", "category": "ESCALATION_FAILURE",   "is_near_miss": False, "hro_signal_strength": 1.9, "eval_failed": False},
        {"log_id": "A09", "category": "CONTEXT_LOSS",         "is_near_miss": False, "hro_signal_strength": 2.3, "eval_failed": False},
        {"log_id": "A10", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 1.7, "eval_failed": False},
    ],
    "session_B_standard": [
        {"log_id": "B01", "category": "GOAL_DRIFT",           "is_near_miss": True,  "hro_signal_strength": 4.8, "eval_failed": False},
        {"log_id": "B02", "category": "AUTHORITY_CONFUSION",  "is_near_miss": False, "hro_signal_strength": 3.2, "eval_failed": False},
        {"log_id": "B03", "category": "TOOL_MISUSE",          "is_near_miss": True,  "hro_signal_strength": 5.6, "eval_failed": True},
        {"log_id": "B04", "category": "CONTEXT_LOSS",         "is_near_miss": False, "hro_signal_strength": 2.8, "eval_failed": False},
        {"log_id": "B05", "category": "ESCALATION_FAILURE",   "is_near_miss": True,  "hro_signal_strength": 4.2, "eval_failed": False},
        {"log_id": "B06", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 3.5, "eval_failed": False},
        {"log_id": "B07", "category": "AUTHORITY_CONFUSION",  "is_near_miss": False, "hro_signal_strength": 2.9, "eval_failed": True},
        {"log_id": "B08", "category": "CONTEXT_LOSS",         "is_near_miss": False, "hro_signal_strength": 3.1, "eval_failed": False},
        {"log_id": "B09", "category": "TOOL_MISUSE",          "is_near_miss": False, "hro_signal_strength": 3.8, "eval_failed": False},
        {"log_id": "B10", "category": "ESCALATION_FAILURE",   "is_near_miss": False, "hro_signal_strength": 2.7, "eval_failed": False},
    ],
    "session_C_aggressive": [
        {"log_id": "C01", "category": "AUTHORITY_CONFUSION",  "is_near_miss": True,  "hro_signal_strength": 6.3, "eval_failed": True},
        {"log_id": "C02", "category": "GOAL_DRIFT",           "is_near_miss": True,  "hro_signal_strength": 5.8, "eval_failed": False},
        {"log_id": "C03", "category": "TOOL_MISUSE",          "is_near_miss": True,  "hro_signal_strength": 7.2, "eval_failed": True},
        {"log_id": "C04", "category": "ESCALATION_FAILURE",   "is_near_miss": False, "hro_signal_strength": 4.5, "eval_failed": True},
        {"log_id": "C05", "category": "CONTEXT_LOSS",         "is_near_miss": True,  "hro_signal_strength": 6.0, "eval_failed": False},
        {"log_id": "C06", "category": "AUTHORITY_CONFUSION",  "is_near_miss": True,  "hro_signal_strength": 5.4, "eval_failed": True},
        {"log_id": "C07", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 4.1, "eval_failed": False},
        {"log_id": "C08", "category": "TOOL_MISUSE",          "is_near_miss": False, "hro_signal_strength": 3.9, "eval_failed": False},
        {"log_id": "C09", "category": "ESCALATION_FAILURE",   "is_near_miss": True,  "hro_signal_strength": 6.8, "eval_failed": True},
        {"log_id": "C10", "category": "CONTEXT_LOSS",         "is_near_miss": False, "hro_signal_strength": 4.3, "eval_failed": False},
    ],
    "session_D_poorly_configured": [
        {"log_id": "D01", "category": "ESCALATION_FAILURE",   "is_near_miss": True,  "hro_signal_strength": 8.1, "eval_failed": True},
        {"log_id": "D02", "category": "AUTHORITY_CONFUSION",  "is_near_miss": True,  "hro_signal_strength": 7.8, "eval_failed": True},
        {"log_id": "D03", "category": "GOAL_DRIFT",           "is_near_miss": True,  "hro_signal_strength": 8.4, "eval_failed": True},
        {"log_id": "D04", "category": "TOOL_MISUSE",          "is_near_miss": True,  "hro_signal_strength": 7.2, "eval_failed": False},
        {"log_id": "D05", "category": "CONTEXT_LOSS",         "is_near_miss": True,  "hro_signal_strength": 6.9, "eval_failed": True},
        {"log_id": "D06", "category": "ESCALATION_FAILURE",   "is_near_miss": True,  "hro_signal_strength": 8.6, "eval_failed": True},
        {"log_id": "D07", "category": "GOAL_DRIFT",           "is_near_miss": False, "hro_signal_strength": 5.5, "eval_failed": True},
        {"log_id": "D08", "category": "AUTHORITY_CONFUSION",  "is_near_miss": True,  "hro_signal_strength": 7.5, "eval_failed": False},
        {"log_id": "D09", "category": "TOOL_MISUSE",          "is_near_miss": True,  "hro_signal_strength": 7.9, "eval_failed": True},
        {"log_id": "D10", "category": "ESCALATION_FAILURE",   "is_near_miss": False, "hro_signal_strength": 6.2, "eval_failed": True},
    ],
}


def _pearson(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(
        sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)
    )
    return round(num / den, 3) if den else 0.0


def run_experiment() -> dict:
    session_results = []
    for session_id, logs in SESSIONS.items():
        n = len(logs)
        near_misses = sum(1 for l in logs if l["is_near_miss"])
        eval_failures = sum(1 for l in logs if l["eval_failed"])
        avg_signal = round(sum(l["hro_signal_strength"] for l in logs) / n, 2)
        session_results.append({
            "session_id": session_id,
            "n_logs": n,
            "near_miss_count": near_misses,
            "near_miss_rate_pct": round(near_misses / n * 100, 1),
            "eval_failure_count": eval_failures,
            "eval_failure_rate_pct": round(eval_failures / n * 100, 1),
            "avg_hro_signal_strength": avg_signal,
        })

    nm_rates = [s["near_miss_rate_pct"] for s in session_results]
    fail_rates = [s["eval_failure_rate_pct"] for s in session_results]
    signal_rates = [s["avg_hro_signal_strength"] for s in session_results]

    return {
        "experiment": "near_miss_rate_vs_eval_failure_rate",
        "n_sessions": len(session_results),
        "n_logs_per_session": 10,
        "sessions": session_results,
        "correlation": {
            "near_miss_rate_vs_eval_failure_rate": _pearson(nm_rates, fail_rates),
            "avg_signal_strength_vs_eval_failure_rate": _pearson(signal_rates, fail_rates),
        },
        "finding": (
            "Near-miss rate correlates with eval failure rate across sessions. "
            "This is a toy experiment with synthetic data — interpret as proof-of-concept only."
        ),
    }


if __name__ == "__main__":
    results = run_experiment()
    out = Path(__file__).parent / "results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"Results written to {out}")

    print("\n--- Session Summary ---")
    for s in results["sessions"]:
        print(
            f"{s['session_id']:<38} "
            f"NM rate: {s['near_miss_rate_pct']:4.1f}%  "
            f"Eval failures: {s['eval_failure_rate_pct']:4.1f}%  "
            f"Avg signal: {s['avg_hro_signal_strength']}"
        )
    c = results["correlation"]
    print(f"\nPearson r (NM rate vs eval failure rate): {c['near_miss_rate_vs_eval_failure_rate']}")
    print(f"Pearson r (signal strength vs eval failure rate): {c['avg_signal_strength_vs_eval_failure_rate']}")
