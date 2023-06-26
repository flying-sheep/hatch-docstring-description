from hatchling.metadata.plugin.interface import MetadataHookInterface


class ReadDescriptionHook(MetadataHookInterface):
    """Metadata hook reading the first sentence of the docstring into `description`."""

    PLUGIN_NAME = "custom"

    def update(self, metadata):
        """See https://ofek.dev/hatch/latest/plugins/metadata-hook/ for more information."""

        metadata["description"] = read_description()
