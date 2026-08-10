# pyenvcheck

`pyenvcheck` is a lightweight, framework-agnostic Python developer tool that scans your Python projects to diagnose their configuration, code-quality tooling, Git setups, dependency definitions, documentation completeness, and overall repository health.

It helps developers quickly check if a Python repository is built, configured, and cleaned according to modern ecosystem standards.

## Why it exists

While tools like `ruff` lint code, `mypy` checks types, and `pip-audit` scans vulnerabilities, `pyenvcheck` acts as a meta-scanner:
1. **Tooling Checkup**: Verifies if these tools (Ruff, Black, pytest, mypy) are actually configured and present in your configuration files.
2. **Hygiene Auditor**: Detects unignored temporary files (like `.DS_Store`), build artifacts (like `build/`, `dist/`), and caches (like `__pycache__`) that might leak into version control.
3. **Completeness Checkup**: Ensures essential project meta-files (README with installation/usage sections, LICENSE, `.gitignore`, tests directory) exist.

---

## Installation

Install `pyenvcheck` with `pip`:

```bash
pip install pyenvcheck
```

---

## Basic Usage

Run the doctor in your current project directory:

```bash
pyenvcheck
```

Or target a specific path:

```bash
pyenvcheck ./my-project-path
```

### CLI Options

`pyenvcheck` offers several useful arguments:

- `path`: (Optional) Path to target directory (default: `.`).
- `-v, --verbose`: Print detailed diagnostic explanations and recommendations for all checks.
- `-q, --quiet`: Suppress all normal stdout output.
- `--json`: Output check results in structured, stable JSON.
- `--ci`: Run in Continuous Integration mode (affects exit codes).
- `--threshold <int>`: Target minimum health score to pass in CI mode (default: `80`).
- `--category <category_name>`: Only run checks in a specific category (e.g. `git`, `documentation`). Specify multiple times or as comma-separated values to select multiple categories.

---

## Example Output

### Terminal Output
```
pyenvcheck Checkup
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

`pyenvcheck` is built with a security-first philosophy:
- **Local-Only**: All checks run locally on your machine. No source code or file contents are sent to external servers.
- **Read-Only**: The tool will never modify, create, delete, or overwrite any of your project files.
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
- `pyenvcheck fix`: Interactive prompt to safely generate recommended configurations (like `.gitignore` or boilerplate configurations for Ruff).
- Integration with lockfile validation (Pipfile, poetry.lock, pdm.lock).
