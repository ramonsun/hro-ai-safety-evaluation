"""
Real incident validation: run the HRO classifier and scorer against 3 reconstructed
logs based on published AI safety incidents.

These are NOT original system logs — they are reconstructed from public incident
descriptions. The purpose is to test whether the classifier assigns the expected
failure mode to each incident.

Expected classifications:
  real_incident_001 (Waymo school bus)  → ESCALATION_FAILURE, is_near_miss: false
  real_incident_002 (agent bought eggs) → AUTHORITY_CONFUSION, is_near_miss: false
  real_incident_003 (coding agent lost files) → CONTEXT_LOSS, is_near_miss: false

Usage:
    python experiment/real_incident_analysis.py
"""

import json
import os
from pathlib import Path

from classifier.classify import classify_log
from scorer.hro_scorer import score_log

INCIDENT_FILES = [
    "data/real_incidents/incident_waymo_school_bus.json",
    "data/real_incidents/incident_agent_bought_eggs.json",
    "data/real_incidents/incident_coding_agent_lost_files.json",
]

EXPECTED = {
    "real_incident_001": {"category": "ESCALATION_FAILURE", "is_near_miss": False},
    "real_incident_002": {"category": "AUTHORITY_CONFUSION", "is_near_miss": False},
    "real_incident_003": {"category": "CONTEXT_LOSS",        "is_near_miss": False},
}


def run() -> dict:
    results = []
    for fpath in INCIDENT_FILES:
        log = json.loads(Path(fpath).read_text())
        print(f"\n--- Classifying {log['log_id']} ---")
        classification = classify_log(log)
        score = score_log(log, classification)
        result = {**classification, **score, "source": log.get("source")}

        expected = EXPECTED.get(log["log_id"], {})
        result["expected_category"] = expected.get("category")
        result["category_match"] = (result["category"] == expected.get("category"))
        result["near_miss_match"] = (result.get("is_near_miss", False) == expected.get("is_near_miss", False))

        results.append(result)
        print(f"  category:   {result['category']}  (expected: {expected.get('category')})  match={result['category_match']}")
        print(f"  is_near_miss: {result.get('is_near_miss')}  match={result['near_miss_match']}")
        print(f"  signal_strength: {result.get('hro_signal_strength')}")
        print(f"  recommendation: {result.get('recommendation')}")

    correct = sum(1 for r in results if r["category_match"])
    output = {
        "n_incidents": len(results),
        "classifier_accuracy": f"{correct}/{len(results)}",
        "results": results,
    }

    out_path = Path(__file__).parent / "real_incident_results.json"
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nResults written to {out_path}")
    print(f"Classifier accuracy: {correct}/{len(results)} expected modes correct")
    return output


if __name__ == "__main__":
    run()
