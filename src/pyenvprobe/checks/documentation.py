from __future__ import annotations

from pyenvprobe.models import CheckResult, ProjectContext, Severity, Status

README_NAMES = {"readme.md", "readme.rst", "readme.txt", "readme"}
LICENSE_NAMES = {"license", "license.md", "license.txt", "copying", "copying.txt"}


def check_readme_present(context: ProjectContext) -> list[CheckResult]:
    """Checks if a README file is present in the project root."""
    readme_file = None
    for f in context.files:
        if "/" not in f and f.lower() in README_NAMES:
            readme_file = f
            break

    if readme_file:
        return [
            CheckResult(
                id="PD301",
                category="documentation",
                title="README found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"README file found: '{readme_file}'",
                recommendation="No action needed.",
                metadata={"readme_file": readme_file},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD301",
                category="documentation",
                title="README found",
                status=Status.FAIL,
                severity=Severity.HIGH,
                message="No README file was found in the project root.",
                recommendation="Create a README.md file in the root of your project to document its purpose and usage.",
            )
        ]


def check_license_present(context: ProjectContext) -> list[CheckResult]:
    """Checks if a LICENSE file is present in the project root."""
    license_file = None
    for f in context.files:
        if "/" not in f and f.lower() in LICENSE_NAMES:
            license_file = f
            break

    if license_file:
        return [
            CheckResult(
                id="PD302",
                category="documentation",
                title="LICENSE found",
                status=Status.PASS,
                severity=Severity.LOW,
                message=f"LICENSE file found: '{license_file}'",
                recommendation="No action needed.",
                metadata={"license_file": license_file},
            )
        ]
    else:
        return [
            CheckResult(
                id="PD302",
                category="documentation",
                title="LICENSE found",
                status=Status.FAIL,
                severity=Severity.HIGH,
                message="No LICENSE file was found in the project root.",
                recommendation="Add a LICENSE file (e.g. MIT, Apache 2.0) to declare permissions for your project.",
            )
        ]


def check_readme_contents(context: ProjectContext) -> list[CheckResult]:
    """Validates that the README contains installation and usage sections."""
    readme_file = None
    for f in context.files:
        if "/" not in f and f.lower() in README_NAMES:
            readme_file = f
            break

    if not readme_file:
        return [
            CheckResult(
                id="PD303",
                category="documentation",
                title="README completeness",
                status=Status.SKIP,
                severity=Severity.LOW,
                message="Skipped: README file is missing.",
                recommendation="Create a README first.",
            )
        ]

    # Read README content
    readme_path = context.root_path / readme_file
    try:
        with open(readme_path, encoding="utf-8", errors="ignore") as readme_file_obj:
            content = readme_file_obj.read(50000).lower()  # Read up to 50KB
    except Exception as e:
        return [
            CheckResult(
                id="PD303",
                category="documentation",
                title="README completeness",
                status=Status.WARN,
                severity=Severity.LOW,
                message=f"Could not read README file content: {e}",
                recommendation="Verify README file permissions and encoding.",
            )
        ]

    has_install = "install" in content or "setup" in content or "bootstrap" in content
    has_usage = (
        "usage" in content or "quickstart" in content or "getting started" in content
    )

    missing = []
    if not has_install:
        missing.append("Installation")
    if not has_usage:
        missing.append("Usage")

    if not missing:
        return [
            CheckResult(
                id="PD303",
                category="documentation",
                title="README completeness",
                status=Status.PASS,
                severity=Severity.LOW,
                message="README contains installation and usage instructions.",
                recommendation="No action needed.",
            )
        ]
    else:
        missing_str = " and ".join(missing)
        return [
            CheckResult(
                id="PD303",
                category="documentation",
                title="README completeness",
                status=Status.WARN,
                severity=Severity.LOW,
                message=f"README appears to be missing standard sections: {missing_str}",
                recommendation=f"Add clear instructions for {missing_str} in your README file.",
                metadata={"missing_sections": missing},
            )
        ]
