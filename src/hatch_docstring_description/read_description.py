from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from hatchling.builders.wheel import WheelBuilder
from hatchling.metadata.plugin.interface import MetadataHookInterface


class DummyBuilder(WheelBuilder):
    def get_version_api() -> dict[str, Callable[[str, dict], str]]:
        return {}


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "docstring-description"

    def update(self, metadata: dict[str, Any]) -> None:
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        if self.config.get("path"):
            path = Path(self.root) / self.config["path"]
        else:
            packages = cast(list[str], DummyBuilder(self.root).config.packages)
            if len(packages) != 1:
                msg = "Multiple packages not supported" if len(packages) > 1 else f"No packages found in {self.root}"
                raise RuntimeError(msg)
            path = Path(self.root) / packages[0]
            path = (path / "__init__.py") if path.is_dir() else path.with_name(path.name + ".py")
        metadata["description"] = read_description(path)


def read_description(pkg_file: Path) -> str:
    """Returns the first sentence of the docstring."""
    return pkg_file.read_text()
