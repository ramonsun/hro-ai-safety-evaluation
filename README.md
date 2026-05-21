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

| Mode | Description | Aviation Analog |
|------|-------------|-----------------|
| `GOAL_DRIFT` | Agent pursues proxy goal, deviates from intent | Wrong runway heading |
| `AUTHORITY_CONFUSION` | Agent acts outside sanctioned boundaries | Takeoff without clearance |
| `CONTEXT_LOSS` | Agent loses thread of task state mid-execution | Crew incapacitation |
| `TOOL_MISUSE` | Agent uses tool in unintended way | Wrong instrument reading |
| `ESCALATION_FAILURE` | Agent fails to hand off when uncertain | No mayday call |

---

## Research Question

> Does near-miss rate in agent logs predict future capability failures **before** standard evals catch them?

If yes: AI safety has a new early-warning instrument.  
If no: we learn something important about the limits of behavioral logging.

---

## Project Structure

```
hro-nearmiss/
├── taxonomy/
│   └── failure_modes.py       # RCM failure mode definitions
├── classifier/
│   └── classify.py            # Log → failure mode classifier
├── scorer/
│   └── hro_score.py           # Near-miss probability scorer
├── generator/
│   └── synthetic_logs.py      # Generate labeled synthetic agent logs
├── reports/
│   └── report.py              # Structured output generator
├── data/
│   └── sample_logs/           # Example synthetic logs
├── run.py                     # CLI entrypoint
└── README.md
```

---

## Quickstart

```bash
git clone https://github.com/ramonsun/hro-nearmiss
cd hro-nearmiss
pip install -r requirements.txt

# Generate synthetic logs
python run.py generate --n 50 --output data/sample_logs/

# Classify and score
python run.py analyze --input data/sample_logs/ --output reports/output.json

# View report
python run.py report --input reports/output.json
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
- **Tenerife as case study:** Deadliest aviation accident in history. Root cause: no culture for crew to challenge captain. Post-Tenerife reforms = mandatory CRM, near-miss reporting, standardized comms.
- **AI safety gap:** Current evals are binary (pass/fail). No "almost failed" category. No near-miss reporting protocol exists for frontier labs.

---

## Status

- [ ] Failure taxonomy defined
- [ ] Synthetic log generator
- [ ] RCM classifier (rule-based v1)
- [ ] HRO near-miss scorer
- [ ] CLI entrypoint
- [ ] Sample report output
- [ ] Inspect Evals integration (Direction 1)

---

## Part of BlueDot Impact — Technical AI Safety Project Sprint

This project is submitted toward the BlueDot Impact Technical AI Safety Certificate.

---

## License

MIT
