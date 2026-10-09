import pytest

from src.confidence_scoring import confidence, route, brier

import json
import subprocess
import sys
from pathlib import Path


def test_confidence_is_deterministic_and_bounded():
    args = (0.9, 0.6, True, 1)
    assert confidence(*args) == confidence(*args)
    assert 0 <= confidence(*args) <= 1


def test_self_report_has_only_small_weight():
    low = confidence(0.0, 1.0, True, 3)
    high = confidence(1.0, 1.0, True, 3)
    assert high - low == pytest.approx(0.15)


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_out_of_range_self_report(value):
    with pytest.raises(ValueError):
        confidence(value, 0.5, True, 1)


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_rejects_out_of_range_agreement(value):
    with pytest.raises(ValueError):
        confidence(0.5, value, True, 1)


def test_rejects_negative_evidence_count():
    with pytest.raises(ValueError):
        confidence(0.5, 0.5, True, -1)


def test_rejects_invalid_validation_type():
    with pytest.raises(TypeError):
        confidence(0.5, 0.5, 1, 1)


def test_evidence_score_caps_at_three():
    assert confidence(0.5, 0.5, True, 3) == confidence(0.5, 0.5, True, 10)


def test_route_threshold_boundaries():
    assert route(0.8) == "act"
    assert route(0.5) == "ask_human"
    assert route(0.499) == "escalate"


def test_route_rejects_inverted_thresholds():
    with pytest.raises(ValueError):
        route(0.7, act_at=0.5, ask_at=0.8)


def test_brier_perfect_predictions():
    assert brier([(1.0, True), (0.0, False)]) == 0.0


def test_brier_penalizes_wrong_predictions():
    assert brier([(0.0, True), (1.0, False)]) == 1.0


def test_brier_rejects_empty_dataset():
    with pytest.raises(ValueError):
        brier([])

def test_route_acts_exactly_at_act_threshold():
    assert route(0.8, act_at=0.8, ask_at=0.5) == "act"


def test_route_asks_human_just_below_act_threshold():
    assert route(0.799, act_at=0.8, ask_at=0.5) == "ask_human"


def test_route_asks_human_exactly_at_ask_threshold():
    assert route(0.5, act_at=0.8, ask_at=0.5) == "ask_human"


def test_route_escalates_just_below_ask_threshold():
    assert route(0.499, act_at=0.8, ask_at=0.5) == "escalate"


def test_route_rejects_out_of_range_score():
    with pytest.raises(ValueError):
        route(1.1)


def test_route_rejects_non_numeric_score():
    with pytest.raises(TypeError):
        route("high")


def test_route_rejects_boolean_score():
    with pytest.raises(TypeError):
        route(True)


def test_route_accepts_equal_thresholds():
    assert route(0.7, act_at=0.7, ask_at=0.7) == "act"
    assert route(0.699, act_at=0.7, ask_at=0.7) == "escalate"

def test_overconfident_answer_with_weak_signals_is_not_acted_on():
    score = confidence(
        self_report=0.99,
        agreement=0.2,
        validated=False,
        evidence_count=0,
    )

    assert score == 0.218
    assert route(score) == "escalate"


def test_strong_signals_can_support_action():
    score = confidence(
        self_report=0.9,
        agreement=1.0,
        validated=True,
        evidence_count=3,
    )

    assert score == 0.985
    assert route(score) == "act"


def test_overconfidence_score_is_lower_than_supported_confidence():
    overconfident = confidence(0.99, 0.2, False, 0)
    supported = confidence(0.9, 1.0, True, 3)

    assert overconfident < supported


def test_threshold_comparison_creates_valid_report():
    project_root = Path(__file__).resolve().parents[1]
    report_path = project_root / "evidence" / "threshold_results.json"

    result = subprocess.run(
        [sys.executable, str(project_root / "evidence" / "threshold_comparison.py")],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Chosen policy:" in result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_count"] == 20
    assert len(report["comparison"]) == 3
    assert report["chosen_policy"] == "permissive"


def test_all_threshold_policies_count_all_cases():
    project_root = Path(__file__).resolve().parents[1]
    report = json.loads(
        (project_root / "evidence" / "threshold_results.json").read_text(
            encoding="utf-8"
        )
    )

    for policy in report["comparison"]:
        assert (
            policy["acted_on"]
            + policy["sent_to_human"]
            + policy["escalated"]
            == 20
        )
        assert 0 <= policy["wrong_answers_acted_on"] <= policy["acted_on"]