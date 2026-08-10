from __future__ import annotations

from pyenvcheck.models import CheckResult, ProjectContext, Severity, Status


def check_pyproject_toml(context: ProjectContext) -> list[CheckResult]:
    """Checks if pyproject.toml exists in the project root."""
    if "pyproject.toml" in context.files:
        return [
            CheckResult(
                id="PD101",
                category="structure",
                title="pyproject.toml found",
                status=Status.PASS,
                severity=Severity.LOW,
                message="pyproject.toml was found in the project root.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD101",
                category="structure",
                title="pyproject.toml found",
                status=Status.FAIL,
                severity=Severity.HIGH,
                message="pyproject.toml is missing from the project root.",
                recommendation="Create a pyproject.toml file in your repository root to configure packaging and tools.",
            )
        ]


def check_requirements_txt(context: ProjectContext) -> list[CheckResult]:
    """Checks for requirements.txt or dependency declarations."""
    has_reqs = len(context.requirements_files) > 0
    has_pyproject = "pyproject.toml" in context.files
    has_pyproject_deps = (
        context.pyproject.get("project", {}).get("dependencies") is not None
    )

    if has_reqs:
        files_str = ", ".join(context.requirements_files)
        return [
            CheckResult(
                id="PD102",
                category="structure",
                title="Requirements file found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"Requirements/dependency file(s) found: {files_str}",
                recommendation="No action needed.",
                metadata={"requirements_files": context.requirements_files},
            )
        ]
    elif has_pyproject and has_pyproject_deps:
        return [
            CheckResult(
                id="PD102",
                category="structure",
                title="Requirements file found",
                status=Status.PASS,
                severity=Severity.LOW,
                message="Dependencies are managed via pyproject.toml.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD102",
                category="structure",
                title="Requirements file found",
                status=Status.WARN,
                severity=Severity.LOW,
                message="No requirements.txt or other dependency file was found.",
                recommendation="Create a requirements.txt file (or declare dependencies in pyproject.toml) if your project has external dependencies.",
            )
        ]


def check_tests_dir(context: ProjectContext) -> list[CheckResult]:
    """Checks if a tests or test directory exists."""
    has_tests = "tests" in context.dirs or "test" in context.dirs

    if has_tests:
        return [
            CheckResult(
                id="PD103",
                category="structure",
                title="Tests directory found",
                status=Status.PASS,
                severity=Severity.LOW,
                message="A test directory ('tests/' or 'test/') exists.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD103",
                category="structure",
                title="Tests directory found",
                status=Status.FAIL,
                severity=Severity.MEDIUM,
                message="No test directory ('tests/' or 'test/') was found.",
                recommendation="Create a 'tests/' directory in your project root to organize unit and integration tests.",
            )
        ]


def check_project_layout(context: ProjectContext) -> list[CheckResult]:
    """Checks if the project matches standard layouts (src or flat package)."""
    # Look for 'src/' directory
    has_src = "src" in context.dirs

    # Look for any top-level package directories containing __init__.py
    # Excluding test/build/dist/etc.
    exclude_pkgs = {"tests", "test", ".venv", "venv", "build", "dist"}
    flat_packages = []
    for d in context.dirs:
        if "/" not in d and d not in exclude_pkgs:
            # Check if this directory contains a __init__.py
            init_file = f"{d}/__init__.py"
            if init_file in context.files:
                flat_packages.append(d)

    if has_src:
        return [
            CheckResult(
                id="PD104",
                category="structure",
                title="Project structure layout",
                status=Status.PASS,
                severity=Severity.LOW,
                message="Project uses the standard 'src/' layout.",
                recommendation="No action needed.",
            )
        ]
    elif flat_packages:
        pkgs_str = ", ".join(flat_packages)
        return [
            CheckResult(
                id="PD104",
                category="structure",
                title="Project structure layout",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"Project uses a flat layout with package(s): {pkgs_str}",
                recommendation="No action needed.",
                metadata={"packages": flat_packages},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD104",
                category="structure",
                title="Project structure layout",
                status=Status.WARN,
                severity=Severity.LOW,
                message="No standard 'src/' layout or package folder containing '__init__.py' was detected.",
                recommendation="Consider placing package code inside a 'src/' folder or a package folder containing '__init__.py'.",
            )
        ]
