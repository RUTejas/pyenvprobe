from __future__ import annotations

from pyenvcheck.models import CheckResult, ProjectContext, Severity, Status

COMMON_CACHES_DIRS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "build",
    "dist",
}

COMMON_CACHES_FILES = {
    ".coverage",
}


def check_git_repo(context: ProjectContext) -> list[CheckResult]:
    """Checks if the project is part of a Git repository."""
    is_repo = context.git_info.get("is_repo", False)

    if is_repo:
        return [
            CheckResult(
                id="PD201",
                category="git",
                title="Git repository detected",
                status=Status.PASS,
                severity=Severity.LOW,
                message="The project is initialized as a Git repository.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD201",
                category="git",
                title="Git repository detected",
                status=Status.FAIL,
                severity=Severity.HIGH,
                message="The project is not initialized as a Git repository.",
                recommendation="Initialize a Git repository using: git init",
            )
        ]


def check_gitignore_present(context: ProjectContext) -> list[CheckResult]:
    """Checks if .gitignore is present in the project root."""
    has_gitignore = context.git_info.get("has_gitignore", False)

    if has_gitignore:
        return [
            CheckResult(
                id="PD202",
                category="git",
                title=".gitignore found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=".gitignore exists in the project root.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD202",
                category="git",
                title=".gitignore found",
                status=Status.FAIL,
                severity=Severity.HIGH,
                message="No .gitignore file was found in the project root.",
                recommendation="Create a .gitignore file to prevent local cache and temp files from being committed.",
            )
        ]


def check_caches_gitignored(context: ProjectContext) -> list[CheckResult]:
    """Checks if existing local cache files/directories are ignored in .gitignore."""
    matcher = context.git_info.get("matcher")
    has_gitignore = context.git_info.get("has_gitignore", False)

    unignored = []

    # Check directories
    for d in context.dirs:
        # Check if the directory name matches any common cache
        parts = d.split("/")
        if any(part in COMMON_CACHES_DIRS for part in parts) and (
            not has_gitignore or (matcher and not matcher.is_ignored(d, is_dir=True))
        ):
            unignored.append(f"{d}/")

    # Check files
    for f in context.files:
        filename = f.split("/")[-1]
        if filename in COMMON_CACHES_FILES and (
            not has_gitignore or (matcher and not matcher.is_ignored(f, is_dir=False))
        ):
            unignored.append(f)

    if unignored:
        unignored_str = ", ".join(unignored)
        return [
            CheckResult(
                id="PD203",
                category="git",
                title="Cache directories ignored",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message=f"Local cache directories/files exist but are not ignored in .gitignore: {unignored_str}",
                recommendation="Add cache files and directories (like __pycache__, .venv, .pytest_cache) to your .gitignore.",
                metadata={"unignored_caches": unignored},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD203",
                category="git",
                title="Cache directories ignored",
                status=Status.PASS,
                severity=Severity.LOW,
                message="All existing local cache files and directories are ignored.",
                recommendation="No action needed.",
            )
        ]
