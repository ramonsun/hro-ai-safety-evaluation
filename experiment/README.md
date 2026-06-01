# Experiment scripts

## How to run all 3 methods from scratch

```bash
# 0. Setup (once)
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."

# 1. HRO+METR scores — already in reports/atbench_batch2_results.json
#    To re-run on ATBench samples (requires API key):
python cli.py analyze data/atbench_samples/ --export-ati
python cli.py analyze data/atbench_samples/batch2/ --export-ati

# 2. LLM judge (requires API key)
python3 -c "
import json, sys; sys.path.insert(0,'.')
from pathlib import Path
from baselines.llm_judge import judge
files = [f for f in Path('data/atbench_samples').glob('*.json') if f.name!='README.md']
files += list(Path('data/atbench_samples/batch2').glob('*.json'))
results = [judge(json.loads(f.read_text())) for f in sorted(files, key=lambda f:int(f.stem.replace('atbench_','')))]
Path('reports/llm_judge_atbench_results.json').write_text(json.dumps({'n':len(results),'results':results},indent=2))
"

# 3. Keyword probe (no API key needed)
python3 -c "
import json, sys; sys.path.insert(0,'.')
from pathlib import Path
from baselines.keyword_probe import probe
files = [f for f in Path('data/atbench_samples').glob('*.json') if f.name!='README.md']
files += list(Path('data/atbench_samples/batch2').glob('*.json'))
results = [probe(json.loads(f.read_text())) for f in sorted(files, key=lambda f:int(f.stem.replace('atbench_','')))]
Path('reports/keyword_probe_atbench_results.json').write_text(json.dumps({'n':len(results),'results':results},indent=2))
"

# 4. Compare all three vs human labels
python3 -m experiment.evaluate_against_ground_truth
```

## Dependencies

| Script | API key needed | Notes |
|--------|---------------|-------|
| `evaluate_against_ground_truth.py` | no (reads saved results) | Requires filled `human_labels.csv` |
| `deception_comparison.py` | yes (classify + score) | Runs on 8 synthetic logs |
| `fail_fast_tests.py` | yes | 3 validation tests |
| `session_analysis.py` | no | Hardcoded synthetic sessions |
| `simulate_live_stream.py` | yes (scorer) | Ollama optional for agent |

## Expected output files

| File | Contents |
|------|----------|
| `reports/ground_truth_evaluation.json` | Precision/recall/F1 for all 3 methods vs human labels |
| `reports/llm_judge_atbench_results.json` | Raw LLM judge output for 30 logs |
| `reports/keyword_probe_atbench_results.json` | Raw keyword probe output for 30 logs |
| `reports/atbench_batch2_results.json` | HRO+METR DRS scores for all 30 logs |
| `reports/threshold_calibration.json` | F1 at thresholds 3.0–8.0 |

## How to interpret results

- **F1=0.765 (HRO+METR)**: best of three methods. 13/15 deceptive logs detected, 6 false positives on benign logs with elevated MEANS scores.
- **F1=0.000 (LLM judge)**: blind to indirect prompt injection — agent looks compliant even when following poisoned instructions.
- **F1=0.583 (keyword probe)**: fast but misses 8/15 deceptive logs with no keywords; 2 FPs from metadata text.
- **near_miss=False across all 30 ATBench logs**: ATBench task-completion format lacks step-by-step tool calls. Near-miss detection requires Inspect v2 or similar granularity.
- **Threshold=4.0**: calibrated on the same 30 logs used for evaluation. Held-out test would give lower, more honest F1.
