"""
inspect_plugin.py — stub for wiring HRO near-miss scorer as an Inspect Evals
post-processing step on an existing log directory.

Usage (once implemented):
    python inspect_plugin.py --log-dir /path/to/inspect/logs --export json

TODO: install inspect_ai (pip install inspect-ai) and replace stubs below.
"""

import json
from pathlib import Path

# TODO: from inspect_ai.log import read_eval_log
# TODO: from classifier.classify import classify_log
# TODO: from scorer.hro_scorer import score_log


def process_inspect_log_dir(log_dir: str) -> list[dict]:
    """
    TODO: Walk an Inspect eval log directory, convert each sample into the
    HRO log schema, run classify_log + score_log, and return scored results.
    """
    results = []
    for log_file in Path(log_dir).glob("*.json"):
        raw = json.loads(log_file.read_text())
        # TODO: map Inspect sample fields → HRO log schema
        # hro_log = {"log_id": raw["id"], "input": raw["input"], "output": raw["output"], ...}
        # classification = classify_log(hro_log)
        # score = score_log(hro_log, classification)
        # results.append({**classification, **score})
        _ = raw  # placeholder
    return results


if __name__ == "__main__":
    # TODO: wire click CLI (--log-dir, --export)
    raise NotImplementedError("inspect_plugin is a stub — see TODOs above.")
