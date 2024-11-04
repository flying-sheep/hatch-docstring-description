"""Implementation of the hook class."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Any

from hatchling.builders.wheel import WheelBuilder, WheelBuilderConfig
from hatchling.metadata.plugin.interface import MetadataHookInterface


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
            if len(cfg.packages) != 1:
                msg = (
                    "Multiple packages not supported" if len(cfg.packages) > 1 else f"No packages found in {self.root}"
                )
                raise RuntimeError(msg)
            stem = Path(self.root) / cfg.packages[0]
            path = (stem / "__init__.py") if stem.is_dir() else stem.with_name(f"{stem.name}.py")
        metadata["description"] = read_description(path)


def read_description(pkg_file: Path) -> str:
    """Return the first sentence of the docstring."""
    mod = ast.parse(pkg_file.read_text(), pkg_file)
    return ast.get_docstring(mod)
