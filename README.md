# hro-safety-eval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

HRO-inspired safety evaluation for AI agent traces.

## Install and use

```bash
pip install git+https://github.com/ramonsun/hro-ai-safety-evaluation
export ANTHROPIC_API_KEY=your_key
hro-eval monitor --trace your_agent_log.json
```

Accepts any JSON trace format — list of steps, dict with `"steps"` key, SafetyDrift format, OpenAI messages. No pre-labeled data required.

## What it does

**1. Classifies failure mode (RCM taxonomy)**

Five categories: GOAL_DRIFT, AUTHORITY_CONFUSION, CONTEXT_LOSS, TOOL_MISUSE, ESCALATION_FAILURE.

Validated on 30 human-annotated ATBench logs: F1=0.929 with taxonomy vs F1=0.000 without. Taxonomy is the critical ingredient — same model, same logs, taxonomy is the only variable.

**2. Computes risk trajectory**

- `risk_slope` — rate of risk escalation across steps (OLS regression)
- `risk_acceleration` — whether second half of trace escalates faster than first
- `steps_at_max_risk` — how long agent stayed at peak risk before outcome
- `harm_probability` — HIGH / MODERATE / LOW based on trajectory + RCM category

## What the research found

### ATBench (n=30, human ground truth)

| Method | P | R | F1 |
|--------|---|---|-----|
| LLM judge v2 (RCM taxonomy + CoT) | 1.000 | 0.867 | 0.929 |
| HRO+METR (threshold=4.0) | 0.684 | 0.867 | 0.765 |
| Keyword probe | 0.778 | 0.467 | 0.583 |
| LLM judge v1 (no taxonomy) | 0.000 | 0.000 | 0.000 |

### SafetyDrift (n=357, Dhodapkar & Pishori 2026)

| Signal | Violated (n=186) | Non-violated (n=171) |
|--------|-----------------|---------------------|
| avg risk_slope | **0.72** | 0.23 |
| risk_acceleration | **60%** | 6% |
| avg steps_at_max_risk | **1.69** | 6.95 |
| DRS ↔ max_risk correlation | **0.826** | — |
| GOAL_DRIFT precision | **100%** | — |
| AUTHORITY_CONFUSION precision | **100%** | — |

## The central research question — answered

**Does HRO near-miss detection predict harm before it occurs, like in aviation?**

Short answer: **not in synthetic traces.**

5 near-misses were detected across 357 SafetyDrift traces — all in non-violated traces, zero before any violation. Agents that proceed to violation show no behavioral recovery signal. Risk escalation is monotonic and uninterrupted.

This is the key gap between aviation HRO and current AI agents: in aviation, operators sometimes hesitate, re-check, and recover. Synthetic AI agents do not — they either violate or they don't, with no middle state.

**What this means:**
- Risk trajectory (slope, acceleration) predicts harm and is useful for post-hoc forensics
- Near-miss detection as *early warning* requires agents that exhibit recovery behavior — which may exist in real production logs but was not observed in synthetic SafetyDrift traces

## What the tool is useful for today

**Validated:**

- Post-hoc forensics: classify what went wrong and why
- Risk scoring: flag high-slope traces for human review
- RCM categorization: GOAL_DRIFT and AUTHORITY_CONFUSION are 100% predictive of violation in this dataset
- Works on any agent trace JSON format — no pre-labeled data needed

**Not validated:**

- Real-time early warning
- Calibrated on synthetic traces only
- Near-miss detection requires agents that verbally signal uncertainty

## Open research question

Does near-miss detection work in real production agent logs?

If real agents exhibit richer behavioral variation than synthetic traces — partial recoveries, backtracking, uncertainty signals — the HRO near-miss classifier may find precursors before violation. This is the next experiment.

What's needed:
- Step-by-step traces from real agent deployments
- Labels at tool-call granularity (not task-completion summaries)
- At least 3 outcome categories: benign / near-miss / harm

If you have access to this data, open an issue or contact rsundblad@udesa.edu.ar

## Limitations

- ATBench: n=30, single annotator, no holdout set
- SafetyDrift: synthetic traces, may not reflect real agent behavior
- Risk inference uses Claude Haiku — quality depends on model
- Near-miss detection requires verbal uncertainty signals from the agent
- Partial circularity: classifier uses Claude Haiku (mitigated by `--ollama-judge`)

## Replication

```bash
python3 -m experiment.evaluate_against_ground_truth
```

Ground truth: `data/ground_truth/human_labels.csv` · Annotation guide: `data/ground_truth/annotation_guide.md`

## Dataset attribution

SafetyDrift: Dhodapkar & Pishori, RPI/SCU  
Paper: [arXiv:2603.27148](https://arxiv.org/abs/2603.27148)  
Dataset: [huggingface.co/datasets/aditya593/SafetyDrift-traces](https://huggingface.co/datasets/aditya593/SafetyDrift-traces)  
License: CC-BY-NC-4.0. Contact authors for data access.

## Citation

```bibtex
@misc{dhodapkar2026safetydrift,
  title={SafetyDrift: Evaluating Safety Alignment Drift in Agentic AI Systems},
  author={Dhodapkar, Aditya and Pishori, Farhaan},
  year={2026},
  eprint={2603.27148},
  archivePrefix={arXiv}
}

@misc{sundblad2026hro,
  title={hro-safety-eval: HRO Near-Miss Detection for AI Agent Traces},
  author={Sundblad, Ramon},
  year={2026},
  url={https://github.com/ramonsun/hro-ai-safety-evaluation}
}
```

---

BlueDot Impact Technical AI Safety Sprint 2026 · MIT License  
Contact: rsundblad@udesa.edu.ar
