from pathlib import Path


def read_description(pkg_dir: Path) -> str:
    """Returns the first sentence of the docstring."""
    return pkg_dir.read_text()
