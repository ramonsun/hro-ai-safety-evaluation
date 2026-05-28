"""
inspect_plugin.py — Post-processing HRO near-miss scorer for Inspect Evals log directories.

Converts Inspect eval log format (v2) to the HRO log schema, runs the classifier
and scorer on each sample, and outputs a near-miss report.

Usage:
    pip install inspect-ai  # required
    python inspect_plugin.py --log-dir /path/to/inspect/logs --export json

Inspect v2 log format (per sample):
    {
      "id": "sample_001",
      "input": [{"role": "user", "content": "..."}],
      "output": {"model": "...", "choices": [{"message": {"content": "..."}}]},
      "score": {"value": 1, "explanation": "..."},
      "metadata": {"task": "...", "tool": "..."}
    }
"""

import json
import sys
from pathlib import Path

import click

from classifier.classify import classify_log
from scorer.hro_scorer import score_log


def _inspect_sample_to_hro_log(sample: dict, log_id: str) -> dict:
    """Convert one Inspect eval sample to the HRO log schema."""
    # Extract user-facing input text
    input_messages = sample.get("input", [])
    input_text = " ".join(
        m.get("content", "") for m in input_messages if m.get("role") == "user"
    )

    # Extract model output text
    choices = sample.get("output", {}).get("choices", [])
    output_text = choices[0]["message"]["content"] if choices else None

    # Infer status from eval score (score=1 → success, score=0 → failed)
    score_val = sample.get("score", {}).get("value")
    status = "success" if score_val == 1 else "failed"

    metadata = sample.get("metadata", {})

    return {
        "log_id": log_id,
        "agent": sample.get("model", metadata.get("model", "unknown-model")),
        "task_type": metadata.get("task", "eval_task"),
        "timestamp": sample.get("timestamp", ""),
        "input": input_text,
        "output": output_text,
        "status": status,
        "error": sample.get("error"),
        "tool_used": metadata.get("tool"),
        "eval_score": score_val,
        "eval_explanation": sample.get("score", {}).get("explanation"),
    }


def process_inspect_log_file(log_file: Path) -> list[dict]:
    """
    Parse one Inspect eval log file (.json, v2 format) and return HRO-scored results.
    Each sample in the file becomes one scored log entry.
    """
    raw = json.loads(log_file.read_text())

    # TODO: handle Inspect .eval binary format (use inspect_ai.log.read_eval_log)
    samples = raw.get("samples", [])
    if not samples:
        print(f"[inspect_plugin] No samples found in {log_file.name}", file=sys.stderr)
        return []

    results = []
    for i, sample in enumerate(samples):
        log_id = sample.get("id", f"{log_file.stem}_{i:03d}")
        hro_log = _inspect_sample_to_hro_log(sample, log_id)
        classification = classify_log(hro_log)
        score = score_log(hro_log, classification)
        results.append({**classification, **score})

    return results


def process_inspect_log_dir(log_dir: str) -> list[dict]:
    """Walk a directory of Inspect eval log files and return all scored results."""
    all_results = []
    for log_file in sorted(Path(log_dir).glob("*.json")):
        print(f"[inspect_plugin] Processing {log_file.name}")
        all_results.extend(process_inspect_log_file(log_file))
    return all_results


@click.command()
@click.option("--log-dir", required=True, type=click.Path(exists=True),
              help="Path to directory of Inspect eval log files (.json)")
@click.option("--export", "fmt", type=click.Choice(["json", "csv"]), default="json",
              help="Output format for near-miss report")
def main(log_dir: str, fmt: str) -> None:
    """Run HRO near-miss scorer on an Inspect eval log directory."""
    results = process_inspect_log_dir(log_dir)
    if not results:
        print("No results. Check log directory format.")
        return

    from reports.exporter import export
    out = export(results, fmt)
    print(f"Near-miss report written to: {out}")
    near_misses = sum(1 for r in results if r.get("is_near_miss"))
    print(f"Processed {len(results)} samples — {near_misses} near-misses detected.")


if __name__ == "__main__":
    main()
