from __future__ import annotations

import os

try:
    from openai import OpenAI  # type: ignore[import-not-found]
except ImportError:
    OpenAI = None

from pyenvprobe.models import CheckResult, ProjectContext

SYSTEM_PROMPT = """You are PyEnvProbeAI, an expert Python developer and technical writer embedded into the pyenvprobe CLI tool.
Your job is to read project context and generate highly accurate, PEP-compliant fixes for the user's repository.
Do not wrap your final output in markdown code blocks unless requested. Output raw text if it is meant to be inserted directly into a file.
"""


class PyEnvProbeAI:
    def __init__(self) -> None:
        if OpenAI is None:
            raise ImportError(
                "The 'openai' package is required for AI features. Install it with: pip install pyenvprobe[ai]"
            )

        api_key = os.environ.get("PYENVPROBE_API_KEY") or os.environ.get(
            "OPENAI_API_KEY"
        )
        if not api_key:
            raise ValueError(
                "AI API key not found. Please set the PYENVPROBE_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Fast, cheap, capable model

    def generate_readme(self, context: ProjectContext) -> str | None:
        """Generates a complete README.md based on the project context."""
        try:
            # Gather some context
            pyproject_toml = context.pyproject
            project_name = pyproject_toml.get("project", {}).get(
                "name", "Unknown Project"
            )
            description = pyproject_toml.get("project", {}).get("description", "")

            prompt = f"Project Name: {project_name}\nDescription: {description}\n\n"
            prompt += "Please generate a professional, complete README.md for this Python project. "
            prompt += "It MUST include a title, description, Installation section, and Usage section."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            if content:
                # Strip markdown blocks if they wrapped the whole thing
                content = content.strip()
                if content.startswith("```markdown"):
                    content = content[11:]
                if content.endswith("```"):
                    content = content[:-3]

                readme_path = context.root_path / "README.md"
                with open(readme_path, "w", encoding="utf-8") as f:
                    f.write(content.strip() + "\n")
                return "Generated and saved a comprehensive README.md using AI."
            return "Failed to generate README content."
        except Exception as e:
            return f"AI Generation failed: {e}"

    def generate_docstrings(
        self, context: ProjectContext, missing_nodes: list[dict]
    ) -> str | None:
        """Generates and inserts docstrings for functions that lack them."""
        # This is a complex AST transformation, so for the MVP we will demonstrate it
        # by generating a generic file containing the suggested docstrings.
        # Fully splicing into arbitrary Python code robustly is best done with libcst or similar,
        # but we'll try a basic insertion or just print them for now.

        # To avoid destroying the user's code, we will generate the docstrings
        # and append them to an AI_DOCSTRINGS.md file for the user to review.
        try:
            prompt = "Here are several Python function signatures that are missing docstrings:\n\n"
            for node in missing_nodes:
                prompt += f"- File: {node['file']}, Function: {node['name']}\n"

            prompt += "\nPlease write a PEP-257 compliant docstring for each. Format your response as a list."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            if content:
                out_path = context.root_path / "AI_DOCSTRINGS.md"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write("# AI Generated Docstrings\n\n" + content.strip() + "\n")
                return f"Generated docstrings and saved them to {out_path.name} for review."
            return "Failed to generate docstrings."
        except Exception as e:
            return f"AI Generation failed: {e}"

    def generate_tests(
        self, context: ProjectContext, untested_files: list[str]
    ) -> str | None:
        """Generates unit tests for files missing them using AI."""
        try:
            tests_dir = context.root_path / "tests"
            tests_dir.mkdir(exist_ok=True)

            generated_files = []
            for src_file in untested_files[
                :3
            ]:  # Limit to 3 files to avoid hitting token limits
                full_path = context.root_path / src_file
                filename = full_path.name

                with open(full_path, encoding="utf-8") as f:
                    source_code = f.read()

                prompt = f"Write a robust, complete test suite using `pytest` for the following Python file ({filename}).\n\n"
                prompt += f"```python\n{source_code}\n```\n\n"
                prompt += "Only output the Python code for the test file. Do not include markdown codeblocks or any other text. Start your response directly with the imports."

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                )

                content = response.choices[0].message.content
                if content:
                    content = content.strip()
                    if content.startswith("```python"):
                        content = content[9:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()

                    test_filename = f"test_{filename}"
                    test_path = tests_dir / test_filename
                    with open(test_path, "w", encoding="utf-8") as f:
                        f.write(content + "\n")
                    generated_files.append(test_filename)

            if generated_files:
                return f"Successfully generated {len(generated_files)} test files: {', '.join(generated_files)}."
            return "Failed to generate any test files."
        except Exception as e:
            return f"AI Test Generation failed: {e}"


def apply_ai_fix(context: ProjectContext, result: CheckResult) -> str | None:
    try:
        ai = PyEnvProbeAI()
    except Exception as e:
        return f"AI Initialization Error: {e}"

    if result.id in ("PD301", "PD303"):
        return ai.generate_readme(context)
    elif result.id == "PD403":
        missing_nodes = result.metadata.get("missing_docstrings", [])
        if missing_nodes:
            return ai.generate_docstrings(context, missing_nodes)
    elif result.id == "PD402":
        untested_files = result.metadata.get("untested_files", [])
        if untested_files:
            return ai.generate_tests(context, untested_files)
    return None
