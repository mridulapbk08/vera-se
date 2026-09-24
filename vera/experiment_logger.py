import json
from datetime import datetime
from pathlib import Path


class ExperimentLogger:
    def __init__(self, output_dir: str = "vera_runs"):
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_run(
        self,
        bug_description: str,
        results,
    ):
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_file = (
            self.output_dir
            / f"run_{timestamp}.json"
        )

        data = {
            "timestamp": timestamp,
            "bug_description": bug_description,
            "candidates": [],
        }

        for result in results:
            data["candidates"].append(
                {
                    "candidate_id": (
                        result.candidate_id
                    ),
                    "tests_passed": (
                        result.tests_passed
                    ),
                    "tests_failed": (
                        result.tests_failed
                    ),
                    "test_score": (
                        result.test_score
                    ),
                    "change_risk_score": (
                        result.change_risk_score
                    ),
                    "syntax_valid": (
                        result.syntax_valid
                    ),
                    "changed_functions": (
                        result.changed_functions
                    ),
                    "unrelated_function_changes": (
                        result.unrelated_function_changes
                    ),
                    "lines_added": (
                        result.lines_added
                    ),
                    "lines_removed": (
                        result.lines_removed
                    ),
                    "final_score": (
                        result.final_score
                    ),
                    "accepted": (
                        result.accepted
                    ),
                }
            )

        output_file.write_text(
            json.dumps(
                data,
                indent=2,
            )
        )

        return output_file