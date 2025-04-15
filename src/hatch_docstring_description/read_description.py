"""Implementation of the hook class."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path, PurePath
from typing import Any

from hatchling.builders.wheel import WheelBuilder, WheelBuilderConfig
from hatchling.metadata.plugin.interface import MetadataHookInterface
from hatchling.metadata.utils import normalize_project_name


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "docstring-description"

    def update(self, metadata: dict[str, Any]) -> None:
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""
        if ("update", __file__) in ((frame.function, frame.filename) for frame in inspect.stack()[1:]):
            return

        if "description" in metadata or "description" not in metadata.get("dynamic", []):
            msg = "You need to add 'description' to your `dynamic` fields and not to `[project]`."
            raise TypeError(msg)

        if self.config.get("path"):
            path = Path(self.root) / self.config["path"]
        else:
            cfg: WheelBuilderConfig = WheelBuilder(self.root).config
            if len(cfg.packages) == 0:
                msg = f"No packages found in {self.root}."
                raise RuntimeError(msg)
            if (pkg := _get_pkg(cfg)) is None:
                msg = "Multiple packages are only supported if one matches the project name."
                raise RuntimeError(msg)
            stem = Path(self.root) / pkg
            path = (stem / "__init__.py") if stem.is_dir() else stem.with_name(f"{stem.name}.py")
        metadata["description"] = read_description(path)


def _get_pkg(cfg: WheelBuilderConfig) -> PurePath | None:
    """Get only package or package matching the project name."""
    if len(cfg.packages) == 1:
        return PurePath(cfg.packages[0])
    for pkg in map(PurePath, cfg.packages):
        pkg_name = pkg.name
        if normalize_project_name(pkg_name) == cfg.builder.metadata.name:
            return pkg
    return None


def read_description(pkg_file: Path) -> str:
    """Return the first sentence of the docstring."""
    mod = ast.parse(pkg_file.read_text(), pkg_file)
    docstring = ast.get_docstring(mod)
    return docstring.strip().split("\n\n", 1)[0]
