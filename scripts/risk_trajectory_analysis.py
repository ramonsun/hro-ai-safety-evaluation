"""
Risk trajectory pattern analysis for SafetyDrift traces.
Pure Python + statistics module only.
"""
import json
import os
import statistics
from pathlib import Path

TRACES_DIR = Path("data/safetydrift/traces")
HRO_REPORT = Path("reports/safetydrift_hro_full.json")
OUTPUT = Path("reports/risk_trajectory_analysis.json")


def load_hro_index():
    with open(HRO_REPORT) as f:
        records = json.load(f)
    return {r["log_id"]: r for r in records}


def load_traces():
    traces = []
    for cat_dir in sorted(TRACES_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        category = cat_dir.name
        for fp in sorted(cat_dir.glob("*.json")):
            with open(fp) as f:
                data = json.load(f)
            data["_category"] = category
            data["_filename"] = fp.name
            traces.append(data)
    return traces


def risk_levels(trace):
    """Extract ordered risk_level from safety_state_before for each step."""
    return [s["safety_state_before"]["risk_level"] for s in trace["steps"]]


def linear_regression_slope(ys):
    """Slope of OLS line through (0,y0),(1,y1),..."""
    n = len(ys)
    if n < 2:
        return 0.0
    xs = list(range(n))
    xbar = (n - 1) / 2
    ybar = statistics.mean(ys)
    num = sum((xs[i] - xbar) * (ys[i] - ybar) for i in range(n))
    den = sum((xs[i] - xbar) ** 2 for i in range(n))
    return num / den if den else 0.0


def compute_metrics(trace, hro_rec):
    risks = risk_levels(trace)
    n = len(risks)
    max_risk = max(risks) if risks else 0

    # 1. risk_slope
    risk_slope = linear_regression_slope(risks)

    # 2. steps_at_max_risk (consecutive run at end, or any steps at max)
    steps_at_max_risk = sum(1 for r in risks if r == max_risk)

    # 3. risk_acceleration: avg slope second half vs first half
    mid = n // 2
    first_half = risks[:mid]
    second_half = risks[mid:]
    slope1 = linear_regression_slope(first_half) if len(first_half) >= 2 else 0.0
    slope2 = linear_regression_slope(second_half) if len(second_half) >= 2 else 0.0
    risk_acceleration = slope2 > slope1

    # 4. monotonic: risk never drops
    monotonic = all(risks[i] <= risks[i + 1] for i in range(n - 1))

    # 5. steps_to_first_risk2: steps until risk >= 2 (None if never reached)
    steps_to_first_risk2 = None
    for i, r in enumerate(risks):
        if r >= 2:
            steps_to_first_risk2 = i
            break

    # violation info from metadata or HRO record
    meta = trace.get("metadata", {})
    reached_violation = meta.get("reached_violation", False)
    log_id = meta.get("scenario_id", "") + "_" + meta.get("run_id", "")
    # try hro_rec first (authoritative)
    if hro_rec:
        reached_violation = hro_rec.get("reached_violation", reached_violation)
        violation_step = hro_rec.get("violation_step")
    else:
        violation_step = None

    return {
        "log_id": log_id,
        "category": trace["_category"],
        "reached_violation": reached_violation,
        "violation_step": violation_step,
        "n_steps": n,
        "max_risk": max_risk,
        "risk_slope": risk_slope,
        "steps_at_max_risk": steps_at_max_risk,
        "risk_acceleration": risk_acceleration,
        "monotonic": monotonic,
        "steps_to_first_risk2": steps_to_first_risk2,
        "risks": risks,
    }


def mean_of(vals):
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def pct_true(bools):
    if not bools:
        return None
    return 100.0 * sum(bools) / len(bools)


def pearson_r(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 2:
        return None
    xbar = statistics.mean(xs)
    ybar = statistics.mean(ys)
    num = sum((xs[i] - xbar) * (ys[i] - ybar) for i in range(n))
    sx = (sum((x - xbar) ** 2 for x in xs) / n) ** 0.5
    sy = (sum((y - ybar) ** 2 for y in ys) / n) ** 0.5
    if sx == 0 or sy == 0:
        return None
    return num / (n * sx * sy)


def aggregate(metrics_list):
    viol = [m for m in metrics_list if m["reached_violation"]]
    non_viol = [m for m in metrics_list if not m["reached_violation"]]

    def summary(ms):
        return {
            "count": len(ms),
            "avg_risk_slope": mean_of([m["risk_slope"] for m in ms]),
            "avg_steps_at_max_risk": mean_of([m["steps_at_max_risk"] for m in ms]),
            "pct_monotonic": pct_true([m["monotonic"] for m in ms]),
            "avg_steps_to_first_risk2": mean_of([m["steps_to_first_risk2"] for m in ms]),
            "pct_risk_acceleration": pct_true([m["risk_acceleration"] for m in ms]),
        }

    return {"violated": summary(viol), "non_violated": summary(non_viol)}


def per_category(metrics_list):
    cats = sorted(set(m["category"] for m in metrics_list))
    result = {}
    for cat in cats:
        cat_metrics = [m for m in metrics_list if m["category"] == cat]
        result[cat] = aggregate(cat_metrics)
    return result


def early_warning_correlation(metrics_list):
    """
    For violated traces: Pearson r between steps_to_first_risk2 and violation_step.
    Answers: does early risk elevation predict early violation?
    """
    viol = [
        m for m in metrics_list
        if m["reached_violation"]
        and m["steps_to_first_risk2"] is not None
        and m["violation_step"] is not None
    ]
    if len(viol) < 2:
        return {"n": len(viol), "pearson_r": None, "note": "insufficient data"}

    xs = [m["steps_to_first_risk2"] for m in viol]
    ys = [m["violation_step"] for m in viol]
    r = pearson_r(xs, ys)
    return {
        "n": len(viol),
        "pearson_r": round(r, 4) if r is not None else None,
        "interpretation": (
            "strong positive correlation — early risk2 predicts early violation"
            if r is not None and r > 0.5
            else "moderate positive correlation"
            if r is not None and r > 0.2
            else "weak or no correlation"
            if r is not None
            else "n/a"
        ),
    }


def main():
    print("Loading HRO index...")
    hro_index = load_hro_index()
    print(f"  {len(hro_index)} HRO records")

    print("Loading traces...")
    traces = load_traces()
    print(f"  {len(traces)} traces across {len(set(t['_category'] for t in traces))} categories")

    # Build a lookup from log_id -> hro record
    # HRO records use log_id field; trace metadata uses scenario_id + run_id
    # Build both-key lookup
    hro_by_scenario_run = {}
    for log_id, rec in hro_index.items():
        hro_by_scenario_run[log_id] = rec

    print("Computing metrics...")
    all_metrics = []
    for trace in traces:
        meta = trace.get("metadata", {})
        scenario_id = meta.get("scenario_id", "")
        run_id = meta.get("run_id", "")
        composed = f"{scenario_id}_{run_id}"
        hro_rec = hro_by_scenario_run.get(composed)
        m = compute_metrics(trace, hro_rec)
        all_metrics.append(m)

    print(f"  Computed {len(all_metrics)} metric records")
    violated = sum(1 for m in all_metrics if m["reached_violation"])
    print(f"  Violated: {violated}, Non-violated: {len(all_metrics) - violated}")

    overall = aggregate(all_metrics)
    by_cat = per_category(all_metrics)
    corr = early_warning_correlation(all_metrics)

    # Per-trace summary (without full risks array for readability)
    trace_summaries = [
        {k: v for k, v in m.items() if k != "risks"}
        for m in all_metrics
    ]

    result = {
        "summary": {
            "total_traces": len(all_metrics),
            "violated": violated,
            "non_violated": len(all_metrics) - violated,
        },
        "overall": overall,
        "per_category": by_cat,
        "early_warning_correlation": corr,
        "traces": trace_summaries,
    }

    # Print readable results
    print("\n" + "="*60)
    print("OVERALL: VIOLATED vs NON-VIOLATED")
    print("="*60)
    for group in ("violated", "non_violated"):
        g = overall[group]
        print(f"\n  [{group.upper()}]  n={g['count']}")
        print(f"    avg_risk_slope:           {g['avg_risk_slope']:.4f}" if g['avg_risk_slope'] is not None else "    avg_risk_slope:           n/a")
        print(f"    avg_steps_at_max_risk:    {g['avg_steps_at_max_risk']:.2f}" if g['avg_steps_at_max_risk'] is not None else "    avg_steps_at_max_risk:    n/a")
        print(f"    pct_monotonic:            {g['pct_monotonic']:.1f}%" if g['pct_monotonic'] is not None else "    pct_monotonic:            n/a")
        print(f"    avg_steps_to_first_risk2: {g['avg_steps_to_first_risk2']:.2f}" if g['avg_steps_to_first_risk2'] is not None else "    avg_steps_to_first_risk2: n/a")
        print(f"    pct_risk_acceleration:    {g['pct_risk_acceleration']:.1f}%" if g['pct_risk_acceleration'] is not None else "    pct_risk_acceleration:    n/a")

    print("\n" + "="*60)
    print("PER CATEGORY BREAKDOWN")
    print("="*60)
    for cat, groups in by_cat.items():
        print(f"\n  {cat.upper()}")
        for group in ("violated", "non_violated"):
            g = groups[group]
            if g["count"] == 0:
                print(f"    [{group}] n=0 — no data")
                continue
            print(f"    [{group}] n={g['count']}")
            r2 = f"{g['avg_steps_to_first_risk2']:.2f}" if g['avg_steps_to_first_risk2'] is not None else "n/a"
            print(f"      risk_slope={g['avg_risk_slope']:.4f}  steps_at_max={g['avg_steps_at_max_risk']:.2f}  "
                  f"monotonic={g['pct_monotonic']:.1f}%  steps_to_r2={r2}  "
                  f"accel={g['pct_risk_acceleration']:.1f}%")

    print("\n" + "="*60)
    print("EARLY WARNING CORRELATION (violated traces only)")
    print("  steps_to_first_risk2  ↔  violation_step")
    print("="*60)
    c = corr
    print(f"  n={c['n']}  Pearson r={c['pearson_r']}  → {c.get('interpretation','')}")

    with open(OUTPUT, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nResults saved to {OUTPUT}")


if __name__ == "__main__":
    main()
