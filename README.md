# HRO Near-Miss Classifier for Agentic AI Systems

> Borrowing aviation and nuclear safety culture to catch AI failures before they happen.

---

## The Problem

AI safety treats safety as a **measurement problem**: build better benchmarks, run better evals, get better scores.

Aviation tried this. It didn't work until the 1977 Tenerife disaster — 583 dead — forced a different question:

> *What almost went wrong, and why did no one report it?*

High Reliability Organizations (HROs) — nuclear plants, aircraft carriers, air traffic control — don't just measure failures. They build **near-miss culture**: every close call is reported, classified, and acted on before the crash happens.

AI agent logs contain near-miss signals today. No framework captures them.

**This project builds one.**

---

## What This Is

A Python CLI that:

1. Ingests agent interaction logs (synthetic or real)
2. Classifies each log entry using an **RCM-derived failure taxonomy** (5 failure modes)
3. Scores **near-miss probability** per entry using HRO-style weak signal detection
4. Outputs a structured report: what almost failed, severity, frequency

**RCM** (Reliability Centered Maintenance) provides the vocabulary to define what a near-miss *is* in agent logs.  
**HRO** provides the cultural protocol for what to *do* with that signal.

---

## The 5 Failure Modes (RCM Taxonomy for Agents)

| Mode | Description | Aviation Analog | Nuclear Analog |
|------|-------------|-----------------|----------------|
| `GOAL_DRIFT` | Agent pursues proxy goal, deviates from intent | Wrong runway heading | Optimizing output over safety margins |
| `AUTHORITY_CONFUSION` | Agent acts outside sanctioned boundaries | Takeoff without clearance | Operator bypasses interlock |
| `CONTEXT_LOSS` | Agent loses thread of task state mid-execution | Crew incapacitation | Shift handoff information loss |
| `TOOL_MISUSE` | Agent uses tool in unintended way | Wrong instrument reading | Wrong control rod procedure |
| `ESCALATION_FAILURE` | Agent fails to hand off when uncertain | No mayday call | Suppressing reactor warning alarms |

---

## Research Question

> Does near-miss rate in agent logs predict future capability failures **before** standard evals catch them?

If yes: AI safety has a new early-warning instrument.  
If no: we learn something important about the limits of behavioral logging.

---

## Project Structure

```
hro-ai-safety-evaluation/
├── taxonomy/
│   └── rcm_taxonomy.py        # RCM failure mode definitions
├── classifier/
│   └── classify.py            # Log → failure mode classifier (Claude API)
├── scorer/
│   └── hro_scorer.py          # HRO near-miss scorer (Claude API)
├── generator/
│   └── generate.py            # Generate synthetic agent logs (Claude API)
├── reports/
│   └── exporter.py            # JSON and CSV report exporter
├── data/
│   └── sample_logs/           # Example agent logs
├── cli.py                     # CLI entrypoint
└── README.md
```

---

## Quickstart

```bash
git clone https://github.com/ramonsun/hro-ai-safety-evaluation
cd hro-ai-safety-evaluation

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY="sk-ant-..."

# Analyze all sample logs and print results
python cli.py analyze data/sample_logs/

# Analyze and export a JSON report to reports/
python cli.py analyze data/sample_logs/ --export json

# Export as CSV instead
python cli.py analyze data/sample_logs/ --export csv

# Generate 3 synthetic logs and save them to data/sample_logs/
python cli.py generate -n 3 --save
```

---

## Directions

**Direction 1 (Core):** Deploy HRO scorer as post-processing layer on Inspect Evals. Every benchmark run outputs a near-miss report alongside pass/fail scores.

**Direction 2 (Validation):** Run scorer against published AI incident reports. Did near-miss signals exist before the failure? Were they ignored?

**Direction 3 (Moonshot):** Publish HRO reporting protocol as open specification. Test whether near-miss culture survives capability-race pressure — the same pressure that almost killed it pre-Tenerife.

---

## Theoretical Grounding

- **HRO Theory:** Weick & Roberts (1993), Weick, Sutcliffe & Obstfeld (1999)
- **RCM:** Nowlan & Heap (1978) — *Reliability-Centered Maintenance*, United Airlines / US Navy
- **Tenerife as case study:** Deadliest aviation accident in history. Root cause: no culture for crew to challenge captain. Post-Tenerife reforms = mandatory CRM, near-miss reporting, standardized comms. Aviation fatality rates per flight hour declined significantly in the decades following Tenerife, a period that coincides with widespread HRO adoption across the industry.
- **Chernobyl as multi-mode case study:** The 1986 disaster exhibited all five failure modes simultaneously — operators drifted from test protocol (GOAL_DRIFT), bypassed safety interlocks (AUTHORITY_CONFUSION), lost situational awareness during the overnight shift (CONTEXT_LOSS), misapplied the reactor control procedure (TOOL_MISUSE), and suppressed warning signals rather than escalating (ESCALATION_FAILURE).
- **AI safety gap:** Current evals are binary (pass/fail). No "almost failed" category. No near-miss reporting protocol exists for frontier labs.

---

## Status

- [x] RCM failure taxonomy defined
- [x] Sample agent log files
- [x] RCM classifier (Claude API)
- [x] HRO near-miss scorer (Claude API)
- [x] Synthetic log generator (Claude API)
- [x] JSON and CSV report exporter
- [x] CLI entrypoint with summary view
- [x] Pipeline runs end-to-end

---

## Limitations & Known Issues

1. **Near-miss vs full miss:** The scorer does not yet distinguish between "almost happened" and "happened but low severity" — some logged events are actual failures, not near-misses.
2. **Frequency not implemented:** Current reports show per-log scores only; frequency analysis across sessions requires more logs and additional aggregation code.
3. **Taxonomy assumptions:** The 5 failure modes are adapted from RCM theory, not validated against real AI incident data — different assumptions could produce different or additional modes.
4. **Coverage:** Aviation/nuclear taxonomies use 40+ modes; 5 modes may miss failure patterns not yet observed in synthetic logs.
5. **Non-deterministic scoring:** The Claude API produces slightly different scores and reasoning on repeated analysis of identical logs — results are probabilistic, not reproducible exactly.

---

## Part of BlueDot Impact — Technical AI Safety Project Sprint

This project is submitted toward the BlueDot Impact Technical AI Safety Certificate.

---

## License

MIT
