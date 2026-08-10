from __future__ import annotations

from pyenvcheck.models import CheckResult, ProjectContext, Severity, Status


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
