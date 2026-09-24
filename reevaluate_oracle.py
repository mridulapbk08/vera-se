import csv
import tempfile
import shutil
import subprocess
import re
from pathlib import Path

from vera.tasks import TASKS


INPUT_CSV = Path(
    "experiment_results/vera_experiment_results.csv"
)

OUTPUT_CSV = Path(
    "experiment_results/vera_experiment_results_rechecked.csv"
)


TASK_MAP = {
    task.task_id: task
    for task in TASKS
}


def parse_test_results(output):
    passed = 0
    failed = 0

    passed_match = re.search(
        r"(\d+) passed",
        output,
    )

    failed_match = re.search(
        r"(\d+) failed",
        output,
    )

    if passed_match:
        passed = int(
            passed_match.group(1)
        )

    if failed_match:
        failed = int(
            failed_match.group(1)
        )

    return passed, failed


def run_oracle(
    task,
    patched_code,
    file_path,
):
    repo_path = Path(
        task.repo_path
    ).resolve()

    oracle_path = Path(
        task.oracle_tests_path
    ).resolve()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_repo = (
            Path(temp_dir)
            / "repo"
        )

        shutil.copytree(
            repo_path,
            temp_repo,
        )

        target_file = (
            temp_repo
            / file_path
        )

        target_file.write_text(
            patched_code
        )

        oracle_files = list(
            oracle_path.glob(
                "test_*.py"
            )
        )

        if not oracle_files:
            raise RuntimeError(
                f"No oracle tests found for "
                f"{task.task_id}"
            )

        for oracle_file in oracle_files:
            shutil.copy2(
                oracle_file,
                temp_repo
                / oracle_file.name,
            )

        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "-q",
                *[
                    file.name
                    for file
                    in oracle_files
                ],
            ],
            cwd=temp_repo,
            capture_output=True,
            text=True,
            timeout=30,
        )

        passed, failed = (
            parse_test_results(
                result.stdout
            )
        )

        correct = (
            result.returncode == 0
            and failed == 0
            and passed > 0
        )

        return {
            "passed": passed,
            "failed": failed,
            "correct": correct,
        }


def as_bool(value):
    return (
        str(value)
        .strip()
        .lower()
        == "true"
    )


def calculate_metrics(
    rows,
    decision_key,
):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for row in rows:
        predicted = as_bool(
            row[
                decision_key
            ]
        )

        actual = as_bool(
            row[
                "oracle_correct"
            ]
        )

        if predicted and actual:
            tp += 1

        elif predicted and not actual:
            fp += 1

        elif (
            not predicted
            and not actual
        ):
            tn += 1

        else:
            fn += 1

    total = (
        tp
        + fp
        + tn
        + fn
    )

    accuracy = (
        (tp + tn) / total
        if total
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if tp + fp
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn
        else 0.0
    )

    far = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    frr = (
        fn / (fn + tp)
        if fn + tp
        else 0.0
    )

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "far": far,
        "frr": frr,
    }


def print_metrics(
    name,
    metrics,
):
    print(
        "\n"
        + "=" * 70
    )

    print(name)

    print(
        "=" * 70
    )

    print(
        f"TP: {metrics['tp']}"
    )

    print(
        f"FP: {metrics['fp']}"
    )

    print(
        f"TN: {metrics['tn']}"
    )

    print(
        f"FN: {metrics['fn']}"
    )

    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.3f}"
    )

    print(
        f"Precision: "
        f"{metrics['precision']:.3f}"
    )

    print(
        f"Recall: "
        f"{metrics['recall']:.3f}"
    )

    print(
        f"False acceptance rate: "
        f"{metrics['far']:.3f}"
    )

    print(
        f"False rejection rate: "
        f"{metrics['frr']:.3f}"
    )


def main():
    rows = []

    with INPUT_CSV.open(
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(
            csv_file
        )

        original_fieldnames = (
            reader.fieldnames
        )

        for index, row in enumerate(
            reader,
            start=1,
        ):
            task_id = row[
                "task_id"
            ]

            task = TASK_MAP[
                task_id
            ]

            oracle_result = (
                run_oracle(
                    task=task,
                    patched_code=(
                        row[
                            "patched_code"
                        ]
                    ),
                    file_path=(
                        row[
                            "file_path"
                        ]
                    ),
                )
            )

            old_correct = (
                row[
                    "oracle_correct"
                ]
            )

            row[
                "old_oracle_correct"
            ] = old_correct

            row[
                "oracle_correct"
            ] = str(
                oracle_result[
                    "correct"
                ]
            )

            row[
                "oracle_passed"
            ] = oracle_result[
                "passed"
            ]

            row[
                "oracle_failed"
            ] = oracle_result[
                "failed"
            ]

            rows.append(
                row
            )

            changed = (
                as_bool(old_correct)
                != oracle_result[
                    "correct"
                ]
            )

            marker = (
                "CHANGED"
                if changed
                else "same"
            )

            print(
                f"{index}/240 "
                f"{task_id} "
                f"run={row['run_id']} "
                f"candidate="
                f"{row['candidate_id']} "
                f"{marker}"
            )

    fieldnames = list(
        original_fieldnames
    )

    if (
        "old_oracle_correct"
        not in fieldnames
    ):
        fieldnames.append(
            "old_oracle_correct"
        )

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            rows
        )

    print(
        "\nRe-evaluation complete."
    )

    print(
        f"Saved to: {OUTPUT_CSV}"
    )

    baseline_a = (
        calculate_metrics(
            rows,
            "baseline_a",
        )
    )

    baseline_b = (
        calculate_metrics(
            rows,
            "baseline_b",
        )
    )

    vera = (
        calculate_metrics(
            rows,
            "vera",
        )
    )

    print_metrics(
        "BASELINE A",
        baseline_a,
    )

    print_metrics(
        "BASELINE B",
        baseline_b,
    )

    print_metrics(
        "VERA-SE",
        vera,
    )

    changed_rows = [
        row
        for row in rows
        if (
            as_bool(
                row[
                    "old_oracle_correct"
                ]
            )
            != as_bool(
                row[
                    "oracle_correct"
                ]
            )
        )
    ]

    print(
        "\n"
        + "=" * 70
    )

    print(
        "ORACLE LABELS CHANGED: "
        f"{len(changed_rows)}"
    )

    print(
        "=" * 70
    )

    for row in changed_rows:
        print(
            f"{row['task_id']} | "
            f"run {row['run_id']} | "
            f"candidate "
            f"{row['candidate_id']} | "
            f"{row['old_oracle_correct']} "
            f"-> "
            f"{row['oracle_correct']}"
        )


if __name__ == "__main__":
    main()