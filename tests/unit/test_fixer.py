import tempfile
from pathlib import Path
from unittest.mock import patch

from pyenvprobe.fixer import (
    append_to_gitignore,
    create_gitignore,
    create_tests_dir,
    init_git_repo,
)
from pyenvprobe.models import ProjectContext


@patch("pyenvprobe.fixer.subprocess.run")
def test_init_git_repo(mock_run):
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(root_path=tmp_path)
        res = init_git_repo(context)
        assert "Initialized" in res
        mock_run.assert_called_once()


def test_create_gitignore():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(root_path=tmp_path)
        res = create_gitignore(context)
        assert "Created" in res
        assert (tmp_path / ".gitignore").exists()
        assert ".pytest_cache" in (tmp_path / ".gitignore").read_text(encoding="utf-8")


def test_append_to_gitignore():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(root_path=tmp_path)
        res = append_to_gitignore(context, ["my_secret.env"])
        assert "Appended" in res
        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert "my_secret.env" in content
        assert "Auto-added by pyenvprobe" in content


def test_create_tests_dir():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(root_path=tmp_path)
        res = create_tests_dir(context)
        assert "Created" in res
        assert (tmp_path / "tests").is_dir()
        assert (tmp_path / "tests" / "__init__.py").exists()
