"""
fetch_atbench.py — Download ATBench500 from HuggingFace and save first 30 rows.

Run locally (requires internet access):
    python poc/fetch_atbench.py

The Claude Code environment cannot reach HuggingFace (404 at time of writing).
If the dataset URL has changed, update URL below and re-run.
"""

import json
import sys
from pathlib import Path

import pandas as pd

URL = (
    "https://huggingface.co/datasets/AI45Research/ATBench/resolve/"
    "refs%2Fconvert%2Fparquet/default/test/0000.parquet"
)

OUT = Path(__file__).parent / "atbench_raw.json"


def main() -> None:
    print(f"Downloading ATBench parquet from:\n  {URL}\n")
    try:
        df = pd.read_parquet(URL)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "\nHuggingFace unreachable or dataset moved.\n"
            "Run poc/atbench_mock.py to generate schema-matched synthetic data.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Total rows : {len(df)}")
    print(f"Columns    : {list(df.columns)}")

    first_traj = str(df.iloc[0].get("trajectory", df.iloc[0].to_dict()))
    print(f"\nFirst trajectory (truncated to 500 chars):\n{first_traj[:500]}")

    dist = df["label"].value_counts().sort_index()
    print("\nLabel distribution:")
    for lbl, cnt in dist.items():
        tag = "safe" if lbl == 0 else "unsafe"
        print(f"  {lbl} ({tag}): {cnt}")

    sample = df.head(30).to_dict(orient="records")
    OUT.write_text(json.dumps(sample, indent=2, default=str))
    print(f"\nSaved first 30 rows to {OUT}")


if __name__ == "__main__":
    main()
