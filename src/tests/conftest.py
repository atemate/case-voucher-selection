from pathlib import Path

import pytest


CURRENT_DIR = Path(__file__).parent
TESTS_DIR = CURRENT_DIR

PROJECT_ROOT = TESTS_DIR.parent.parent


@pytest.fixture
def project_root() -> Path:
    path = PROJECT_ROOT
    assert path.is_dir()
    ls = [p.name for p in path.iterdir()]
    assert "src" in ls, ls
    assert "data" in ls, ls
    return path


@pytest.fixture
def data_root(project_root: Path) -> Path:
    return project_root / "data"


@pytest.fixture
def all_orders_raw_path(data_root: Path) -> Path:
    # TODO: instead of reading the whole dataset, prepare a small part
    return data_root / "data.parquet"
