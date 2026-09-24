import csv
from pathlib import Path

from vera.baselines import BaselineEvaluator
from vera.behavior_analyzer import BehaviorAnalyzer
from vera.executor import PatchExecutor
from vera.oracle_executor import OracleExecutor
from vera.patch_generator import PatchGenerator
from vera.repository import RepositoryAnalyzer
from vera.tasks import TASKS
from vera.verifier import PatchVerifier


RUNS_PER_TASK = 10
CANDIDATES_PER_RUN = 4

OUTPUT_DIR = Path("experiment_results")
OUTPUT_DIR.mkdir(exist_ok=True)

CSV_PATH = OUTPUT_DIR / "vera_experiment_results.csv"


def run_candidate(
    task,
    run_id,
    patch,
    repository,
    original_code,
    executor,
    oracle_executor,
    verifier,
    behavior_analyzer,
):
    execution_result = executor.execute(
        patch
    )

    behavior_result = (
        behavior_analyzer.analyze(
            patch
        )
    )

    verification_result = (
        verifier.verify(
            patch=patch,
            original_code=original_code,
            execution_result=execution_result,
            behavior_result=behavior_result,
            target_function=(
                task.target_function
            ),
        )
    )

    oracle_result = (
        oracle_executor.execute(
            patch
        )
    )

    baseline_a = (
        BaselineEvaluator
        .visible_tests_only(
            verification_result
        )
    )

    baseline_b = (
        BaselineEvaluator
        .visible_and_hidden_tests(
            verification_result
        )
    )

    vera_decision = (
        BaselineEvaluator
        .vera_decision(
            verification_result
        )
    )

    return {
        "run_id": run_id,
        "task_id": task.task_id,
        "candidate_id": (
            patch.candidate_id
        ),
        "file_path": (
            patch.file_path
        ),
        "explanation": (
            patch.explanation
        ),
        "patched_code": (
            patch.patched_code
        ),
        "visible_passed": (
            verification_result
            .tests_passed
        ),
        "visible_failed": (
            verification_result
            .tests_failed
        ),
        "hidden_passed": (
            verification_result
            .hidden_tests_passed
        ),
        "hidden_failed": (
            verification_result
            .hidden_tests_failed
        ),
        "behavior_passed": (
            verification_result
            .behavior_tests_passed
        ),
        "behavior_failed": (
            verification_result
            .behavior_tests_failed
        ),
        "behavior_score": (
            verification_result
            .behavior_preservation_score
        ),
        "change_risk_score": (
            verification_result
            .change_risk_score
        ),
        "syntax_valid": (
            verification_result
            .syntax_valid
        ),
        "changed_functions": (
            ",".join(
                verification_result
                .changed_functions
            )
        ),
        "unrelated_function_changes": (
            verification_result
            .unrelated_function_changes
        ),
        "lines_added": (
            verification_result
            .lines_added
        ),
        "lines_removed": (
            verification_result
            .lines_removed
        ),
        "vera_score": (
            verification_result
            .final_score
        ),
        "baseline_a": (
            baseline_a
        ),
        "baseline_b": (
            baseline_b
        ),
        "vera": (
            vera_decision
        ),
        "oracle_correct": (
            oracle_result[
                "correct"
            ]
        ),
        "oracle_passed": (
            oracle_result[
                "passed"
            ]
        ),
        "oracle_failed": (
            oracle_result[
                "failed"
            ]
        ),
    }


def calculate_metrics(
    rows,
    decision_key,
):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for row in rows:
        predicted = bool(
            row[
                decision_key
            ]
        )

        actual = bool(
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
        tp + fp + tn + fn
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

    false_acceptance_rate = (
        fp / (fp + tn)
        if fp + tn
        else 0.0
    )

    false_rejection_rate = (
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
        "false_acceptance_rate": (
            false_acceptance_rate
        ),
        "false_rejection_rate": (
            false_rejection_rate
        ),
    }


def print_metrics(
    name,
    metrics,
):
    print(
        "\n"
        + "=" * 70
    )

    print(
        name
    )

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
        f"{metrics['false_acceptance_rate']:.3f}"
    )

    print(
        f"False rejection rate: "
        f"{metrics['false_rejection_rate']:.3f}"
    )


def save_csv(
    rows,
):
    if not rows:
        return

    fieldnames = list(
        rows[0].keys()
    )

    with CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = (
            csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


def main():
    print(
        "=" * 70
    )

    print(
        "VERA-SE MULTI-RUN EXPERIMENT"
    )

    print(
        f"Tasks: {len(TASKS)}"
    )

    print(
        f"Runs per task: "
        f"{RUNS_PER_TASK}"
    )

    print(
        f"Candidates per run: "
        f"{CANDIDATES_PER_RUN}"
    )

    expected_candidates = (
        len(TASKS)
        * RUNS_PER_TASK
        * CANDIDATES_PER_RUN
    )

    print(
        f"Expected candidates: "
        f"{expected_candidates}"
    )

    print(
        "=" * 70
    )

    all_rows = []

    generator = PatchGenerator()

    for task in TASKS:
        print(
            "\n"
            + "#" * 70
        )

        print(
            f"TASK: {task.task_id}"
        )

        print(
            "#" * 70
        )

        repository = (
            RepositoryAnalyzer(
                task.repo_path
            )
        )

        context = (
            repository.build_context()
        )

        original_code = (
            repository.read_file(
                task.source_file
            )
        )

        executor = (
            PatchExecutor(
                repo_path=(
                    task.repo_path
                ),
                hidden_tests_path=(
                    task.hidden_tests_path
                ),
            )
        )

        oracle_executor = (
            OracleExecutor(
                repo_path=(
                    task.repo_path
                ),
                oracle_tests_path=(
                    task.oracle_tests_path
                ),
            )
        )

        verifier = (
            PatchVerifier()
        )

        behavior_analyzer = (
            BehaviorAnalyzer(
                task.task_id
            )
        )

        for run_id in range(
            1,
            RUNS_PER_TASK + 1,
        ):
            print(
                f"\nRun "
                f"{run_id}/"
                f"{RUNS_PER_TASK}"
            )

            try:
                patches = (
                    generator.generate(
                        task_id=(
                            task.task_id
                        ),
                        repository_context=(
                            context
                        ),
                        bug_description=(
                            task.bug_description
                        ),
                        candidate_count=(
                            CANDIDATES_PER_RUN
                        ),
                    )
                )

            except Exception as exc:
                print(
                    f"Generation failed: "
                    f"{exc}"
                )

                continue

            print(
                f"Generated "
                f"{len(patches)} "
                f"candidate(s)"
            )

            for patch_index, patch in enumerate(
                patches,
                start=1,
            ):
                print(
                    f"  Candidate "
                    f"{patch_index}/"
                    f"{len(patches)}"
                )

                try:
                    row = run_candidate(
                        task=task,
                        run_id=run_id,
                        patch=patch,
                        repository=repository,
                        original_code=(
                            original_code
                        ),
                        executor=executor,
                        oracle_executor=(
                            oracle_executor
                        ),
                        verifier=verifier,
                        behavior_analyzer=(
                            behavior_analyzer
                        ),
                    )

                    all_rows.append(
                        row
                    )

                except Exception as exc:
                    print(
                        f"    Candidate failed: "
                        f"{exc}"
                    )

            save_csv(
                all_rows
            )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "EXPERIMENT COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Candidates evaluated: "
        f"{len(all_rows)}"
    )

    print(
        f"Results saved to: "
        f"{CSV_PATH}"
    )

    baseline_a_metrics = (
        calculate_metrics(
            all_rows,
            "baseline_a",
        )
    )

    baseline_b_metrics = (
        calculate_metrics(
            all_rows,
            "baseline_b",
        )
    )

    vera_metrics = (
        calculate_metrics(
            all_rows,
            "vera",
        )
    )

    print_metrics(
        "BASELINE A - "
        "VISIBLE TESTS ONLY",
        baseline_a_metrics,
    )

    print_metrics(
        "BASELINE B - "
        "VISIBLE + HIDDEN TESTS",
        baseline_b_metrics,
    )

    print_metrics(
        "VERA-SE",
        vera_metrics,
    )


if __name__ == "__main__":
    main()