from __future__ import annotations

import contextlib
import fnmatch
import os
import sys
from pathlib import Path
from typing import Any

from pyenvcheck.models import ProjectContext

# Import tomllib or fallback to tomli
tomllib: Any = None
if sys.version_info >= (3, 11):
    import tomllib
else:
    import importlib

    with contextlib.suppress(ImportError):
        tomllib = importlib.import_module("tomli")

# Directories we should detect but NOT walk into
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".tox",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
    ".idea",
    ".vscode",
}

LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5 MB


class GitignoreMatcher:
    """A lightweight, pure-Python matcher for .gitignore rules using fnmatch."""

    def __init__(self, root_path: Path, gitignore_content: str) -> None:
        self.root_path = root_path
        self.rules: list[
            tuple[str, bool, bool, bool]
        ] = []  # (pattern, is_dir_only, is_negated, is_anchored)

        for line in gitignore_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            is_negated = False
            if line.startswith("!"):
                is_negated = True
                line = line[1:]

            is_dir_only = line.endswith("/")
            if is_dir_only:
                line = line[:-1]

            is_anchored = False
            if line.startswith("/"):
                is_anchored = True
                line = line[1:]
            elif "/" in line:
                is_anchored = True

            # Standardize Windows separators in pattern
            line = line.replace("\\", "/")
            self.rules.append((line, is_dir_only, is_negated, is_anchored))

    def is_ignored(self, rel_path_str: str, is_dir: bool = False) -> bool:
        """Determines if a relative path is ignored based on the loaded rules."""
        # Standardize separators
        rel_path_str = rel_path_str.replace("\\", "/")
        parts = rel_path_str.split("/")

        ignored = False
        for pattern, is_dir_only, is_negated, is_anchored in self.rules:
            if is_dir_only and not is_dir:
                continue

            matches = False
            if is_anchored:
                # Anchored matches relative to the root (so no subpath prefix match)
                if fnmatch.fnmatchcase(rel_path_str, pattern):
                    matches = True
            else:
                # Unanchored matches anywhere (matches any path component or the whole filename)
                if "/" not in pattern:
                    if any(fnmatch.fnmatchcase(part, pattern) for part in parts):
                        matches = True
                else:
                    if fnmatch.fnmatchcase(
                        rel_path_str, pattern
                    ) or fnmatch.fnmatchcase(rel_path_str, "*/" + pattern):
                        matches = True

            if matches:
                ignored = not is_negated

        return ignored


def scan_project(root_path: Path) -> ProjectContext:
    """Scans the given project directory and builds a ProjectContext."""
    context = ProjectContext(root_path=root_path.resolve())

    if not root_path.exists():
        context.errors.append(f"Directory '{root_path}' does not exist.")
        return context

    if not root_path.is_dir():
        context.errors.append(f"Path '{root_path}' is not a directory.")
        return context

    # 1. Parse pyproject.toml
    pyproject_path = root_path / "pyproject.toml"
    if pyproject_path.is_file():
        try:
            parser = globals().get("tomllib")
            if parser is None:
                context.errors.append(
                    "Cannot parse pyproject.toml: tomli package is missing on Python < 3.11."
                )
            else:
                with open(pyproject_path, "rb") as pyproject_file:
                    context.pyproject = parser.load(pyproject_file)
        except Exception as e:
            context.errors.append(f"Error parsing pyproject.toml: {e}")

    # 2. Detect Git repository
    is_git = False
    # Check current or parent directories for .git folder
    current = context.root_path
    while True:
        if (current / ".git").is_dir():
            is_git = True
            break
        parent = current.parent
        if parent == current:
            break
        current = parent

    context.git_info["is_repo"] = is_git

    # Read .gitignore if it exists in target root
    gitignore_path = root_path / ".gitignore"
    gitignore_content = ""
    if gitignore_path.is_file():
        try:
            with open(
                gitignore_path, encoding="utf-8", errors="ignore"
            ) as gitignore_file:
                gitignore_content = gitignore_file.read()
        except Exception as e:
            context.errors.append(f"Error reading .gitignore: {e}")

    matcher = GitignoreMatcher(context.root_path, gitignore_content)
    context.git_info["matcher"] = matcher
    context.git_info["has_gitignore"] = gitignore_path.is_file()

    # 3. Walk directory structure
    # Limit max number of walked files to prevent hanging
    max_files = 10000
    file_count = 0

    for root, dirs, files in os.walk(root_path):
        current_dir = Path(root)

        # Calculate relative path of current dir from root_path
        try:
            rel_dir = current_dir.relative_to(root_path)
            rel_dir_str = "" if rel_dir == Path(".") else str(rel_dir)
        except ValueError:
            continue

        # Filter directories in-place to avoid walking into skipped ones
        pruned_dirs = []
        for d in dirs:
            dir_rel_path = os.path.join(rel_dir_str, d) if rel_dir_str else d
            # Record directory presence
            context.dirs.add(dir_rel_path.replace("\\", "/"))

            if d in SKIP_DIRS:
                continue
            pruned_dirs.append(d)

        # Modifying dirs in-place affects os.walk's recursion
        dirs[:] = pruned_dirs

        for f in files:
            file_count += 1
            if file_count > max_files:
                context.errors.append(
                    f"Scan limit of {max_files} files exceeded. Stopping walk."
                )
                return context

            file_rel_path = os.path.join(rel_dir_str, f) if rel_dir_str else f
            file_rel_path_standard = file_rel_path.replace("\\", "/")
            context.files.add(file_rel_path_standard)

            # Record requirements files
            if f == "requirements.txt" or (
                f.endswith(".txt") and "requirements" in f.lower()
            ):
                context.requirements_files.append(file_rel_path_standard)

            # Check file size
            try:
                full_path = current_dir / f
                # Avoid checking size of symlinks that might be broken
                if not full_path.is_symlink():
                    sz = full_path.stat().st_size
                    if sz > LARGE_FILE_THRESHOLD:
                        context.large_files.append((file_rel_path_standard, sz))
            except OSError:
                # Handle permissions/missing file race conditions gracefully
                pass

    return context
