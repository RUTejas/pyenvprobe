# Contributing to pyenvcheck

Welcome! We are excited that you want to contribute to `pyenvcheck`.

## Developer Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/pyenvcheck/pyenvcheck.git
   cd pyenvcheck
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -e ".[dev]"
   ```

## Running Quality Checks

We use `pytest` for testing and `ruff` for linting/formatting.

- Run tests:
  ```bash
  pytest
  ```

- Run linter:
  ```bash
  ruff check src tests
  ```

- Run formatter check:
  ```bash
  ruff format --check src tests
  ```

- Run static type checker:
  ```bash
  mypy src
  ```

## Designing New Checks
All checks live under [src/pyenvcheck/checks/](file:///c:/Downloads/opensource%20101/src/pyenvcheck/checks/).
1. Implement the check inside the appropriate category file.
2. Register the check function in `src/pyenvcheck/checks/__init__.py`.
3. Provide a stable `PDxxx` identifier, severity, and category.
4. Add unit tests for healthy/failing scenarios in `tests/`.
