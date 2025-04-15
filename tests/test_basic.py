"""Basic tests: Hook is found, works, and throws expected errors."""

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING, Any, Literal

import pytest
from hatchling.metadata.core import ProjectMetadata
from hatchling.plugin.manager import PluginManager
from packaging.metadata import Metadata

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from hatch_docstring_description.read_description import ReadDescriptionHook

# TODO(flying-sheep): should hatch support single file modules? "mypkg.py", "src/mypkg.py"
# https://github.com/flying-sheep/hatch-docstring-description/issues/14


PYPROJECT_TOML_BASIC = """\
[build-system]
requires = ['hatchling', 'hatch-docstring-description']
build-backend = 'hatchling.build'

[project]
name = '{proj_name}'
version = '1.0'
requires-python = '>=3.9'
dynamic = ['description']

[tool.hatch.metadata.hooks.docstring-description]
"""


def mk_project(root: Path, pkg_loc: Literal[".", "src"], proj_name: str = "mypkg") -> Path:
    project_path = root / proj_name
    project_path.mkdir()  # error if it exists
    (project_path / "pyproject.toml").write_text(PYPROJECT_TOML_BASIC.format(proj_name=proj_name))
    pkg_file_path = project_path / pkg_loc / "mypkg/__init__.py"
    pkg_file_path.parent.mkdir(parents=True, exist_ok=True)
    pkg_file_path.write_text('"""A docstring."""\n')
    return project_path


@pytest.fixture(params=[".", "src"])
def pkg_loc(request: pytest.FixtureRequest) -> Literal[".", "src"]:
    return request.param


@pytest.fixture
def basic_project(tmp_path: Path, pkg_loc: Literal[".", "src"]) -> Path:
    return mk_project(tmp_path, pkg_loc)


@pytest.fixture
def mk_multi_pkg_proj(tmp_path: Path, pkg_loc: Literal[".", "src"]) -> Callable[[str], Path]:
    def make(proj_name: str) -> Path:
        proj = mk_project(tmp_path, pkg_loc, proj_name=proj_name)
        prefix = "src/" if pkg_loc == "src" else ""
        with (proj / "pyproject.toml").open("a") as proj_file:
            proj_file.write(f"[tool.hatch.build.targets.wheel]\npackages = ['{prefix}mypkg', '{prefix}my_other_pkg']\n")
        (pkg2 := (proj / pkg_loc / "my_other_pkg")).mkdir()
        (pkg2 / "__init__.py").write_text('"""A second docstring."""\n')
        return proj

    return make


def get_hook_cls() -> type[ReadDescriptionHook]:
    pm = PluginManager()
    pm.metadata_hook.collect(include_third_party=True)
    plugin = pm.manager.get_plugin("docstring-description")
    return plugin.hatch_register_metadata_hook()


def mk_hook(project_path: Path) -> tuple[ReadDescriptionHook, dict[str, Any]]:
    hook_cls = get_hook_cls()
    hook = hook_cls(project_path, {})
    metadata = ProjectMetadata(project_path, None).config["project"]
    return hook, metadata


def test_load_plugin() -> None:
    from hatch_docstring_description.read_description import ReadDescriptionHook

    assert get_hook_cls() is ReadDescriptionHook


@pytest.mark.parametrize(("docstring", "expected"), [("A docstring.", "A docstring."), ("1.\n\n2", "1.")])
def test_read_description(tmp_path: Path, docstring: str, expected: str) -> None:
    from hatch_docstring_description.read_description import read_description

    path = tmp_path / "pkg.py"
    path.write_text(repr(docstring))
    assert read_description(path) == expected


def test_basic(basic_project: Path) -> None:
    hook, metadata = mk_hook(basic_project)
    hook.update(metadata)
    assert metadata["description"] == "A docstring."


def test_e2e(basic_project: Path, tmp_path: Path) -> None:
    import zipfile

    from build.__main__ import build_package

    out_dir = tmp_path / "dist"
    build_package(
        srcdir=basic_project,
        outdir=out_dir,
        distributions=["wheel"],
        isolation=False,
    )
    with (
        zipfile.ZipFile(out_dir / "mypkg-1.0-py3-none-any.whl", "r") as whl,
        whl.open("mypkg-1.0.dist-info/METADATA") as metadata_file,
    ):
        metadata = Metadata.from_email(metadata_file.read().decode("utf-8"))
    assert metadata.name == "mypkg"
    assert metadata.dynamic is None
    assert metadata.summary == "A docstring."


@pytest.mark.xfail(reason="plugin_manager.metadata_hook.get('...') doesn’t work yet")
def test_explicit(basic_project: Path, pkg_loc: Literal[".", "src"]) -> None:
    prefix = "src/" if pkg_loc == "src" else ""
    (basic_project / pkg_loc / "mypkg" / "core.py").write_text('"""A docstring somewhere else."""\n')
    with (basic_project / "pyproject.toml").open("a") as proj_file:
        proj_file.write(f"path = ['{prefix}mypkg/core.py']\n")
    hook, metadata = mk_hook(basic_project)
    hook.update(metadata)
    assert metadata["description"] == "A docstring somewhere else."


def test_multi_package(mk_multi_pkg_proj: Callable[[str], Path]) -> None:
    """When one package matches the project name, use that one’s docstring."""
    hook, metadata = mk_hook(mk_multi_pkg_proj("mypkg"))
    hook.update(metadata)
    assert metadata["description"] == "A docstring."


def test_multi_package_error(mk_multi_pkg_proj: Callable[[str], Path]) -> None:
    """If none of the packages match the project name, raise an error."""
    hook, metadata = mk_hook(mk_multi_pkg_proj("yet_other_name"))
    with pytest.raises(RuntimeError, match=r"Multiple packages are only supported if one matches the project name"):
        hook.update(metadata)


def test_field_error(basic_project: Path) -> None:
    (basic_project / "pyproject.toml").write_text("[project]\nname = 'mypkg'\n")
    hook, metadata = mk_hook(basic_project)
    with pytest.raises(TypeError, match=r"You need to add 'description'"):
        hook.update(metadata)


def test_no_package_error(tmp_path: Path) -> None:
    code = dedent(
        """\
        [project]
        name = 'mypkg'
        dynamic = ['description']
        [tool.hatch.build.targets.wheel]
        include = ['pyproject.toml']
        """,
    )
    (tmp_path / "pyproject.toml").write_text(code)
    hook, metadata = mk_hook(tmp_path)
    with pytest.raises(RuntimeError, match=r"No packages found"):
        hook.update(metadata)
