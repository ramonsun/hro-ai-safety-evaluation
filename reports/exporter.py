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
            "log_id", "category", "metr_dimensions", "confidence", "is_near_miss",
            "means_score", "motive_score", "opportunity_score",
            "recovery_factor", "deception_risk_score", "recommendation",
        ]
        with out.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                row = dict(r)
                row["metr_dimensions"] = "|".join(r.get("metr_dimensions", []))
                writer.writerow(row)
    return out
