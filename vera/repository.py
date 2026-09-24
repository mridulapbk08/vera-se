from pathlib import Path


class RepositoryAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

        if not self.repo_path.exists():
            raise FileNotFoundError(
                f"Repository does not exist: {self.repo_path}"
            )

    def get_python_files(self) -> list[Path]:
        files = []

        for path in self.repo_path.rglob("*.py"):
            if "__pycache__" not in path.parts:
                files.append(path)

        return files

    def read_file(self, relative_path: str) -> str:
        path = self.repo_path / relative_path

        if not path.exists():
            raise FileNotFoundError(path)

        return path.read_text()

    def build_context(self) -> str:
        sections = []

        for path in self.get_python_files():
            relative = path.relative_to(self.repo_path)

            sections.append(
                f"FILE: {relative}\n\n"
                f"{path.read_text()}\n"
            )

        return "\n".join(sections)