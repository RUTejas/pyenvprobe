from __future__ import annotations

import re

from pyenvprobe.models import CheckResult, ProjectContext, Severity, Status

# Version operators to check if dependency is pinned or ranged
VERSION_OPERATORS = ["==", ">=", "<=", "~=", ">", "<", "!=", "@"]

UNWANTED_PATTERNS = [
    r"\.DS_Store$",
    r"Thumbs\.db$",
    r".*~$",
    r".*\.bak$",
    r".*\.tmp$",
]

UNWANTED_DIRS = {
    "build",
    "dist",
}

SECRET_PATTERNS = [
    r"\.env$",
    r"\.env\..*$",
    r".*id_rsa$",
    r".*\.pem$",
    r"credentials\.json$",
    r"client_secret.*\.json$",
]


def parse_requirements_line(line: str) -> str | None:
    """Parses a requirements.txt line and returns the dependency specification if valid."""
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("-"):
        return None
    # Strip comments at end of line
    if " #" in line:
        line = line.split(" #")[0].strip()
    # Strip environment markers (separated by ;)
    if ";" in line:
        line = line.split(";")[0].strip()
    return line


def is_unpinned(dep_spec: str) -> bool:
    """Checks if a dependency specification string is completely unpinned."""
    dep_spec = dep_spec.strip()
    if not dep_spec:
        return False
    # If it contains any of the version/location operators, it is considered pinned/ranged
    if any(op in dep_spec for op in VERSION_OPERATORS):
        return False
    # Ignore editable installs or git URLs
    return not (dep_spec.startswith(".") or "git+" in dep_spec or "://" in dep_spec)


def check_dependencies_defined(context: ProjectContext) -> list[CheckResult]:
    """Checks if the project has defined any dependencies in configurations."""
    has_deps = False

    # Check pyproject.toml PEP 621 dependencies
    if context.pyproject:
        project_sec = context.pyproject.get("project", {})
        if project_sec.get("dependencies") or project_sec.get("optional-dependencies"):
            has_deps = True
        # Poetry check
        poetry_sec = context.pyproject.get("tool", {}).get("poetry", {})
        if poetry_sec.get("dependencies") or poetry_sec.get("group", {}):
            has_deps = True

    # Check requirements files
    for req_file in context.requirements_files:
        req_path = context.root_path / req_file
        try:
            with open(req_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if parse_requirements_line(line):
                        has_deps = True
                        break
        except Exception:
            pass

    if has_deps:
        return [
            CheckResult(
                id="PD601",
                category="dependencies",
                title="Dependencies defined",
                status=Status.PASS,
                severity=Severity.LOW,
                message="Dependencies are defined in the project configurations.",
                recommendation="No action needed.",
            )
        ]
    else:
        return [
            CheckResult(
                id="PD601",
                category="dependencies",
                title="Dependencies defined",
                status=Status.WARN,
                severity=Severity.LOW,
                message="No dependency declarations were detected.",
                recommendation="Specify project dependencies in pyproject.toml or requirements.txt if third-party packages are needed.",
            )
        ]


def check_unpinned_dependencies(context: ProjectContext) -> list[CheckResult]:
    """Verifies that project dependencies are pinned or have version constraints."""
    unpinned = []

    # 1. Parse pyproject.toml dependencies
    if context.pyproject:
        project_sec = context.pyproject.get("project", {})
        deps = project_sec.get("dependencies", [])
        for dep in deps:
            if is_unpinned(dep):
                unpinned.append(f"{dep} (pyproject.toml)")

        # Poetry dependencies
        poetry_deps = (
            context.pyproject.get("tool", {}).get("poetry", {}).get("dependencies", {})
        )
        for dep_name, dep_val in poetry_deps.items():
            if dep_name.lower() == "python":
                continue
            # If dependency is just "*" or empty, it is unpinned
            if dep_val == "*" or not dep_val:
                unpinned.append(f"{dep_name} (pyproject.toml poetry)")

    # 2. Parse requirements files
    for req_file in context.requirements_files:
        req_path = context.root_path / req_file
        try:
            with open(req_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    spec = parse_requirements_line(line)
                    if spec and is_unpinned(spec):
                        unpinned.append(f"{spec} ({req_file})")
        except Exception:
            pass

    if unpinned:
        unpinned_str = ", ".join(unpinned)
        return [
            CheckResult(
                id="PD602",
                category="dependencies",
                title="Unpinned dependencies",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message=f"Unpinned dependencies detected: {unpinned_str}",
                recommendation="Pin dependencies to specific versions (e.g. package==1.0.0) or ranges (e.g. package>=1.0.0) to ensure reproducible builds.",
                metadata={"unpinned_dependencies": unpinned},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD602",
                category="dependencies",
                title="Unpinned dependencies",
                status=Status.PASS,
                severity=Severity.LOW,
                message="All defined dependencies have version specifications or pins.",
                recommendation="No action needed.",
            )
        ]


def check_unwanted_files(context: ProjectContext) -> list[CheckResult]:
    """Checks for unignored unwanted temporary files or build directories."""
    matcher = context.git_info.get("matcher")
    has_gitignore = context.git_info.get("has_gitignore", False)

    unwanted = []

    # Check files
    for f in context.files:
        filename = f.split("/")[-1]
        if any(re.match(pat, filename) for pat in UNWANTED_PATTERNS) and (
            not has_gitignore or (matcher and not matcher.is_ignored(f, is_dir=False))
        ):
            unwanted.append(f)

    # Check directories
    for d in context.dirs:
        parts = d.split("/")
        if any(part in UNWANTED_DIRS for part in parts) and (
            not has_gitignore or (matcher and not matcher.is_ignored(d, is_dir=True))
        ):
            unwanted.append(f"{d}/")

    # Egg info check
    for d in context.dirs:
        parts = d.split("/")
        if any(part.endswith(".egg-info") for part in parts) and (
            not has_gitignore or (matcher and not matcher.is_ignored(d, is_dir=True))
        ):
            unwanted.append(f"{d}/")

    if unwanted:
        unwanted_str = ", ".join(unwanted)
        return [
            CheckResult(
                id="PD701",
                category="hygiene",
                title="Repository hygiene",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message=f"Temporary files or build artifacts detected and not gitignored: {unwanted_str}",
                recommendation="Remove unwanted build/temporary files and add them to your .gitignore.",
                metadata={"unwanted_files": unwanted},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD701",
                category="hygiene",
                title="Repository hygiene",
                status=Status.PASS,
                severity=Severity.LOW,
                message="No unignored temporary or build files detected.",
                recommendation="No action needed.",
            )
        ]


def check_large_files(context: ProjectContext) -> list[CheckResult]:
    """Checks if there are files larger than 5MB that are not ignored."""
    matcher = context.git_info.get("matcher")
    has_gitignore = context.git_info.get("has_gitignore", False)

    unignored_large_files = []
    for f, sz in context.large_files:
        if not has_gitignore or (matcher and not matcher.is_ignored(f, is_dir=False)):
            unignored_large_files.append((f, sz))

    if unignored_large_files:
        items = [f"{f} ({sz // (1024 * 1024)}MB)" for f, sz in unignored_large_files]
        items_str = ", ".join(items)
        return [
            CheckResult(
                id="PD702",
                category="hygiene",
                title="Large files found",
                status=Status.WARN,
                severity=Severity.MEDIUM,
                message=f"Large files (> 5MB) are not ignored: {items_str}",
                recommendation="Large binaries should not be tracked directly in Git. Add them to .gitignore or use Git LFS.",
                metadata={
                    "large_files": [
                        {"path": f, "size_bytes": sz} for f, sz in unignored_large_files
                    ]
                },
            )
        ]
    else:
        return [
            CheckResult(
                id="PD702",
                category="hygiene",
                title="Large files found",
                status=Status.PASS,
                severity=Severity.LOW,
                message="No unignored large files (> 5MB) were found.",
                recommendation="No action needed.",
            )
        ]


def check_secrets_exposed(context: ProjectContext) -> list[CheckResult]:
    """Checks if sensitive files (e.g. .env, private keys) are exposed in the repository."""
    matcher = context.git_info.get("matcher")
    has_gitignore = context.git_info.get("has_gitignore", False)

    exposed = []
    for f in context.files:
        filename = f.split("/")[-1]
        if any(re.match(pat, filename, re.IGNORECASE) for pat in SECRET_PATTERNS) and (
            not has_gitignore or (matcher and not matcher.is_ignored(f, is_dir=False))
        ):
            exposed.append(f)

    if exposed:
        exposed_str = ", ".join(exposed)
        return [
            CheckResult(
                id="PD703",
                category="security",
                title="Secret file exposure",
                status=Status.FAIL,
                severity=Severity.CRITICAL,
                message=f"Potential sensitive files are not ignored: {exposed_str}",
                recommendation="IMMEDIATELY add secret/credential files (like .env or .pem files) to your .gitignore and revoke any leaked credentials.",
                metadata={"exposed_secrets": exposed},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD703",
                category="security",
                title="Secret file exposure",
                status=Status.PASS,
                severity=Severity.LOW,
                message="No unignored sensitive or secret files were detected.",
                recommendation="No action needed.",
            )
        ]
