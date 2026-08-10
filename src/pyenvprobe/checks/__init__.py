from __future__ import annotations

from typing import Callable

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
from pyenvprobe.checks.python import (
    check_missing_docstrings,
    check_python_project,
    check_python_version,
)
from pyenvprobe.checks.structure import (
    check_project_layout,
    check_pyproject_toml,
    check_requirements_txt,
    check_tests_dir,
)
from pyenvprobe.checks.testing import check_missing_tests, check_testing_config
from pyenvprobe.checks.tooling import check_tooling_config
from pyenvprobe.models import CheckResult, ProjectContext

# Registry of check functions
ALL_CHECKS: list[Callable[[ProjectContext], list[CheckResult]]] = [
    # Python
    check_python_project,
    check_python_version,
    check_missing_docstrings,
    # Structure
    check_pyproject_toml,
    check_requirements_txt,
    check_tests_dir,
    check_project_layout,
    # Git
    check_git_repo,
    check_gitignore_present,
    check_caches_gitignored,
    # Documentation
    check_readme_present,
    check_license_present,
    check_readme_contents,
    # Testing
    check_testing_config,
    check_missing_tests,
    # Tooling
    check_tooling_config,
    # Dependencies / hygiene / security
    check_dependencies_defined,
    check_unpinned_dependencies,
    check_unwanted_files,
    check_large_files,
    check_secrets_exposed,
]


def run_all_checks(
    context: ProjectContext, categories: list[str] | None = None
) -> list[CheckResult]:
    """Runs all registered checks and optionally filters by categories."""
    results = []
    for check_fn in ALL_CHECKS:
        try:
            check_results = check_fn(context)
            for res in check_results:
                if categories is None or res.category in categories:
                    results.append(res)
        except Exception as e:
            # Shield check execution from unexpected crashes
            # We can log this or add it to scanned errors
            context.errors.append(f"Check {check_fn.__name__} failed: {e}")
    return results
