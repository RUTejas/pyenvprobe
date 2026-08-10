from __future__ import annotations

from pathlib import Path

from pyenvprobe.checks.dependencies import (
    check_dependencies_defined,
    check_large_files,
    check_secrets_exposed,
    check_unpinned_dependencies,
    check_unwanted_files,
)
from pyenvprobe.checks.documentation import (
    check_license_present,
    check_readme_contents,
    check_readme_present,
)
from pyenvprobe.checks.git import (
    check_caches_gitignored,
    check_git_repo,
    check_gitignore_present,
)
from pyenvprobe.checks.python import check_python_project, check_python_version
from pyenvprobe.checks.structure import (
    check_project_layout,
    check_pyproject_toml,
    check_requirements_txt,
    check_tests_dir,
)
from pyenvprobe.checks.testing import check_testing_config
from pyenvprobe.checks.tooling import check_tooling_config
from pyenvprobe.models import Status
from pyenvprobe.scanner import GitignoreMatcher, scan_project


def test_gitignore_matcher() -> None:
    content = """
# comment
__pycache__/
*.bak
/.venv
!/important.bak
    """
    matcher = GitignoreMatcher(Path("/dummy"), content)

    # Test directory matching
    assert matcher.is_ignored("__pycache__", is_dir=True) is True
    assert matcher.is_ignored("src/__pycache__", is_dir=True) is True

    # Test file matching with wildcard
    assert matcher.is_ignored("file.bak", is_dir=False) is True
    assert matcher.is_ignored("src/file.bak", is_dir=False) is True

    # Test root-level matching
    assert matcher.is_ignored(".venv", is_dir=True) is True
    assert matcher.is_ignored("src/.venv", is_dir=True) is False

    # Test negation
    assert matcher.is_ignored("important.bak", is_dir=False) is False


def test_scanner_basic(temp_project: Path) -> None:
    # Set up files
    (temp_project / "src").mkdir()
    (temp_project / "src" / "main.py").write_text("print('hello')")
    (temp_project / ".git").mkdir()
    (temp_project / ".git" / "config").write_text("")
    (temp_project / ".venv").mkdir()
    (temp_project / ".venv" / "some_lib.py").write_text("")  # skipped dir
    (temp_project / "pyproject.toml").write_text("[project]\nname='test'")

    context = scan_project(temp_project)

    assert "src/main.py" in context.files
    # Verify we did NOT walk into skipped directories
    assert ".venv/some_lib.py" not in context.files
    assert ".git/config" not in context.files

    assert context.git_info["is_repo"] is True
    assert context.pyproject["project"]["name"] == "test"


def test_python_checks(temp_project: Path) -> None:
    context_empty = scan_project(temp_project)
    res_empty = check_python_project(context_empty)[0]
    assert res_empty.status == Status.FAIL

    (temp_project / "main.py").write_text("")
    context_py = scan_project(temp_project)
    res_py = check_python_project(context_py)[0]
    assert res_py.status == Status.PASS


def test_python_version(temp_project: Path) -> None:
    # 1. Missing
    (temp_project / "pyproject.toml").write_text("[project]\nname='test'")
    context = scan_project(temp_project)
    assert check_python_version(context)[0].status == Status.WARN

    # 2. Present PEP 621
    (temp_project / "pyproject.toml").write_text("[project]\nrequires-python = '>=3.9'")
    context = scan_project(temp_project)
    res = check_python_version(context)[0]
    assert res.status == Status.PASS
    assert res.metadata["requires_python"] == ">=3.9"


def test_structure_checks(temp_project: Path) -> None:
    # Test pyproject.toml
    context = scan_project(temp_project)
    assert check_pyproject_toml(context)[0].status == Status.FAIL

    (temp_project / "pyproject.toml").write_text("")
    context = scan_project(temp_project)
    assert check_pyproject_toml(context)[0].status == Status.PASS

    # Test requirements files
    assert check_requirements_txt(context)[0].status == Status.WARN

    (temp_project / "requirements.txt").write_text("requests==2.31.0")
    context = scan_project(temp_project)
    res_req = check_requirements_txt(context)[0]
    assert res_req.status == Status.PASS
    assert "requirements.txt" in res_req.metadata["requirements_files"]

    # Test tests directory
    assert check_tests_dir(context)[0].status == Status.FAIL
    (temp_project / "tests").mkdir()
    context = scan_project(temp_project)
    assert check_tests_dir(context)[0].status == Status.PASS

    # Test layout
    # Currently empty
    assert check_project_layout(context)[0].status == Status.WARN
    # Flat package
    (temp_project / "mypackage").mkdir()
    (temp_project / "mypackage" / "__init__.py").write_text("")
    context = scan_project(temp_project)
    assert check_project_layout(context)[0].status == Status.PASS

    # Src layout
    (temp_project / "src").mkdir()
    context = scan_project(temp_project)
    assert check_project_layout(context)[0].status == Status.PASS


def test_git_checks(temp_project: Path) -> None:
    context = scan_project(temp_project)
    assert check_git_repo(context)[0].status == Status.FAIL
    assert check_gitignore_present(context)[0].status == Status.FAIL

    # Setup git repo
    (temp_project / ".git").mkdir()
    (temp_project / ".gitignore").write_text("")
    context = scan_project(temp_project)
    assert check_git_repo(context)[0].status == Status.PASS
    assert check_gitignore_present(context)[0].status == Status.PASS


def test_caches_gitignored(temp_project: Path) -> None:
    # 1. Cache folder exists but not ignored
    (temp_project / ".git").mkdir()
    (temp_project / "__pycache__").mkdir()
    (temp_project / "__pycache__" / "file.pyc").write_text("")
    context = scan_project(temp_project)
    assert check_caches_gitignored(context)[0].status == Status.WARN

    # 2. Add gitignore
    (temp_project / ".gitignore").write_text("__pycache__/")
    context = scan_project(temp_project)
    assert check_caches_gitignored(context)[0].status == Status.PASS


def test_doc_checks(temp_project: Path) -> None:
    context = scan_project(temp_project)
    assert check_readme_present(context)[0].status == Status.FAIL
    assert check_license_present(context)[0].status == Status.FAIL
    assert check_readme_contents(context)[0].status == Status.SKIP

    # Add files
    (temp_project / "README.md").write_text(
        "# My project\n\n## Installation\npip install .\n\n## Usage\npython -m myproject"
    )
    (temp_project / "LICENSE").write_text("MIT License")
    context = scan_project(temp_project)
    assert check_readme_present(context)[0].status == Status.PASS
    assert check_license_present(context)[0].status == Status.PASS
    assert check_readme_contents(context)[0].status == Status.PASS


def test_readme_incomplete(temp_project: Path) -> None:
    (temp_project / "README.md").write_text("# Incomplete README")
    context = scan_project(temp_project)
    res = check_readme_contents(context)[0]
    assert res.status == Status.WARN
    assert "missing_sections" in res.metadata


def test_testing_and_tooling_configs(temp_project: Path) -> None:
    context = scan_project(temp_project)
    assert check_testing_config(context)[0].status == Status.WARN
    assert check_tooling_config(context)[0].status == Status.WARN

    # Add to pyproject.toml
    (temp_project / "pyproject.toml").write_text(
        "[tool.pytest.ini_options]\naddopts = '-v'\n[tool.ruff]\nline-length = 88"
    )
    context = scan_project(temp_project)
    assert check_testing_config(context)[0].status == Status.PASS
    assert check_tooling_config(context)[0].status == Status.PASS


def test_dependency_checks(temp_project: Path) -> None:
    # No deps
    context = scan_project(temp_project)
    assert check_dependencies_defined(context)[0].status == Status.WARN
    assert check_unpinned_dependencies(context)[0].status == Status.PASS

    # Pinned requirements
    (temp_project / "requirements.txt").write_text("requests==2.31.0\npytest>=7.0")
    context = scan_project(temp_project)
    assert check_dependencies_defined(context)[0].status == Status.PASS
    assert check_unpinned_dependencies(context)[0].status == Status.PASS

    # Unpinned requirements
    (temp_project / "requirements.txt").write_text("requests\npytest")
    context = scan_project(temp_project)
    assert check_unpinned_dependencies(context)[0].status == Status.WARN


def test_unwanted_large_secrets(temp_project: Path) -> None:
    # Temporary files
    (temp_project / "file.bak").write_text("backup")
    (temp_project / ".DS_Store").write_text("")
    (temp_project / ".env").write_text("API_KEY=123")

    # Mock a large file
    (temp_project / "large_binary.bin").write_bytes(b"\x00" * (6 * 1024 * 1024))

    context = scan_project(temp_project)

    # 1. Unwanted files check
    res_hygiene = check_unwanted_files(context)[0]
    assert res_hygiene.status == Status.WARN
    assert "file.bak" in res_hygiene.metadata["unwanted_files"]
    assert ".DS_Store" in res_hygiene.metadata["unwanted_files"]

    # 2. Large files check
    res_large = check_large_files(context)[0]
    assert res_large.status == Status.WARN
    assert "large_binary.bin" in [
        item["path"] for item in res_large.metadata["large_files"]
    ]

    # 3. Secrets check
    res_secrets = check_secrets_exposed(context)[0]
    assert res_secrets.status == Status.FAIL
    assert ".env" in res_secrets.metadata["exposed_secrets"]
