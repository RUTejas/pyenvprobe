from __future__ import annotations

from pyenvprobe.models import CheckResult, ProjectContext, Severity, Status


def check_python_project(context: ProjectContext) -> list[CheckResult]:
    """Verifies that the project contains Python files."""
    has_python_files = any(f.endswith(".py") for f in context.files)

    if has_python_files:
        return [
            CheckResult(
                id="PD001",
                category="python",
                title="Python files detected",
                status=Status.PASS,
                severity=Severity.LOW,
                message="The project contains Python (.py) source files.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD001",
                category="python",
                title="Python files detected",
                status=Status.FAIL,
                severity=Severity.CRITICAL,
                message="No Python source files (.py) were found in the scanned directory.",
                recommendation="Ensure you are running projectdoctor inside a Python project directory.",
            )
        ]


def check_python_version(context: ProjectContext) -> list[CheckResult]:
    """Checks if a target Python version configuration is declared."""
    # 1. Check in pyproject.toml PEP 621 requires-python
    requires_python = context.pyproject.get("project", {}).get("requires-python")

    # 2. Fallback to poetry configuration
    if not requires_python:
        requires_python = (
            context.pyproject.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
            .get("python")
        )

    if requires_python:
        return [
            CheckResult(
                id="PD002",
                category="python",
                title="Python version configured",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"Target Python version is set to: '{requires_python}'",
                recommendation="No action needed.",
                metadata={"requires_python": requires_python},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD002",
                category="python",
                title="Python version configured",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message="No target Python version was detected in configuration files.",
                recommendation="Specify the required Python version in pyproject.toml under [project] using the 'requires-python' key, e.g. requires-python = '>=3.9'.",
            )
        ]
