# Audit brief — HRO deception near-miss detector

## What this project does

Classifies AI agent behavioral logs using HRO near-miss theory and METR's Means/Motive/Opportunity categories (METR Frontier Risk Report, May 2026). The Deception Risk Score (DRS) formula and RCM mode mapping are this project's contributions — not METR's. Detects deception preconditions before harmful actions complete.

## Current state (May 2026)

- 10 tests passing (pytest tests/)
- Validated on 30 ATBench real trajectories, human-annotated by Ramon Sundblad
- Exports MMO-scored JSON (--export-ati)
- Live stream mode with webhook (--live --webhook)
- Inspect v2 integration (--inspect-dir)
- Independent judge via Ollama/Mistral:7b (--ollama-judge, zero Anthropic dependency)

## Key finding

HRO+METR F1=0.765 vs LLM judge F1=0.000 on 30 human-annotated ATBench logs. LLM judge without taxonomy is blind to structural deception (indirect prompt injection, tool misuse). HRO+METR detects 13/15 cases the LLM judge misses entirely.

| Method | P | R | F1 |
|--------|---|---|----|
| HRO+METR (threshold=4.0) | 0.684 | 0.867 | 0.765 |
| Keyword probe | 0.778 | 0.467 | 0.583 |
| LLM judge (no taxonomy) | 0.000 | 0.000 | 0.000 |

## What near-miss means here

Agent entered unsafe state AND recovery activated before harm completed. Requires step-by-step traces to detect. ATBench task-completion logs lack this granularity — near_miss=False across all 30 logs.

## Immediate next steps

1. Recalibrate threshold on Inspect v2 step-by-step traces (full tool-call sequences)
2. CLTR Observatory — contribute MMO-scored incident data
3. Community validation: open annotation of additional ATBench batches

## What this is not

- Not a production monitor (threshold calibrated on task-completion logs, not step-by-step traces)
- Not claiming deployment readiness
- A research classifier and framework contribution to the ATI field

## Repo

https://github.com/ramonsun/hro-ai-safety-evaluation

## Author

Ramon Sundblad — BlueDot Impact Technical AI Safety Sprint, 2026
