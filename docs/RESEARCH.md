# Research: Python Repository Health Tooling

Before implementing `pyenvprobe`, we analyzed the Python tooling ecosystem to understand existing tools, identify gaps, and ensure `pyenvprobe` is lightweight, unique, and highly valuable without duplicating existing efforts.

## Existing Tools Investigated

### 1. Linters & Formatters (Ruff, Black, isort, flake8, pylint)
- **Purpose**: Enforce style, check for syntax bugs, format code, and sort imports.
- **Overlap**: `pyenvprobe` will NOT perform line-by-line static linting or formatting.
- **Identified Gap**: These tools assume you already have them configured and installed. They do not report if they are *missing* or if their configurations are invalid/inconsistent across the project.

### 2. Type Checkers (mypy, pyright)
- **Purpose**: Validate type hints and static types.
- **Overlap**: None. `pyenvprobe` will not run type analysis.
- **Identified Gap**: Many projects lack static type configuration or don't specify target Python versions. `pyenvprobe` will detect if a type checker config is present.

### 3. Testing Frameworks (pytest, unittest, tox)
- **Purpose**: Run unit and integration tests.
- **Overlap**: None. `pyenvprobe` does not execute tests.
- **Identified Gap**: Checks if `tests/` exists, whether the testing tools are configured, and if the tests are discoverable.

### 4. Dependency & Vulnerability Analyzers (pip-audit, bandit, deptry)
- **Purpose**: Check for vulnerable dependencies (`pip-audit`), security flaws in code (`bandit`), and unused/missing imports/dependencies (`deptry`).
- **Overlap**: None. `pyenvprobe` will not parse imports or check vulnerability databases.
- **Identified Gap**: `pyenvprobe` checks if dependencies are pinned, if they are configured correctly in `pyproject.toml` or `requirements.txt`, and whether lockfiles/tool configs exist.

### 5. Repository Cleanliness & Git
- **Purpose**: Version control and ignoring generated files.
- **Overlap**: None.
- **Identified Gap**: Many Python repositories commit unwanted cache directories (`__pycache__`, `.pytest_cache`, `.venv`) or large files (> 5MB) because their `.gitignore` is missing or incomplete. `pyenvprobe` scans for these specific issues.

---

## What pyenvprobe Will NOT Do
To remain lightweight, fast, and maintainable, `pyenvprobe` will intentionally avoid:
- Running actual test suites.
- Parsing Python Abstract Syntax Trees (AST) for linting/formatting rules.
- Querying external vulnerability databases (like PyPI or OSV).
- Automatically modifying source files (read-only by default).
- Spawning slow subprocesses of other tools unless explicitly requested.

---

## Gaps pyenvprobe Will Fill
1. **Bootstrap/Sanity Check**: Quickly answer: "Is this repository configured according to modern Python standards?"
2. **Hygiene Verification**: Detect unignored cache directories, large generated binaries, and leftover build artifacts.
3. **Completeness Check**: Ensure the presence of essential metadata (README with installation/usage instructions, LICENSE, `.gitignore`, tests).
4. **Tooling Discovery**: Check whether formatting, linting, testing, and typing tools are configured (e.g., Ruff, pytest, mypy).

---

## PyPI Name Check
- Package name `pyenvprobe` is available on PyPI.
- Similar package `doctor` exists but is a Flask parameter validation utility. No name conflicts exist.

---

## MVP Scope (Phase 1)
- Python project detection and minimum Python version verification.
- Metadata checks (README, LICENSE).
- Git repository sanity (presence of `.git` and `.gitignore`, ensuring caches/temporary files are ignored).
- Structure check (flat/src layout, tests folder).
- Tooling configuration detection (pytest, Ruff/Black/mypy).
- Local cache leak detection (unignored cache files).
- Obvious large file checking.
- Stable, documented JSON output format.
- A clean, beautiful CLI report with a health score.
