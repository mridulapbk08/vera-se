from vera.baselines import BaselineEvaluator
from vera.behavior_analyzer import BehaviorAnalyzer
from vera.evaluator import ExperimentEvaluator
from vera.executor import PatchExecutor
from vera.oracle_executor import OracleExecutor
from vera.patch_generator import PatchGenerator
from vera.repository import RepositoryAnalyzer
from vera.tasks import TASKS
from vera.verifier import PatchVerifier


def print_metrics(name, metrics):
    print(f"\n{name}")

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


def run_task(task):
    print(
        "\n"
        + "=" * 70
    )

    print(
        f"Running {task.task_id}"
    )

    print(
        "=" * 70
    )

    repository = RepositoryAnalyzer(
        task.repo_path
    )

    context = (
        repository.build_context()
    )

    original_code = (
        repository.read_file(
            task.source_file
        )
    )

    generator = PatchGenerator()

    patches = generator.generate(
        task_id=task.task_id,
        repository_context=context,
        bug_description=(
            task.bug_description
        ),
        candidate_count=4,
    )

    executor = PatchExecutor(
        repo_path=task.repo_path,
        hidden_tests_path=(
            task.hidden_tests_path
        ),
    )

    oracle_executor = OracleExecutor(
        repo_path=task.repo_path,
        oracle_tests_path=(
            task.oracle_tests_path
        ),
    )

    verifier = PatchVerifier()

    behavior_analyzer = (
        BehaviorAnalyzer(
            task.task_id
        )
    )

    results = []
    ground_truth = {}

    for patch in patches:
        print(
            f"\nCandidate "
            f"{patch.candidate_id}"
        )

        print("-" * 40)

        print(
            patch.explanation
        )

        # -----------------------------
        # Visible + hidden test execution
        # -----------------------------

        execution_result = (
            executor.execute(
                patch
            )
        )

        # -----------------------------
        # Behavior-preservation analysis
        # -----------------------------

        behavior_result = (
            behavior_analyzer.analyze(
                patch
            )
        )

        # -----------------------------
        # VERA verification
        # -----------------------------

        result = verifier.verify(
            patch=patch,
            original_code=(
                original_code
            ),
            execution_result=(
                execution_result
            ),
            behavior_result=(
                behavior_result
            ),
            target_function=(
                task.target_function
            ),
        )

        results.append(
            result
        )

        # -----------------------------
        # Held-out oracle evaluation
        # -----------------------------

        oracle_result = (
            oracle_executor.execute(
                patch
            )
        )

        ground_truth[
            patch.candidate_id
        ] = oracle_result[
            "correct"
        ]

        # -----------------------------
        # Baseline decisions
        # -----------------------------

        baseline_a = (
            BaselineEvaluator
            .visible_tests_only(
                result
            )
        )

        baseline_b = (
            BaselineEvaluator
            .visible_and_hidden_tests(
                result
            )
        )

        # -----------------------------
        # Candidate output
        # -----------------------------

        print(
            f"Visible tests: "
            f"{result.tests_passed} passed, "
            f"{result.tests_failed} failed"
        )

        print(
            f"Hidden tests: "
            f"{result.hidden_tests_passed} passed, "
            f"{result.hidden_tests_failed} failed"
        )

        print(
            f"Behavior probes: "
            f"{result.behavior_tests_passed} passed, "
            f"{result.behavior_tests_failed} failed"
        )

        print(
            f"Behavior preservation score: "
            f"{result.behavior_preservation_score:.3f}"
        )

        print(
            f"Changed functions: "
            f"{result.changed_functions}"
        )

        print(
            f"Unrelated changes: "
            f"{result.unrelated_function_changes}"
        )

        print(
            f"Syntax valid: "
            f"{result.syntax_valid}"
        )

        print(
            f"Change risk: "
            f"{result.change_risk_score:.3f}"
        )

        print(
            f"Lines added: "
            f"{result.lines_added}"
        )

        print(
            f"Lines removed: "
            f"{result.lines_removed}"
        )

        print(
            f"VERA score: "
            f"{result.final_score:.3f}"
        )

        print(
            f"Baseline A: "
            f"{baseline_a}"
        )

        print(
            f"Baseline B: "
            f"{baseline_b}"
        )

        print(
            f"VERA: "
            f"{result.accepted}"
        )

        print(
            f"Oracle tests: "
            f"{oracle_result['passed']} passed, "
            f"{oracle_result['failed']} failed"
        )

        print(
            f"GROUND TRUTH CORRECT: "
            f"{oracle_result['correct']}"
        )

    # -----------------------------
    # Evaluate methods against oracle
    # -----------------------------

    evaluator = ExperimentEvaluator(
        ground_truth
    )

    baseline_a_metrics = (
        evaluator.evaluate_method(
            results,
            BaselineEvaluator
            .visible_tests_only,
        )
    )

    baseline_b_metrics = (
        evaluator.evaluate_method(
            results,
            BaselineEvaluator
            .visible_and_hidden_tests,
        )
    )

    vera_metrics = (
        evaluator.evaluate_method(
            results,
            BaselineEvaluator
            .vera_decision,
        )
    )

    return {
        "task_id": task.task_id,
        "results": results,
        "ground_truth": ground_truth,
        "baseline_a": (
            baseline_a_metrics
        ),
        "baseline_b": (
            baseline_b_metrics
        ),
        "vera": (
            vera_metrics
        ),
    }


def aggregate_metrics(
    task_runs,
    key,
):
    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for run in task_runs:
        metrics = run[key]

        tp += metrics[
            "true_positive"
        ]

        fp += metrics[
            "false_positive"
        ]

        tn += metrics[
            "true_negative"
        ]

        fn += metrics[
            "false_negative"
        ]

    total = (
        tp
        + fp
        + tn
        + fn
    )

    accuracy = (
        (tp + tn) / total
        if total > 0
        else 0.0
    )

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0.0
    )

    false_acceptance_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0.0
    )

    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "false_acceptance_rate": (
            false_acceptance_rate
        ),
    }


def main():
    print(
        "=" * 70
    )

    print(
        "VERA-SE MULTI-BUG BENCHMARK"
    )

    print(
        "Behavior-Preservation + "
        "Held-Out Oracle Evaluation"
    )

    print(
        "=" * 70
    )

    task_runs = []

    for task in TASKS:
        run = run_task(
            task
        )

        task_runs.append(
            run
        )

    baseline_a = (
        aggregate_metrics(
            task_runs,
            "baseline_a",
        )
    )

    baseline_b = (
        aggregate_metrics(
            task_runs,
            "baseline_b",
        )
    )

    vera = (
        aggregate_metrics(
            task_runs,
            "vera",
        )
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "AGGREGATE BENCHMARK RESULTS"
    )

    print(
        "=" * 70
    )

    print_metrics(
        "Baseline A - "
        "Visible Tests Only",
        baseline_a,
    )

    print_metrics(
        "Baseline B - "
        "Visible + Hidden Tests",
        baseline_b,
    )

    print_metrics(
        "VERA-SE - "
        "Verification + Behavior Preservation",
        vera,
    )

    print(
        "\n"
        + "=" * 70
    )


if __name__ == "__main__":
    main()