# Audit brief — HRO deception near-miss detector

## What this project does

Classifies AI agent behavioral logs using HRO near-miss theory and METR's Means/Motive/Opportunity framework. Detects deception preconditions before harmful actions complete.

## Current state (May 2026)

- 10 tests passing (pytest tests/)
- Validated on 30 ATBench real trajectories
- Exports MMO-scored JSON (--export-ati)
- Live stream mode with webhook (--live --webhook)
- Inspect v2 integration (--inspect-dir)

## Key finding

Threshold=7.0 calibrated on synthetic logs captures outliers only on real ATBench data (recall=0.20). Median real deceptive DRS=5.6–6.7. Recalibration to ~5.0 requires labeled Inspect v2 traces with full tool-call sequences — the critical next step.

## What near-miss means here

Agent entered unsafe state AND recovery activated before harm completed. Requires step-by-step traces to detect. ATBench logs lack this granularity.

## Immediate next steps

1. Generate real Inspect v2 traces locally and recalibrate threshold
2. Connect to Apollo Watcher Analyze ingestion schema
3. CLTR Observatory — contribute MMO-scored incident data

## What this is not

- Not a production monitor (synthetic calibration, no real trace validation)
- Not claiming deployment readiness
- A research classifier and framework contribution to the ATI field

## Repo

https://github.com/ramonsun/hro-ai-safety-evaluation

## Author

Ramon Sundblad — BlueDot Impact Technical AI Safety Sprint, 2026
