from dataclasses import dataclass, field


@dataclass
class CandidatePatch:
    candidate_id: int
    file_path: str
    original_code: str
    patched_code: str
    explanation: str = ""


@dataclass
class VerificationResult:
    candidate_id: int

    tests_passed: int = 0
    tests_failed: int = 0

    hidden_tests_passed: int = 0
    hidden_tests_failed: int = 0

    test_score: float = 0.0
    hidden_test_score: float = 0.0

    behavior_tests_passed: int = 0
    behavior_tests_failed: int = 0
    behavior_preservation_score: float = 0.0

    change_risk_score: float = 0.0

    syntax_valid: bool = True

    changed_functions: list = field(
        default_factory=list
    )

    unrelated_function_changes: int = 0

    lines_added: int = 0
    lines_removed: int = 0

    final_score: float = 0.0

    accepted: bool = False

    stdout: str = ""
    stderr: str = ""

    metadata: dict = field(
        default_factory=dict
    )