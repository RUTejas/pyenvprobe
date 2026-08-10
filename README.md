# pyenvprobe

[![PyPI version](https://img.shields.io/pypi/v/pyenvprobe.svg)](https://pypi.org/project/pyenvprobe/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyenvprobe.svg)](https://pypi.org/project/pyenvprobe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`pyenvprobe` is a lightweight, framework-agnostic Python developer tool that scans your Python projects to diagnose their configuration, code-quality tooling, Git setups, dependency definitions, documentation completeness, and overall repository health.

It helps developers quickly check if a Python repository is built, configured, and cleaned according to modern ecosystem standards.

## Why it exists

While tools like `ruff` lint code, `mypy` checks types, and `pip-audit` scans vulnerabilities, `pyenvprobe` acts as a meta-scanner:
1. **Tooling Checkup**: Verifies if these tools (Ruff, Black, pytest, mypy) are actually configured and present in your configuration files.
2. **Hygiene Auditor**: Detects unignored temporary files (like `.DS_Store`), build artifacts (like `build/`, `dist/`), and caches (like `__pycache__`) that might leak into version control.
3. **Completeness Checkup**: Ensures essential project meta-files (README with installation/usage sections, LICENSE, `.gitignore`, tests directory) exist.

---

## Installation

Install `pyenvprobe` with `pip`:

```bash
pip install pyenvprobe
```

To enable **Smart AI Auto-Fixes**, install with the `ai` extra:
```bash
pip install pyenvprobe[ai]
```

---

## Basic Usage

Run the doctor in your current project directory:

```bash
pyenvprobe
```

Or target a specific path:

```bash
pyenvprobe ./my-project-path
```

### Python API Usage

You can also import `pyenvprobe` into your own scripts for custom integrations or CI steps:

```python
from pathlib import Path
from pyenvprobe.scanner import scan_project
from pyenvprobe.checks import run_all_checks
from pyenvprobe.scoring import calculate_health_score

# 1. Scan your project directory
context = scan_project(Path("./my-project"))

# 2. Run the diagnostic checks
results = run_all_checks(context)

# 3. Calculate health score
score = calculate_health_score(results)
print(f"Project Health Score: {score}/100")
```

### CLI Options

`pyenvprobe` offers several useful arguments:

- `path`: (Optional) Path to target directory (default: `.`).
- `-v, --verbose`: Print detailed diagnostic explanations and recommendations for all checks.
- `-q, --quiet`: Suppress all normal stdout output.
- `--json`: Output check results in structured, stable JSON.
- `--fix`: Interactively prompt to automatically resolve supported issues (like generating `.gitignore` or `tests/`).
- `--ai`: Supercharges `--fix` with Smart AI Auto-Fixes. Generates missing docstrings and READMEs by analyzing your codebase context. Requires `PYENVPROBE_API_KEY` (or `OPENAI_API_KEY`) in your environment.
- `--ci`: Run in Continuous Integration mode (affects exit codes).
- `--threshold <int>`: Target minimum health score to pass in CI mode (default: `80`).
- `--category <category_name>`: Only run checks in a specific category (e.g. `git`, `documentation`). Specify multiple times or as comma-separated values to select multiple categories.

---

## Example Output

### Terminal Output
```
pyenvprobe Checkup
────────────────────────────────

Python
  ✓ Python files detected
  ✓ Python version configured

Structure
  ✓ pyproject.toml found
  ✓ Requirements file found
  ✓ Tests directory found
  ✓ Project structure layout

Testing
  ✓ Test configuration found

Tooling
  ✓ Code quality configuration found

Git
  ✓ Git repository detected
  ✓ .gitignore found
  ✓ Cache directories ignored

Documentation
  ✓ README found
  ✓ LICENSE found
  ✓ README completeness

Dependencies
  ✓ Dependencies defined
  ✓ Unpinned dependencies

Hygiene
  ✓ Repository hygiene
  ✓ Large files found

Security
  ✓ Secret file exposure

────────────────────────────────
Project health: 100/100
```

### JSON Output (`--json`)
```json
{
  "project_path": "/projects/my-app",
  "score": 90,
  "summary": {
    "total": 18,
    "pass": 16,
    "warn": 2,
    "fail": 0,
    "skip": 0,
    "info": 0
  },
  "results": [
    {
      "id": "PD103",
      "category": "structure",
      "title": "Tests directory found",
      "status": "FAIL",
      "severity": "MEDIUM",
      "message": "No test directory ('tests/' or 'test/') was found.",
      "recommendation": "Create a 'tests/' directory in your project root to organize unit and integration tests.",
      "metadata": {}
    }
  ]
}
```

---

## Exit Codes

- `0`: Scan completed successfully. In `--ci` mode, indicates that the project health score meets the threshold and no `CRITICAL` severity failures are detected.
- `1`: (Only with `--ci`) Indicates that the health score is below the threshold or one or more `CRITICAL` severity checks failed.
- `2`: Invalid CLI usage, non-existent target directory, or target path is not a directory.

---

## Security & Privacy

`pyenvprobe` is built with a security-first philosophy:
- **Local-Only**: All checks run locally on your machine. By default, no source code or file contents are sent to external servers. If you explicitly use the `--ai` flag, only context for the targeted fix (e.g. function signatures) is sent to the LLM via your API key.
- **Read-Only by Default**: The standard scanner will never modify, create, delete, or overwrite any of your project files. It only suggests fixes. If you explicitly pass the `--fix` flag, you are interactively prompted before any file is touched.
- **Safe Secrets Detection**: Scans for files that might leak secrets (like `.env` or `.pem`), but only flags their unignored presence. It never reads or prints secret key values.

---

## Supported Checks

A full list of check codes, categories, and descriptions can be found in [docs/CHECKS.md](file:///c:/Downloads/opensource%20101/docs/CHECKS.md).

---

## Development & Contribution

See [CONTRIBUTING.md](file:///c:/Downloads/opensource%20101/CONTRIBUTING.md) for environment setup and instructions for running the test suite.

---

## Roadmap

Future checks and configurations under consideration:
- Integration with lockfile validation (Pipfile, poetry.lock, pdm.lock).
- Auto-fixing syntax formatting directly from Ruff/Black outputs.
- ML-powered tech debt and vulnerability predictions based on git histories.
