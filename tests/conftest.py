from pathlib import Path

import pytest

KB_DIR = Path(__file__).resolve().parent.parent / "src" / "dermavision" / "modules" / "rules" / "kb"


@pytest.fixture
def kb_dir() -> Path:
    return KB_DIR
