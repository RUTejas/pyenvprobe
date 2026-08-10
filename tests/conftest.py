from __future__ import annotations

import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """Provides a temporary directory path that is cleaned up after the test."""
    temp_dir = tempfile.mkdtemp()
    path = Path(temp_dir)
    yield path
    shutil.rmtree(temp_dir, ignore_errors=True)
