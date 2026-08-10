# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-11

### Added
- **Smart AI Auto-Fixes (`--ai`)**: Integrate an LLM directly into the CLI by setting the `PYENVPROBE_API_KEY` (or `OPENAI_API_KEY`) environment variable. Install the optional dependency via `pip install pyenvprobe[ai]`.
- **AI Docstring Generation (`PD403`)**: New AST-based check that finds missing Python docstrings and uses AI to safely generate and suggest PEP-257 compliant docstrings.
- **AI README Generation**: The `--ai` flag supercharges the documentation checks (`PD301`, `PD303`). It analyzes your project context and writes a beautiful, complete `README.md` for you.

## [0.2.0] - 2026-08-11

### Added
- **Auto-Fix Engine**: Interactive `--fix` flag to automatically resolve supported issues.
- **Git Initialization Fix (`PD201`)**: Automatically runs `git init`.
- **Gitignore Fixes (`PD202`, `PD203`, `PD701`, `PD703`)**: Automatically generates standard Python `.gitignore` files and safely appends missing caches, build artifacts, and exposed secrets.
- **Test Structure Fix (`PD103`)**: Creates `tests/` directory with `__init__.py`.
- **Python API Support**: Official support and documentation for importing `pyenvprobe` functions in Python scripts.

### Changed
- **Rebrand**: Fully renamed the internal module and CLI entrypoint to `pyenvprobe` to match the PyPI registry.
- **Community Standards**: Added `CODE_OF_CONDUCT.md`, Issue Templates, Pull Request Templates, and Dependabot for automated maintenance.

## [0.1.0] - 2026-08-09

### Added
- Initial project release.
- Directory scanner and target project analyzer.
- Core checkup plugins for python, structure, git, docs, tests, and dependencies.
- Beautiful, colorized CLI output showing categories and individual check results.
- Stable `--json` machine-readable output.
- `--ci` flag for pipeline integration with custom exit codes.
- Deterministic project health scoring system (0-100).
