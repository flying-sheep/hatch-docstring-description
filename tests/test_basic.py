"""Basic tests: Hook is found, works, and throws expected errors."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager

from hatch_docstring_description.read_description import ReadDescriptionHook

if TYPE_CHECKING:
    from collections.abc import Generator

# TODO(flying-sheep): should hatch support single file modules? "mypkg.py", "src/mypkg.py"
# https://github.com/flying-sheep/hatch-docstring-description/issues/14


@pytest.fixture(params=["mypkg/__init__.py", "src/mypkg/__init__.py"])
def basic_project(request: pytest.FixtureRequest, tmp_path: Path) -> Generator[Path, None, None]:
    pkg_path = tmp_path / "mypkg"
    pkg_path.mkdir()  # error if it exists
    (pkg_path / "pyproject.toml").write_text("[project]\nname = 'mypkg'\ndynamic = ['description']")
    pkg_file_path = pkg_path / Path(request.param)
    pkg_file_path.parent.mkdir(parents=True, exist_ok=True)
    pkg_file_path.write_text('"""A docstring."""')
    return pkg_path


def test_basic(tmp_path: Path, basic_project: Path) -> None:
    hook = ReadDescriptionHook(basic_project, {})
    metadata = ProjectMetadata(basic_project, None).config["project"]
    hook.update(metadata)
    assert metadata["description"] == "A docstring."


def test_field_error(basic_project: Path) -> None:
    (basic_project / "pyproject.toml").write_text("[project]\nname = 'mypkg'")
    hook = ReadDescriptionHook(basic_project, {})
    metadata = ProjectMetadata(basic_project, None).config["project"]
    with pytest.raises(TypeError, match=r"You need to add 'description'"):
        hook.update(metadata)


def test_load_plugin() -> None:
    pm = PluginManager()
    pm.metadata_hook.collect(include_third_party=True)
    plugin = pm.manager.get_plugin("docstring-description")
    assert plugin.hatch_register_metadata() is ReadDescriptionHook
