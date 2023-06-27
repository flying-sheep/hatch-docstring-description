from pathlib import Path

import pytest

from hatch_docstring_description.read_description_hook import ReadDescriptionHook


@pytest.fixture
def basic_package(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("")
    pkg_dir = tmp_path / "src" / "mypkg"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text('"""A dosctring."""')
    yield pkg_dir


def test_basic(tmp_path, basic_package):
    hook = ReadDescriptionHook(tmp_path, {})
    hook.update(metadata := {})
    assert metadata["description"] == "A dosctring."
