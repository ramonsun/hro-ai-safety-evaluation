# hro-safety-eval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

**What we tested:** whether near-miss detection from aviation safety and nuclear power plant safety can predict AI agent harm before it occurs.  
**What we found:** it doesn't. Not because the framework is wrong, but because current agents go straight to the harmful action without pausing, checking, or showing any warning signs first.  
**Why it matters:** if agents always escalate all the way to a violation without any hesitation, the problem is in how agents are built, not in how we measure them.

---

## What this is

A Python CLI that scores deception risk in AI agent traces using two frameworks from high-reliability industries:

- **RCM** (Reliability Centered Maintenance): an aviation safety failure taxonomy adapted into five agent categories: goal drift, authority confusion, context loss, tool misuse, escalation failure.
- **HRO** (High Reliability Organization): monitors behavioral precursors before harm, anchored to METR's May 2026 means/motive/opportunity model.

The tool tracks risk trajectory (slope, acceleration, time at peak) and outputs a Deception Risk Score (DRS 0–10).

---

## What was found

### 1. Structural detection works on real data (ATBench, n=30)

| Method | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| Keyword probe | 0.714 | 0.667 | 0.690 |
| HRO classifier | 0.857 | 0.800 | **0.828** |

**3 backdoor cases** where the keyword probe missed entirely: the agent trusted poisoned tool output (indirect prompt injection, description injection, unreliable misinformation) with zero deception keywords present. HRO caught them via structural signals: Opportunity + Motive + Means.

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

Accepts any JSON trace format. No pre-labeled data required. Substitute a local model with `--ollama-judge`.

---

## Open research agenda

Three experiments would validate or invalidate the near-miss approach:

1. Label 100 existing Inspect AI traces with a 3-outcome schema (safe / near-miss / harm)
2. Test agent variance: do GPT-4o-class agents show higher recovery variance than Claude 3.5?
3. Controlled architecture study: give agents an explicit "pause and check" tool, then measure near-miss rate

If you have access to production agent traces with step-by-step tool-call granularity, open an issue or email [rsundblad@udesa.edu.ar](mailto:rsundblad@udesa.edu.ar)

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

- ATBench: AI45Lab, Shanghai AI Lab. [arXiv:2601.18491](https://arxiv.org/abs/2601.18491)
- SafetyDrift: Dhodapkar & Pishori, RPI/SCU. [arXiv:2603.27148](https://arxiv.org/abs/2603.27148) (CC-BY-NC-4.0)

## Citation

```bibtex
@misc{sundblad2026hro,
  title={hro-safety-eval: HRO Near-Miss Detection for AI Agent Traces},
  author={Sundblad, Ramon},
  year={2026},
  url={https://github.com/ramonsun/hro-ai-safety-evaluation}
}
```

---

BlueDot Impact Technical AI Safety Sprint 2026 · MIT License · [rsundblad@udesa.edu.ar](mailto:rsundblad@udesa.edu.ar)
