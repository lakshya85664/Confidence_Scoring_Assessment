"""Topic 18, Task 4: evaluate confidence calibration on 20 labelled cases."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.confidence_scoring import brier


CASES = [
    (0.95, True),
    (0.90, True),
    (0.85, True),
    (0.80, True),
    (0.75, True),
    (0.70, True),
    (0.65, True),
    (0.60, True),
    (0.55, True),
    (0.50, True),
    (0.45, False),
    (0.40, False),
    (0.35, False),
    (0.30, False),
    (0.25, False),
    (0.20, False),
    (0.15, False),
    (0.10, False),
    (0.05, False),
    (0.01, False),
]


def main():
    score = brier(CASES)
    rows = [
        {
            "case_id": index,
            "predicted_confidence": probability,
            "correct_outcome": outcome,
            "squared_error": round((probability - float(outcome)) ** 2, 4),
        }
        for index, (probability, outcome) in enumerate(CASES, start=1)
    ]

    report = {
        "case_count": len(CASES),
        "brier_score": score,
        "interpretation": (
            "Lower is better. This deterministic sample contains high-confidence "
            "correct predictions and low-confidence incorrect predictions."
        ),
        "cases": rows,
    }

    output_path = PROJECT_ROOT / "evidence" / "calibration_results.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Topic 18 - Calibration Analysis")
    print("=" * 44)
    print(f"Cases: {len(CASES)}")
    print(f"Brier score: {score:.3f}")
    print("Lower Brier scores indicate better calibration.")
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()