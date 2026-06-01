# HRO deception near-miss detector

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ramonsun/hro-ai-safety-evaluation/blob/main/demo/hro_demo.ipynb)

Classifies AI agent logs for deception risk using HRO theory + METR MMO framework. Validated on 30 human-annotated ATBench logs.

## Install

```bash
pip install git+https://github.com/ramonsun/hro-ai-safety-evaluation
export ANTHROPIC_API_KEY=your_key
hro-eval analyze ./your_logs/
# No API key: hro-eval analyze ./your_logs/ --ollama-judge
```

## Results (n=30, ATBench, human ground truth)

| Method | P | R | F1 |
|--------|---|---|-----|
| LLM judge v2 (RCM taxonomy + CoT) | 1.000 | 0.867 | 0.929 |
| HRO+METR (threshold=4.0) | 0.684 | 0.867 | 0.765 |
| Keyword probe | 0.778 | 0.467 | 0.583 |
| LLM judge v1 (no taxonomy) | 0.000 | 0.000 | 0.000 |

Key finding: explicit failure-mode taxonomy is the critical ingredient. Full analysis: [RESULTS.md](RESULTS.md)

## What this is

A research artifact. Not a production tool.

**Validated:** Explicit RCM taxonomy (5 failure modes) is necessary and sufficient for deception detection in task-completion logs. LLM judge without taxonomy: F1=0.000. Same judge with taxonomy: F1=0.929.

**Not yet validated:** Near-miss detection — the central research question — requires step-by-step traces with tool-call granularity (Inspect v2 format). ATBench logs lack this detail. Near-miss detection on real agentic traces is the critical next experiment.

## Limitations

- n=30, single annotator (Ramon Sundblad), no holdout set
- Threshold=4.0 calibrated on task-completion logs — may not generalize
- Near-miss detection requires Inspect v2 traces, not yet validated on real harmful vs near-miss vs benign trace set
- Partial circularity: classifier uses Claude Haiku (mitigated by --ollama-judge)

## Replication

```bash
python3 -m experiment.evaluate_against_ground_truth
```

Ground truth: `data/ground_truth/human_labels.csv` · Annotation guide: `data/ground_truth/annotation_guide.md`

## Open research question

**Central question not yet validated:** Does near-miss precede harm in agentic traces?

The classifier detects deception (F1=0.765) and flags near-miss states (recovery_factor=0.5 in DRS). But no public dataset exists with labeled [near-miss → harm] sequences in step-by-step agent traces.

**What's needed:** ~200 traces with tool-call granularity, labeled in 3 categories: benign / near-miss / harm. ATBench lacks this — it's task-completion summaries only.

**Closest existing work:** SafetyDrift (Stein & Pishori, arXiv 2603.27148) validated that safety drift predicts harm using Markov chains on 357 labeled traces. Same problem, different approach (Markov chains vs HRO taxonomy). Data not yet public.

If you have access to step-by-step agentic traces with safety labels, open an issue or email rsundblad@udesa.edu.ar

Part of [BlueDot Impact](https://bluedot.org) Technical AI Safety Sprint 2026 · MIT License
