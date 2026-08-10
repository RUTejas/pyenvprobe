import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from pyenvprobe.models import ProjectContext


def test_ai_generate_readme():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(
            root_path=tmp_path,
            pyproject={"project": {"name": "TestProj", "description": "A test."}},
        )

        with patch.dict(os.environ, {"PYENVPROBE_API_KEY": "dummy_key"}):
            with patch("pyenvprobe.ai.OpenAI") as mock_openai:
                # Mock the response
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "# TestProj\nA test README."
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from pyenvprobe.ai import PyEnvProbeAI

                ai = PyEnvProbeAI()
                res = ai.generate_readme(context)

                assert "Generated and saved" in res
                assert (tmp_path / "README.md").exists()
                assert "TestProj" in (tmp_path / "README.md").read_text(
                    encoding="utf-8"
                )


def test_ai_generate_docstrings():
    with tempfile.TemporaryDirectory() as td:
        tmp_path = Path(td)
        context = ProjectContext(root_path=tmp_path)
        missing_nodes = [{"file": "test.py", "name": "my_func", "lineno": 1}]

        with patch.dict(os.environ, {"PYENVPROBE_API_KEY": "dummy_key"}):
            with patch("pyenvprobe.ai.OpenAI") as mock_openai:
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[
                    0
                ].message.content = '"""This is a test docstring."""'
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                from pyenvprobe.ai import PyEnvProbeAI

                ai = PyEnvProbeAI()
                res = ai.generate_docstrings(context, missing_nodes)

                assert "Generated docstrings" in res
                assert (tmp_path / "AI_DOCSTRINGS.md").exists()
                assert "test docstring" in (tmp_path / "AI_DOCSTRINGS.md").read_text(
                    encoding="utf-8"
                )
