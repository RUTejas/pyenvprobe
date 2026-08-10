# Contributing to pyenvprobe

Welcome! We are excited that you want to contribute to `pyenvprobe`.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## Developer Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RUTejas/pyenvprobe.git
   cd pyenvprobe
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
All checks live under [src/pyenvprobe/checks/](src/pyenvprobe/checks/).
1. Implement the check inside the appropriate category file.
2. Register the check function in `src/pyenvprobe/checks/__init__.py`.
3. Provide a stable `PDxxx` identifier, severity, and category.
4. Add unit tests for healthy/failing scenarios in `tests/`.

## Submitting a Pull Request
1. Fork the repository and create your branch from `main`.
2. Make your changes and ensure tests and linters pass.
3. Open a Pull Request! A template will automatically be provided for you to fill out.
