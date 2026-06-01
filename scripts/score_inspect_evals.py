"""
scripts/score_inspect_evals.py — Convert .eval zip files → HRO DRS scores.

Reads all .eval files in data/inspect_real/, extracts samples with tool-call
granularity, runs the HRO scorer, and writes reports/inspect_real_calibration.json.

Usage:
    python3 scripts/score_inspect_evals.py
"""

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from classifier.classify import classify_log
from scorer.hro_scorer import score_log


def extract_samples(eval_path: Path) -> list[dict]:
    """Extract HRO-schema log dicts from a single .eval zip file."""
    results = []
    with zipfile.ZipFile(eval_path) as zf:
        names = zf.namelist()
        header = json.loads(zf.read("header.json"))
        model = header.get("eval", {}).get("model", "unknown")

        sample_files = [n for n in names if n.startswith("samples/") and n.endswith(".json")]
        for sf in sorted(sample_files):
            sample = json.loads(zf.read(sf))

            # Extract input text
            input_text = sample.get("input", "")
            if isinstance(input_text, list):
                input_text = " ".join(m.get("content", "") for m in input_text if m.get("role") == "user")

            # Extract tool calls from messages
            tool_calls = []
            messages = sample.get("messages", [])
            for msg in messages:
                for tc in msg.get("tool_calls", []):
                    tool_calls.append({
                        "function": tc.get("function", "unknown"),
                        "arguments": tc.get("arguments", {}),
                    })

            # Extract final output
            choices = sample.get("output", {}).get("choices", [])
            if choices:
                output_content = choices[0]["message"].get("content", "")
                if isinstance(output_content, list):
                    output_text = " ".join(
                        b.get("text", "") for b in output_content if isinstance(b, dict)
                    )
                else:
                    output_text = str(output_content)
            else:
                output_text = ""

            score_val = sample.get("scores", {})
            score_val = next(iter(score_val.values()), {}).get("value", None) if score_val else None
            status = "success" if score_val == "C" else "failed"

            results.append({
                "log_id": sample.get("id", sf),
                "agent": model,
                "task_type": "tool_call_eval",
                "timestamp": "",
                "input": input_text,
                "output": output_text,
                "status": status,
                "error": None,
                "tool_calls": tool_calls,
                "tool_used": tool_calls[0]["function"] if tool_calls else None,
                "eval_score": score_val,
                "source_file": eval_path.name,
            })
    return results


def main():
    eval_dir = Path("data/inspect_real")
    eval_files = sorted(eval_dir.glob("*.eval"))
    if not eval_files:
        print("No .eval files found in data/inspect_real/")
        sys.exit(1)

    all_logs = []
    for ef in eval_files:
        print(f"Reading {ef.name} ...")
        samples = extract_samples(ef)
        all_logs.extend(samples)
        print(f"  → {len(samples)} samples extracted")

    print(f"\nScoring {len(all_logs)} total samples ...")
    scored = []
    for log in all_logs:
        classification = classify_log(log)
        drs = score_log(log, classification)
        scored.append({
            **log,
            "hro_category": classification,
            "drs": drs,
        })
        cat_label = classification.get("category", "?") if isinstance(classification, dict) else str(classification)
        print(f"  [{log['log_id']}]  tool={log.get('tool_used','—')}  category={cat_label}  drs={drs}")

    output = {
        "source": "inspect_real",
        "total_samples": len(scored),
        "samples": scored,
    }
    out_path = Path("reports/inspect_real_calibration.json")
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nSaved → {out_path}")


if __name__ == "__main__":
    main()
