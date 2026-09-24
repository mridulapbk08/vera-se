import json
import urllib.error
import urllib.request

from vera.models import CandidatePatch


class PatchGenerator:
    def __init__(
        self,
        model_name="qwen2.5-coder:7b",
        ollama_url="http://localhost:11434/api/generate",
    ):
        self.model_name = model_name
        self.ollama_url = ollama_url

    @staticmethod
    def _find_source_file(
        repository_context,
    ):
        for line in repository_context.splitlines():
            line = line.strip()

            if not line.startswith("FILE:"):
                continue

            file_path = line.replace(
                "FILE:",
                "",
                1,
            ).strip()

            filename = file_path.split("/")[-1]

            if (
                filename.endswith(".py")
                and not filename.startswith("test_")
            ):
                return file_path

        raise RuntimeError(
            "Could not determine source file "
            "from repository context."
        )

    def _call_ollama(
        self,
        prompt,
    ):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.7,
            },
        }

        request_data = json.dumps(
            payload
        ).encode("utf-8")

        request = urllib.request.Request(
            self.ollama_url,
            data=request_data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=300,
            ) as response:
                body = response.read().decode(
                    "utf-8"
                )

        except urllib.error.URLError as error:
            raise RuntimeError(
                "Could not connect to Ollama. "
                "Make sure 'ollama serve' is running."
            ) from error

        outer_response = json.loads(
            body
        )

        generated_text = outer_response.get(
            "response",
            "",
        )

        if not generated_text:
            raise RuntimeError(
                "Ollama returned an empty response."
            )

        return generated_text

    @staticmethod
    def _parse_response(
        generated_text,
    ):
        try:
            data = json.loads(
                generated_text
            )

        except json.JSONDecodeError as error:
            print(
                "\nRAW MODEL RESPONSE:\n"
            )

            print(
                generated_text
            )

            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from error

        if "candidates" not in data:
            raise RuntimeError(
                "Model output is missing "
                "'candidates'."
            )

        if not isinstance(
            data["candidates"],
            list,
        ):
            raise RuntimeError(
                "'candidates' must be a list."
            )

        return data

    def generate(
        self,
        task_id,
        repository_context,
        bug_description,
        candidate_count=4,
    ):
        source_file = self._find_source_file(
            repository_context
        )

        prompt = f"""
You are a software repair agent being evaluated
inside the VERA-SE research framework.

TASK:
{task_id}

BUG REPORT:
{bug_description}

SOURCE FILE THAT MAY BE MODIFIED:
{source_file}

REPOSITORY CONTENT:
{repository_context}

Generate exactly {candidate_count} candidate repairs.

STRICT REQUIREMENTS:

1. You may modify ONLY:
   {source_file}

2. Do NOT modify any test file.

3. Every candidate's file_path MUST be exactly:
   {source_file}

4. patched_code MUST contain the COMPLETE contents
   of {source_file}, not merely the changed function.

5. Preserve every unrelated function already present
   in the source file.

6. Every candidate should be a legitimate independent
   attempt to solve the bug.

7. Candidate repairs should be meaningfully different
   when reasonable.

8. patched_code must contain valid Python source code.

9. Do not add markdown fences.

10. Return JSON only.

Required JSON structure:

{{
    "candidates": [
        {{
            "candidate_id": 1,
            "file_path": "{source_file}",
            "patched_code": "complete Python source code",
            "explanation": "short explanation"
        }}
    ]
}}
"""

        generated_text = self._call_ollama(
            prompt
        )

        data = self._parse_response(
            generated_text
        )

        patches = []

        for index, item in enumerate(
            data["candidates"],
            start=1,
        ):
            file_path = item.get(
                "file_path",
                ""
            )

            patched_code = item.get(
                "patched_code",
                ""
            )

            explanation = item.get(
                "explanation",
                ""
            )

            if not patched_code:
                print(
                    f"Skipping candidate {index}: "
                    "empty patched_code"
                )
                continue

            if file_path != source_file:
                print(
                    f"Skipping candidate {index}: "
                    f"attempted file '{file_path}' "
                    f"instead of '{source_file}'"
                )
                continue

            patch = CandidatePatch(
                candidate_id=item.get(
                    "candidate_id",
                    index,
                ),
                file_path=file_path,
                original_code="",
                patched_code=patched_code,
                explanation=explanation,
            )

            patches.append(
                patch
            )

        if not patches:
            raise RuntimeError(
                "The model produced no usable "
                "candidate patches."
            )

        return patches[:candidate_count]