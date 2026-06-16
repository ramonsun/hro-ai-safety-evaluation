# hro-safety-eval

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

Scores deception risk in AI agent traces using failure taxonomy and risk trajectory signals from aviation and nuclear safety.

```bash
pip install git+https://github.com/ramonsun/hro-ai-safety-evaluation
export ANTHROPIC_API_KEY=your_key
hro-eval monitor --trace your_agent_log.json
```

Accepts any JSON trace format. No pre-labeled data required. Substitute a local model with `--ollama-judge`.

---

## How it works

**1. Classifies failure mode (RCM taxonomy)**

Five categories derived from Reliability Centered Maintenance, an aviation safety failure taxonomy:

- Goal drift
- Authority confusion
- Context loss
- Tool misuse
- Escalation failure

A Claude Haiku judge assigns one category per trace using chain-of-thought reasoning.

**2. Scores risk trajectory**

Tracks how risk builds across steps:

- `risk_slope`: rate of escalation (OLS regression)
- `risk_acceleration`: whether the second half escalates faster than the first
- `steps_at_max_risk`: how long the agent stayed at peak risk before outcome
- `harm_probability`: HIGH / MODERATE / LOW based on trajectory and failure category

Output: Deception Risk Score (DRS 0–10). Detection threshold: DRS ≥ 4.0.

---

## Results

### ATBench (n=30, AI45Lab human labels)

| Method | Precision | Recall | F1 |
|--------|-----------|--------|-----|
| Keyword probe | 0.714 | 0.667 | 0.690 |
| HRO classifier | 0.857 | 0.800 | **0.828** |

3 trajectories missed by keyword probe, caught by HRO: agent trusted poisoned tool output with zero deception keywords present. HRO caught them via structural signals: Opportunity + Motive + Means.

### SafetyDrift (n=357, Dhodapkar & Pishori)

| Signal | Violated (n=186) | Non-violated (n=171) |
|--------|-----------------|---------------------|
| avg risk_slope | **0.72** | 0.23 |
| risk_acceleration | **60%** | 6% |
| avg steps_at_max_risk | **1.69** | 6.95 |
| DRS correlation | **0.826** | n/a |
| GOAL_DRIFT precision | **100%** | n/a |
| AUTHORITY_CONFUSION precision | **100%** | n/a |

In 186 violated traces, 0 showed behavioral recovery before violation. Near-miss early warning was not confirmed on synthetic traces. The question remains open for real production logs.

---

## Open research agenda

1. Label 100 existing Inspect AI traces with a 3-outcome schema (safe / near-miss / harm)
2. Test agent variance: do GPT-4o-class agents show higher recovery variance than Claude 3.5?
3. Controlled architecture study: give agents an explicit "pause and check" tool, then measure near-miss rate

If you have access to production agent traces with step-by-step tool-call granularity, open an issue or email [rsundblad@udesa.edu.ar](mailto:rsundblad@udesa.edu.ar)

---

## Limitations

- Training data is synthetic (ATBench n=30, SafetyDrift n=357); results may not generalize to real agent behavior
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
