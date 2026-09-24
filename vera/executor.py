import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.models import CandidatePatch


class PatchExecutor:
    def __init__(
        self,
        repo_path: str,
        hidden_tests_path: str,
    ):
        self.repo_path = Path(
            repo_path
        ).resolve()

        self.hidden_tests_path = Path(
            hidden_tests_path
        ).resolve()

    def execute(
        self,
        patch: CandidatePatch,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_repo = Path(temp_dir) / "repo"

            shutil.copytree(
                self.repo_path,
                temp_repo,
            )

            target_file = (
                temp_repo
                / patch.file_path
            )

            if not target_file.exists():
                raise FileNotFoundError(
                    "Candidate attempted to modify "
                    "unknown file: "
                    f"{patch.file_path}"
                )

            target_file.write_text(
                patch.patched_code
            )

            visible_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "-q",
                ],
                cwd=temp_repo,
                capture_output=True,
                text=True,
                timeout=30,
            )

            hidden_files = list(
                self.hidden_tests_path.glob(
                    "test_*.py"
                )
            )

            for hidden_file in hidden_files:
                shutil.copy2(
                    hidden_file,
                    temp_repo / hidden_file.name,
                )

            hidden_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "-q",
                    *[
                        file.name
                        for file in hidden_files
                    ],
                ],
                cwd=temp_repo,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "visible_return_code": (
                    visible_result.returncode
                ),
                "visible_stdout": (
                    visible_result.stdout
                ),
                "visible_stderr": (
                    visible_result.stderr
                ),
                "hidden_return_code": (
                    hidden_result.returncode
                ),
                "hidden_stdout": (
                    hidden_result.stdout
                ),
                "hidden_stderr": (
                    hidden_result.stderr
                ),
            }