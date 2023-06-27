from pathlib import Path

import pytest
from hatchling.metadata.core import ProjectMetadata

from hatch_docstring_description.read_description import ReadDescriptionHook

# TODO: should hatch support single file modules? "mypkg.py", "src/mypkg.py"


@pytest.fixture(params=["mypkg/__init__.py", "src/mypkg/__init__.py"])
def basic_project(request, tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'mypkg'\ndynamic = ['description']")
    pkg_file_path = tmp_path / Path(request.param)
    pkg_file_path.parent.mkdir(parents=True, exist_ok=True)
    pkg_file_path.write_text('"""A docstring."""')
    yield pkg_file_path.parent if pkg_file_path.stem == "__init__" else pkg_file_path


def test_basic(tmp_path, basic_project):
    hook = ReadDescriptionHook(tmp_path, {})
    metadata = ProjectMetadata(tmp_path, None).config["project"]
    hook.update(metadata)
    assert metadata["description"] == "A docstring."
