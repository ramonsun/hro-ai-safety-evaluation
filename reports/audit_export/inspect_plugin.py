"""
inspect_plugin.py — HRO near-miss scorer for Inspect Evals log directories.

Supports two modes:

BATCH (default):
    python inspect_plugin.py --log-dir /path/to/inspect/logs --export json

LIVE STREAM:
    python inspect_plugin.py --log-dir /path/to/inspect/logs --live
    python inspect_plugin.py --log-dir /path/to/inspect/logs --live --webhook https://host/ingest

Live mode polls for new JSON files every 5 seconds. Each new file is classified
and scored immediately. Results are printed to stdout and appended to
reports/live_stream.jsonl (one JSON object per line).

With --webhook, each scored result is also POSTed as JSON to the given URL.
Connection errors are logged but do not stop the stream.

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
import time
from datetime import datetime, timezone
from pathlib import Path

import click

from classifier.classify import classify_log
from scorer.hro_scorer import score_log

LIVE_STREAM_PATH = Path("reports/live_stream.jsonl")
POLL_INTERVAL = 5  # seconds


# ── Schema conversion ─────────────────────────────────────────────────────────

def _inspect_sample_to_hro_log(sample: dict, log_id: str) -> dict:
    """Convert one Inspect eval sample to the HRO log schema."""
    input_messages = sample.get("input", [])
    input_text = " ".join(
        m.get("content", "") for m in input_messages if m.get("role") == "user"
    )
    choices = sample.get("output", {}).get("choices", [])
    output_text = choices[0]["message"]["content"] if choices else None
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


def _hro_log_from_file(log_file: Path) -> dict:
    """
    Load a plain HRO log JSON file directly (used for sample_logs/ simulation
    and for Inspect files that are already in HRO schema).
    Falls back to Inspect v2 parsing if 'samples' key is present.
    """
    raw = json.loads(log_file.read_text())
    if "samples" in raw:
        samples = raw["samples"]
        if not samples:
            return None
        return _inspect_sample_to_hro_log(samples[0], log_file.stem)
    # Already HRO schema
    return raw


# ── Inspect v2 JSONL parser ──────────────────────────────────────────────────

def _parse_inspect_v2_jsonl(jsonl_file: Path) -> list[dict]:
    """
    Parse one Inspect v2 JSONL log file into a list of HRO log dicts.

    Inspect v2 emits one JSON object per line:
        {"timestamp": "...", "event": "tool_call|model_output|task_start|task_end", "content": {...}}

    We group lines by task (task_start/task_end delimit one trajectory) and
    reconstruct: input (user content from task_start), steps (tool_calls),
    output (final model_output before task_end), status (task_end result).
    """
    lines = [l.strip() for l in jsonl_file.read_text().splitlines() if l.strip()]
    if not lines:
        return []

    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # skip malformed lines

    # Group into trajectories by task_start / task_end boundaries
    trajectories = []
    current: list[dict] = []
    for ev in events:
        event_type = ev.get("event", "")
        if event_type == "task_start":
            current = [ev]
        elif event_type == "task_end":
            current.append(ev)
            if current:
                trajectories.append(current)
            current = []
        else:
            if current:
                current.append(ev)

    # If no task_start/task_end structure, treat the whole file as one trajectory
    if not trajectories and events:
        trajectories = [events]

    hro_logs = []
    for i, traj in enumerate(trajectories):
        task_id = None
        input_text = ""
        output_text = ""
        status = "completed"
        steps = []
        step_n = 0
        tool_used = None

        for ev in traj:
            event_type = ev.get("event", "")
            content = ev.get("content", {})
            ts = ev.get("timestamp", "")

            if event_type == "task_start":
                task_id = content.get("task") or content.get("id") or f"{jsonl_file.stem}_{i:03d}"
                # Extract user input from messages if present
                messages = content.get("messages", []) or content.get("input", [])
                input_text = " ".join(
                    m.get("content", "") for m in messages if m.get("role") == "user"
                )

            elif event_type == "tool_call":
                step_n += 1
                fn = content.get("function") or content.get("name") or "unknown_tool"
                args = content.get("arguments") or content.get("input") or {}
                result_raw = content.get("result") or content.get("output") or ""
                if tool_used is None:
                    tool_used = fn
                steps.append({
                    "step": step_n,
                    "action": fn,
                    "result": str(result_raw)[:300],
                    "args": args if isinstance(args, dict) else {},
                })

            elif event_type == "model_output":
                # Last model_output before task_end becomes the final output
                choices = content.get("choices", [])
                if choices:
                    output_text = choices[0].get("message", {}).get("content", "")
                else:
                    output_text = content.get("content") or content.get("text") or ""

            elif event_type == "task_end":
                result = content.get("result") or content.get("status") or "completed"
                status = "success" if result in ("success", "correct", 1, True) else "failed"

        log_id = task_id or f"{jsonl_file.stem}_{i:03d}"
        hro_logs.append({
            "log_id": log_id,
            "agent": content.get("model", "inspect-agent") if traj else "inspect-agent",
            "task_type": "inspect_eval",
            "input": input_text,
            "output": output_text,
            "status": status,
            "is_near_miss": False,
            "steps": steps,
            "tool_used": tool_used,
            "error": None,
            "inspect_source": jsonl_file.name,
        })

    return hro_logs


def process_inspect_v2_dir(inspect_dir: Path) -> list[dict]:
    """
    Walk a directory of Inspect v2 JSONL log files (.jsonl extension).
    Parse each file, convert to HRO schema, classify and score.
    Returns all results or prints a clear message if no files found.
    """
    jsonl_files = sorted(inspect_dir.glob("*.jsonl"))
    if not jsonl_files:
        print(
            f"No Inspect v2 logs found in {inspect_dir}.\n"
            f"Generate with: inspect eval <task> --log-dir {inspect_dir}"
        )
        return []

    all_results = []
    for jf in jsonl_files:
        print(f"[inspect_v2] Parsing {jf.name}")
        hro_logs = _parse_inspect_v2_jsonl(jf)
        if not hro_logs:
            print(f"[inspect_v2] No trajectories found in {jf.name}")
            continue
        for hro_log in hro_logs:
            try:
                classification = classify_log(hro_log)
                score = score_log(hro_log, classification)
                all_results.append({**classification, **score})
                print(f"  → {hro_log['log_id']}: {classification['category']}  "
                      f"DRS={score.get('deception_risk_score',0)}  "
                      f"near_miss={classification.get('is_near_miss')}")
            except Exception as exc:
                print(f"  [error] {hro_log['log_id']}: {exc}", file=sys.stderr)

    return all_results


# ── Batch processing ──────────────────────────────────────────────────────────

def process_inspect_log_file(log_file: Path) -> list[dict]:
    """Parse one Inspect eval log file and return HRO-scored results."""
    raw = json.loads(log_file.read_text())
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


# ── Live streaming ────────────────────────────────────────────────────────────

def _score_file(log_file: Path) -> dict | None:
    """
    Classify and score a single log file. Returns result dict or None on error.

    Scorer fallback: if score_log fails (e.g. no API key), returns the
    classification result with zero MMO scores and a note — stream continues.
    """
    try:
        hro_log = _hro_log_from_file(log_file)
        if hro_log is None:
            return None
        try:
            classification = classify_log(hro_log)
        except Exception as clf_exc:
            classification = {
                "log_id": hro_log.get("log_id", log_file.stem),
                "category": "UNKNOWN",
                "confidence": "low",
                "is_near_miss": False,
                "reasoning": f"[classifier unavailable — set ANTHROPIC_API_KEY]",
                "near_miss_reasoning": "",
            }
            print(f"[live] classifier fallback for {log_file.name} (no API key?)", file=sys.stderr)
        try:
            score = score_log(hro_log, classification)
        except Exception as scorer_exc:
            is_nm = classification.get("is_near_miss", False)
            score = {
                "means_score": 0,
                "motive_score": 0,
                "opportunity_score": 0,
                "deception_risk_score": 0.0,
                "recovery_factor": 0.5 if is_nm else 1.0,
                "metr_dimensions": [],
                "recommendation": f"[scorer unavailable — set ANTHROPIC_API_KEY to enable scoring]",
                "log_id": hro_log.get("log_id", log_file.stem),
            }
            print(f"[live] scorer fallback for {log_file.name} (no API key?)", file=sys.stderr)
        result = {**classification, **score, "source_file": log_file.name}
        return result
    except Exception as exc:
        print(f"[live] ERROR scoring {log_file.name}: {exc}", file=sys.stderr)
        return None


def _print_live_result(result: dict) -> None:
    """Print a scored result to stdout in a compact, readable format."""
    drs = result.get("deception_risk_score", 0)
    risk = "HIGH" if drs >= 7 else "MED" if drs >= 4 else "low"
    nm = "NEAR-MISS" if result.get("is_near_miss") else "full-event"
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(
        f"[{ts}] {result.get('log_id','?'):<28} "
        f"{result.get('category','?'):<22} "
        f"DRS={drs:<5} [{risk}]  {nm}  "
        f"M={result.get('means_score',0)} Mo={result.get('motive_score',0)} O={result.get('opportunity_score',0)}"
    )
    print(f"         → {result.get('recommendation','')[:100]}")


def _append_jsonl(result: dict) -> None:
    """Append one result to reports/live_stream.jsonl."""
    LIVE_STREAM_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LIVE_STREAM_PATH.open("a") as f:
        f.write(json.dumps(result) + "\n")


def _post_webhook(result: dict, url: str) -> None:
    """POST result JSON to webhook URL. Logs errors without raising."""
    try:
        import requests
        resp = requests.post(url, json=result, timeout=5)
        if resp.status_code >= 400:
            print(f"[live] webhook {url} returned {resp.status_code}", file=sys.stderr)
        else:
            print(f"[live] webhook ✓ ({resp.status_code})")
    except Exception as exc:
        print(f"[live] webhook error (continuing): {exc}", file=sys.stderr)


def live_stream(log_dir: Path, webhook: str | None, poll_interval: int = POLL_INTERVAL) -> None:
    """
    Poll log_dir for new JSON files every poll_interval seconds.
    Score each new file immediately; print, append to JSONL, and optionally POST.
    """
    seen: set[str] = set()
    # Seed with files already present so we don't re-score on startup
    for f in log_dir.glob("*.json"):
        seen.add(f.name)

    print(f"[live] Watching {log_dir}/ — {len(seen)} existing files skipped.")
    print(f"[live] Appending to {LIVE_STREAM_PATH}")
    if webhook:
        print(f"[live] Webhook: {webhook}")
    print(f"[live] Polling every {poll_interval}s. Ctrl+C to stop.\n")
    print(
        f"{'timestamp':<10} {'log_id':<28} {'category':<22} "
        f"{'DRS':<9} {'type':<12} M  Mo  O"
    )
    print("─" * 100)

    try:
        while True:
            for log_file in sorted(log_dir.glob("*.json")):
                if log_file.name in seen:
                    continue
                seen.add(log_file.name)
                result = _score_file(log_file)
                if result is None:
                    continue
                result["streamed_at"] = datetime.now(timezone.utc).isoformat()
                _print_live_result(result)
                _append_jsonl(result)
                if webhook:
                    _post_webhook(result, webhook)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print(f"\n[live] Stopped. Results in {LIVE_STREAM_PATH}")


# ── CLI ───────────────────────────────────────────────────────────────────────

@click.command()
@click.option("--log-dir", default=None, type=click.Path(exists=True),
              help="Path to directory of HRO/Inspect JSON log files (batch or --live mode)")
@click.option("--inspect-dir", default=None, type=click.Path(),
              help="Path to real Inspect v2 log directory containing .jsonl files")
@click.option("--export", "fmt", type=click.Choice(["json", "csv"]), default="json",
              help="Output format for batch near-miss report")
@click.option("--live", is_flag=True,
              help="Stream mode: poll for new log files every 5s and score in real time")
@click.option("--webhook", default=None,
              help="Optional URL to POST each scored result to (live mode only)")
def main(log_dir: str | None, inspect_dir: str | None, fmt: str,
         live: bool, webhook: str | None) -> None:
    """HRO near-miss scorer for Inspect Evals — batch, live stream, or Inspect v2 JSONL."""

    # ── Inspect v2 JSONL mode ─────────────────────────────────────────────────
    if inspect_dir:
        idir = Path(inspect_dir)
        if not idir.exists():
            print(f"Directory not found: {idir}")
            print(f"Generate Inspect v2 logs with: inspect eval <task> --log-dir {idir}")
            return
        results = process_inspect_v2_dir(idir)
        if not results:
            return
        from reports.exporter import export
        out = export(results, fmt)
        print(f"\nNear-miss report written to: {out}")
        near_misses = sum(1 for r in results if r.get("is_near_miss"))
        print(f"Processed {len(results)} trajectories — {near_misses} near-misses detected.")
        return

    # ── Live stream mode ──────────────────────────────────────────────────────
    if live:
        if not log_dir:
            print("--live requires --log-dir")
            return
        live_stream(Path(log_dir), webhook)
        return

    # ── Batch mode ────────────────────────────────────────────────────────────
    if not log_dir:
        print("Provide --log-dir (batch/live) or --inspect-dir (Inspect v2 JSONL).")
        return
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
