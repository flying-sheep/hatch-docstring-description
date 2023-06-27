import ast
from pathlib import Path
from typing import Any, cast

from hatchling.builders.wheel import WheelBuilder
from hatchling.metadata.plugin.interface import MetadataHookInterface


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "docstring-description"

    def update(self, metadata: dict[str, Any]) -> None:
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        if "description" in metadata or "description" not in metadata.get("dynamic", []):
            msg = "You need to add 'description' to your `dynamic` fields and not to `[project]`."
            raise TypeError(msg)

        if self.config.get("path"):
            path = Path(self.root) / self.config["path"]
        else:
            packages = cast(list[str], WheelBuilder(self.root).config.packages)
            if len(packages) != 1:
                msg = "Multiple packages not supported" if len(packages) > 1 else f"No packages found in {self.root}"
                raise RuntimeError(msg)
            stem = Path(self.root) / packages[0]
            path = (stem / "__init__.py") if stem.is_dir() else stem.with_name(f"{stem.name}.py")
        metadata["description"] = read_description(path)


def read_description(pkg_file: Path) -> str:
    """Returns the first sentence of the docstring."""
    mod = ast.parse(pkg_file.read_text(), pkg_file)
    return ast.get_docstring(mod)
