import shutil
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent


@pytest.fixture
def desk(tmp_path, monkeypatch):
    shutil.copytree(PROJECT / "config", tmp_path / "config")
    monkeypatch.setenv("DESK_ROOT", str(tmp_path))
    monkeypatch.setenv("DESK_NO_NOTIFY", "1")
    return tmp_path
