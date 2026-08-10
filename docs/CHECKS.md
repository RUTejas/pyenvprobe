# Diagnostic Checks in pyenvcheck

This document outlines the list of diagnostic checks supported by `pyenvcheck` MVP.

## Summary of Checks

| ID | Category | Title | Default Severity | Description |
|---|---|---|---|---|
| `PD001` | `python` | Python project detected | `CRITICAL` | Verifies the presence of `.py` files in the workspace. |
| `PD002` | `python` | Python version configured | `MEDIUM` | Verifies if target Python version (`requires-python`) is specified in `pyproject.toml`. |
| `PD101` | `structure` | pyproject.toml found | `HIGH` | Checks if `pyproject.toml` exists in the root directory. |
| `PD102` | `structure` | Requirements file found | `LOW` | Checks for `requirements.txt` or standard requirements files. |
| `PD103` | `structure` | Tests directory found | `MEDIUM` | Checks if a `tests/` or `test/` directory is present. |
| `PD104` | `structure` | Project structure layout | `LOW` | Checks if project uses a standard layout (e.g., `src/` layout or clean flat layout). |
| `PD201` | `git` | Git repository detected | `HIGH` | Checks if the directory is a Git repository. |
| `PD202` | `git` | .gitignore found | `HIGH` | Verifies that a `.gitignore` file exists in the root directory. |
| `PD203` | `git` | Cache directories ignored | `MEDIUM` | Checks if common Python caches (e.g., `__pycache__`, `.pytest_cache`) are gitignored. |
| `PD301` | `documentation` | README found | `HIGH` | Checks if `README.md`, `README.rst`, or `README` exists. |
| `PD302` | `documentation` | LICENSE found | `HIGH` | Checks if a LICENSE file exists in the root directory. |
| `PD303` | `documentation` | README completeness | `LOW` | Checks if README contains standard sections (Installation, Usage). |
| `PD401` | `testing` | Test configuration found | `LOW` | Checks if testing framework (pytest, unittest) is configured. |
| `PD501` | `tooling` | Code quality configuration found | `LOW` | Checks if Ruff, Black, mypy, etc. are configured in `pyproject.toml` or config files. |
| `PD601` | `dependencies` | Dependencies defined | `LOW` | Checks if dependencies are specified in `pyproject.toml` or `requirements.txt`. |
| `PD602` | `dependencies` | Unpinned dependencies | `MEDIUM` | Checks if dependencies are completely unpinned. |
| `PD701` | `hygiene` | Repository hygiene | `MEDIUM` | Checks for temporary files or build artifacts that are not gitignored. |
| `PD702` | `hygiene` | Large files found | `MEDIUM` | Checks for files > 5MB in the project that are not gitignored. |
| `PD703` | `security` | Secret file exposure | `CRITICAL` | Scans for potential secret files (e.g. `.env`, private keys) that are not ignored. |

---

## Detailed Check Definitions

### `PD001` - Python project detected
- **Explanation**: If no Python files (`*.py`) are found in the project directory, `pyenvcheck` cannot perform meaningful analysis.
- **Recommendation**: Ensure you are running `pyenvcheck` in a directory containing Python code.

### `PD002` - Python version configured
- **Explanation**: Not specifying a target Python version makes it difficult for dependencies, linters, and type checkers to enforce correctness.
- **Recommendation**: Add `requires-python = ">=3.9"` under `[project]` in your `pyproject.toml`.

### `PD101` - pyproject.toml found
- **Explanation**: `pyproject.toml` is the modern standard configuration file for Python packaging and tools (PEP 518, PEP 621).
- **Recommendation**: Create a `pyproject.toml` in your project root to centralize configuration.

### `PD203` - Cache directories ignored
- **Explanation**: Committing local caches (like `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.venv`) bloats the repository.
- **Recommendation**: Add these directories to your `.gitignore`.

### `PD303` - README completeness
- **Explanation**: A good README should tell other developers how to install and run your project.
- **Recommendation**: Include sections for "Installation" and "Usage" in your README.

### `PD703` - Secret file exposure
- **Explanation**: Files like `.env`, private keys (`.pem`, `id_rsa`), and credentials should never be committed or left unignored.
- **Recommendation**: Add sensitive files to `.gitignore` and use environment variables instead of hardcoded secrets.
