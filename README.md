# hatch-docstring-description

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-docstring-description.svg)](https://pypi.org/project/hatch-docstring-description)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-docstring-description.svg)](https://pypi.org/project/hatch-docstring-description)
[![Coverage](https://codecov.io/github/flying-sheep/hatch-docstring-description/branch/main/graph/badge.svg?token=FZCw1cXSTL)](https://codecov.io/github/flying-sheep/hatch-docstring-description)

## Usage

1. Include it as a plugin to your `pyproject.toml`:

   ```toml
   [build-system]
   requires = ["hatchling", "hatch-docstring-description"]
   build-backend = "hatchling.build"
   ```

2. Mark your `description` field as `dynamic`:

   ```toml
   [project]
   dynamic = ["description"]
   ```

## License

`hatch-docstring-description` is distributed under the terms of the [GPL 3 (or later)](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
