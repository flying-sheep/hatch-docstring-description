from hatchling.plugin import hookimpl

from .read_description import ReadDescriptionHook


@hookimpl
def hatch_register_metadata():
    return ReadDescriptionHook
