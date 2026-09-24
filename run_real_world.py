import csv
import difflib
import hashlib
import os
from datetime import datetime
from pathlib import Path

from vera.real_world_executor import RealWorldExecutor
from vera.real_world_oracle_executor import RealWorldOracleExecutor
from vera.real_world_patch_generator import RealWorldPatchGenerator
from vera.real_world_region_patch_generator import (
    RealWorldRegionPatchGenerator,
)
from vera.real_world_tasks import REAL_WORLD_TASKS
from vera.real_world_verifier import RealWorldPatchVerifier


CANDIDATE_COUNT = 4

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RUN_ID = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)

RESULTS_CSV = (
    RESULTS_DIR
    / f"real_world_candidates_{RUN_ID}.csv"
)

TASK_SUMMARY_CSV = (
    RESULTS_DIR
    / f"real_world_task_summary_{RUN_ID}.csv"
)

PATCHES_DIR = (
    RESULTS_DIR
    / f"real_world_patches_{RUN_ID}"
)

PATCHES_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


CANDIDATE_FIELDS = [
    "run_id",
    "task_id",
    "repair_type",
    "source_file",
    "target_function",
    "region_start_line",
    "region_end_line",

    "requested_candidates",
    "valid_generated_candidates",

    "candidate_id",
    "explanation",

    "patched_code_file",
    "diff_file",
    "patched_code_sha256",

    "visible_passed",
    "visible_return_code",

    "syntax_valid",
    "target_changed",
    "scope_preserved",
    "changed_functions",
    "unrelated_function_changes",

    "lines_added",
    "lines_removed",
    "scope_lines",
    "change_risk_score",

    "vera_score",
    "vera_accept",

    "oracle_passed",
    "oracle_failed",
    "oracle_correct",

    "baseline_a_accept",
    "baseline_a_false_acceptance",
    "baseline_a_false_rejection",

    "vera_false_acceptance",
    "vera_false_rejection",
]


TASK_SUMMARY_FIELDS = [
    "run_id",
    "task_id",
    "repair_type",

    "requested_candidates",
    "valid_generated_candidates",
    "generation_complete",

    "visible_accepted",
    "vera_accepted",
    "oracle_correct",

    "baseline_a_false_acceptances",
    "baseline_a_false_rejections",

    "vera_false_acceptances",
    "vera_false_rejections",

    "vera_selected_candidate_id",
    "vera_selected_score",
]


def initialize_csv(
    path: Path,
    fieldnames,
):
    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()


def append_csv_row(
    path: Path,
    fieldnames,
    row,
):
    with path.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writerow(
            row
        )


def main():
    initialize_csv(
        RESULTS_CSV,
        CANDIDATE_FIELDS,
    )

    initialize_csv(
        TASK_SUMMARY_CSV,
        TASK_SUMMARY_FIELDS,
    )

    verifier = (
        RealWorldPatchVerifier()
    )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "VERA-SE REAL-WORLD EXPERIMENT"
    )

    print(
        "=" * 70
    )

    print(
        f"Run ID: {RUN_ID}"
    )

    print(
        f"Candidate results: "
        f"{RESULTS_CSV}"
    )

    print(
        f"Task summary: "
        f"{TASK_SUMMARY_CSV}"
    )

    start_task_id = os.environ.get(
        "VERA_START_TASK_ID"
    )

    tasks_to_run = list(
        REAL_WORLD_TASKS
    )

    if start_task_id:
        task_ids = [
            task.task_id
            for task in tasks_to_run
        ]

        if start_task_id not in task_ids:
            raise RuntimeError(
                f"Unknown VERA_START_TASK_ID: "
                f"{start_task_id}"
            )

        start_index = task_ids.index(
            start_task_id
        )

        tasks_to_run = (
            tasks_to_run[start_index:]
        )

        print(
            f"\nRESUME MODE: starting from "
            f"{start_task_id}"
        )

    for task in tasks_to_run:
        print(
            "\n"
            + "=" * 70
        )

        print(
            f"REAL-WORLD TASK: "
            f"{task.task_id}"
        )

        print(
            "=" * 70
        )

        executor = RealWorldExecutor(
            repo_path=task.repo_path,
            visible_test_command=(
                task.visible_test_command
            ),
        )

        oracle_executor = (
            RealWorldOracleExecutor(
                repo_path=task.repo_path,
                oracle_test_path=(
                    task.oracle_test_path
                ),
            )
        )

        # ====================================================
        # Candidate generation
        # ====================================================

        if task.repair_type == "function":
            generator = (
                RealWorldPatchGenerator()
            )

            patches = generator.generate(
                task_id=task.task_id,
                repo_path=task.repo_path,
                source_file=task.source_file,
                target_function=(
                    task.target_function
                ),
                bug_description=(
                    task.bug_description
                ),
                candidate_count=(
                    CANDIDATE_COUNT
                ),
            )

        elif task.repair_type == "region":
            generator = (
                RealWorldRegionPatchGenerator()
            )

            patches = generator.generate(
                task_id=task.task_id,
                repo_path=task.repo_path,
                source_file=task.source_file,
                bug_description=(
                    task.bug_description
                ),
                region_start_line=(
                    task.region_start_line
                ),
                region_end_line=(
                    task.region_end_line
                ),
                candidate_count=(
                    CANDIDATE_COUNT
                ),
            )

        else:
            raise ValueError(
                f"Unknown repair type: "
                f"{task.repair_type}"
            )

        valid_candidate_count = len(
            patches
        )

        generation_complete = (
            valid_candidate_count
            == CANDIDATE_COUNT
        )

        print(
            f"\nRequested: "
            f"{CANDIDATE_COUNT}"
        )

        print(
            f"Valid generated: "
            f"{valid_candidate_count}"
        )

        # ====================================================
        # Task counters
        # ====================================================

        visible_accepted_count = 0
        vera_accepted_count = 0
        oracle_correct_count = 0

        baseline_false_acceptance_count = 0
        baseline_false_rejection_count = 0

        vera_false_acceptance_count = 0
        vera_false_rejection_count = 0

        verifier_results = []

        # ====================================================
        # Evaluate candidates
        # ====================================================

        for patch in patches:
            print(
                "\n"
                + "-" * 70
            )

            print(
                f"Candidate "
                f"{patch.candidate_id}"
            )

            print(
                "-" * 70
            )

            print(
                patch.explanation
            )

            # =================================================
            # 1. Triggering test
            # =================================================

            visible_result = (
                executor.execute(
                    patch
                )
            )

            visible_passed = (
                visible_result[
                    "return_code"
                ]
                == 0
            )

            if visible_passed:
                visible_accepted_count += 1

            print(
                "\nVisible triggering test:"
            )

            print(
                f"PASS: "
                f"{visible_passed}"
            )

            # =================================================
            # 2. VERA verification
            #
            # IMPORTANT:
            # This happens BEFORE oracle execution.
            # =================================================

            verification = (
                verifier.verify(
                    patch=patch,
                    visible_result=(
                        visible_result
                    ),
                    repair_type=(
                        task.repair_type
                    ),
                    target_function=(
                        task.target_function
                    ),
                    region_start_line=(
                        task.region_start_line
                    ),
                    region_end_line=(
                        task.region_end_line
                    ),
                )
            )

            verifier_results.append(
                verification
            )

            vera_accept = (
                verification.accepted
            )

            if vera_accept:
                vera_accepted_count += 1

            print(
                "\nVERA verification:"
            )

            print(
                f"Syntax valid: "
                f"{verification.syntax_valid}"
            )

            print(
                f"Target changed: "
                f"{verification.target_changed}"
            )

            print(
                f"Scope preserved: "
                f"{verification.scope_preserved}"
            )

            print(
                f"Change risk: "
                f"{verification.change_risk_score:.3f}"
            )

            print(
                f"VERA score: "
                f"{verification.vera_score:.3f}"
            )

            print(
                f"VERA ACCEPT: "
                f"{vera_accept}"
            )

            # =================================================
            # 3. Held-out oracle
            #
            # Evaluation only.
            # The decision above is already frozen.
            # =================================================

            oracle_result = (
                oracle_executor.execute(
                    patch
                )
            )

            oracle_correct = bool(
                oracle_result[
                    "correct"
                ]
            )

            if oracle_correct:
                oracle_correct_count += 1

            print(
                "\nHeld-out oracle:"
            )

            print(
                f"Passed: "
                f"{oracle_result['passed']}"
            )

            print(
                f"Failed: "
                f"{oracle_result['failed']}"
            )

            print(
                f"ORACLE-LABELED CORRECT: "
                f"{oracle_correct}"
            )

            # =================================================
            # Baseline A
            # =================================================

            baseline_a = (
                visible_passed
            )

            baseline_false_acceptance = (
                baseline_a
                and not oracle_correct
            )

            baseline_false_rejection = (
                not baseline_a
                and oracle_correct
            )

            if baseline_false_acceptance:
                baseline_false_acceptance_count += 1

            if baseline_false_rejection:
                baseline_false_rejection_count += 1

            # =================================================
            # VERA diagnostics
            # =================================================

            vera_false_acceptance = (
                vera_accept
                and not oracle_correct
            )

            vera_false_rejection = (
                not vera_accept
                and oracle_correct
            )

            if vera_false_acceptance:
                vera_false_acceptance_count += 1

            if vera_false_rejection:
                vera_false_rejection_count += 1

            if baseline_false_acceptance:
                print(
                    ">>> FALSE ACCEPTANCE "
                    "BY VISIBLE BASELINE"
                )

            if vera_false_acceptance:
                print(
                    ">>> FALSE ACCEPTANCE "
                    "BY VERA"
                )

            if vera_false_rejection:
                print(
                    ">>> FALSE REJECTION "
                    "BY VERA"
                )

            # =================================================
            # Save exact candidate patch immediately
            #
            # Reproducibility logging only.
            # This does NOT affect generation or verification.
            # =================================================

            safe_task_id = (
                task.task_id
                .replace("/", "_")
                .replace("\\", "_")
            )

            candidate_stem = (
                f"{safe_task_id}"
                f"_candidate_{patch.candidate_id}"
            )

            patched_code_path = (
                PATCHES_DIR
                / f"{candidate_stem}.patched.py"
            )

            diff_path = (
                PATCHES_DIR
                / f"{candidate_stem}.diff"
            )

            patched_code_path.write_text(
                patch.patched_code,
                encoding="utf-8",
            )

            unified_diff = "".join(
                difflib.unified_diff(
                    patch.original_code.splitlines(
                        keepends=True
                    ),
                    patch.patched_code.splitlines(
                        keepends=True
                    ),
                    fromfile=(
                        f"a/{patch.file_path}"
                    ),
                    tofile=(
                        f"b/{patch.file_path}"
                    ),
                )
            )

            diff_path.write_text(
                unified_diff,
                encoding="utf-8",
            )

            patched_code_sha256 = (
                hashlib.sha256(
                    patch.patched_code.encode(
                        "utf-8"
                    )
                )
                .hexdigest()
            )

            # =================================================
            # Save candidate result immediately
            # =================================================

            row = {
                "run_id": RUN_ID,
                "task_id": (
                    task.task_id
                ),
                "repair_type": (
                    task.repair_type
                ),
                "source_file": (
                    task.source_file
                ),
                "target_function": (
                    task.target_function
                    or ""
                ),
                "region_start_line": (
                    task.region_start_line
                    or ""
                ),
                "region_end_line": (
                    task.region_end_line
                    or ""
                ),

                "requested_candidates": (
                    CANDIDATE_COUNT
                ),
                "valid_generated_candidates": (
                    valid_candidate_count
                ),

                "candidate_id": (
                    patch.candidate_id
                ),
                "explanation": (
                    patch.explanation
                ),

                "patched_code_file": (
                    str(
                        patched_code_path
                    )
                ),
                "diff_file": (
                    str(
                        diff_path
                    )
                ),
                "patched_code_sha256": (
                    patched_code_sha256
                ),

                "visible_passed": (
                    visible_passed
                ),
                "visible_return_code": (
                    visible_result[
                        "return_code"
                    ]
                ),

                "syntax_valid": (
                    verification.syntax_valid
                ),
                "target_changed": (
                    verification.target_changed
                ),
                "scope_preserved": (
                    verification.scope_preserved
                ),
                "changed_functions": (
                    "|".join(
                        verification.changed_functions
                    )
                ),
                "unrelated_function_changes": (
                    verification
                    .unrelated_function_changes
                ),

                "lines_added": (
                    verification.lines_added
                ),
                "lines_removed": (
                    verification.lines_removed
                ),
                "scope_lines": (
                    verification.scope_lines
                ),
                "change_risk_score": (
                    verification
                    .change_risk_score
                ),

                "vera_score": (
                    verification.vera_score
                ),
                "vera_accept": (
                    vera_accept
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
                "oracle_correct": (
                    oracle_correct
                ),

                "baseline_a_accept": (
                    baseline_a
                ),
                "baseline_a_false_acceptance": (
                    baseline_false_acceptance
                ),
                "baseline_a_false_rejection": (
                    baseline_false_rejection
                ),

                "vera_false_acceptance": (
                    vera_false_acceptance
                ),
                "vera_false_rejection": (
                    vera_false_rejection
                ),
            }

            append_csv_row(
                RESULTS_CSV,
                CANDIDATE_FIELDS,
                row,
            )

            print(
                "\nSaved candidate result."
            )

            if not visible_passed:
                print(
                    "\nVisible test stderr:"
                )

                print(
                    visible_result[
                        "stderr"
                    ]
                )

            if not oracle_correct:
                print(
                    "\nOracle output:"
                )

                print(
                    oracle_result[
                        "stdout"
                    ]
                )

                print(
                    oracle_result[
                        "stderr"
                    ]
                )

        # ====================================================
        # Select best VERA candidate
        #
        # Uses verifier evidence ONLY.
        # Oracle labels are not used for selection.
        # ====================================================

        eligible = [
            result
            for result
            in verifier_results
            if result.accepted
        ]

        selected_candidate_id = ""
        selected_score = ""

        if eligible:
            selected = max(
                eligible,
                key=lambda result: (
                    result.vera_score,
                    -result.change_risk_score,
                ),
            )

            selected_candidate_id = (
                selected.candidate_id
            )

            selected_score = (
                selected.vera_score
            )

        # ====================================================
        # Task summary
        # ====================================================

        summary = {
            "run_id": RUN_ID,
            "task_id": (
                task.task_id
            ),
            "repair_type": (
                task.repair_type
            ),

            "requested_candidates": (
                CANDIDATE_COUNT
            ),
            "valid_generated_candidates": (
                valid_candidate_count
            ),
            "generation_complete": (
                generation_complete
            ),

            "visible_accepted": (
                visible_accepted_count
            ),
            "vera_accepted": (
                vera_accepted_count
            ),
            "oracle_correct": (
                oracle_correct_count
            ),

            "baseline_a_false_acceptances": (
                baseline_false_acceptance_count
            ),
            "baseline_a_false_rejections": (
                baseline_false_rejection_count
            ),

            "vera_false_acceptances": (
                vera_false_acceptance_count
            ),
            "vera_false_rejections": (
                vera_false_rejection_count
            ),

            "vera_selected_candidate_id": (
                selected_candidate_id
            ),
            "vera_selected_score": (
                selected_score
            ),
        }

        append_csv_row(
            TASK_SUMMARY_CSV,
            TASK_SUMMARY_FIELDS,
            summary,
        )

        print(
            "\nTASK SUMMARY"
        )

        print(
            f"Valid candidates: "
            f"{valid_candidate_count}/"
            f"{CANDIDATE_COUNT}"
        )

        print(
            f"Visible accepted: "
            f"{visible_accepted_count}"
        )

        print(
            f"VERA accepted: "
            f"{vera_accepted_count}"
        )

        print(
            f"Oracle correct: "
            f"{oracle_correct_count}"
        )

        print(
            f"Baseline false acceptances: "
            f"{baseline_false_acceptance_count}"
        )

        print(
            f"VERA false acceptances: "
            f"{vera_false_acceptance_count}"
        )

        print(
            f"VERA false rejections: "
            f"{vera_false_rejection_count}"
        )

        print(
            f"VERA selected candidate: "
            f"{selected_candidate_id}"
        )

    print(
        "\n"
        + "=" * 70
    )

    print(
        "REAL-WORLD EXPERIMENT COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"\nCandidate CSV:\n"
        f"{RESULTS_CSV}"
    )

    print(
        f"\nTask summary CSV:\n"
        f"{TASK_SUMMARY_CSV}"
    )


if __name__ == "__main__":
    main()
