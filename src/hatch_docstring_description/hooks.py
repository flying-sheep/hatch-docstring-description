from hatchling.plugin import hookimpl

from .read_description_hook import ReadDescriptionHook


@hookimpl
def hatch_register_metadata():
    return ReadDescriptionHook
