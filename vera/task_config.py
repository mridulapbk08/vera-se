from dataclasses import dataclass


@dataclass
class BenchmarkTask:
    task_id: str
    repo_path: str
    hidden_tests_path: str
    oracle_tests_path: str
    source_file: str
    target_function: str
    bug_description: str