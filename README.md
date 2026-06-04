# hro-safety-eval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

HRO-inspired safety evaluation for AI agent traces.

**The idea:** aviation and nuclear safety use near-miss detection to prevent accidents before they happen. Can the same work for AI agents?

**What it does:** classifies why an agent failure happened and scores how fast risk was escalating, using safety frameworks borrowed from aviation and nuclear safety (HRO) and their failure taxonomy (RCM).

**What was found:** failure classification and risk scoring work well. The near-miss early-warning part was not confirmed, but the main bottleneck is data: no public dataset exists with real agent traces labeled at the granularity needed (step-by-step, with near-miss outcomes). Current benchmarks like ATBench only provide coarse binary labels (safe/unsafe) after the fact.

## Install and use

```bash
pip install git+https://github.com/ramonsun/hro-ai-safety-evaluation
export ANTHROPIC_API_KEY=your_key
hro-eval monitor --trace your_agent_log.json
```

Accepts any JSON trace format: list of steps, dict with `"steps"` key, SafetyDrift format, OpenAI messages. No pre-labeled data required.

## What it does

This tool applies two frameworks from high-reliability industries to AI agent traces. High Reliability Organizations (HRO; aviation, nuclear power) operate with near-zero failure rates by monitoring for behavioral precursors before harm occurs. Reliability Centered Maintenance (RCM) is a failure taxonomy from aviation that classifies why systems fail. This project adapts both to AI agents.

**1. Classifies the failure mode (RCM taxonomy)**

Five categories: goal drift, authority confusion, context loss, tool misuse, escalation failure. Given an agent trace, a Claude Haiku judge assigns one category using chain-of-thought reasoning. You can substitute a local model with `--ollama-judge`.

**2. Scores risk trajectory**

Tracks how risk builds across steps, not just whether it peaked:

- `risk_slope`: rate of escalation across steps (OLS regression)
- `risk_acceleration`: whether the second half escalates faster than the first
- `steps_at_max_risk`: how long the agent stayed at peak risk before the outcome
- `harm_probability`: HIGH / MODERATE / LOW based on trajectory shape and failure category

## What was found

### Detecting unsafe agent behavior (ATBench, n=30)

ATBench is a public benchmark of 500 AI agent trajectories labeled safe/unsafe by human annotators (AI45Lab, Shanghai AI Lab, arXiv 2601.18491). Results on a 30-trajectory balanced sample:

| Method | Precision | Recall | F1 |
|--------|-----------|--------|----|
| Keyword probe | 0.714 | 0.667 | 0.690 |
| HRO classifier | 0.857 | 0.800 | 0.828 |

3 trajectories were missed by keyword probe but caught by HRO; the agent trusted poisoned tool output without any deception keywords present (IDs 3, 5, 7).

These are post-hoc detections: HRO classified the trajectory after the agent had already acted. Catching harm before it completes requires step-by-step traces with recovery signals, which ATBench does not provide.

### Risk escalation signals (SafetyDrift, n=357)

SafetyDrift (Dhodapkar & Pishori, RPI/SCU, arXiv 2603.27148) is a dataset of 357 synthetic agent traces labeled by outcome: whether the agent ultimately violated a safety boundary. Violated traces escalate risk 3× faster and rarely show recovery behavior.

| Signal | Violated (n=186) | Non-violated (n=171) |
|--------|-----------------|---------------------|
| avg risk_slope | **0.72** | 0.23 |
| risk_acceleration | **60%** | 6% |
| avg steps_at_max_risk | **1.69** | 6.95 |
| DRS ↔ max_risk correlation | **0.826** | n/a |
| GOAL_DRIFT precision | **100%** | n/a |
| AUTHORITY_CONFUSION precision | **100%** | n/a |

### The early-warning question: not yet answered

The original hypothesis (can HRO detect near-misses before harm occurs, like in aviation) was not confirmed. 0 out of 186 violated traces showed behavioral recovery signals before the violation. Synthetic agents don't hesitate. Answering this requires real production logs with step-by-step granularity and at least 3 outcome labels (safe / near-miss / harm). No public dataset with this structure exists yet.

## What the tool is useful for today

**Validated:**

- Post-hoc forensics: classify what went wrong and why
- Risk scoring: flag high-slope traces for human review
- GOAL_DRIFT and AUTHORITY_CONFUSION are 100% predictive of violation in SafetyDrift
- Works on any agent trace JSON format; no pre-labeled data needed

**Not validated:**

- Real-time early warning before harm completes
- Generalization beyond synthetic traces
- Near-miss detection without verbal uncertainty signals from the agent

## Open question

Does near-miss detection work in real production agent logs, where agents may partially recover?

What's needed:
- Step-by-step traces from real agent deployments
- Labels at tool-call granularity, not task-completion summaries
- At least 3 outcome categories: safe / near-miss / harm

If you have access to this data, open an issue or contact rsundblad@udesa.edu.ar

## Limitations

- ATBench sample: n=30, balanced but small; results may not generalize
- SafetyDrift traces are synthetic; real agent behavior may differ
- Risk inference uses Claude Haiku; quality depends on the model (mitigate with `--ollama-judge`)
- Post-hoc only: current detection fires after the agent has acted, not during

## Replication

```bash
python3 -m experiment.evaluate_against_ground_truth
```

Ground truth: `data/ground_truth/human_labels.csv` · Annotation guide: `data/ground_truth/annotation_guide.md`

## Dataset attribution

SafetyDrift: Dhodapkar & Pishori, RPI/SCU  
Paper: [arXiv:2603.27148](https://arxiv.org/abs/2603.27148)  
License: CC-BY-NC-4.0. Contact authors for data access.

ATBench: AI45Lab, Shanghai AI Lab  
Paper: [arXiv:2601.18491](https://arxiv.org/abs/2601.18491)

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

MIT License · Contact: rsundblad@udesa.edu.ar
