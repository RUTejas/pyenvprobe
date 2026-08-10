import subprocess

from pyenvprobe.models import CheckResult, ProjectContext

DEFAULT_GITIGNORE = """
# Python caches
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Build artifacts
build/
dist/
*.egg-info/
*.egg

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""


def init_git_repo(context: ProjectContext) -> str | None:
    try:
        subprocess.run(
            ["git", "init"],
            cwd=context.root_path,
            check=True,
            capture_output=True,
            text=True,
        )
        return "Initialized an empty Git repository."
    except Exception as e:
        return f"Failed to initialize Git repository: {e}"


def create_gitignore(context: ProjectContext) -> str | None:
    path = context.root_path / ".gitignore"
    if path.exists():
        return ".gitignore already exists."
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(DEFAULT_GITIGNORE.strip() + "\n")
        return "Created standard Python .gitignore."
    except Exception as e:
        return f"Failed to create .gitignore: {e}"


def append_to_gitignore(
    context: ProjectContext, paths_to_ignore: list[str]
) -> str | None:
    path = context.root_path / ".gitignore"
    try:
        if not path.exists():
            create_gitignore(context)
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n# Auto-added by pyenvprobe\n")
            for p in paths_to_ignore:
                f.write(f"{p}\n")
        return f"Appended {len(paths_to_ignore)} items to .gitignore."
    except Exception as e:
        return f"Failed to append to .gitignore: {e}"


def create_tests_dir(context: ProjectContext) -> str | None:
    path = context.root_path / "tests"
    if path.exists():
        return "Tests directory already exists."
    try:
        path.mkdir(exist_ok=True)
        (path / "__init__.py").touch(exist_ok=True)
        return "Created tests/ directory with __init__.py."
    except Exception as e:
        return f"Failed to create tests directory: {e}"


def apply_fix(context: ProjectContext, result: CheckResult) -> str | None:
    """Applies the fix corresponding to the check ID and returns a success message or error."""
    if not result.fixable:
        return None

    if result.id == "PD201":
        return init_git_repo(context)
    elif result.id == "PD202":
        return create_gitignore(context)
    elif result.id == "PD203":
        unignored = result.metadata.get("unignored_caches", [])
        return append_to_gitignore(context, unignored) if unignored else None
    elif result.id == "PD701":
        unwanted = result.metadata.get("unwanted_files", [])
        return append_to_gitignore(context, unwanted) if unwanted else None
    elif result.id == "PD703":
        exposed = result.metadata.get("exposed_secrets", [])
        return append_to_gitignore(context, exposed) if exposed else None
    elif result.id == "PD103":
        return create_tests_dir(context)

    return None
