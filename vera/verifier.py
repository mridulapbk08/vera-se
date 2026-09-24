import difflib
import re

from vera.ast_analyzer import ASTAnalyzer
from vera.models import (
    CandidatePatch,
    VerificationResult,
)


class PatchVerifier:
    @staticmethod
    def calculate_diff_metrics(
        original: str,
        modified: str,
    ):
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        diff = list(
            difflib.unified_diff(
                original_lines,
                modified_lines,
            )
        )

        lines_added = 0
        lines_removed = 0

        for line in diff:
            if line.startswith("+++"):
                continue

            if line.startswith("---"):
                continue

            if line.startswith("+"):
                lines_added += 1

            elif line.startswith("-"):
                lines_removed += 1

        denominator = max(
            len(original_lines),
            1,
        )

        change_risk = (
            lines_added + lines_removed
        ) / denominator

        change_risk = min(
            change_risk,
            1.0,
        )

        return (
            lines_added,
            lines_removed,
            change_risk,
        )

    @staticmethod
    def parse_test_results(
        output: str,
    ):
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

    def verify(
        self,
        patch: CandidatePatch,
        original_code: str,
        execution_result: dict,
        behavior_result: dict,
        target_function: str,
    ) -> VerificationResult:

        syntax_valid = (
            ASTAnalyzer.parse_code(
                patch.patched_code
            )
            is not None
        )

        changed_functions = (
            ASTAnalyzer.changed_functions(
                original_code,
                patch.patched_code,
            )
        )

        unrelated_changes = [
            function_name
            for function_name in changed_functions
            if function_name != target_function
        ]

        (
            visible_passed,
            visible_failed,
        ) = self.parse_test_results(
            execution_result[
                "visible_stdout"
            ]
        )

        (
            hidden_passed,
            hidden_failed,
        ) = self.parse_test_results(
            execution_result[
                "hidden_stdout"
            ]
        )

        visible_total = (
            visible_passed
            + visible_failed
        )

        hidden_total = (
            hidden_passed
            + hidden_failed
        )

        if visible_total > 0:
            test_score = (
                visible_passed
                / visible_total
            )
        else:
            test_score = 0.0

        if hidden_total > 0:
            hidden_test_score = (
                hidden_passed
                / hidden_total
            )
        else:
            hidden_test_score = 0.0

        (
            lines_added,
            lines_removed,
            change_risk,
        ) = self.calculate_diff_metrics(
            original_code,
            patch.patched_code,
        )

        syntax_score = (
            1.0
            if syntax_valid
            else 0.0
        )

        behavior_score = (
            behavior_result[
                "score"
            ]
        )

        unrelated_penalty = min(
            len(
                unrelated_changes
            )
            * 0.15,
            0.30,
        )

        final_score = (
            0.25 * test_score
            + 0.30 * hidden_test_score
            + 0.25 * behavior_score
            + 0.10 * syntax_score
            + 0.10 * (
                1 - change_risk
            )
            - unrelated_penalty
        )

        final_score = max(
            0.0,
            min(
                final_score,
                1.0,
            ),
        )

        accepted = (
    execution_result[
        "visible_return_code"
    ] == 0
    and execution_result[
        "hidden_return_code"
    ] == 0
    and syntax_valid
    and target_function
    in changed_functions
    and len(
        unrelated_changes
    ) == 0
    and behavior_score >= 1.00
    and final_score >= 0.80
)

        return VerificationResult(
            candidate_id=(
                patch.candidate_id
            ),

            tests_passed=(
                visible_passed
            ),
            tests_failed=(
                visible_failed
            ),

            hidden_tests_passed=(
                hidden_passed
            ),
            hidden_tests_failed=(
                hidden_failed
            ),

            test_score=(
                test_score
            ),
            hidden_test_score=(
                hidden_test_score
            ),

            behavior_tests_passed=(
                behavior_result[
                    "passed"
                ]
            ),
            behavior_tests_failed=(
                behavior_result[
                    "failed"
                ]
            ),
            behavior_preservation_score=(
                behavior_score
            ),

            change_risk_score=(
                change_risk
            ),

            syntax_valid=(
                syntax_valid
            ),

            changed_functions=sorted(
                changed_functions
            ),

            unrelated_function_changes=(
                len(
                    unrelated_changes
                )
            ),

            lines_added=(
                lines_added
            ),
            lines_removed=(
                lines_removed
            ),

            final_score=(
                final_score
            ),

            accepted=(
                accepted
            ),

            stdout=execution_result[
                "visible_stdout"
            ],
            stderr=execution_result[
                "visible_stderr"
            ],
        )