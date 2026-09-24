import json
import subprocess
import sys
import tempfile
from pathlib import Path

from vera.models import CandidatePatch


class BehaviorAnalyzer:
    def __init__(self, task_id: str):
        self.task_id = task_id

    def _probe_code(self) -> str:
        if self.task_id == "task_1_percentage":
            return """
import json
from candidate import percentage

checks = []

try:
    checks.append(
        abs(
            percentage(2, 5) - 40.0
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        abs(
            percentage(-3, 8) - (-37.5)
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    result = percentage(11, 20)

    checks.append(
        isinstance(
            result,
            (int, float),
        )
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        if self.task_id == "task_2_string":
            return """
import json
from candidate import normalize_name

checks = []

try:
    checks.append(
        normalize_name(
            "  Mary  Jane  "
        )
        == "mary  jane"
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        normalize_name(
            "  Anne-Marie  "
        )
        == "anne-marie"
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        normalize_name(
            "  O'Neil  "
        )
        == "o'neil"
    )
except Exception:
    checks.append(False)

try:
    result = normalize_name(
        "Alice"
    )

    checks.append(
        isinstance(
            result,
            str,
        )
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        if self.task_id == "task_3_list":
            return """
import json
from candidate import last_item

checks = []

try:
    values = [
        5,
        6,
        7,
    ]

    result = last_item(
        values
    )

    checks.append(
        result == 7
    )

    checks.append(
        values == [
            5,
            6,
            7,
        ]
    )
except Exception:
    checks.extend(
        [
            False,
            False,
        ]
    )

try:
    checks.append(
        last_item(
            (
                "x",
                "y",
            )
        )
        == "y"
    )
except Exception:
    checks.append(False)

try:
    values = [
        1,
        2,
        3,
    ]

    first = last_item(
        values
    )

    second = last_item(
        values
    )

    checks.append(
        first == 3
        and second == 3
        and values
        == [
            1,
            2,
            3,
        ]
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        if self.task_id == "task_4_dict":
            return """
import json
from candidate import get_value

checks = []

try:
    data = {
        "name": "Alice",
        "age": 30,
    }

    original = data.copy()

    result = get_value(
        data,
        "name",
    )

    checks.append(
        result == "Alice"
    )

    checks.append(
        data == original
    )
except Exception:
    checks.extend(
        [
            False,
            False,
        ]
    )

try:
    data = {
        "x": 10,
    }

    original = data.copy()

    result = get_value(
        data,
        "missing",
        99,
    )

    checks.append(
        result == 99
    )

    checks.append(
        data == original
    )
except Exception:
    checks.extend(
        [
            False,
            False,
        ]
    )

try:
    data = {
        "key": "value",
    }

    first = get_value(
        data,
        "key",
    )

    second = get_value(
        data,
        "key",
    )

    checks.append(
        first == "value"
        and second == "value"
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        if self.task_id == "task_5_format":
            return """
import json
from candidate import clean_label

checks = []

try:
    checks.append(
        clean_label(
            "  Hello  World  "
        )
        == "hello  world"
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        clean_label(
            "  Version 2.0  "
        )
        == "version 2.0"
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        clean_label(
            "  Name: Alice  "
        )
        == "name: alice"
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        clean_label(
            "  Input/Output  "
        )
        == "input/output"
    )
except Exception:
    checks.append(False)

try:
    result = clean_label(
        "hello"
    )

    checks.append(
        isinstance(
            result,
            str,
        )
        and result == "hello"
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        if self.task_id == "task_6_numeric":
            return """
import json
from candidate import average

checks = []

try:
    checks.append(
        abs(
            average(1, 2) - 1.5
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        abs(
            average(-10, -20) - (-15)
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        abs(
            average(-5, 15) - 5
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    checks.append(
        abs(
            average(1.2, 2.8) - 2.0
        ) < 1e-9
    )
except Exception:
    checks.append(False)

try:
    result = average(
        1,
        3,
    )

    checks.append(
        isinstance(
            result,
            (int, float),
        )
        and abs(
            result - 2.0
        ) < 1e-9
    )
except Exception:
    checks.append(False)

print(
    json.dumps(checks)
)
"""

        raise ValueError(
            f"No behavior probes for "
            f"{self.task_id}"
        )

    def analyze(
        self,
        patch: CandidatePatch,
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(
                temp_dir
            )

            candidate_file = (
                temp_path
                / "candidate.py"
            )

            candidate_file.write_text(
                patch.patched_code
            )

            probe_file = (
                temp_path
                / "probe.py"
            )

            probe_file.write_text(
                self._probe_code()
            )

            try:
                result = subprocess.run(
                    [
                        sys.executable,
                        "probe.py",
                    ],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            except subprocess.TimeoutExpired:
                return {
                    "passed": 0,
                    "failed": 1,
                    "score": 0.0,
                }

            if result.returncode != 0:
                return {
                    "passed": 0,
                    "failed": 1,
                    "score": 0.0,
                }

            try:
                checks = json.loads(
                    result.stdout.strip()
                )

            except json.JSONDecodeError:
                return {
                    "passed": 0,
                    "failed": 1,
                    "score": 0.0,
                }

            passed = sum(
                1
                for check in checks
                if check is True
            )

            total = len(
                checks
            )

            failed = (
                total - passed
            )

            score = (
                passed / total
                if total > 0
                else 0.0
            )

            return {
                "passed": passed,
                "failed": failed,
                "score": score,
            }