import json
import socket
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path

from vera.models import CandidatePatch


class RealWorldRegionPatchGenerator:
    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        ollama_url: str = "http://localhost:11434/api/generate",
        timeout: int = 180,
        max_retries: int = 2,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.timeout = timeout
        self.max_retries = max_retries

    def _call_ollama(
        self,
        prompt: str,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
            },
        }

        request = urllib.request.Request(
            self.ollama_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        last_error = None

        for attempt in range(
            1,
            self.max_retries + 2,
        ):
            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout,
                ) as response:
                    body = json.loads(
                        response.read().decode("utf-8")
                    )

                return body["response"].strip()

            except (
                TimeoutError,
                socket.timeout,
                urllib.error.URLError,
            ) as exc:
                last_error = exc

                print(
                    "\nOllama request failed "
                    f"(attempt {attempt}/"
                    f"{self.max_retries + 1}): "
                    f"{exc}"
                )

                if attempt <= self.max_retries:
                    print("Retrying Ollama request...")
                    time.sleep(2)

        raise RuntimeError(
            "Ollama generation failed after "
            f"{self.max_retries + 1} attempts."
        ) from last_error

    def _clean_response(
        self,
        response: str,
    ) -> str:
        response = response.strip()

        if response.startswith("```python"):
            response = response[len("```python"):]

        elif response.startswith("```py"):
            response = response[len("```py"):]

        elif response.startswith("```"):
            response = response[3:]

        if response.rstrip().endswith("```"):
            response = response.rstrip()[:-3]

        response = response.replace(
            "--- TARGET REGION ---",
            "",
        )

        response = response.replace(
            "--- END TARGET REGION ---",
            "",
        )

        response = response.replace(
            "--- CONTEXT ---",
            "",
        )

        response = response.replace(
            "--- END CONTEXT ---",
            "",
        )

        prefixes = [
            "Replacement:",
            "REPLACEMENT:",
            "Fixed code:",
            "FIXED CODE:",
            "Candidate:",
            "CANDIDATE:",
        ]

        stripped = response.lstrip()

        for prefix in prefixes:
            if stripped.startswith(prefix):
                stripped = stripped[
                    len(prefix):
                ].lstrip()
                break

        response = stripped

        main_markers = [
            "\ndef main(",
            "\n\ndef main(",
        ]

        for marker in main_markers:
            if marker in response:
                response = response.split(
                    marker,
                    1,
                )[0].rstrip()
                break

        return response.strip()

    def _get_original_indent(
        self,
        original_region: str,
    ) -> str:
        for line in original_region.splitlines():
            if line.strip():
                return line[
                    :len(line) - len(line.lstrip())
                ]

        return ""

    def _preserve_indentation(
        self,
        patched_region: str,
        original_region: str,
    ) -> str:
        original_indent = (
            self._get_original_indent(
                original_region
            )
        )

        dedented = textwrap.dedent(
            patched_region
        ).strip()

        if not dedented:
            return ""

        if original_indent:
            return textwrap.indent(
                dedented,
                original_indent,
            )

        return dedented

    def _extract_definition_name(
        self,
        region: str,
    ):
        stripped = region.lstrip()

        if stripped.startswith("def "):
            first_line = stripped.splitlines()[0]

            before_paren = first_line.split(
                "(",
                1,
            )[0]

            return before_paren.replace(
                "def ",
                "",
                1,
            ).strip()

        if stripped.startswith("async def "):
            first_line = stripped.splitlines()[0]

            before_paren = first_line.split(
                "(",
                1,
            )[0]

            return before_paren.replace(
                "async def ",
                "",
                1,
            ).strip()

        return None

    def _preserves_definition(
        self,
        original_region: str,
        patched_region: str,
    ) -> bool:
        original_name = (
            self._extract_definition_name(
                original_region
            )
        )

        if original_name is None:
            return True

        patched_stripped = patched_region.lstrip()

        expected_def = (
            f"def {original_name}("
        )

        expected_async_def = (
            f"async def {original_name}("
        )

        return (
            patched_stripped.startswith(
                expected_def
            )
            or patched_stripped.startswith(
                expected_async_def
            )
        )

    def generate(
        self,
        task_id: str,
        repo_path: str,
        source_file: str,
        bug_description: str,
        region_start_line: int,
        region_end_line: int,
        candidate_count: int = 4,
    ):
        repo = Path(repo_path).resolve()

        source_path = repo / source_file

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: "
                f"{source_path}"
            )

        original_code = source_path.read_text(
            encoding="utf-8"
        )

        lines = original_code.splitlines()

        if (
            region_start_line < 1
            or region_end_line < region_start_line
            or region_end_line > len(lines)
        ):
            raise ValueError(
                "Invalid target region: "
                f"{region_start_line}-"
                f"{region_end_line} "
                f"for file containing "
                f"{len(lines)} lines."
            )

        original_region = "\n".join(
            lines[
                region_start_line - 1:
                region_end_line
            ]
        )

        context_start = max(
            0,
            region_start_line - 8,
        )

        context_end = min(
            len(lines),
            region_end_line + 8,
        )

        surrounding_context = "\n".join(
            lines[
                context_start:
                context_end
            ]
        )

        patches = []

        for candidate_number in range(
            1,
            candidate_count + 1,
        ):
            prompt = f"""
You are repairing a localized Python software bug.

Task:
{task_id}

Bug description:
{bug_description}

Target file:
{source_file}

You may modify ONLY this exact target region:

--- TARGET REGION ---
{original_region}
--- END TARGET REGION ---

Nearby context for understanding only:

--- CONTEXT ---
{surrounding_context}
--- END CONTEXT ---

Generate ONE candidate repair.

IMPORTANT RULES:

1. Return ONLY the complete replacement
   for the target region.

2. Do not return JSON.

3. Do not use Markdown code fences.

4. Preserve the same logical code scope.

5. If the target region contains a complete
   function or method definition, return the
   complete function or method definition.

6. Do not return only the function body.

7. Do not add unrelated functions.

8. Do not add tests.

9. Do not modify surrounding code.

10. Make the smallest reasonable repair.

11. Preserve all existing parameters,
    signatures, decorators, and class
    membership unless required by the bug.

12. Preserve Python escape sequences exactly.
    For example, if the code needs '\\n' or
    '\\t' inside a Python string literal,
    return those escape sequences as valid
    Python source code.

13. Indentation will be normalized
    automatically, so focus on correct
    relative Python indentation.
"""

            print(
                "\nGenerating region candidate "
                f"{candidate_number}..."
            )

            try:
                raw_response = self._call_ollama(
                    prompt
                )

            except RuntimeError as exc:
                print(
                    "SKIPPED: model generation "
                    f"failed: {exc}"
                )
                continue

            patched_region = self._clean_response(
                raw_response
            )

            patched_region = (
                self._preserve_indentation(
                    patched_region,
                    original_region,
                )
            )

            print("\nGenerated region:")
            print(patched_region)

            if not patched_region:
                print("SKIPPED: empty response.")
                continue

            if not self._preserves_definition(
                original_region,
                patched_region,
            ):
                print(
                    "SKIPPED: replacement "
                    "did not preserve the target "
                    "function/method definition."
                )
                continue

            patched_lines = (
                lines[:region_start_line - 1]
                + patched_region.splitlines()
                + lines[region_end_line:]
            )

            patched_code = (
                "\n".join(patched_lines)
                + "\n"
            )

            try:
                compile(
                    patched_code,
                    source_file,
                    "exec",
                )

            except SyntaxError as exc:
                print(
                    "SKIPPED: invalid Python."
                )
                print(
                    f"Syntax error: {exc}"
                )
                continue

            print(
                "Candidate is syntactically valid."
            )

            patches.append(
                CandidatePatch(
                    candidate_id=candidate_number,
                    file_path=source_file,
                    original_code=original_code,
                    patched_code=patched_code,
                    explanation=(
                        "Localized repair "
                        f"candidate "
                        f"{candidate_number}"
                    ),
                )
            )

        print(
            "\nFinal valid region "
            f"candidates: {len(patches)}"
        )

        return patches
