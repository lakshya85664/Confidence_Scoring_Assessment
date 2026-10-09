"""Topic 18, Task 5: compare routing threshold pairs."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.confidence_scoring import route


# Each case is (confidence score, whether the answer was correct).
CASES = [
    (0.95, True), (0.90, True), (0.85, True), (0.80, True),
    (0.75, True), (0.70, True), (0.65, True), (0.60, True),
    (0.55, True), (0.50, True), (0.45, False), (0.40, False),
    (0.35, False), (0.30, False), (0.25, False), (0.20, False),
    (0.15, False), (0.10, False), (0.05, False), (0.01, False),
]

THRESHOLDS = [
    {"name": "permissive", "act_at": 0.60, "ask_at": 0.35},
    {"name": "balanced", "act_at": 0.80, "ask_at": 0.50},
    {"name": "conservative", "act_at": 0.90, "ask_at": 0.70},
]


def main():
    rows = []

    for policy in THRESHOLDS:
        acted = 0
        wrong_acted = 0
        sent_to_human = 0
        escalated = 0

        for score, was_correct in CASES:
            decision = route(
                score,
                act_at=policy["act_at"],
                ask_at=policy["ask_at"],
            )

            if decision == "act":
                acted += 1
                if not was_correct:
                    wrong_acted += 1
            elif decision == "ask_human":
                sent_to_human += 1
            else:
                escalated += 1

        rows.append({
            **policy,
            "total_cases": len(CASES),
            "acted_on": acted,
            "wrong_answers_acted_on": wrong_acted,
            "sent_to_human": sent_to_human,
            "escalated": escalated,
        })

    # Prefer fewer incorrect actions, then more correct actions.
    chosen = min(
        rows,
        key=lambda row: (
            row["wrong_answers_acted_on"],
            -(
                row["acted_on"]
                - row["wrong_answers_acted_on"]
            ),
        ),
    )

    report = {
        "case_count": len(CASES),
        "comparison": rows,
        "chosen_policy": chosen["name"],
        "selection_reason": (
            "Minimizes incorrect answers acted on, then prefers more correct "
            "actions among policies tied on that measure."
        ),
    }

    output_path = PROJECT_ROOT / "evidence" / "threshold_results.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("Topic 18 - Threshold Comparison")
    print("=" * 68)
    print("Policy        Act  Ask  Acted  Wrong acted  Human  Escalated")
    for row in rows:
        print(
            f"{row['name']:<14}"
            f"{row['act_at']:<5.2f}"
            f"{row['ask_at']:<5.2f}"
            f"{row['acted_on']:<7}"
            f"{row['wrong_answers_acted_on']:<13}"
            f"{row['sent_to_human']:<7}"
            f"{row['escalated']}"
        )

    print(f"Chosen policy: {chosen['name']}")
    print(f"Reason: {report['selection_reason']}")
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()