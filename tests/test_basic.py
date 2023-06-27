from pathlib import Path

import pytest

from hatch_docstring_description.read_description import ReadDescriptionHook


@pytest.fixture(params=["mypkg.py", "src/mypkg.py", "mypkg/__init__.py", "src/mypkg/__init__.py"])
def basic_package(request, tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'mypkg'")
    pkg_file_path = tmp_path / request.param
    pkg_file_path.parent.mkdir(parents=True)
    pkg_file_path.write_text('"""A docstring."""')
    yield pkg_file_path.parent if pkg_file_path.stem == "__init__" else pkg_file_path


def test_basic(tmp_path, basic_package):
    hook = ReadDescriptionHook(tmp_path, {})
    hook.update(metadata := {})
    assert metadata["description"] == "A docstring."
