"""Topic 18: Confidence Scoring — deterministic reference implementation."""

from typing import Literal


Route = Literal["act", "ask_human", "escalate"]


def confidence(
    self_report: float,
    agreement: float,
    validated: bool,
    evidence_count: int,
) -> float:
    """Blend independent confidence signals into a score from 0 to 1."""
    for name, value in (
        ("self_report", self_report),
        ("agreement", agreement),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")

    if not isinstance(validated, bool):
        raise TypeError("validated must be a boolean")

    if isinstance(evidence_count, bool) or not isinstance(evidence_count, int):
        raise TypeError("evidence_count must be an integer")
    if evidence_count < 0:
        raise ValueError("evidence_count cannot be negative")

    evidence = min(evidence_count, 3) / 3

    score = (
        0.15 * self_report
        + 0.35 * agreement
        + 0.30 * float(validated)
        + 0.20 * evidence
    )
    return round(score, 3)


def route(score: float, act_at: float = 0.8, ask_at: float = 0.5) -> Route:
    """Choose an action using two thresholds.

    Scores at or above act_at are acted on.
    Scores at or above ask_at are sent for human review.
    Lower scores are escalated.
    """
    for name, value in (("score", score), ("act_at", act_at), ("ask_at", ask_at)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")

    if ask_at > act_at:
        raise ValueError("ask_at must not be greater than act_at")

    if score >= act_at:
        return "act"
    if score >= ask_at:
        return "ask_human"
    return "escalate"


def brier(predictions: list[tuple[float, bool]]) -> float:
    """Calculate the mean Brier score for probability/outcome pairs."""
    if not predictions:
        raise ValueError("predictions cannot be empty")

    errors = []
    for probability, outcome in predictions:
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise TypeError("each probability must be numeric")
        if not 0 <= probability <= 1:
            raise ValueError("probabilities must be between 0 and 1")
        if not isinstance(outcome, bool):
            raise TypeError("each outcome must be a boolean")

        errors.append((probability - float(outcome)) ** 2)

    return round(sum(errors) / len(errors), 3)


if __name__ == "__main__":
    cases = [
        ("clear", dict(self_report=0.9, agreement=1.0, validated=True, evidence_count=3)),
        ("mixed", dict(self_report=0.9, agreement=0.6, validated=True, evidence_count=1)),
        (
            "overconfident",
            dict(self_report=0.99, agreement=0.2, validated=False, evidence_count=0),
        ),
    ]

    results = []
    print("Topic 18 — Confidence Scoring")
    print("=" * 48)

    for name, signals in cases:
        score = confidence(**signals)
        decision = route(score)
        results.append((name, score, decision))
        print(f"{name} {score:.3f} {decision}")

    calibration_cases = [
        (score, name == "clear")
        for name, score, _ in results
    ]
    print(f"brier: {brier(calibration_cases):.3f}")