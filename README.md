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
2. Applies a **rule-based pre-filter** (keyword heuristics) — high-confidence matches skip the API call entirely
3. Classifies each log entry using an **RCM-derived failure taxonomy** (5 failure modes) via Claude
4. Scores each log with **RPN = Severity × Occurrence × Detectability** (FMEA standard, max 1000)
5. Runs **session analysis**: near-miss rate per 100 interactions, mode distribution, RPN trajectory
6. Outputs a structured report: what almost failed, RPN, HRO flags, recommendation

**RCM** (Reliability Centered Maintenance) provides the vocabulary to define what a near-miss *is* in agent logs.  
**HRO** provides the cultural protocol for what to *do* with that signal.

---

## Near-Miss Definition

A log entry is a near-miss if and only if all three criteria are met: (1) an unsafe state was entered during execution, (2) a recovery mechanism activated before the final output, and (3) the log shows evidence of both. Logs where the unsafe state occurred but recovery is absent are classified as full failures, not near-misses.

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
│   └── rcm_taxonomy.py        # RCM failure mode definitions (5 modes)
├── classifier/
│   ├── classify.py            # Log → failure mode classifier (pre-filter + Claude API)
│   └── pre_filter.py          # Rule-based keyword pre-filter (skips API on clear matches)
├── scorer/
│   └── hro_scorer.py          # HRO near-miss scorer — RPN = S×O×D (Claude API)
├── generator/
│   └── generate.py            # Generate synthetic agent logs (Claude API)
├── reports/
│   ├── exporter.py            # JSON and CSV report exporter
│   └── session_analysis.py    # Session-level aggregation (near-miss rate, RPN trajectory)
├── data/
│   └── sample_logs/           # Example agent logs (incl. validated near-miss logs)
├── inspect_plugin.py          # Stub: Inspect Evals post-processing integration
├── cli.py                     # CLI entrypoint (analyze, generate, --session flag)
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

# Run session analysis (near-miss rate, mode distribution, RPN trajectory)
python cli.py analyze data/sample_logs/ --session

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
- **RCM & RPN:** Nowlan & Heap (1978) — *Reliability-Centered Maintenance*, United Airlines / US Navy. RPN (Risk Priority Number = Severity × Occurrence × Detectability) is the standard FMEA prioritization formula from this lineage, adopted here to rank near-miss severity across agent logs.
- **Tenerife as case study:** Deadliest aviation accident in history (583 fatalities, 27 March 1977). The KLM first officer expressed doubt about takeoff clearance to Captain van Zanten, but the challenge was too weak and too deferential to override the captain's authority. Post-Tenerife reforms included mandatory Crew Resource Management (CRM, NASA/United 1979, FAA 1981), standardized ICAO radiotelephony phraseology (1977–1980), and expansion of non-punitive reporting culture. The Aviation Safety Reporting System (ASRS) had launched in 1976; Tenerife accelerated its adoption. Fatality rates per flight hour declined sharply from the 1980s onward as these operational practices spread across the industry. Academics later labeled this pattern of operational discipline "High Reliability Organization" theory.
- **Chernobyl as multi-mode case study:** The 1986 disaster exhibited operator behaviors that map to all five failure modes — drift from test protocol (`GOAL_DRIFT`), bypass of automatic safety systems to maintain an unstable low-power state (`AUTHORITY_CONFUSION`), loss of situational awareness during the overnight shift (`CONTEXT_LOSS`), late insertion of control rods with a fatal reactor design flaw (`TOOL_MISUSE`), and alarm fatigue in an overwhelmed control room (`ESCALATION_FAILURE`). Critically, the RBMK reactor's design flaws (positive void coefficient, graphite-tipped control rods) were the primary cause; the modes describe *how* the socio-technical system failed, not *who* to blame. In AI safety, this maps to distinguishing agent behavior from eval design flaws.
- **AI safety gap:** Current evals report binary pass/fail scores. Frontier labs collect rich intermediate traces, logprobs, and refusal rates, but no standardized framework exists to classify and act on near-miss signals within those traces. No near-miss reporting protocol equivalent to aviation's ASRS exists for AI labs.

---

## Status

- [x] RCM failure taxonomy defined (5 canonical modes)
- [x] Sample agent logs — including 2 validated near-miss logs
- [x] Rule-based pre-filter (keyword fast path, skips API for clear matches)
- [x] RCM classifier (Claude API, temperature=0, forced to 5 modes)
- [x] Operational near-miss definition (unsafe state + recovery + evidence)
- [x] HRO near-miss scorer — RPN = Severity × Occurrence × Detectability
- [x] Deterministic HRO flags (failure mode → principle mapping in code)
- [x] Session analysis (near-miss rate per 100, mode distribution, RPN trajectory)
- [x] Synthetic log generator (Claude API)
- [x] JSON and CSV report exporter
- [x] CLI entrypoint with `--session` flag and RPN summary table
- [x] Pipeline runs end-to-end
- [ ] Inspect Evals integration (stub only — `inspect_plugin.py`)

---

## Limitations & Known Issues

1. ~~**Near-miss vs full miss**~~ — **Fixed:** classifier now applies a strict 3-criterion operational definition and returns `is_near_miss` on every log.
2. ~~**Frequency not implemented**~~ — **Fixed:** `--session` flag computes near-miss rate per 100 interactions, mode distribution, and RPN trajectory across all logs in a directory.
3. **Taxonomy assumptions:** The 5 failure modes are adapted from RCM theory, not validated against real AI incident data — different assumptions could produce different or additional modes.
4. **Coverage:** Aviation/nuclear taxonomies use 40+ modes; 5 modes may miss failure patterns not yet observed in synthetic logs.
5. ~~**Non-deterministic scoring**~~ — **Partially fixed:** `temperature=0` on all API calls reduces variance; pre-filter path is fully deterministic. LLM scores for ambiguous logs still vary slightly across API versions.
6. **Inspect integration:** `inspect_plugin.py` is a stub — requires `inspect_ai` install and schema mapping work to function.

---

## Part of BlueDot Impact — Technical AI Safety Project Sprint

This project is submitted toward the BlueDot Impact Technical AI Safety Certificate.

---

## License

MIT
