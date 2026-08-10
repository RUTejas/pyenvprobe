# JSON Schema: pyenvprobe Output

This document defines the schema for the JSON output when `pyenvprobe` is run with the `--json` option.

## JSON Schema Example

```json
{
  "project_path": "C:/projects/my-python-project",
  "score": 82,
  "summary": {
    "total": 15,
    "pass": 11,
    "warn": 3,
    "fail": 1,
    "skip": 0,
    "info": 0
  },
  "results": [
    {
      "id": "PD101",
      "category": "structure",
      "title": "pyproject.toml found",
      "status": "PASS",
      "severity": "LOW",
      "message": "pyproject.toml was found in the root directory.",
      "recommendation": "No action required.",
      "metadata": {
        "path": "pyproject.toml"
      }
    },
    {
      "id": "PD302",
      "category": "documentation",
      "title": "LICENSE found",
      "status": "FAIL",
      "severity": "HIGH",
      "message": "No LICENSE file was detected in the project root.",
      "recommendation": "Add a LICENSE file (e.g., MIT, Apache-2.0) to your repository root.",
      "metadata": {}
    }
  ]
}
```

## Field Specifications

- **`project_path`** (string): Absolute path of the directory checked.
- **`score`** (integer): Calculated project health score from `0` to `100`.
- **`summary`** (object): Summary counts of the statuses for all checks:
  - `total` (integer): Total number of checks run.
  - `pass` (integer)
  - `warn` (integer)
  - `fail` (integer)
  - `skip` (integer)
  - `info` (integer)
- **`results`** (array of objects): Detailed check outcomes.
  - **`id`** (string): Stable check identifier (e.g., `PD001`).
  - **`category`** (string): The category of the check (`python`, `structure`, `git`, `documentation`, `testing`, `tooling`, `dependencies`, `hygiene`, `security`).
  - **`title`** (string): Short human-readable check name.
  - **`status`** (string): One of `PASS`, `WARN`, `FAIL`, `SKIP`, `INFO`.
  - **`severity`** (string): One of `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
  - **`message`** (string): Explanatory finding text.
  - **`recommendation`** (string): Concrete instruction to fix the issue.
  - **`metadata`** (object): Optional check-specific data (e.g. lists of files, versions detected).
