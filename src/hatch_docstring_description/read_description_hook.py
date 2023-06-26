from pathlib import Path
from typing import Any

from hatchling.metadata.plugin.interface import MetadataHookInterface

from .read_description import read_description


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "docstring-description"

    def update(self, metadata: dict[str, Any]) -> None:
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        path = Path(self.config.get("path", path))
        metadata["description"] = read_description(Path(self.root) / path)
