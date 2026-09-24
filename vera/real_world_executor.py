import shutil
import subprocess
import tempfile
from pathlib import Path

from vera.models import CandidatePatch


class RealWorldExecutor:
    def __init__(
        self,
        repo_path: str,
        visible_test_command: list,
    ):
        self.repo_path = Path(
            repo_path
        ).resolve()

        self.visible_test_command = (
            visible_test_command
        )

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

            env_python = (
                self._get_python()
            )

            command = list(
                self.visible_test_command
            )

            if (
                command
                and command[0] == "python"
            ):
                command[0] = str(
                    env_python
                )

            env = {
                **dict(
                    __import__("os").environ
                ),
                "PYTHONPATH": str(
                    temp_repo
                ),
            }

            result = subprocess.run(
                command,
                cwd=temp_repo,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )

            return {
                "return_code": (
                    result.returncode
                ),
                "stdout": (
                    result.stdout
                ),
                "stderr": (
                    result.stderr
                ),
            }