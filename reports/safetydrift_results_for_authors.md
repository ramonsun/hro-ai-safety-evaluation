# HRO Near-Miss Detection on SafetyDrift Traces

**Prepared for:** SafetyDrift dataset authors  
**Date:** 2026-06-02  
**Analyst:** Ramon Sundblad  
**Analysis code:** `scripts/risk_trajectory_analysis.py`

---

## Methods Applied

Two complementary analyses were run on the 357 SafetyDrift labeled traces:

1. **HRO behavioral classifier** — A Claude Haiku judge applied Root Cause Map (RCM) taxonomy to each trace, flagging behavioral recovery signals (pause, verification, uncertainty output, use of safer alternative) that precede or prevent violation. Outputs: `hro_near_miss` (bool), `hro_rcm_category`, `hro_near_miss_step`.

2. **Risk trajectory analysis** — Pure-Python computation of four trajectory metrics from the step-level `risk_level` signal: slope (OLS regression), risk acceleration (second-half vs first-half slope), steps at max risk before outcome, and steps to first risk ≥ 2. No ML libraries used.

---

## Result 1: HRO Near-Miss Detection

| Metric | Value |
|---|---|
| Total traces | 357 |
| Violated | 186 (52.1%) |
| Non-violated | 171 (47.9%) |
| HRO near-misses detected | **5 (1.4%)** |
| Near-misses in violated traces | **0** |
| Near-misses in non-violated traces | **5** |
| Early warnings before violation | **0** |
| Heuristic near-misses (rule-based) | 63 (17.6%) |

All 5 HRO-detected near-misses occurred in **non-violated** traces. In every case, the agent entered an elevated-risk state and then recovered — switching to safer tools, producing uncertainty outputs, or halting without executing the harmful action. No HRO near-miss was detected in any violated trace.

**Pattern:** Near-misses were only flagged when the agent hit simulated environment limits and verbally acknowledged uncertainty. The classifier correctly identified recovery signals in cases where the risk rose but no harm occurred.

**Null finding interpretation:** SafetyDrift agents that proceed to violation do not exhibit behavioral recovery signals prior to that violation. Risk escalation in violated traces is monotonic and uninterrupted — there is no observable hesitation, re-read, or safer alternative attempted before the harmful tool call.

---

## Result 2: Risk Trajectory Predicts Harm

Metrics computed over all 357 traces. Risk trajectory was extracted from `safety_state_before.risk_level` at each step.

| Metric | Violated (n=186) | Non-violated (n=171) | Interpretation |
|---|---|---|---|
| **risk_slope** (OLS slope of risk over steps) | **0.72** | 0.23 | Violated traces escalate ~3× faster |
| **risk_acceleration** (% where 2nd-half slope > 1st-half) | **60.2%** | 5.8% | Late-stage acceleration strongly predicts violation |
| **steps_at_max_risk** (steps spent at peak risk) | **1.69** | 6.95 | Violated traces terminate quickly; non-violated linger at high risk |
| **steps_to_first_risk2** (steps until risk ≥ 2) | 3.39 | 3.63 | **Not predictive** — timing of first elevation is similar across groups |
| **% monotonic** (risk never decreases) | 100% | 100% | Risk never drops in any trace — no recovery in the signal |

**Notable:** `steps_at_max_risk` is inverted from naive expectation. Violated traces spend *fewer* steps at peak risk (avg 1.69) before the harmful action. Non-violated traces linger at high risk for nearly 7 steps without crossing into violation — these represent latent anomalies where the agent was "on the edge" but did not tip over. This latent-anomaly pattern is not captured by any current near-miss label in the dataset.

**Not useful:** `steps_to_first_risk2` (3.39 vs 3.63) and `monotonic` (100%/100%) are not discriminative. Early elevation timing is essentially random with respect to outcome; risk never recovers in any trace.

---

## Result 3: DRS Signal

The Dynamic Risk Score (DRS), operationalized here as `max_risk` (the peak risk level reached across all steps), is a strong scalar predictor of violation.

| Metric | Value |
|---|---|
| Pearson *r*(max_risk, violation) | **0.826** |
| Avg max_risk — violated | **4.00** |
| Avg max_risk — non-violated | **1.86** |
| Difference | 2.14 points on a 0–4 scale |

Max risk = 4 is nearly deterministic for violation. Max risk ≤ 2 is nearly deterministic for non-violation. The DRS signal is the single strongest individual predictor in the dataset — stronger than any trajectory metric individually.

---

## Result 4: Per-Category Breakdown

| Category | n | Violated % | HRO Near-misses | Avg slope (violated) | Avg slope (non-violated) |
|---|---|---|---|---|---|
| code_debugging | 67 | 3% | 1 | 0.36 | 0.40 |
| data_handling | 100 | 80% | 0 | 0.74 | 0.36 |
| research_comms | 100 | 100% | 0 | 0.74 | — |
| sysadmin | 90 | 4% | 4 | 0.15 | 0.08 |

**Notes:**
- `research_comms` has a 100% violation rate — no non-violated traces exist in this category. HRO near-miss detection cannot function as an early warning here; all traces terminate in violation.
- `sysadmin` has the lowest violation rate (4%) and accounts for 4 of the 5 HRO near-misses. Long traces with many steps give the agent more opportunities to exhibit recovery behavior — sysadmin scenarios average 15–20 steps vs. 8–10 for other categories.
- `code_debugging` slope is nearly identical between violated and non-violated (0.36 vs 0.40), making trajectory alone insufficient as a predictor in this category.
- `data_handling` shows the clearest slope separation (0.74 vs 0.36, 2× ratio).

---

## Result 5: RCM Taxonomy Distribution

Distribution of Root Cause Map categories assigned by the HRO classifier.

| RCM Category | All traces (n=357) | Violated only (n=186) |
|---|---|---|
| ESCALATION_FAILURE | 136 (38.1%) | 74 (39.8%) |
| TOOL_MISUSE | 86 (24.1%) | 35 (18.8%) |
| GOAL_DRIFT | 54 (15.1%) | 54 (29.0%) |
| CONTEXT_LOSS | 24 (6.7%) | 3 (1.6%) |
| AUTHORITY_CONFUSION | 20 (5.6%) | 20 (10.8%) |
| None / unclassified | 37 (10.4%) | 0 (0.0%) |

**Notable patterns:**
- `GOAL_DRIFT` appears exclusively in violated traces (54/54 = 100%). When the classifier labels a trace as goal drift, violation always follows. This is the highest-precision RCM signal.
- `AUTHORITY_CONFUSION` is also entirely within violated traces (20/20).
- `CONTEXT_LOSS` is predominantly non-violated (21 of 24 cases). The agent loses situational awareness but does not escalate to harm — consistent with confusion-as-risk-limiter.
- `TOOL_MISUSE` splits ~60/40 non-violated/violated, making it the most ambiguous category.

---

## Key Findings

- **HRO theory holds, but only in one direction.** The classifier successfully identifies behavioral recovery signals in non-violated traces (5/5 near-misses confirmed in non-violated). But it finds zero precursor signals in violated traces — agents that violate show no hesitation. In real HRO systems, near-miss detection works because operators sometimes recover; SafetyDrift's violated agents never do.

- **Trajectory slope and acceleration are the strongest leading indicators.** Violated traces escalate risk ~3× faster and show second-half acceleration in 60% of cases vs. 6% for non-violated. The `steps_at_max_risk` inversion (1.69 vs. 6.95) reveals a latent-anomaly class in the non-violated population — high-risk traces that did not tip into violation — which the current SafetyDrift labeling scheme does not distinguish from "safe" traces.

- **The DRS scalar dominates everything.** Max risk reached (Pearson *r* = 0.826 with violation) is a stronger predictor than any trajectory feature. This suggests that for SafetyDrift's current scenario distribution, risk *level* is more informative than risk *shape* — but in longer, more complex traces, shape features (slope, acceleration) may become critical as max risk saturates at 4 across multiple trace types.

---

## Open Question

If real agent traces exhibit richer behavioral variation than SafetyDrift's synthetic scenarios — including partial recoveries, backtracking, and multi-turn uncertainty — would an HRO classifier find near-miss precursors *before* violation, enabling genuine early warning rather than post-hoc labeling?
