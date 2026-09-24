import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.models import CandidatePatch


class RealWorldOracleExecutor:
    def __init__(
        self,
        repo_path: str,
        oracle_test_path: str,
    ):
        self.repo_path = Path(
            repo_path
        ).resolve()

        self.oracle_test_path = Path(
            oracle_test_path
        ).resolve()

    def _get_python(self) -> Path:
        local_env = (
            self.repo_path
            / "env"
            / "bin"
            / "python"
        )

        if local_env.exists():
            return local_env

        shared_black_env = Path(
            "/Users/mridulaprabhakar/"
            "bugsinpy-work/black-1/black/"
            "env/bin/python"
        )

        if shared_black_env.exists():
            return shared_black_env

        raise RuntimeError(
            "No usable Python environment found."
        )

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
                ignore=shutil.ignore_patterns(
                    ".git",
                    "env",
                    "__pycache__",
                    ".pytest_cache",
                    ".mypy_cache",
                    ".tox",
                    "docs",
                ),
                symlinks=True,
                ignore_dangling_symlinks=True,
            )

            target_file = (
                temp_repo
                / patch.file_path
            )

            if not target_file.exists():
                return {
                    "return_code": 1,
                    "passed": 0,
                    "failed": 1,
                    "correct": False,
                    "stdout": "",
                    "stderr": (
                        "Target file does not exist: "
                        f"{patch.file_path}"
                    ),
                }

            target_file.write_text(
                patch.patched_code,
                encoding="utf-8",
            )

            if not self.oracle_test_path.exists():
                raise RuntimeError(
                    "Oracle file not found: "
                    f"{self.oracle_test_path}"
                )

            oracle_copy = (
                temp_repo
                / "test_vera_oracle.py"
            )

            shutil.copy2(
                self.oracle_test_path,
                oracle_copy,
            )

            env_python = (
                self._get_python()
            )

            env = {
                **os.environ,
                "PYTHONPATH": str(
                    temp_repo
                ),
            }

            result = subprocess.run(
                [
                    str(env_python),
                    "-m",
                    "pytest",
                    "-q",
                    "test_vera_oracle.py",
                ],
                cwd=temp_repo,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

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

            correct = (
                result.returncode == 0
                and passed > 0
                and failed == 0
            )

            return {
                "return_code": (
                    result.returncode
                ),
                "passed": passed,
                "failed": failed,
                "correct": correct,
                "stdout": (
                    result.stdout
                ),
                "stderr": (
                    result.stderr
                ),
            }