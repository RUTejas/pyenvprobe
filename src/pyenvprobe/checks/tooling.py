from __future__ import annotations

from pyenvprobe.models import CheckResult, ProjectContext, Severity, Status


def check_tooling_config(context: ProjectContext) -> list[CheckResult]:
    """Checks if common code quality tools (Ruff, Black, mypy, etc.) are configured."""
    tools = []
    config_sources = []

    # Check pyproject.toml
    if context.pyproject:
        tool_section = context.pyproject.get("tool", {})
        for t in ["ruff", "black", "mypy", "isort", "pylint", "flake8"]:
            if t in tool_section:
                tools.append(t)
                config_sources.append(f"pyproject.toml (tool.{t})")

    # Check other standalone config files
    for f in context.files:
        if "/" not in f:  # Only root files
            if f == "ruff.toml" or f == ".ruff.toml":
                if "ruff" not in tools:
                    tools.append("ruff")
                config_sources.append(f)
            elif f == "mypy.ini":
                if "mypy" not in tools:
                    tools.append("mypy")
                config_sources.append(f)
            elif f == ".isort.cfg":
                if "isort" not in tools:
                    tools.append("isort")
                config_sources.append(f)
            elif f == ".flake8":
                if "flake8" not in tools:
                    tools.append("flake8")
                config_sources.append(f)

    if tools:
        tools_str = ", ".join(tools)
        sources_str = ", ".join(config_sources)
        return [
            CheckResult(
                id="PD501",
                category="tooling",
                title="Code quality configuration found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"Code quality tools configured: {tools_str} (via {sources_str})",
                recommendation="No action needed.",
                metadata={"configured_tools": tools, "config_sources": config_sources},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD501",
                category="tooling",
                title="Code quality configuration found",
                status=Status.WARN,
                severity=Severity.LOW,
                message="No common code quality tools (e.g. Ruff, Black, mypy) were detected.",
                recommendation="Configure code quality tools to format, lint, and type check your repository. We recommend starting with Ruff (add [tool.ruff] in pyproject.toml).",
            )
        ]
