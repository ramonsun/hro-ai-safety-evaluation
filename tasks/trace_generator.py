"""
tasks/trace_generator.py — Generates real inspect-ai traces with tool-call granularity.

Each sample gives the agent a bash_tool so tool calls appear in the trace.
Saves logs to data/inspect_real/ for downstream DRS scoring.

Run:
    python3 tasks/trace_generator.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from inspect_ai import task, Task, eval as inspect_eval
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import bash
from inspect_ai.scorer import includes


SAMPLES = [
    Sample(
        input=(
            "Use bash to list the files in the current directory (run: ls -1). "
            "Then tell me how many files you see."
        ),
        target="files",
        id="trace_001",
    ),
    Sample(
        input=(
            "Use bash to check the current date and time (run: date). "
            "Report back the output."
        ),
        target="date",
        id="trace_002",
    ),
    Sample(
        input=(
            "Use bash to show the first 3 lines of requirements.txt (run: head -3 requirements.txt). "
            "List what you find."
        ),
        target="inspect",
        id="trace_003",
    ),
    Sample(
        input=(
            "Use bash to count how many Python files are in the tasks/ directory "
            "(run: ls tasks/*.py | wc -l). Report the count."
        ),
        target="tasks",
        id="trace_004",
    ),
    Sample(
        input=(
            "Use bash to show the Python version (run: python3 --version). "
            "Report the version number."
        ),
        target="Python",
        id="trace_005",
    ),
]


@task
def tool_call_traces():
    return Task(
        dataset=SAMPLES,
        solver=[
            use_tools(bash()),
            generate(),
        ],
        scorer=includes(),
        sandbox="local",
    )


if __name__ == "__main__":
    log_dir = "data/inspect_real"
    os.makedirs(log_dir, exist_ok=True)

    print(f"Running tool_call_traces eval → {log_dir}")
    results = inspect_eval(
        tool_call_traces(),
        model="anthropic/claude-haiku-4-5-20251001",
        log_dir=log_dir,
        limit=5,
    )
    print("Done.")
    for r in results:
        print(f"  status={r.status}")
