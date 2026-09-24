from dataclasses import dataclass
from typing import Optional


@dataclass
class RealWorldTask:
    task_id: str
    repo_path: str
    source_file: str
    bug_description: str
    visible_test_command: list
    oracle_test_path: str

    repair_type: str = "function"

    target_function: Optional[str] = None

    region_start_line: Optional[int] = None
    region_end_line: Optional[int] = None