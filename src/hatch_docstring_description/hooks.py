"""Hook module referenced by ``hatch``’s entry point."""

from __future__ import annotations

from hatchling.plugin import hookimpl

from .read_description import ReadDescriptionHook


@hookimpl
def hatch_register_metadata_hook() -> type[ReadDescriptionHook]:
    """Pluggy hook implementation returning a hatch metadata hook class."""
    return ReadDescriptionHook
