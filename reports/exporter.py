import json
import csv
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(__file__).parent


def export(results: list[dict], fmt: str = "json") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if fmt == "json":
        out = REPORTS_DIR / f"report_{timestamp}.json"
        out.write_text(json.dumps(results, indent=2))
    else:
        out = REPORTS_DIR / f"report_{timestamp}.csv"
        fields = [
            "log_id", "category", "confidence",
            "severity", "detectability", "recoverability", "near_miss_score",
            "hro_flags", "recommendation",
        ]
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                row = dict(r)
                row["hro_flags"] = "|".join(r.get("hro_flags", []))
                writer.writerow(row)
    return out
