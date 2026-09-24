import ast
import difflib
from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from vera.ast_analyzer import ASTAnalyzer
from vera.models import CandidatePatch


@dataclass
class RealWorldVerificationResult:
    candidate_id: int

    visible_passed: bool

    syntax_valid: bool

    target_changed: bool
    scope_preserved: bool

    changed_functions: List[str]
    unrelated_function_changes: int

    lines_added: int
    lines_removed: int

    scope_lines: int
    change_risk_score: float

    vera_score: float
    accepted: bool


class RealWorldPatchVerifier:
    """
    Verification used for the real-world BugsInPy phase.

    IMPORTANT:
    This verifier must never use the held-out oracle.

    The oracle is evaluation-only and is executed after this verifier
    has made its decision.
    """

    MAX_CHANGE_RISK = 0.50

    @staticmethod
    def _syntax_valid(code: str) -> bool:
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    @staticmethod
    def _diff_metrics(
        original: str,
        modified: str,
    ) -> Tuple[int, int]:
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
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

        return lines_added, lines_removed

    @staticmethod
    def _function_line_count(
        code: str,
        target_function: str,
    ) -> int:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return 1

        for node in ast.walk(tree):
            if (
                isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and node.name == target_function
            ):
                start = getattr(
                    node,
                    "lineno",
                    1,
                )

                end = getattr(
                    node,
                    "end_lineno",
                    start,
                )

                return max(
                    end - start + 1,
                    1,
                )

        return 1

    @staticmethod
    def _region_scope_preserved(
        original: str,
        modified: str,
        region_start_line: int,
        region_end_line: int,
    ) -> Tuple[bool, bool]:
        """
        Check whether modifications are restricted to the requested
        original-code region.

        Returns:
            scope_preserved
            target_changed
        """

        original_lines = original.splitlines()
        modified_lines = modified.splitlines()

        matcher = difflib.SequenceMatcher(
            a=original_lines,
            b=modified_lines,
        )

        start_index = region_start_line - 1
        end_index = region_end_line

        target_changed = False
        scope_preserved = True

        for (
            tag,
            i1,
            i2,
            j1,
            j2,
        ) in matcher.get_opcodes():
            if tag == "equal":
                continue

            # Insertions have no consumed original lines.
            if tag == "insert":
                insertion_point = i1

                if (
                    start_index
                    <= insertion_point
                    <= end_index
                ):
                    target_changed = True
                else:
                    scope_preserved = False

                continue

            # replace/delete consume original-code lines.
            overlaps_region = (
                i1 < end_index
                and i2 > start_index
            )

            fully_inside_region = (
                i1 >= start_index
                and i2 <= end_index
            )

            if overlaps_region:
                target_changed = True

            if not fully_inside_region:
                scope_preserved = False

        return (
            scope_preserved,
            target_changed,
        )

    def verify(
        self,
        patch: CandidatePatch,
        visible_result: dict,
        repair_type: str,
        target_function: Optional[str] = None,
        region_start_line: Optional[int] = None,
        region_end_line: Optional[int] = None,
    ) -> RealWorldVerificationResult:

        original_code = patch.original_code
        patched_code = patch.patched_code

        visible_passed = (
            visible_result["return_code"]
            == 0
        )

        syntax_valid = self._syntax_valid(
            patched_code
        )

        (
            lines_added,
            lines_removed,
        ) = self._diff_metrics(
            original_code,
            patched_code,
        )

        changed_functions: Set[str] = set()

        unrelated_function_changes = 0

        target_changed = False
        scope_preserved = False
        scope_lines = 1

        # ====================================================
        # Function-level repair
        # ====================================================

        if repair_type == "function":
            if target_function is None:
                raise ValueError(
                    "target_function is required "
                    "for function repair"
                )

            changed_functions = (
                ASTAnalyzer.changed_functions(
                    original_code,
                    patched_code,
                )
            )

            target_changed = (
                target_function
                in changed_functions
            )

            unrelated = {
                name
                for name in changed_functions
                if name != target_function
            }

            unrelated_function_changes = len(
                unrelated
            )

            scope_preserved = (
                unrelated_function_changes
                == 0
            )

            scope_lines = (
                self._function_line_count(
                    original_code,
                    target_function,
                )
            )

        # ====================================================
        # Region-level repair
        # ====================================================

        elif repair_type == "region":
            if (
                region_start_line is None
                or region_end_line is None
            ):
                raise ValueError(
                    "region line numbers are required "
                    "for region repair"
                )

            (
                scope_preserved,
                target_changed,
            ) = self._region_scope_preserved(
                original_code,
                patched_code,
                region_start_line,
                region_end_line,
            )

            scope_lines = max(
                region_end_line
                - region_start_line
                + 1,
                1,
            )

        else:
            raise ValueError(
                f"Unknown repair type: "
                f"{repair_type}"
            )

        # ====================================================
        # Risk
        # ====================================================

        changed_lines = (
            lines_added
            + lines_removed
        )

        change_risk = (
            changed_lines
            / max(
                scope_lines,
                1,
            )
        )

        change_risk = min(
            change_risk,
            1.0,
        )

        # ====================================================
        # Risk-aware ranking score
        #
        # This score is for ranking/evidence.
        # Acceptance itself is determined by explicit gates below.
        # ====================================================

        vera_score = (
            0.45
            * (
                1.0
                if visible_passed
                else 0.0
            )
            + 0.15
            * (
                1.0
                if syntax_valid
                else 0.0
            )
            + 0.15
            * (
                1.0
                if scope_preserved
                else 0.0
            )
            + 0.10
            * (
                1.0
                if target_changed
                else 0.0
            )
            + 0.15
            * (
                1.0
                - change_risk
            )
        )

        vera_score = max(
            0.0,
            min(
                vera_score,
                1.0,
            ),
        )

        # ====================================================
        # VERA decision
        #
        # These gates are evaluated BEFORE the oracle.
        # ====================================================

        accepted = (
            visible_passed
            and syntax_valid
            and target_changed
            and scope_preserved
            and change_risk
            <= self.MAX_CHANGE_RISK
        )

        return RealWorldVerificationResult(
            candidate_id=patch.candidate_id,

            visible_passed=visible_passed,

            syntax_valid=syntax_valid,

            target_changed=target_changed,
            scope_preserved=scope_preserved,

            changed_functions=sorted(
                changed_functions
            ),

            unrelated_function_changes=(
                unrelated_function_changes
            ),

            lines_added=lines_added,
            lines_removed=lines_removed,

            scope_lines=scope_lines,
            change_risk_score=change_risk,

            vera_score=vera_score,
            accepted=accepted,
        )
