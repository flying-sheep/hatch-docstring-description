"""Basic tests: Hook is found, works, and throws expected errors."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

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
    (pkg_path / "pyproject.toml").write_text("[project]\nname = 'mypkg'\ndynamic = ['description']\n")
    pkg_file_path = pkg_path / Path(request.param)
    pkg_file_path.parent.mkdir(parents=True, exist_ok=True)
    pkg_file_path.write_text('"""A docstring."""\n')
    return pkg_path


@pytest.fixture()
def multi_pkg_project(basic_project: Path) -> Generator[Path, None, None]:
    pkgs_dir = (basic_project / "src") if (basic_project / "src").is_dir() else basic_project
    prefix = "src/" if pkgs_dir.name == "src" else ""
    with (basic_project / "pyproject.toml").open("a") as proj_file:
        proj_file.write(f"[tool.hatch.build.targets.wheel]\npackages = ['{prefix}mypkg', '{prefix}my_other_pkg']\n")
    (pkg2 := (pkgs_dir / "my_other_pkg")).mkdir()
    (pkg2 / "__init__.py").write_text('"""A second docstring."""\n')
    return basic_project


def mk_hook(project_path: Path) -> tuple[ReadDescriptionHook, dict[str, Any]]:
    hook = ReadDescriptionHook(project_path, {})
    metadata = ProjectMetadata(project_path, None).config["project"]
    return hook, metadata


def test_basic(basic_project: Path) -> None:
    hook, metadata = mk_hook(basic_project)
    hook.update(metadata)
    assert metadata["description"] == "A docstring."


def test_field_error(basic_project: Path) -> None:
    (basic_project / "pyproject.toml").write_text("[project]\nname = 'mypkg'\n")
    hook, metadata = mk_hook(basic_project)
    with pytest.raises(TypeError, match=r"You need to add 'description'"):
        hook.update(metadata)


def test_multi_package_error(multi_pkg_project: Path) -> None:
    hook, metadata = mk_hook(multi_pkg_project)
    with pytest.raises(RuntimeError, match=r"Multiple packages not supported"):
        hook.update(metadata)


def test_no_package_error(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'mypkg'\ndynamic = ['description']\n")
    hook, metadata = mk_hook(tmp_path)
    with pytest.raises(RuntimeError, match=r"No packages found"):
        hook.update(metadata)


def test_load_plugin() -> None:
    pm = PluginManager()
    pm.metadata_hook.collect(include_third_party=True)
    plugin = pm.manager.get_plugin("docstring-description")
    assert plugin.hatch_register_metadata() is ReadDescriptionHook
