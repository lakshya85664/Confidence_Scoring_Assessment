# Topic 18 — Confidence Scoring Assessment

## Project Overview
This project implements a deterministic confidence-scoring and routing system. It combines self-reported confidence, signal agreement, validation status, and evidence quantity to decide whether to act, ask a human, or escalate. It runs locally and requires no API key.

## Project Structure
```text
Confidence_Scoring_Assessment/
├── src/confidence_scoring.py
├── tests/test_confidence_scoring.py
├── evidence/calibration_analysis.py
├── evidence/calibration_results.json
├── evidence/calibration_output.txt
├── evidence/threshold_comparison.py
├── evidence/threshold_results.json
├── evidence/threshold_output.txt
├── evidence/run_output.txt
├── evidence/pytest_output.txt
├── requirements.txt
└── .gitignore
```

## Task 1 — Confidence Scoring
The score combines self-reported confidence (15%), agreement (35%), validation success (30%), and evidence count (20%). Evidence count is normalized to a maximum of three items.

`confidence = 0.15 × self_report + 0.35 × agreement + 0.30 × validated + 0.20 × min(evidence_count, 3) / 3`

Inputs are validated and the resulting score is rounded to three decimal places.

## Task 2 — Routing
The `route()` function applies two thresholds:
- Score at or above `act_at`: `act`
- Score at or above `ask_at` but below `act_at`: `ask_human`
- Score below `ask_at`: `escalate`

The default thresholds are 0.80 and 0.50. Invalid scores and inverted thresholds are rejected.

## Task 3 — Overconfidence
A case with self-reported confidence 0.99, agreement 0.20, failed validation, and zero evidence scores 0.218 and is escalated. A strongly supported case scores 0.985 and is acted on. Self-reported confidence alone does not override weak supporting signals.

## Task 4 — Calibration
The calibration script evaluates 20 labelled synthetic cases. The observed Brier score is **0.084**; lower values are better. Because the dataset is deliberately constructed, this score is not evidence of real-world calibration.

## Task 5 — Threshold Comparison
| Policy | Act threshold | Human threshold | Acted on | Wrong actions | Human review | Escalated |
|---|---:|---:|---:|---:|---:|---:|
| Permissive | 0.60 | 0.35 | 8 | 0 | 5 | 7 |
| Balanced | 0.80 | 0.50 | 4 | 0 | 6 | 10 |
| Conservative | 0.90 | 0.70 | 2 | 0 | 4 | 14 |

The implemented rule chooses the permissive policy because all three policies had zero incorrect actions in this synthetic dataset, and the permissive policy acted correctly on the most cases. This does not establish that permissive thresholds are safest in production.

## Validation Results
- Full regression suite: **27 passed**
- Calibration cases: **20**
- Brier score: **0.084**
- Threshold policies compared: **3**
- API key required: **No**
- Stretch task: **Not attempted**

## How to Run
Run from the project directory with the virtual environment activated:
```bat
python -m pytest tests\test_confidence_scoring.py -q
python src\confidence_scoring.py
python evidence\calibration_analysis.py
python evidence\threshold_comparison.py
python -m pytest -q
```

## Reflection (Approximately 300 Words)
This project helped me understand that a confidence score should represent the strength of supporting evidence rather than simply repeat how certain a model says it is. I implemented a weighted score using self-reported confidence, agreement between signals, validation status, and evidence count. Giving self-reported confidence only a 15 percent weight makes it less influential than the other signals. Input validation also matters because invalid probabilities, negative evidence counts, or incorrect data types could otherwise produce misleading decisions.

The routing function turns the score into an operational decision. High scores can be acted on, intermediate scores are sent to a human, and low scores are escalated. Testing values exactly at and just below the thresholds helped verify the boundary behavior. The overconfidence example was particularly useful: even with self-reported confidence of 0.99, weak agreement, failed validation, and no evidence led to a score of 0.218 and escalation.

I then evaluated 20 labelled examples using the Brier score. The score was 0.084 for this synthetic dataset. The Brier score measures the mean squared difference between a predicted probability and the observed binary outcome, with lower values indicating better probabilistic predictions. Because the examples were deliberately constructed, this result should not be interpreted as proof of real-world calibration.

Finally, I compared permissive, balanced, and conservative routing thresholds. Each policy produced zero incorrect actions on the selected dataset, but the permissive policy acted on more cases. This illustrates the trade-off between taking more actions and sending more cases for review or escalation. It also shows why threshold selection must be tested on representative data that includes difficult and incorrect high-confidence predictions. Overall, the assessment provided practical experience in scoring, routing, calibration measurement, deterministic testing, and evidence-based comparison. Future improvements could include larger representative datasets, calibration plots, and cost-sensitive evaluation that accounts for the different consequences of incorrect actions, human review, and escalation.
