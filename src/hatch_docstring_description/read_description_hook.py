from pathlib import Path
from typing import Any, Callable

from hatchling.builders.config import BuilderConfig
from hatchling.builders.plugin.interface import BuilderInterface
from hatchling.metadata.plugin.interface import MetadataHookInterface

from .read_description import read_description


class DummyBuilder(BuilderInterface):
    PLUGIN_NAME = "wheel"

    def get_version_api() -> dict[str, Callable[[str, dict], str]]:
        return {}


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "docstring-description"

    def update(self, metadata: dict[str, Any]) -> None:
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        builder = DummyBuilder(self.root, config=self.config)
        cfg = BuilderConfig(
            builder,
            root=self.root,
            plugin_name=builder.PLUGIN_NAME,
            build_config=builder.build_config,
            target_config=builder.target_config,
        )
        if len(cfg.packages) != 1:
            msg = "Multiple packages not supported" if len(cfg.packages) > 1 else f"No packages found in {self.root}"
            raise RuntimeError(msg)

        path = Path(self.config.get("path", cfg.packages[0]))
        metadata["description"] = read_description(Path(self.root) / path)
