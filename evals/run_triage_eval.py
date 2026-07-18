"""
Runs the triage agent against the hand-labeled test cases and reports
accuracy, plus a breakdown of exactly which cases were misclassified.

Run with: python -m evals.run_triage_eval
"""

import time
from agents.triage_agent import triage_email
from evals.triage_test_cases import TEST_CASES


def run_eval():
    correct = 0
    failures = []

    for i, case in enumerate(TEST_CASES, start=1):
        result = triage_email(case["sender"], case["subject"], case["body"])
        is_correct = result.classification == case["expected"]

        status = "PASS" if is_correct else "FAIL"
        print(f"[{status}] #{i} {case['subject']!r}")
        print(f"       expected={case['expected']}  got={result.classification}  conf={result.confidence:.2f}")

        if is_correct:
            correct += 1
        else:
            failures.append({
                "subject": case["subject"],
                "expected": case["expected"],
                "got": result.classification,
                "reasoning": result.reasoning,
            })

        time.sleep(4.5)  # stay under free-tier 15 req/min limit

    total = len(TEST_CASES)
    accuracy = (correct / total) * 100

    print("\n" + "=" * 60)
    print(f"TRIAGE ACCURACY: {correct}/{total} ({accuracy:.1f}%)")
    print("=" * 60)

    if failures:
        print("\nFailure details:")
        for f in failures:
            print(f"  - {f['subject']!r}")
            print(f"    expected: {f['expected']}, got: {f['got']}")
            print(f"    model reasoning: {f['reasoning']}")


if __name__ == "__main__":
    run_eval()