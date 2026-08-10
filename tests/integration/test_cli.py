from __future__ import annotations

import json
from pathlib import Path

import pytest

from pyenvcheck.cli import main


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "pyenvcheck" in captured.out
    assert "--json" in captured.out


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "pyenvcheck 0.1.0" in captured.out


def test_cli_invalid_path(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["/non-existent-directory-abc-123"])
    assert exit_code == 2
    captured = capsys.readouterr()
    assert "Error: Path" in captured.err


def test_cli_run_success(
    temp_project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Set up basic project
    (temp_project / "src").mkdir()
    (temp_project / "src" / "main.py").write_text("print('hello')")
    (temp_project / "pyproject.toml").write_text(
        "[project]\nname='test'\nrequires-python = '>=3.9'\ndependencies = ['requests>=2.0.0']\n"
        "[tool.pytest.ini_options]\n"
        "[tool.ruff]\n"
    )
    (temp_project / "README.md").write_text(
        "# Test Project\n\n## Installation\npip install .\n\n## Usage\npython main.py"
    )
    (temp_project / "LICENSE").write_text("MIT License")
    (temp_project / "tests").mkdir()
    (temp_project / ".git").mkdir()
    (temp_project / ".gitignore").write_text("__pycache__/")

    # Run check
    exit_code = main([str(temp_project)])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "pyenvcheck Checkup" in captured.out
    assert "Python files detected" in captured.out
    assert "100/100" in captured.out


def test_cli_json_output(
    temp_project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (temp_project / "main.py").write_text("print('hello')")

    exit_code = main([str(temp_project), "--json"])
    assert exit_code == 0
    captured = capsys.readouterr()

    # Try parsing JSON
    data = json.loads(captured.out)
    assert "score" in data
    assert "results" in data
    assert len(data["results"]) > 0


def test_cli_category_filter(
    temp_project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (temp_project / "main.py").write_text("print('hello')")

    exit_code = main([str(temp_project), "--category", "python"])
    assert exit_code == 0
    captured = capsys.readouterr()

    assert "Python" in captured.out
    assert "Structure" not in captured.out  # Should be filtered out


def test_cli_ci_mode_pass(temp_project: Path) -> None:
    # Setup healthy project
    (temp_project / "main.py").write_text("print('hello')")
    (temp_project / "pyproject.toml").write_text(
        "[project]\nname='test'\nrequires-python = '>=3.9'"
    )
    (temp_project / "README.md").write_text(
        "# Test Project\n\n## Installation\npip install .\n\n## Usage\npython main.py"
    )
    (temp_project / "LICENSE").write_text("MIT License")
    (temp_project / "tests").mkdir()
    (temp_project / ".git").mkdir()
    (temp_project / ".gitignore").write_text("__pycache__/")

    exit_code = main([str(temp_project), "--ci"])
    assert exit_code == 0


def test_cli_ci_mode_fail(
    temp_project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Setup poor project (many missing elements, health score will be low)
    (temp_project / "main.py").write_text("print('hello')")

    exit_code = main([str(temp_project), "--ci", "--threshold", "90"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "CI Failure" in captured.err
