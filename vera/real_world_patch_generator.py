import ast
import json
import socket
import textwrap
import time
import urllib.error
import urllib.request
from pathlib import Path

from vera.models import CandidatePatch


class RealWorldPatchGenerator:
    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        ollama_url: str = (
            "http://localhost:11434/api/generate"
        ),
        timeout: int = 300,
        max_retries: int = 3,
        max_generation_multiplier: int = 3,
    ):
        self.model = model
        self.ollama_url = ollama_url
        self.timeout = timeout
        self.max_retries = max_retries

        # Example:
        # candidate_count = 4
        # maximum generation attempts = 12
        #
        # Invalid Python generations do not immediately
        # consume one of the requested valid candidates.
        self.max_generation_multiplier = (
            max_generation_multiplier
        )

    # ============================================================
    # AST helpers
    # ============================================================

    def _find_function_node(
        self,
        source_code: str,
        target_function: str,
    ):
        tree = ast.parse(source_code)

        matching_nodes = []

        for node in ast.walk(tree):
            if (
                isinstance(
                    node,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef,
                    ),
                )
                and node.name == target_function
            ):
                matching_nodes.append(node)

        if not matching_nodes:
            raise ValueError(
                f"Function not found: "
                f"{target_function}"
            )

        if len(matching_nodes) > 1:
            raise ValueError(
                "Multiple functions found with name "
                f"{target_function}. "
                "Function-only replacement is ambiguous."
            )

        return matching_nodes[0]

    def _extract_function(
        self,
        source_code: str,
        target_function: str,
    ) -> str:
        node = self._find_function_node(
            source_code,
            target_function,
        )

        lines = source_code.splitlines()

        function_code = "\n".join(
            lines[
                node.lineno - 1:
                node.end_lineno
            ]
        )

        # Important for methods/nested functions.
        # The LLM receives a standalone function.
        return textwrap.dedent(
            function_code
        ).strip()

    def _extract_context(
        self,
        source_code: str,
        target_function: str,
        context_lines: int = 35,
    ) -> str:
        """
        Return surrounding source context without sending
        the entire repository/file to the model.
        """
        node = self._find_function_node(
            source_code,
            target_function,
        )

        lines = source_code.splitlines()

        start = max(
            0,
            node.lineno - 1 - context_lines,
        )

        end = min(
            len(lines),
            node.end_lineno + context_lines,
        )

        context = "\n".join(
            lines[start:end]
        )

        return context

    def _get_original_indent(
        self,
        source_code: str,
        node,
    ) -> str:
        lines = source_code.splitlines()

        function_line = lines[
            node.lineno - 1
        ]

        return function_line[
            :len(function_line)
            - len(function_line.lstrip())
        ]

    # ============================================================
    # Candidate normalization
    # ============================================================

    def _normalize_function_code(
        self,
        function_code: str,
    ) -> str:
        """
        Perform formatting-only normalization.

        This does NOT attempt to repair candidate semantics.
        It only removes common output formatting artifacts.
        """
        code = function_code.strip()

        # Occasionally models still return Markdown fences
        # despite explicit instructions.
        if code.startswith("```"):
            lines = code.splitlines()

            if lines:
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            code = "\n".join(lines)

        # The most important fix for the previous
        # "unexpected indent" failures.
        code = textwrap.dedent(
            code
        ).strip()

        return code

    # ============================================================
    # Candidate validation
    # ============================================================

    def _validate_generated_function(
        self,
        function_code: str,
        original_function: str,
        target_function: str,
    ):
        """
        Validate that the model returned exactly one complete
        function with the correct name and signature.
        """

        try:
            generated_tree = ast.parse(
                function_code
            )

        except SyntaxError as exc:
            return (
                False,
                f"Syntax error: {exc}",
            )

        # We expect exactly one top-level function.
        if len(generated_tree.body) != 1:
            return (
                False,
                "Candidate must contain exactly "
                "one top-level statement.",
            )

        generated_node = (
            generated_tree.body[0]
        )

        if not isinstance(
            generated_node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            return (
                False,
                "Candidate is not a function "
                "definition.",
            )

        if generated_node.name != target_function:
            return (
                False,
                "Candidate changed function name "
                f"from {target_function} to "
                f"{generated_node.name}.",
            )

        try:
            original_tree = ast.parse(
                original_function
            )
        except SyntaxError as exc:
            raise RuntimeError(
                "Original function could not be "
                "parsed."
            ) from exc

        if (
            len(original_tree.body) != 1
            or not isinstance(
                original_tree.body[0],
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
        ):
            raise RuntimeError(
                "Original function extraction "
                "is invalid."
            )

        original_node = (
            original_tree.body[0]
        )

        # Preserve sync/async function type.
        if type(generated_node) is not type(
            original_node
        ):
            return (
                False,
                "Candidate changed function type "
                "(sync/async).",
            )

        # Preserve function signature.
        original_args = ast.dump(
            original_node.args,
            include_attributes=False,
        )

        generated_args = ast.dump(
            generated_node.args,
            include_attributes=False,
        )

        if original_args != generated_args:
            return (
                False,
                "Candidate changed the function "
                "signature.",
            )

        return True, ""

    # ============================================================
    # Function replacement
    # ============================================================

    def _replace_function(
        self,
        source_code: str,
        target_function: str,
        new_function_code: str,
    ) -> str:
        node = self._find_function_node(
            source_code,
            target_function,
        )

        lines = source_code.splitlines()

        start = node.lineno - 1
        end = node.end_lineno

        original_indent = (
            self._get_original_indent(
                source_code,
                node,
            )
        )

        normalized_code = (
            textwrap.dedent(
                new_function_code
            )
            .strip()
        )

        replacement_lines = []

        for line in normalized_code.splitlines():
            if line.strip():
                replacement_lines.append(
                    original_indent + line
                )
            else:
                replacement_lines.append("")

        new_lines = (
            lines[:start]
            + replacement_lines
            + lines[end:]
        )

        return "\n".join(new_lines) + "\n"

    # ============================================================
    # Ollama
    # ============================================================

    def _call_ollama(
        self,
        prompt: str,
    ):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                # Lower temperature is preferable for
                # program repair. We need correctness
                # more than creative output.
                "temperature": 0.25,
            },
        }

        encoded_payload = json.dumps(
            payload
        ).encode("utf-8")

        last_error = None

        for attempt in range(
            1,
            self.max_retries + 2,
        ):
            # Re-create the request for every attempt.
            request = urllib.request.Request(
                self.ollama_url,
                data=encoded_payload,
                headers={
                    "Content-Type":
                    "application/json",
                },
                method="POST",
            )

            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.timeout,
                ) as response:
                    response_body = json.loads(
                        response
                        .read()
                        .decode("utf-8")
                    )

                raw_response = (
                    response_body.get(
                        "response",
                        "",
                    )
                )

                if not raw_response:
                    raise RuntimeError(
                        "Ollama returned an empty "
                        "response."
                    )

                try:
                    data = json.loads(
                        raw_response
                    )

                except json.JSONDecodeError as exc:
                    print(
                        "\nRAW MODEL RESPONSE:"
                    )
                    print(raw_response)

                    raise RuntimeError(
                        "Ollama returned "
                        "invalid JSON."
                    ) from exc

                if not isinstance(
                    data,
                    dict,
                ):
                    raise RuntimeError(
                        "Ollama JSON response "
                        "is not an object."
                    )

                return data

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
                    print(
                        "Retrying Ollama request..."
                    )

                    time.sleep(2)

        raise RuntimeError(
            "Ollama generation failed after "
            f"{self.max_retries + 1} attempts."
        ) from last_error

    # ============================================================
    # Main generation
    # ============================================================

    def generate(
        self,
        task_id: str,
        repo_path: str,
        source_file: str,
        target_function: str,
        bug_description: str,
        candidate_count: int = 4,
    ):
        repo = Path(
            repo_path
        ).resolve()

        source_path = (
            repo
            / source_file
        )

        if not source_path.exists():
            raise FileNotFoundError(
                f"Source file does not exist: "
                f"{source_path}"
            )

        original_code = (
            source_path.read_text(
                encoding="utf-8"
            )
        )

        original_function = (
            self._extract_function(
                original_code,
                target_function,
            )
        )

        surrounding_context = (
            self._extract_context(
                original_code,
                target_function,
            )
        )

        patches = []

        generation_attempt = 0

        maximum_attempts = max(
            candidate_count,
            candidate_count
            * self.max_generation_multiplier,
        )

        while (
            len(patches) < candidate_count
            and generation_attempt
            < maximum_attempts
        ):
            generation_attempt += 1

            valid_candidate_number = (
                len(patches) + 1
            )

            prompt = f"""
You are repairing a real bug in an existing Python software project.

TASK ID:
{task_id}

BUG DESCRIPTION:
{bug_description}

TARGET FILE:
{source_file}

TARGET FUNCTION:
{target_function}

CURRENT BUGGY FUNCTION:
--- BEGIN FUNCTION ---
{original_function}
--- END FUNCTION ---

LOCAL SOURCE CONTEXT:
--- BEGIN CONTEXT ---
{surrounding_context}
--- END CONTEXT ---

Generate ONE minimal candidate repair for the target function.

STRICT REQUIREMENTS:

1. Modify ONLY the target function.

2. Return the COMPLETE target function,
   not a fragment and not the whole file.

3. Preserve the exact function name.

4. Preserve the exact function signature.

5. Preserve whether the function is synchronous
   or asynchronous.

6. Do not add tests.

7. Do not add imports outside the target function.

8. Do not add unrelated functions or classes.

9. Do not invent parser tokens, constants, APIs,
   attributes, or helper functions that are not
   supported by the supplied source context.

10. Prefer existing AST/node structures and APIs
    already used by the project.

11. Make the smallest behaviorally meaningful repair.

12. The returned function MUST parse as valid Python.

13. Do not return Markdown code fences.

14. Do not escape the Python source into literal
    backslash-n sequences beyond normal JSON encoding.

15. Do not include prose inside patched_function.

Return strict JSON with exactly these fields:

{{
  "patched_function": "complete Python function source",
  "explanation": "one short sentence describing the repair"
}}
""".strip()

            print(
                "\nGenerating function candidate "
                f"{valid_candidate_number} "
                f"(attempt {generation_attempt}/"
                f"{maximum_attempts})..."
            )

            try:
                data = self._call_ollama(
                    prompt
                )

            except RuntimeError as exc:
                print(
                    "REJECTED GENERATION: "
                    f"{exc}"
                )
                continue

            function_code = data.get(
                "patched_function",
                "",
            )

            explanation = data.get(
                "explanation",
                "",
            )

            if not isinstance(
                function_code,
                str,
            ):
                print(
                    "REJECTED GENERATION: "
                    "patched_function is not "
                    "a string."
                )
                continue

            if not isinstance(
                explanation,
                str,
            ):
                explanation = str(
                    explanation
                )

            if not function_code.strip():
                print(
                    "REJECTED GENERATION: "
                    "empty patched_function."
                )
                continue

            function_code = (
                self._normalize_function_code(
                    function_code
                )
            )

            (
                is_valid,
                validation_error,
            ) = (
                self._validate_generated_function(
                    function_code=(
                        function_code
                    ),
                    original_function=(
                        original_function
                    ),
                    target_function=(
                        target_function
                    ),
                )
            )

            if not is_valid:
                print(
                    "REJECTED GENERATION: "
                    f"{validation_error}"
                )
                continue

            patched_code = (
                self._replace_function(
                    original_code=(
                        original_code
                    ),
                    target_function=(
                        target_function
                    ),
                    new_function_code=(
                        function_code
                    ),
                )
            )

            try:
                compile(
                    patched_code,
                    source_file,
                    "exec",
                )

            except SyntaxError as exc:
                print(
                    "REJECTED GENERATION: "
                    "patched source is "
                    "invalid Python."
                )

                print(
                    f"Syntax error: {exc}"
                )

                continue

            # Avoid identical/no-op candidates.
            if (
                function_code.strip()
                == original_function.strip()
            ):
                print(
                    "REJECTED GENERATION: "
                    "candidate did not modify "
                    "the target function."
                )
                continue

            # Avoid duplicate candidates.
            duplicate = any(
                patch.patched_code
                == patched_code
                for patch in patches
            )

            if duplicate:
                print(
                    "REJECTED GENERATION: "
                    "duplicate candidate."
                )
                continue

            candidate_id = (
                len(patches) + 1
            )

            print(
                "Candidate "
                f"{candidate_id} is "
                "syntactically valid."
            )

            patches.append(
                CandidatePatch(
                    candidate_id=(
                        candidate_id
                    ),
                    file_path=(
                        source_file
                    ),
                    original_code=(
                        original_code
                    ),
                    patched_code=(
                        patched_code
                    ),
                    explanation=(
                        explanation.strip()
                    ),
                )
            )

        print(
            "\nRequested valid function "
            f"candidates: {candidate_count}"
        )

        print(
            "Generation attempts used: "
            f"{generation_attempt}"
        )

        print(
            "Valid function candidates: "
            f"{len(patches)}"
        )

        if len(patches) < candidate_count:
            print(
                "WARNING: Generator could not "
                "produce the requested number "
                "of valid candidates within "
                f"{maximum_attempts} attempts."
            )

        return patches