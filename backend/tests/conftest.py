from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.storage import init_db


@pytest.fixture
def tmp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    db = init_db(db_path)
    yield db
    db.close()
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def mock_status():
    mock_path = Path(__file__).parent.parent.parent / "frontend" / "mock-data" / "status.json"
    return json.loads(mock_path.read_text())
