import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.models import CandidatePatch


class OracleExecutor:
    def __init__(
        self,
        repo_path: str,
        oracle_tests_path: str,
    ):
        self.repo_path = Path(
            repo_path
        ).resolve()

        self.oracle_tests_path = Path(
            oracle_tests_path
        ).resolve()

    @staticmethod
    def _parse_test_results(output: str):
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

    def execute(
        self,
        patch: CandidatePatch,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo = (
                Path(temp_dir)
                / "repo"
            )

            shutil.copytree(
                self.repo_path,
                temp_repo,
            )

            target_file = (
                temp_repo
                / patch.file_path
            )

            if not target_file.exists():
                return {
                    "passed": 0,
                    "failed": 1,
                    "correct": False,
                    "stdout": "",
                    "stderr": (
                        "Patch modified an "
                        "unknown source file."
                    ),
                }

            target_file.write_text(
                patch.patched_code
            )

            oracle_files = list(
                self.oracle_tests_path.glob(
                    "test_*.py"
                )
            )

            if not oracle_files:
                raise RuntimeError(
                    "No oracle tests found in "
                    f"{self.oracle_tests_path}"
                )

            for oracle_file in oracle_files:
                shutil.copy2(
                    oracle_file,
                    temp_repo / oracle_file.name,
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
                self._parse_test_results(
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
                "stdout": result.stdout,
                "stderr": result.stderr,
            }