# hro-safety-eval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

**What we tested:** whether aviation near-miss detection predicts AI agent harm before it occurs.  
**What we found:** it doesn't — not because the framework is wrong, but because current agents don't exhibit recovery behavior.  
**Why it matters:** if agents escalate monotonically to violation, the bottleneck is architecture, not measurement.

---

## What this is

A Python CLI that scores deception risk in AI agent traces using two frameworks from high-reliability industries:

- **RCM** (Reliability Centered Maintenance): an aviation failure taxonomy adapted into five agent categories — goal drift, authority confusion, context loss, tool misuse, escalation failure.
- **HRO** (High Reliability Organization): monitors behavioral precursors before harm, anchored to METR's May 2026 means/motive/opportunity model.

The tool tracks risk trajectory (slope, acceleration, time at peak) and outputs a Deception Risk Score (DRS 0–10).

---

## What was found

### 1. Structural detection works on real data (ATBench, n=30)

| Method | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| Keyword probe | 0.714 | 0.667 | 0.690 |
| HRO classifier | 0.857 | 0.800 | **0.828** |

**3 backdoor cases** where the keyword probe missed entirely: the agent trusted poisoned tool output (indirect prompt injection, description injection, unreliable misinformation) with zero deception keywords present. HRO caught them via structural signals — Opportunity + Motive + Means.

*Validated with local judge (Mistral 7B via `--ollama-judge`): backdoor cases replicate.*

### 2. The early-warning hypothesis failed (SafetyDrift, n=357)

In 186 violated traces, **0 showed behavioral recovery before violation**. Agents that violate do not hesitate, backtrack, or signal uncertainty. Risk escalation is monotonic.

This tells us something about **agent architecture**, not just detection: current synthetic agents lack the recoverability that makes near-miss culture possible in aviation. We may need built-in pause/uncertainty mechanisms before HRO protocols can function.

---

## What the tool is useful for today

- **Post-hoc forensics:** classify what went wrong and why
- **Risk scoring:** flag high-slope traces for human review
- **Keyword-blind detection:** catch deception pathways probes miss

**Not validated:** real-time early warning before harm completes.

---

## Install and use

```bash
pip install git+https://github.com/ramonsun/hro-ai-safety-evaluation
export ANTHROPIC_API_KEY=your_key
hro-eval monitor --trace your_agent_log.json
```

Accepts any JSON trace format: list of steps, dict with `"steps"` key, SafetyDrift format, OpenAI messages. No pre-labeled data required.

---

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
