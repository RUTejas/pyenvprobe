from __future__ import annotations

from pyenvprobe.models import CheckResult, ProjectContext, Severity, Status


def check_testing_config(context: ProjectContext) -> list[CheckResult]:
    """Checks if a testing framework (like pytest or tox) is configured."""
    has_pytest_config = False
    config_sources = []

    # Check pyproject.toml
    if context.pyproject:
        tool_section = context.pyproject.get("tool", {})
        if "pytest" in tool_section:
            has_pytest_config = True
            config_sources.append("pyproject.toml (tool.pytest)")
        if "tox" in tool_section:
            has_pytest_config = True
            config_sources.append("pyproject.toml (tool.tox)")

    # Check config files
    for f in context.files:
        if "/" not in f:  # Only root files
            if f == "pytest.ini":
                has_pytest_config = True
                config_sources.append("pytest.ini")
            elif f == "tox.ini":
                has_pytest_config = True
                config_sources.append("tox.ini")
            elif f == "setup.cfg":
                has_pytest_config = True
                config_sources.append("setup.cfg")

    if has_pytest_config:
        sources_str = ", ".join(config_sources)
        return [
            CheckResult(
                id="PD401",
                category="testing",
                title="Test configuration found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"Testing configuration found in: {sources_str}",
                recommendation="No action needed.",
                metadata={"config_sources": config_sources},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD401",
                category="testing",
                title="Test configuration found",
                status=Status.WARN,
                severity=Severity.LOW,
                message="No testing configuration (e.g. pytest, tox) was detected.",
                recommendation="Consider adding pytest configuration under [tool.pytest.ini_options] in pyproject.toml, or create a pytest.ini file.",
            )
        ]


def check_missing_tests(context: ProjectContext) -> list[CheckResult]:
    """Finds source files that don't have a corresponding test file."""
    src_files = [
        f
        for f in context.files
        if f.endswith(".py")
        and (f.startswith("src/") or "/" not in f)
        and not f.startswith("tests/")
        and not f.startswith("test_")
        and f != "setup.py"
        and f != "conftest.py"
    ]
    test_files = [
        f
        for f in context.files
        if f.startswith("tests/") or f.startswith("test_") or "_test.py" in f
    ]

    untested_files = []
    for src in src_files:
        filename = src.split("/")[-1]
        if filename == "__init__.py":
            continue

        expected_test_name = f"test_{filename}"
        found = any(expected_test_name in t for t in test_files)
        if not found:
            untested_files.append(src)

    if untested_files:
        return [
            CheckResult(
                id="PD402",
                category="testing",
                title="Missing Unit Tests",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message=f"Found {len(untested_files)} source files without a corresponding test file (e.g. {untested_files[0]}).",
                recommendation="Create tests for all modules. Run with --fix --ai to auto-generate comprehensive test suites using AI.",
                metadata={"untested_files": untested_files},
                fixable=True,
            )
        ]
    return [
        CheckResult(
            id="PD402",
            category="testing",
            title="Missing Unit Tests",
            status=Status.PASS,
            severity=Severity.LOW,
            message="All source files appear to have corresponding test files.",
            recommendation="No action needed.",
        )
    ]
